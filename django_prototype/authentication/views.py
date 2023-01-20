from django.shortcuts import render
from .models import User
from rest_framework.viewsets import ModelViewSet
from .serializer import UserSerializer

# Create your views here.
class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
# t = User.get(id=1)
# t.value = 999
# t.save(['value'])