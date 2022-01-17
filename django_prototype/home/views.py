from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.

def index(request):
    return HttpResponse("You are at home.")

def redirect(request):
    return HttpResponseRedirect(reverse('home:index'))