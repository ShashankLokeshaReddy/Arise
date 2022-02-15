from django.http import HttpResponse
from django.template import loader
import pandas as pd


# Create your views here.
def index(request):
    template = loader.get_template('home/index.html')
    return HttpResponse(template.render({}, request))


def test_api(request):
    # rufe get capacities auf --> Tabelle
    # request enthält irgendwie Datum
    selected_date = request.GET['date']

    print(selected_date)
    template = loader.get_template('home/production_info_table.html')
    print('loading data')
    data = pd.read_csv('tmp_data/test_data.csv')
    print('data loaded')
    data = data[data.Start.str.startswith(selected_date)]
    html = data.to_html()

    # return JsonResponse({"selected_date": selected_date})
    # return HttpResponse(template.render({}, request))
    return HttpResponse(html)
