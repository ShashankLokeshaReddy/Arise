from rest_framework.serializers import ModelSerializer

from .models import Machine

class MachinesSerializer(ModelSerializer):
    class Meta:
        model = Machine
        fields = ['resourceId', 'title', 'start', 'end']