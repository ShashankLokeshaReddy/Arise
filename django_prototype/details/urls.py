from django.urls import path

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register('details', DetailsViewSet)


urlpatterns = router.urls