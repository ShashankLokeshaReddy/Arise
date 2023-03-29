from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Job

class JobsSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ['Job_ID', 'FEFCO_Teil', 'ArtNr_Teil', 'ID_DRUCK', 'Druckflaeche', 'BOGEN_LAENGE_BRUTTO', 'BOGEN_BREITE_BRUTTO', 'MaschNr', 'Start', 'Ende', 'Ruestzeit_Ist', 'Ruestzeit_Soll', 'Laufzeit_Ist', 'Laufzeit_Soll', 'Nutzen', 'Menge_Soll', 'Menge_Ist', 'Bemerkung', 'LTermin', 'Kunde']
