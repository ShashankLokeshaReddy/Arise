from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView, View
from rest_framework.decorators import action
from django_pandas.io import read_frame
from rest_framework import status
from rest_framework.response import Response
from django.forms.models import model_to_dict
from django.http import JsonResponse
from .heuristics import heuristic
import json
from django.views.generic import TemplateView
from rest_framework.decorators import api_view


from .models import Machine
from .serializer import MachinesSerializer
from django.views.decorators.csrf import csrf_exempt


class MachinesViewSet(ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachinesSerializer

class UpdateDatabaseUpdateView(ModelViewSet):
    
    serializer_class = MachinesSerializer

    def get_queryset(self):
        machines = Machine.objects.all()
        return machines
    
    # def update(self, request, pk):
    #     entry = Machine.objects.get(id=23)
    #     entry.resourceId="SL 4"
    #     entry.Start="2023-01-03T16:30:00Z"
    #     entry.Ende="2023-01-03T16:30:00Z"
    #     entry.save(update_fields=['resourceId','Start','Ende'])


        '''pk = request.data["id"]
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
    
class Updater(ModelViewSet):
    #@action(detail=False, methods=["post"])
    def post(self, request, pk):
        if request.method == "POST":
            json_data = json.loads(request.body)
            savedstring = ""
            for instance in json_data:
                serializer = MachinesSerializer(data = instance)
                if serializer.is_valid():
                    id = int(instance['id'])
                    resourceId = instance['resourceId']
                    start = instance['start']
                    end = instance['end']
                    print(instance)
                    entry = Machine.objects.get(id=id)
                    print("tt")
                    entry.resourceId = resourceId
                    entry.Start = start
                    entry.Ende = end
                    entry.save(update_fields=['resourceId','Start','Ende'])
                    #response = Response(json.loads("Abgespeichert"))
                    print("t")
                    savedstring += str(instance)
                else:
                    return Response("Data not serializable")
            return Response("The following got saved: " + savedstring)
        else: return Response("You need to access via Post Request to make this view")
        
# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# def updateit(request):
#     if request.method == "POST":
#         json_data = json.loads(request.body)
#         for instance in json_data:
#             serializer = MachinesSerializer(data = json_data)
#             print(serializer)
#             if serializer.is_valid():
#                 print("serializer valid")
#                 entry = Machine.objects.get(id = int(instance['id']))
#                 print("test")
#                 entry.resourceId = instance['resourceId']
#                 entry.Start = instance['start']
#                 entry.Ende = instance['end']
#                 entry.save(update_fields=['resourceId','Start','Ende'])
#                 #response = Response(json.loads("Abgespeichert"))
#                 print("t")
#                 return Response("The following got saved: " + str(instance))
#         else: return Response("Data not serializable")




