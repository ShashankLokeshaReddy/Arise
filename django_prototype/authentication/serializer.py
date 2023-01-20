from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User

class UserListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        user_mapping = {user.id: user for user in instance}
        data_mapping = {item['id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for user_id, data in data_mapping.items():
            user = user_mapping.get(user_id, None)
            if user is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(user, data))


        return ret

class UserSerializer(ModelSerializer):
    #resourceId = serializers.CharField(source='resourceId')
    id = serializers.IntegerField()
    email = serializers.CharField()
    password = serializers.CharField()
    class Meta:
        model = User
        fields = ['id','email', 'password']
        list_serializer_class = UserListSerializer