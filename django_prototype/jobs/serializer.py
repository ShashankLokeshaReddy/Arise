from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Job

class JobsSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ['Fefco_Teil','ArtNr_Teil','ID_Druck','Druckflaeche','Bogen_Laenge_Brutto','Bogen_Breite_Brutto','Maschine','Ruestzeit_Ist','Ruestzeit_Soll','Laufzeit_Ist','Laufzeit_Soll','Zeit_Ist','Zeit_Soll','Werkzeug_Nutzen','Bestell_Nutzen','Menge_Soll','Menge_Ist','Bemerkung','LTermin','KndNr','Suchname','AKNR','TeilNr','SchrittNr','Start','Ende','Summe_Minuten','ID_Maschstatus','Maschstatus','Lieferdatum_Rohmaterial','BE_Erledigt']
