from django.http import HttpResponse, JsonResponse
from django.template import loader


# Create your views here.
def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render({}, request))


def test_api(request):
    return JsonResponse({"Hello": "World"})
