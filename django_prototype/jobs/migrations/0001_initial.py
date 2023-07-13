from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fefco_Teil', models.CharField(max_length=1000, null=True)),
                ('ArtNr_Teil', models.CharField(max_length=1000, null=True)),
                ('ID_Druck', models.CharField(max_length=1000, null=True)),
                ('Druckflaeche', models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)),
                ('Bogen_Laenge_Brutto', models.CharField(max_length=1000, null=True)),
                ('Bogen_Breite_Brutto', models.CharField(max_length=1000, null=True)),
                ('Maschine', models.CharField(max_length=1000, null=True)),
                ('Ruestzeit_Ist', models.CharField(max_length=1000, null=True)),
                ('Ruestzeit_Soll', models.CharField(max_length=1000, null=True)),
                ('Laufzeit_Ist', models.CharField(max_length=1000, null=True)),
                ('Laufzeit_Soll', models.CharField(max_length=1000, null=True)),
                ('Zeit_Ist', models.CharField(max_length=1000, null=True)),
                ('Zeit_Soll', models.CharField(max_length=1000, null=True)),
                ('Werkzeug_Nutzen', models.CharField(max_length=1000, null=True)),
                ('Bestell_Nutzen', models.CharField(max_length=1000, null=True)),
                ('Menge_Soll', models.CharField(max_length=1000, null=True)),
                ('Menge_Ist', models.CharField(max_length=1000, null=True)),
                ('Bemerkung', models.CharField(max_length=1000, null=True)),
                ('LTermin', models.DateTimeField(null=True)),
                ('KndNr', models.CharField(max_length=1000, null=True)),
                ('Suchname', models.CharField(max_length=1000, null=True)),
                ('AKNR', models.CharField(max_length=1000, null=True)),
                ('TeilNr', models.CharField(max_length=1000, null=True)),
                ('SchrittNr', models.CharField(max_length=1000, null=True)),
                ('Start', models.DateTimeField(null=True)),
                ('Ende', models.DateTimeField(null=True)),
                ('Summe_Minuten', models.CharField(max_length=1000, null=True)),
                ('ID_Maschstatus', models.CharField(max_length=1000, null=True)),
                ('Maschstatus', models.CharField(max_length=1000, null=True)),
                ('Lieferdatum_Rohmaterial', models.DateTimeField(null=True)),
                ('BE_Erledigt', models.CharField(max_length=1000, null=True)),
            ],
            options={
                'ordering': ('AKNR', 'TeilNr', 'SchrittNr', 'Fefco_Teil', 'ArtNr_Teil'),
                'unique_together': {('AKNR', 'TeilNr', 'SchrittNr', 'Fefco_Teil', 'ArtNr_Teil')},  # Add unique constraint
            },
        ),
    ]
