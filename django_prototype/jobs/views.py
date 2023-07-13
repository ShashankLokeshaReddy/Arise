from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .dbconnection import get_df_mit_MachStatus, get_df_ohne_MachStatus, get_df_mit_MachStatus_parameters, get_unscheduled_jobs_ohne_MachStatus
from .models import Job
from .serializer import JobsSerializer
import pandas as pd
from collections import OrderedDict
import os
import sys
from datetime import datetime, timedelta, time
date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir_path)

scripts_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','scripts'))
sys.path.append(scripts_dir_path)

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

pid = []
holidays = []

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
    # convert timezone offset string to datetime.timedelta object
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
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

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

        message = "Upload successful"
        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def deleteJobs(self, request):
        Job.objects.all().delete() # delete all objects in Job model
        message = "All jobs were deleted successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)

    # runs genetic optimizer
    @action(detail=False, methods=['post'])
    def run_preference_learning_optimizer(self, request):
        schedule = Job.objects.all()
        serializer = JobsSerializer(schedule, many=True)
        input_jobs = serializer.data
        # Logic for PL optimizer here and invoke it in a separate process below so that it executes parallely
        # p = multiprocessing.Process(target=run_PL_optimizer_in_diff_process, args=(self,request,input_jobs,))
        # p.start()
        # pid.append(p.pid)
        # p.join()
        response = {'message': 'Preference Learning optimizer complete.'}
        return Response(response)

    @action(detail=False, methods=['post'])
    def run_sjf(self, request):
        # logic for SJF here, once SJF is done, schedules need to be written back into the Jobs db
        return Response({'message': 'SJF completed.'})

    @action(detail=False, methods=['post'])
    def run_deadline_first(self, request):
        # logic for deadline first here, once SJF is done, schedules need to be written back into the Jobs db
        return Response({'message': 'Early Deadline First completed.'})

    @action(detail=False, methods=['post'])
    def stop_genetic_optimizer(self, request):
        try:
            os.kill(pid[0], signal.SIGTERM)
            delete_all_elements(pid)
            return Response({'message': 'Stopping PL Optimizer completed.'})
        except OSError:
            pass
        delete_all_elements(pid)
        return Response({'message': 'Could not find running PL optimizer.'}) 

    # updates a jobs
    @action(detail=False, methods=['post'])
    def setInd(self, request):
        job_data = request.data.copy()
        # print("job_data",job_data)
        job_instance = Job.objects.get(Fefco_Teil=job_data['Fefco_Teil'], ArtNr_Teil=job_data['ArtNr_Teil'], AKNR=job_data['AKNR'], TeilNr=job_data['TeilNr'], SchrittNr=job_data['SchrittNr'])
        print("job_instance",job_instance)
        if 'Start' in job_data and 'Ende' in job_data:
            job_data['Start'] = job_data['Start']
            job_data['Ende'] = job_data['Ende']

        serializer = self.get_serializer(job_instance, data=job_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        message = "Der Auftrag wurde erfolgreich gespeichert"
        return Response({"message": message}, status=status.HTTP_200_OK)

    # gets jobs from Schulte DB
    @action(detail=False, methods=['post'])
    def getSchulteData(self, request):
        info_start = request.POST.get('info_start')
        info_end = request.POST.get('info_end')
        formatted_start_date = datetime.strptime(format_ind_time(info_start), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%d-%m')
        formatted_end_date = datetime.strptime(format_ind_time(info_end), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%d-%m')
        df_mit_MachStatus_parameters = get_df_mit_MachStatus_parameters(formatted_start_date, formatted_end_date)
        
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

    @action(detail=False, methods=['post'])
    def getSchulteDataUnscheduled(self, request):
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