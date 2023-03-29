from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Job
from .serializer import JobsSerializer
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir_path)

scripts_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','scripts'))
sys.path.append(scripts_dir_path)

import signal
import psutil
import multiprocessing
import csv
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from decimal import Decimal

# def format_duration(duration):
#     duration_seconds = duration.total_seconds()
#     if duration_seconds < 86400:
#         duration_formatted = str(timedelta(seconds=duration_seconds))
#     else:
#         duration_formatted = str(timedelta(seconds=duration_seconds)).replace(' days, ', ' days, ')
#     return duration_formatted

pid = []

def delete_all_elements(my_list):
    for i in range(len(my_list) - 1, -1, -1):
        del my_list[i]
    return my_list

class JobsViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobsSerializer
    lookup_field = 'Job_ID'
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
        schedule = Job.objects.all()
        serializer = JobsSerializer(schedule, many=True)
        json_obj = {'Table':serializer.data}
        return JsonResponse(json_obj, safe=False, status=status.HTTP_200_OK)

    # updates a batch of jobs
    @action(detail=False, methods=['post'])
    def setSchedule(self, request):
        jobs_data = request.data["jobs_data"] # assuming the request payload contains a list of jobs
        for job_data in jobs_data:
            try:
                job_instance = Job.objects.get(job=job_data['Job_ID'])
                job_data['Start'] = datetime.strptime(job_data['Start'], date_format)
                job_data['Ende'] = datetime.strptime(job_data['Ende'], date_format)
                serializer = self.get_serializer(job_instance, data=job_data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except:
                # handle exception here
                pass
        return Response(status=status.HTTP_200_OK)

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
            job_instance.Job_ID = job_data['Job_ID']
            job_instance.FEFCO_Teil = job_data['FEFCO_Teil']
            job_instance.ArtNr_Teil = job_data['ArtNr_Teil']
            job_instance.ID_DRUCK = job_data['ID_DRUCK']
            job_instance.BOGEN_LAENGE_BRUTTO = job_data['BOGEN_LAENGE_BRUTTO']
            job_instance.BOGEN_BREITE_BRUTTO = job_data['BOGEN_BREITE_BRUTTO']
            job_instance.MaschNr = job_data['MaschNr']
            job_instance.Start = parse_datetime(job_data['Start']) if job_data['Start'] else None
            job_instance.Ende = parse_datetime(job_data['Ende']) if job_data['Ende'] else None
            job_instance.Ruestzeit_Ist = job_data['Ruestzeit_Ist']
            job_instance.Ruestzeit_Soll = job_data['Ruestzeit_Soll']
            job_instance.Laufzeit_Ist = job_data['Laufzeit_Ist']
            job_instance.Laufzeit_Soll = job_data['Laufzeit_Soll']
            job_instance.Nutzen = job_data['Nutzen']
            job_instance.Menge_Soll = job_data['Menge_Soll']
            job_instance.Menge_Ist = job_data['Menge_Ist']
            job_instance.Bemerkung = job_data['Bemerkung']
            # job_instance.LTermin = job_data['LTermin']
            # job_instance.Kunde = job_data['Kunde']
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
    def run_random(self, request):
        # logic for random here, once SJF is done, schedules need to be written back into the Jobs db
        return Response({'message': 'Release Date Scheduling completed.'})

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
