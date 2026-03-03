from django.shortcuts import render
from core.utils import set_brand


def joint_home(request):
    return render(request, "joint/home.html")


def our_story(request):
    return render(request, "joint/our_story.html")


def dabelo_home(request):
    set_brand(request, "dabelo")
    return render(request, "dabelo/home.html")


def dabelo_about(request):
    set_brand(request, "dabelo")
    return render(request, "dabelo/about.html")


def montee_home(request):
    request = set_brand(request, "montee")
    return render(request, "montee/home.html")


def montee_about(request):
    request = set_brand(request, "montee")
    return render(request, "montee/about.html")
