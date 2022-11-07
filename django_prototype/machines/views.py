from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_pandas.io import read_frame
from rest_framework.response import Response
from django.http import JsonResponse
from .heuristics import heuristic
import json


from .models import Machine
from .serializer import MachinesSerializer


class MachinesViewSet(ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachinesSerializer



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
        df = df[['resourceId', 'title', 'start', 'end', 'AKNR', 'SchrittNr']] #reordering columns
        df = df.to_json(orient="records") #formating json
        
        response = Response(json.loads(df))
        return response





