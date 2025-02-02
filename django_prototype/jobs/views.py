from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import is_aware, make_aware

from .dbconnection import get_scheduled_jobs_ohne_MachStatus, get_unscheduled_jobs_ohne_MachStatus
from .models import Job
from .serializer import JobsSerializer
import pandas as pd
from collections import OrderedDict
import os
import sys
from datetime import datetime, timedelta, time, date
import pytz
from django.utils import timezone
date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir_path)

scripts_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','scripts/PL_Optimizer/PL_Optimizer'))
sys.path.append(scripts_dir_path)
from Main_Optimization import Optimization

import signal
import psutil
import multiprocessing
import csv
import re
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from decimal import Decimal
from itertools import groupby

pid = []
holidays = []

def is_working_day(time):
    return time.weekday() < 5  # 0 to 4 correspond to Monday to Friday

def is_working_hour(time):
    start_hour = 7
    end_hour = 23
    return start_hour <= time.hour < end_hour

def get_next_working_day(current_time):
    while current_time:
        current_time += timedelta(days=1)
        current_time = current_time.replace(hour=7, minute=0, second=0, microsecond=0)
        if is_working_day(current_time):
            return current_time

def delete_all_elements(my_list):
    for i in range(len(my_list) - 1, -1, -1):
        del my_list[i]
    return my_list

def format_ind_time(date_str):
    # extract timezone offset from string
    match = re.search(r'GMT([\+\-]\d{4})', date_str)
    if not match:
        raise ValueError('Invalid date string: no timezone offset found',date_str)
    tz_offset_str = match.group(1)
    # convert timezone offset string to timedelta object
    tz_offset = timedelta(hours=int(tz_offset_str[1:3]), minutes=int(tz_offset_str[3:5]))
    # remove timezone information from string
    date_str = re.sub(r'GMT[\+\-]\d{4}\s+\(.+\)', '', date_str).strip()

    # parse datetime string and add timezone offset
    date_obj = datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S')
    date_obj -= tz_offset

    # format datetime object as ISO 8601 string
    final_date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # print(final_date_str)
    return final_date_str

def is_valid_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        return True
    except ValueError:
        return False

def run_PL_optimizer_in_diff_process_IEM(self, request, input_jobs):
    df = pd.DataFrame(input_jobs)
    # change data types
    df['Start'] = pd.to_datetime(df['Start'])
    df['Ende'] = pd.to_datetime(df['Ende'])
    df['LTermin'] = pd.to_datetime(df['LTermin'])
    df['Lieferdatum_Rohmaterial'] = pd.to_datetime(df['Lieferdatum_Rohmaterial'])
    df['Ruestzeit_Soll'] = df['Ruestzeit_Soll'].astype(int)
    df['Laufzeit_Soll'] = df['Laufzeit_Soll'].astype(int)
    df['Zeit_Soll'] = df['Zeit_Soll'].astype(int)
    # build and rename columns
    df['Release_Date'] = df['Lieferdatum_Rohmaterial'] + pd.Timedelta(days=1)
    df = df.rename(columns = {'LTermin': 'Due_Date', 'Fefco_Teil': 'FEFCO_Teil'}) # rename, because the new Schulte data has different column names

    # divide data by machines: Each machine gets a unique df
    data = {}

    for machine in df.Maschine.unique():
        data[machine] = df[df.Maschine == machine].sort_values('Start').reset_index(drop=True)
        df_test = data[machine].reset_index(drop=True)
        df_test.head()
        schedule, meta_params  = Optimization(df_test)
        schedule = schedule.rename(columns = {'Due_Date': 'LTermin', 'FEFCO_Teil': 'Fefco_Teil'})
        schedule['Start'] = schedule['Start'].astype(str)
        schedule['Ende'] = schedule['Ende'].astype(str)

        # Convert the schedule DataFrame to a list of dictionaries
        sorted_jobs = schedule.to_dict(orient='records')

        # Initialize variables
        machine_current_time = {}  # Dictionary to track current time for each machine

        # Get the current server time in the specified timezone
        timezone = pytz.timezone('Europe/Berlin')
        server_time = datetime.now(timezone)

        # Define the production time range
        start_hour = 7
        end_hour = 23

        # Check if today is a working day
        if not is_working_day(server_time):
            server_time = get_next_working_day(server_time)

        job_instances = []

        # Loop through the data and create Job instances
        for item in sorted_jobs:
            job_instance = Job(
                Fefco_Teil=item['Fefco_Teil'],
                ArtNr_Teil=item['ArtNr_Teil'],
                AKNR=item['AKNR'],
                TeilNr=item['TeilNr'],
                SchrittNr=item['SchrittNr'],
                Maschine=item['Maschine'],
                Start=item['Start'],  # Keep up to six decimal places for seconds
                Ende=item['Ende'], 
                Ruestzeit_Ist=item['Ruestzeit_Ist'],
                Ruestzeit_Soll=item['Ruestzeit_Soll'],
                Laufzeit_Soll=item['Laufzeit_Soll'],
                Lieferdatum_Rohmaterial=item['Lieferdatum_Rohmaterial'],
                LTermin=item['LTermin'],
            )
            job_instances.append(job_instance)
        sorted_jobs = job_instances

        # Iterate through the sorted jobs and schedule them
        for machine_jobs in groupby(sorted_jobs, key=lambda job: job.Maschine):
            # Get the machine and its corresponding jobs
            machine, jobs = machine_jobs

            # Sort the machine jobs based on 'Laufzeit_Soll'
            sorted_machine_jobs = jobs#sorted(jobs, key=lambda job: job.Laufzeit_Soll)

            for job in sorted_machine_jobs:
                # Consider setup time for new jobs
                if machine in machine_current_time:
                    current_time = machine_current_time[machine]
                else:
                    # Adjust the current server time based on daylight saving time
                    if not is_aware(server_time):
                        server_time = make_aware(server_time, timezone)
                    current_time = server_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)

                # Move to the next working day if the current time is not within working hours
                while current_time and not is_working_hour(current_time):
                    current_time = get_next_working_day(current_time)

                # If there is no valid working time for scheduling, move this job to the next production day
                if not current_time:
                    current_time = get_next_working_day(server_time)
                    while current_time and not is_working_hour(current_time):
                        current_time = get_next_working_day(current_time)

                start_time = current_time + timedelta(minutes=int(job.Ruestzeit_Ist))
                end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                # Check if the job.end time exceeds the working hours (11 PM)
                if end_time.hour >= 23:
                    # Unassign start and end times for this job to reschedule it the next morning at 7 AM
                    start_time = None
                    end_time = None
                else:
                    # Check if the job.start time is earlier than the working hours (7 AM)
                    if start_time.hour < 7:
                        # Adjust the job.start time to the first working hour (7 AM)
                        start_time = start_time.replace(hour=7, minute=0)
                        end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                # Save the job's start and end times
                job_instance = Job.objects.get(AKNR=job.AKNR, TeilNr=job.TeilNr, SchrittNr=job.SchrittNr, Fefco_Teil=job.Fefco_Teil, ArtNr_Teil=job.ArtNr_Teil)
                job_instance.Start = start_time
                job_instance.Ende = end_time
                job_instance.save()

                # Update the current time for the machine
                machine_current_time[machine] = end_time

        # Handle unscheduled jobs (jobs without valid schedules)
        unscheduled_jobs = Job.objects.filter(Start=None, Ende=None)
        for job in unscheduled_jobs:
            # Assign start and end times without checking for constraints
            start_time = server_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            start_time += timedelta(days=1)  # Move to the next production day
            start_time += timedelta(minutes=int(job.Ruestzeit_Ist))
            end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

            # Save the job's start and end times
            job_instance = Job.objects.get(AKNR=job.AKNR, TeilNr=job.TeilNr, SchrittNr=job.SchrittNr, Fefco_Teil=job.Fefco_Teil, ArtNr_Teil=job.ArtNr_Teil)
            job_instance.Start = start_time
            job_instance.Ende = end_time
            job_instance.save()

def run_PL_optimizer_in_diff_process_Bielefeld(self, request, input_jobs):
    df = pd.DataFrame(input_jobs)
    # change data types
    df['Start'] = pd.to_datetime(df['Start'])
    df['Ende'] = pd.to_datetime(df['Ende'])
    df['LTermin'] = pd.to_datetime(df['LTermin'])
    df['Lieferdatum_Rohmaterial'] = pd.to_datetime(df['Lieferdatum_Rohmaterial'])
    df['Ruestzeit_Soll'] = df['Ruestzeit_Soll'].astype(int)
    df['Laufzeit_Soll'] = df['Laufzeit_Soll'].astype(int)
    df['Zeit_Soll'] = df['Zeit_Soll'].astype(int)
    # build and rename columns
    df['Release_Date'] = df['Lieferdatum_Rohmaterial'] + pd.Timedelta(days=1)
    df = df.rename(columns = {'LTermin': 'Due_Date', 'Fefco_Teil': 'FEFCO_Teil'}) # rename, because the new Schulte data has different column names

    # divide data by machines: Each machine gets a unique df
    data = {}

    for machine in df.Maschine.unique():
        data[machine] = df[df.Maschine == machine].sort_values('Start').reset_index(drop=True)
        # machine = 'SL12'
        # production_start = pd.Timestamp(date(2017, 3, 10)) # datetime.date(2015, 1, 14)
        # get data which is released before production start and has a due data not before one day after production start
        df_test = data[machine].reset_index(drop=True)
        df_test.head()
        schedule, meta_params  = Optimization(df_test)
        schedule = schedule.rename(columns = {'Due_Date': 'LTermin', 'FEFCO_Teil': 'Fefco_Teil'})
        schedule['Start'] = schedule['Start'].astype(str)
        schedule['Ende'] = schedule['Ende'].astype(str)

        # Convert the schedule DataFrame to a list of dictionaries
        schedule_list = schedule.to_dict(orient='records')

        # Update the database objects with the optimized schedule
        for job_data in schedule_list:
            job_instance = Job.objects.get(AKNR=job_data['AKNR'], TeilNr=job_data['TeilNr'], SchrittNr=job_data['SchrittNr'], Fefco_Teil=job_data['Fefco_Teil'], ArtNr_Teil=job_data['ArtNr_Teil'])
            job_instance.Start = pd.to_datetime(job_data.get('Start')).strftime("%Y-%m-%dT%H:%M:%SZ") if job_data.get('Start') else None
            job_instance.Ende = pd.to_datetime(job_data.get('Ende')).strftime("%Y-%m-%dT%H:%M:%SZ") if job_data.get('Ende') else None
            job_instance.save()

class JobsViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobsSerializer
    lookup_field = 'AKNR'
    pid = None
    parser_classes = (MultiPartParser,)

    # updates a single job, put call
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True) # if partial=False, it updates all fields
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # gets all jobs
    @action(detail=False, methods=['get'])
    def getSchedule(self, request):
        # Get schedule data from the database
        aknr = request.query_params.get('AKNR')
        Fefco_Teil = request.query_params.get('Fefco_Teil')
        ArtNr_Teil = request.query_params.get('ArtNr_Teil')
        teilnr = request.query_params.get('TeilNr')
        schrittnr = request.query_params.get('SchrittNr')

        if aknr is not None and teilnr is not None and schrittnr is not None:
            jobs = Job.objects.filter(Fefco_Teil=Fefco_Teil, ArtNr_Teil=ArtNr_Teil, AKNR=aknr, TeilNr=teilnr, SchrittNr=schrittnr)
        else:
            jobs = Job.objects.all()

        serializer = JobsSerializer(jobs, many=True)
        json_obj = {'Table': serializer.data}
  
        return JsonResponse(json_obj, status=status.HTTP_200_OK)

    # updates a batch of jobs
    # @action(detail=False, methods=['post'])
    # def setSchedule(self, request):
    #     jobs_data = request.data["jobs_data"] # assuming the request payload contains a list of jobs
    #     for job_data in jobs_data:
    #         try:
    #             job_instance = Job.objects.get(AKNR=job_data['AKNR'], TeilNr=job_data['TeilNr'], SchrittNr=job_data['SchrittNr'])
    #             print("job_instance",job_instance)
    #             job_data['Start'] = datetime.strptime(job_data['Start'], date_format)
    #             job_data['Ende'] = datetime.strptime(job_data['Ende'], date_format)
    #             serializer = self.get_serializer(job_instance, data=job_data, partial=True)
    #             serializer.is_valid(raise_exception=True)
    #             self.perform_update(serializer)
    #         except:
    #             # handle exception here
    #             pass
    #     return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def uploadCSV(self, request):
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({'error': 'Keine Datei bereitgestellt'}, status=status.HTTP_400_BAD_REQUEST)

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            jobs_data = list(reader)

            for job_data in jobs_data:
                job_instance = Job()
                job_instance.Fefco_Teil = job_data.get('Fefco_Teil')
                job_instance.ArtNr_Teil = job_data.get('ArtNr_Teil')
                job_instance.ID_Druck = job_data.get('ID_Druck')
                if str(job_data.get('Druckflaeche')) != 'NULL' and str(job_data.get('Druckflaeche')) != '':
                    job_instance.Druckflaeche = job_data.get('Druckflaeche')
                job_instance.Bogen_Laenge_Brutto = job_data.get('Bogen_Laenge_Brutto')
                job_instance.Bogen_Breite_Brutto = job_data.get('Bogen_Breite_Brutto')
                job_instance.Maschine = job_data.get('Maschine')
                job_instance.Start = parse_datetime(job_data.get('Start')) if job_data.get('Start') else None
                job_instance.Ende = parse_datetime(job_data.get('Ende')) if job_data.get('Ende') else None
                job_instance.Ruestzeit_Ist = job_data.get('Ruestzeit_Ist')
                job_instance.Ruestzeit_Soll = job_data.get('Ruestzeit_Soll')
                job_instance.Laufzeit_Ist = job_data.get('Laufzeit_Ist')
                job_instance.Laufzeit_Soll = job_data.get('Laufzeit_Soll')
                job_instance.Zeit_Ist = job_data.get('Zeit_Ist')
                job_instance.Zeit_Soll = job_data.get('Zeit_Soll')
                job_instance.Werkzeug_Nutzen = job_data.get('Werkzeug_Nutzen')
                job_instance.Bestell_Nutzen = job_data.get('Bestell_Nutzen')
                job_instance.Menge_Soll = job_data.get('Menge_Soll')
                job_instance.Menge_Ist = job_data.get('Menge_Ist')
                job_instance.Bemerkung = job_data.get('Bemerkung')
                job_instance.LTermin = parse_datetime(job_data.get('LTermin')) if job_data.get('LTermin') else None
                job_instance.KndNr = job_data.get('KndNr')
                job_instance.Suchname = job_data.get('Suchname')
                job_instance.AKNR = job_data.get('AKNR')
                job_instance.TeilNr = job_data.get('TeilNr')
                job_instance.SchrittNr = job_data.get('SchrittNr')
                job_instance.Summe_Minuten = job_data.get('Summe_Minuten')
                job_instance.ID_Maschstatus = job_data.get('ID_Maschstatus')
                job_instance.Maschstatus = job_data.get('Maschstatus')

                lieferdatum = job_data.get('Lieferdatum_Rohmaterial')
                date_regex = r'\d{1,2}/\d{1,2}/\d{4}'  # dd.mm.yyyy pattern
                if re.match(date_regex, str(lieferdatum)):
                    l_d = datetime.strptime(str(lieferdatum), "%m/%d/%Y").strftime("%Y-%m-%d 00:00:00.000")
                    print("l_d",l_d)
                    job_instance.Lieferdatum_Rohmaterial = parse_datetime(l_d)

                job_instance.BE_Erledigt = job_data.get('BE_Erledigt')
                job_instance.save()

            message = "Hochladen erfolgreich"
            return Response({"message": message}, status=status.HTTP_200_OK)

        except Exception as e:
                # If an exception occurs during the execution of the function, the code inside this block will handle it.
                # You can customize the error message and status code to suit your needs.
                error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
                return Response({"message": error_message})

    @action(detail=False, methods=['post'])
    def deleteJobs(self, request):
        try:
            Job.objects.all().delete() # delete all objects in Job model
            message = "Alle Jobs wurden erfolgreich gelöscht"
            return Response({"message": message}, status=status.HTTP_200_OK)
        
        except Exception as e:
            # If an exception occurs during the execution of the function, the code inside this block will handle it.
            # You can customize the error message and status code to suit your needs.
            error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
            return Response({"message": error_message})

    # runs PL optimizer IEM
    @action(detail=False, methods=['post'])
    def run_preference_learning_optimizer_IEM(self, request):
        try:
            jobs = Job.objects.all()
            serializer = JobsSerializer(jobs, many=True)
            input_jobs = serializer.data
            p = multiprocessing.Process(target=run_PL_optimizer_in_diff_process_IEM, args=(self,request,input_jobs,))
            p.start()
            pid.append(p.pid)
            p.join()
            response = {'message': 'Preference Learning-Optimierer abgeschlossen.'}
            return Response(response)
        except Exception as e:
            # If an exception occurs during the execution of the function, the code inside this block will handle it.
            # You can customize the error message and status code to suit your needs.
            error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
            return Response({"message": error_message})
     
    # runs PL optimizer Bielefeld
    @action(detail=False, methods=['post'])
    def run_preference_learning_optimizer_Bielefeld(self, request):
        try:
            jobs = Job.objects.all()
            serializer = JobsSerializer(jobs, many=True)
            input_jobs = serializer.data
            p = multiprocessing.Process(target=run_PL_optimizer_in_diff_process_Bielefeld, args=(self,request,input_jobs,))
            p.start()
            pid.append(p.pid)
            p.join()
            response = {'message': 'Preference Learning-Optimierer abgeschlossen.'}
            return Response(response)
        except Exception as e:
            # If an exception occurs during the execution of the function, the code inside this block will handle it.
            # You can customize the error message and status code to suit your needs.
            error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
            return Response({"message": error_message})
       
    @action(detail=False, methods=['post'])
    def run_sjf(self, request):
        try:
            # Retrieve the jobs from the database
            jobs = Job.objects.all()

            # Sort the jobs based on 'Laufzeit_Soll' (running time) in ascending order (SJF)
            sorted_jobs = sorted(jobs, key=lambda job: int(job.Laufzeit_Soll))

            # Initialize variables
            machine_current_time = {}  # Dictionary to track current time for each machine

            # Get the current server time in the specified timezone
            timezone = pytz.timezone('Europe/Berlin')
            server_time = datetime.now(timezone)

            # Define the production time range
            start_hour = 7
            end_hour = 23

            # Check if today is a working day
            if not is_working_day(server_time):
                server_time = get_next_working_day(server_time)

            # Iterate through the sorted jobs and schedule them
            for machine_jobs in groupby(sorted_jobs, key=lambda job: job.Maschine):
                # Get the machine and its corresponding jobs
                machine, jobs = machine_jobs

                # Sort the machine jobs based on 'Laufzeit_Soll'
                sorted_machine_jobs = sorted(jobs, key=lambda job: int(job.Laufzeit_Soll))
                for job in sorted_machine_jobs:
                    # Consider setup time for new jobs
                    if machine in machine_current_time:
                        current_time = machine_current_time[machine]
                    else:
                        # Adjust the current server time based on daylight saving time
                        if not is_aware(server_time):
                            server_time = make_aware(server_time, timezone)
                        current_time = server_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)

                    # Move to the next working day if the current time is not within working hours
                    while current_time and not is_working_hour(current_time):
                        current_time = get_next_working_day(current_time)

                    # If there is no valid working time for scheduling, move this job to the next production day
                    if not current_time:
                        current_time = get_next_working_day(server_time)
                        while current_time and not is_working_hour(current_time):
                            current_time = get_next_working_day(current_time)

                    start_time = current_time + timedelta(minutes=int(job.Ruestzeit_Soll))
                    end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                    # Check if the job.end time exceeds the working hours (11 PM)
                    if end_time.hour >= 23:
                        # Unassign start and end times for this job to reschedule it the next morning at 7 AM
                        start_time = None
                        end_time = None
                    else:
                        # Check if the job.start time is earlier than the working hours (7 AM)
                        if start_time.hour < 7:
                            # Adjust the job.start time to the first working hour (7 AM)
                            start_time = start_time.replace(hour=7, minute=0)
                            end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                    # Save the job's start and end times
                    job.Start = start_time
                    job.Ende = end_time
                    job.save()

                    # Update the current time for the machine
                    machine_current_time[machine] = end_time

            # Handle unscheduled jobs (jobs without valid schedules)
            unscheduled_jobs = Job.objects.filter(Start=None, Ende=None)
            for job in unscheduled_jobs:
                # Assign start and end times without checking for constraints
                start_time = server_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
                start_time += timedelta(days=1)  # Move to the next production day
                start_time += timedelta(minutes=int(job.Ruestzeit_Soll))
                end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                # Save the job's start and end times
                job.Start = start_time
                job.Ende = end_time
                job.save()

            # Return response
            return Response({'message': 'SJF abgeschlossen.'})
            
        except Exception as e:
            # If an exception occurs during the execution of the function, the code inside this block will handle it.
            # You can customize the error message and status code to suit your needs.
            error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
            return Response({"message": error_message})

    @action(detail=False, methods=['post'])
    def run_deadline_first(self, request):
        try:
            # Retrieve the jobs from the database
            jobs = Job.objects.all()

            # Sort the jobs based on 'Laufzeit_Soll' (running time) in ascending order (SJF)
            sorted_jobs = sorted(jobs, key=lambda job: job.LTermin)

            # Initialize variables
            machine_current_time = {}  # Dictionary to track current time for each machine

            # Get the current server time in the specified timezone
            timezone = pytz.timezone('Europe/Berlin')
            server_time = datetime.now(timezone)

            # Define the production time range
            start_hour = 7
            end_hour = 23

            # Check if today is a working day
            if not is_working_day(server_time):
                server_time = get_next_working_day(server_time)

            # Iterate through the sorted jobs and schedule them
            for machine_jobs in groupby(sorted_jobs, key=lambda job: job.Maschine):
                # Get the machine and its corresponding jobs
                machine, jobs = machine_jobs

                # Sort the machine jobs based on 'LTermin'
                sorted_machine_jobs = sorted(jobs, key=lambda job: job.LTermin)

                for job in sorted_machine_jobs:
                    # Consider setup time for new jobs
                    if machine in machine_current_time:
                        current_time = machine_current_time[machine]
                    else:
                        # Adjust the current server time based on daylight saving time
                        if not is_aware(server_time):
                            server_time = make_aware(server_time, timezone)
                        current_time = server_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)

                    # Move to the next working day if the current time is not within working hours
                    while current_time and not is_working_hour(current_time):
                        current_time = get_next_working_day(current_time)

                    # If there is no valid working time for scheduling, move this job to the next production day
                    if not current_time:
                        current_time = get_next_working_day(server_time)
                        while current_time and not is_working_hour(current_time):
                            current_time = get_next_working_day(current_time)

                    start_time = current_time + timedelta(minutes=int(job.Ruestzeit_Soll))
                    end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                    # Check if the job.end time exceeds the working hours (11 PM)
                    if end_time.hour >= 23:
                        # Unassign start and end times for this job to reschedule it the next morning at 7 AM
                        start_time = None
                        end_time = None
                    else:
                        # Check if the job.start time is earlier than the working hours (7 AM)
                        if start_time.hour < 7:
                            # Adjust the job.start time to the first working hour (7 AM)
                            start_time = start_time.replace(hour=7, minute=0)
                            end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                    # Save the job's start and end times
                    job.Start = start_time
                    job.Ende = end_time
                    job.save()

                    # Update the current time for the machine
                    machine_current_time[machine] = end_time

            # Handle unscheduled jobs (jobs without valid schedules)
            unscheduled_jobs = Job.objects.filter(Start=None, Ende=None)
            for job in unscheduled_jobs:
                # Assign start and end times without checking for constraints
                start_time = server_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
                start_time += timedelta(days=1)  # Move to the next production day
                start_time += timedelta(minutes=int(job.Ruestzeit_Soll))
                end_time = start_time + timedelta(minutes=int(job.Laufzeit_Soll))

                # Save the job's start and end times
                job.Start = start_time
                job.Ende = end_time
                job.save()

            # Return response
            return Response({'message': 'Deadline first abgeschlossen.'})

        except Exception as e:
            # If an exception occurs during the execution of the function, the code inside this block will handle it.
            # You can customize the error message and status code to suit your needs.
            error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
            return Response({"message": error_message})

    @action(detail=False, methods=['post'])
    def stop_PL_optimizer(self, request):
        try:
            os.kill(pid[0], signal.SIGTERM)
            delete_all_elements(pid)
            return Response({'message': 'Stoppen des PL-Optimierers abgeschlossen.'})
        except OSError:
            pass
        delete_all_elements(pid)
        return Response({'message': 'Der laufende PL-Optimierer konnte nicht gefunden werden.'}) 

    # updates a jobs
    @action(detail=False, methods=['post'])
    def setInd(self, request):
        try:
            job_data = request.data.copy()
            print("job_data",job_data)
            job_instance = Job.objects.get(AKNR=job_data['AKNR'], TeilNr=job_data['TeilNr'], SchrittNr=job_data['SchrittNr'], Fefco_Teil=job_data['Fefco_Teil'], ArtNr_Teil=job_data['ArtNr_Teil'])
            print("job_instance",job_instance)
            if 'Start' in job_data and 'Ende' in job_data:
                job_data['Start'] = job_data['Start']
                job_data['Ende'] = job_data['Ende']

            serializer = self.get_serializer(job_instance, data=job_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            message = "Der Auftrag wurde erfolgreich gespeichert"
            return Response({"message": message}, status=status.HTTP_200_OK)

        except Exception as e:
                # If an exception occurs during the execution of the function, the code inside this block will handle it.
                # You can customize the error message and status code to suit your needs.
                error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
                return Response({"message": error_message})

    # gets jobs from Schulte DB
    @action(detail=False, methods=['post'])
    def getSchulteData(self, request):
        try:
            info_start = request.POST.get('info_start')
            info_end = request.POST.get('info_end')
            formatted_start_date = datetime.strptime(format_ind_time(info_start), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%d-%m')
            formatted_end_date = datetime.strptime(format_ind_time(info_end), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%d-%m')
            df_mit_MachStatus_parameters = get_scheduled_jobs_ohne_MachStatus(formatted_start_date, formatted_end_date)
            
            # Convert the DataFrame to a list of dictionaries with string values
            dict_list = df_mit_MachStatus_parameters.astype(str).to_dict(orient='records')
            # Convert the list of dictionaries to an OrderedDict
            ordered_dict_list = []
            for item in dict_list:
                ordered_dict = OrderedDict()
                for key, value in item.items():
                    if key.endswith('_Date') or key.endswith('_Termin'):
                        # Convert the date to ISO 8601 format
                        value = pd.to_datetime(value).isoformat() + 'Z'
                    ordered_dict[key] = value
                ordered_dict_list.append(ordered_dict)

            json_obj = {'Schulte_data':ordered_dict_list}
            return JsonResponse(json_obj, safe=False, status=status.HTTP_200_OK)

        except Exception as e:
                # If an exception occurs during the execution of the function, the code inside this block will handle it.
                # You can customize the error message and status code to suit your needs.
                error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
                return Response({"message": error_message})

    @action(detail=False, methods=['post'])
    def getSchulteDataUnscheduled(self, request):
        try:
            info_start = request.POST.get('info_start')
            info_end = request.POST.get('info_end')
            print("info_start", type(info_start), "info_end", info_end)
            # Check if info_start is undefined or empty
            if info_start is None or info_start == '' or info_start == 'undefined':
                yesterday = datetime.now().date() - timedelta(days=1)
                formatted_start_date = yesterday.strftime('%Y-%d-%m')
            else:
                formatted_start_date = datetime.strptime(info_start, '%Y-%m-%d').date().strftime('%Y-%d-%m')
            # Check if info_end is undefined or empty
            if info_end is None or info_end == '' or info_start == 'undefined':
                tomorrow = datetime.now().date() + timedelta(days=1)
                formatted_end_date = tomorrow.strftime('%Y-%d-%m')
            else:
                formatted_end_date = datetime.strptime(info_end, '%Y-%m-%d').date().strftime('%Y-%d-%m')
            from_db = True
            if from_db:
                Job.objects.all().delete()
                df_unscheduled_jobs_ohne_MachStatus = get_unscheduled_jobs_ohne_MachStatus(formatted_start_date, formatted_end_date)
                dict_list = df_unscheduled_jobs_ohne_MachStatus.astype(str).to_dict(orient='records')
                for job_data in dict_list:
                    job_instance = Job()
                    job_instance.Fefco_Teil = job_data.get('Fefco_Teil')
                    job_instance.ArtNr_Teil = job_data.get('ArtNr_Teil')
                    job_instance.ID_Druck = job_data.get('ID_Druck')
                    if str(job_data.get('Druckflaeche')) != 'NULL' and str(job_data.get('Druckflaeche')) != '':
                        job_instance.Druckflaeche = job_data.get('Druckflaeche')
                    job_instance.Bogen_Laenge_Brutto = job_data.get('Bogen_Laenge_Brutto')
                    job_instance.Bogen_Breite_Brutto = job_data.get('Bogen_Breite_Brutto')
                    job_instance.Maschine = job_data.get('Maschine')
                    job_instance.Start = parse_datetime(job_data.get('Start')) if job_data.get('Start') else None
                    job_instance.Ende = parse_datetime(job_data.get('Ende')) if job_data.get('Ende') else None
                    job_instance.Ruestzeit_Ist = job_data.get('Ruestzeit_Ist')
                    job_instance.Ruestzeit_Soll = job_data.get('Ruestzeit_Soll')
                    job_instance.Laufzeit_Ist = job_data.get('Laufzeit_Ist')
                    job_instance.Laufzeit_Soll = job_data.get('Laufzeit_Soll')
                    job_instance.Zeit_Ist = job_data.get('Zeit_Ist')
                    job_instance.Zeit_Soll = job_data.get('Zeit_Soll')
                    job_instance.Werkzeug_Nutzen = job_data.get('Werkzeug_Nutzen')
                    job_instance.Bestell_Nutzen = job_data.get('Bestell_Nutzen')
                    job_instance.Menge_Soll = job_data.get('Menge_Soll')
                    job_instance.Menge_Ist = job_data.get('Menge_Ist')
                    job_instance.Bemerkung = job_data.get('Bemerkung')
                    # job_instance.LTermin = parse_datetime(job_data.get('LTermin')) if job_data.get('LTermin') else None
                    job_instance.KndNr = job_data.get('KndNr')
                    job_instance.Suchname = job_data.get('Suchname')
                    job_instance.AKNR = job_data.get('AKNR')
                    job_instance.TeilNr = job_data.get('TeilNr')
                    job_instance.SchrittNr = job_data.get('SchrittNr')
                    job_instance.Summe_Minuten = job_data.get('Summe_Minuten')
                    job_instance.ID_Maschstatus = job_data.get('ID_Maschstatus')
                    job_instance.Maschstatus = job_data.get('Maschstatus')

                    lieferdatum = job_data.get('Lieferdatum_Rohmaterial')
                    LTermin = job_data.get('LTermin')
                    date_regex = r'\d{4}-\d{2}-\d{2}'  # yyyy-mm-dd pattern
                    if re.match(date_regex, str(lieferdatum)):
                        l_d = datetime.strptime(str(lieferdatum), "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
                        job_instance.Lieferdatum_Rohmaterial = parse_datetime(l_d)
                    if re.match(date_regex, str(LTermin)):
                        l_d = datetime.strptime(str(LTermin), "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
                        job_instance.LTermin = parse_datetime(l_d)

                    job_instance.BE_Erledigt = job_data.get('BE_Erledigt')
                    job_instance.save()

            message = "Der Auftrag wurde in DB erfolgreich gespeichert"
            return Response({"message": message, "dict_list":dict_list}, status=status.HTTP_200_OK)
  
        except Exception as e:
                # If an exception occurs during the execution of the function, the code inside this block will handle it.
                # You can customize the error message and status code to suit your needs.
                error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
                return Response({"message": error_message})

    @action(detail=False, methods=['post'])
    def savejobstoCSV(self, request):
        try:
            jobs = Job.objects.all()

            # Generate a unique filename based on the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            filename = f"saved_schedules/jobs_{timestamp}.csv"

            # Create a CSV writer object
            with open(filename, mode='w') as csv_file:
                writer = csv.writer(csv_file)

                # Write the header row
                writer.writerow(['Fefco_Teil', 'ArtNr_Teil', 'ID_Druck', 'Druckflaeche', 'Bogen_Laenge_Brutto', 'Bogen_Breite_Brutto', 'Maschine',
                    'Ruestzeit_Ist', 'Ruestzeit_Soll', 'Laufzeit_Ist', 'Laufzeit_Soll', 'Zeit_Ist', 'Zeit_Soll', 'Werkzeug_Nutzen',
                    'Bestell_Nutzen', 'Menge_Soll', 'Menge_Ist', 'Bemerkung', 'LTermin', 'KndNr', 'Suchname', 'AKNR', 'TeilNr',
                    'SchrittNr', 'Start', 'Ende', 'Summe_Minuten', 'ID_Maschstatus', 'Maschstatus', 'Lieferdatum_Rohmaterial',
                    'BE_Erledigt'])

                # Write the data rows
                for job in jobs:
                    writer.writerow([job.Fefco_Teil, job.ArtNr_Teil, job.ID_Druck, job.Druckflaeche, job.Bogen_Laenge_Brutto, job.Bogen_Breite_Brutto,
                    job.Maschine, job.Ruestzeit_Ist, job.Ruestzeit_Soll, job.Laufzeit_Ist, job.Laufzeit_Soll, job.Zeit_Ist, job.Zeit_Soll,
                    job.Werkzeug_Nutzen, job.Bestell_Nutzen, job.Menge_Soll, job.Menge_Ist, job.Bemerkung, job.LTermin, job.KndNr, job.Suchname,
                    job.AKNR, job.TeilNr, job.SchrittNr, job.Start, job.Ende, job.Summe_Minuten, job.ID_Maschstatus, job.Maschstatus,
                    job.Lieferdatum_Rohmaterial, job.BE_Erledigt])

            message = "Alle Jobs wurden erfolgreich gespeichert"
            return Response({"message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            # If an exception occurs during the execution of the function, the code inside this block will handle it.
            # You can customize the error message and status code to suit your needs.
            error_message = "Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten:" + str(e)
            return Response({"message": error_message})