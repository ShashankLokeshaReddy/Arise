from django.db import models

# Create your models here.
class Job(models.Model):
    Fefco_Teil = models.CharField(max_length=1000, null=True)
    ArtNr_Teil = models.CharField(max_length=1000, null=True)
    ID_Druck = models.CharField(max_length=1000, null=True)
    Druckflaeche = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    Bogen_Laenge_Brutto = models.CharField(max_length=1000, null=True)
    Bogen_Breite_Brutto = models.CharField(max_length=1000, null=True)
    Maschine = models.CharField(max_length=1000, null=True)
    Ruestzeit_Ist = models.CharField(max_length=1000, null=True)
    Ruestzeit_Soll = models.CharField(max_length=1000, null=True)
    Laufzeit_Ist = models.CharField(max_length=1000, null=True)
    Laufzeit_Soll = models.CharField(max_length=1000, null=True)
    Zeit_Ist = models.CharField(max_length=1000, null=True)
    Zeit_Soll = models.CharField(max_length=1000, null=True)
    Werkzeug_Nutzen = models.CharField(max_length=1000, null=True)
    Bestell_Nutzen = models.CharField(max_length=1000, null=True)
    Menge_Soll = models.CharField(max_length=1000, null=True)
    Menge_Ist = models.CharField(max_length=1000, null=True)
    Bemerkung = models.CharField(max_length=1000, null=True)
    LTermin = models.DateTimeField(null=True)
    KndNr = models.CharField(max_length=1000, null=True)
    Suchname = models.CharField(max_length=1000, null=True)
    AKNR = models.CharField(max_length=1000, null=True)
    TeilNr = models.CharField(max_length=1000, null=True)
    SchrittNr = models.CharField(max_length=1000, null=True)
    Start = models.DateTimeField(null=True)
    Ende = models.DateTimeField(null=True)
    Summe_Minuten = models.CharField(max_length=1000, null=True)
    ID_Maschstatus = models.CharField(max_length=1000, null=True)
    Maschstatus = models.CharField(max_length=1000, null=True)
    Lieferdatum_Rohmaterial = models.DateTimeField(null=True)
    BE_Erledigt = models.CharField(max_length=1000, null=True)

    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']