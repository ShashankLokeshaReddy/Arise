from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_pandas.io import read_frame
from rest_framework import status
from rest_framework.response import Response
from django.forms.models import model_to_dict
from django.http import JsonResponse
from .heuristics import heuristic
import json

from .models import Machine
from .serializer import MachinesSerializer


class MachinesViewSet(ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachinesSerializer

class UpdateDatabaseUpdateView(ModelViewSet):
    
    serializer_class = MachinesSerializer

    def get_queryset(self):
        machines = Machine.objects.all()
        return machines
    
    '''def update(self, request, pk):
        pk = request.data["id"]
        updatedMachine = Machine.objects.get(id=pk).__dict__
        print(updatedMachine)
        serializer=MachinesSerializer(data=updatedMachine, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

    
    def patch(self, request, *args, **kwargs):
       
        #machine_object = super().queryset
        #machine_object = self.get_object()
        
        #data = request.data

        machine = Machine.objects.all()
        

        #machine_object.machine = machine
        #machine_object.KndNr = data["title"]
        #machine_object.resourceId = data["resourceId"]
        #machine_object.Start= data["start"]
        #machine_object.Ende = data["end"]
        #machine_object.AKNR = data["AKNR"]
        #machine_object.SchrittNr = data["SchrittNr"]

        #machine_object.save()

        serializer = MachinesSerializer(data=machine, many=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)



class HeuristicalMachinesViewSet(ModelViewSet):
    
    queryset = Machine.objects.all()
    serializer_class = MachinesSerializer
    @action(detail=False, methods=["get"])
    def naive_sorting(self, request, format=None):
        queryset = Machine.objects.all()
        
        df = heuristic(read_frame(queryset)) # using django pandas library to read the queryset in a dataframe
        df['Start'] = df['Start'].astype(str) #fixing date format
        df['Ende'] = df['Ende'].astype(str)
        df.rename(columns={'Start':'start', 'Ende':'end', 'KndNr': 'title'}, inplace=True)#renameing columns like our serializer would do
        df = df[['id','resourceId', 'title', 'start', 'end', 'AKNR', 'SchrittNr']] #reordering columns
        df = df.to_json(orient="records") #formating json
        
        response = Response(json.loads(df))
        return response





