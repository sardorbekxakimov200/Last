from django.urls import path
from . import views

app_name = "timetable"  # ← this is crucial

urlpatterns = [
    path("pupil-now/", views.pupil_now, name="pupil_now"),
    path("simulator/", views.timetable_simulator, name="simulator_view"),  # if you added one
]
