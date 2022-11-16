from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Machine

class MachinesListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        machines_mapping = {machines.id: machines for machines in instance}
        data_mapping = {item['id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for machines_id, data in data_mapping.items():
            machines = machines_mapping.get(machines_id, None)
            if machines is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(machines, data))

        # Perform deletions.
        '''for book_id, book in book_mapping.items():
            if book_id not in data_mapping:
                book.delete()'''

        return ret

class MachinesSerializer(ModelSerializer):
    #resourceId = serializers.CharField(source='resourceId')
    id = serializers.IntegerField()
    start = serializers.DateTimeField(source='Start')
    end = serializers.DateTimeField(source='Ende')
    title = serializers.CharField(source='KndNr')
    class Meta:
        model = Machine
        fields = ['id','resourceId', 'title', 'start', 'end', 'AKNR', 'SchrittNr']
        list_serializer_class = MachinesListSerializer


        '''
        def update(self,instance, validated_data):



        #instance.id = validated_data["id"]
        instance.KndNr = validated_data["KndNr"]
        instance.resourceId = validated_data["resourceId"]
        instance.Start = validated_data["Start"]
        instance.Ende = validated_data["Ende"]
        instance.AKNR = validated_data["AKNR"]
        instance.SchrittNr = validated_data["SchrittNr"]
        instance.save()
        return instance
        '''
