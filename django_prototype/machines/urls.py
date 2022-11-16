from django.urls import path


from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register('machines', MachinesViewSet)
router.register('algorithm', HeuristicalMachinesViewSet, basename='Machine')
router.register('updatedb', UpdateDatabaseUpdateView, basename='Machine')


urlpatterns = router.urls