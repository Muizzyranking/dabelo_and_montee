from django.urls import path

from . import views

urlpatterns = [
    path("", views.joint_home, name="joint_home"),
    path("our_story/", views.our_story, name="our_story"),
    path("dabelo/", views.dabelo_home, name="dabelo_home"),
    path("dabelo/about/", views.dabelo_about, name="dabelo_about"),
    path("montee/", views.montee_home, name="montee_home"),
    path("montee/about/", views.montee_about, name="montee_about"),
]
