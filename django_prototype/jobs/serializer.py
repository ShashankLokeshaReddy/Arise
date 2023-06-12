from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Job

class JobsSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ['FEFCO_Teil','ArtNr_Teil','ID_DRUCK','Druckflaeche','BOGEN_LAENGE_BRUTTO','BOGEN_BREITE_BRUTTO','Maschine','Ruestzeit_Ist','Ruestzeit_Soll','Laufzeit_Ist','Laufzeit_Soll','Zeit_Ist','Zeit_Soll','Werkzeug_Nutzen','Bestell_Nutzen','Menge_Soll','Menge_Ist','Bemerkung','LTermin','KndNr','Suchname','AKNR','TeilNr','SchrittNr','Start','Ende','Summe_Minuten','ID_Maschstatus','Maschstatus','Lieferdatum_Rohmaterial','BE_Erledigt']
