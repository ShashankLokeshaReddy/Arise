from django.http import HttpResponse, JsonResponse
from django.template import loader


# Create your views here.
def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render({}, request))


def test_api(request):
    # rufe get capacities auf --> Tabelle
    # request enthält irgendwie Datum
    selected_date = request.GET['date']

    template = loader.get_template('home/production_info_table.html')
    # return JsonResponse({"selected_date": selected_date})
    return HttpResponse(template.render({}, request))
