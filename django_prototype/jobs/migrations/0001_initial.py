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
                ('Job_ID', models.CharField(max_length=1000, null=True)),
                ('FEFCO_Teil', models.CharField(max_length=1000, null=True)),
                ('ArtNr_Teil', models.CharField(max_length=1000, null=True)),
                ('ID_DRUCK', models.CharField(max_length=1000, null=True)),
                ('Druckflaeche', models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)),
                ('BOGEN_LAENGE_BRUTTO', models.CharField(max_length=1000, null=True)),
                ('BOGEN_BREITE_BRUTTO', models.CharField(max_length=1000, null=True)),
                ('MaschNr', models.CharField(max_length=1000, null=True)),
                ('Start', models.DateTimeField(null=True)),
                ('Ende', models.DateTimeField(null=True)),
                ('Ruestzeit_Ist', models.CharField(max_length=1000, null=True)),
                ('Ruestzeit_Soll', models.CharField(max_length=1000, null=True)),
                ('Laufzeit_Ist', models.CharField(max_length=1000, null=True)),
                ('Laufzeit_Soll', models.CharField(max_length=1000, null=True)),
                ('Nutzen', models.CharField(max_length=1000, null=True)),
                ('Menge_Soll', models.CharField(max_length=1000, null=True)),
                ('Menge_Ist', models.CharField(max_length=1000, null=True)),
                ('Bemerkung', models.CharField(max_length=1000, null=True)),
                ('LTermin', models.CharField(max_length=1000, null=True)),
                ('Kunde', models.CharField(max_length=1000, null=True)),
            ],
            options={
                'ordering': ('Job_ID',),
            },
        ),
    ]
