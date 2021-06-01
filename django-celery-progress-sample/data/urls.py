"""dj_celery_progress_sample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""
from os import name

from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from .views import *

urlpatterns = [
    path("", IndexTemplateView.as_view(), name="index"),
    # path("", index, name="index"),
    path("export-file/", export_file, name="export"),
    path("import-file/", import_file, name="import"),
    path("celery-progress/", get_progress_view, name="progress"),
    path("download-file/", download_file_view, name="download"),
]

