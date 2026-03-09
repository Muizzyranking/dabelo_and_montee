from django.shortcuts import render

from core.seo import (
    seo_dabelo_home,
    seo_home,
    seo_montee_home,
    seo_our_story,
)
from core.utils import set_brand


def joint_home(request):
    context = {"seo": seo_home()}
    return render(request, "joint/home.html", context)


def our_story(request):
    context = {"seo": seo_our_story()}
    return render(request, "joint/our_story.html", context)


def dabelo_home(request):
    request = set_brand(request, "dabelo")
    context = {"seo": seo_dabelo_home()}
    return render(request, "dabelo/home.html", context)


def dabelo_about(request):
    request = set_brand(request, "dabelo")
    return render(request, "dabelo/about.html")


def montee_home(request):
    request = set_brand(request, "montee")
    context = {"seo": seo_montee_home()}
    return render(request, "montee/home.html", context)


def montee_about(request):
    request = set_brand(request, "montee")
    return render(request, "montee/about.html")


def page_not_found(request, exception=None):
    return render(request, "error_pages/404.html", status=404)


def server_error(request):
    return render(request, "error_pages/500.html", status=500)
