from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.template import loader


# Create your views here.
def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render({}, request))
