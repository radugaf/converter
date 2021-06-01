import json
import datetime
import os
import pandas as pd
import random
import string
from logging import raiseExceptions

from celery_progress.backend import Progress
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.db.models import F

from celery.result import AsyncResult
from rest_framework.generics import RetrieveAPIView

from .forms import *
from .utils import in_memory_file_to_temp
from .models import *
from .tasks import *

class IndexTemplateView(TemplateView):
    template_name = "index.html"

def export_file(request):
    target_date = request.POST.get('target_date', None)

    if not target_date:
        raise Http404
    Data.objects.filter(delivery_date=target_date).values('title', 'delivery_date', 'quantity')
    target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d')
    data = list(Data.objects.filter(delivery_date=target_date).values(Product=F('title'), Delivery_Date=F('delivery_date'), Quantity=F('quantity')))
    # data  = list(Data.objects.all().values(Product=F('title'), DeliveryDate=F('delivery_date'), Quantity=F('quantity')))
    df = pd.json_normalize(data)

    random_folder_name = ''.join(random.sample(string.ascii_lowercase, 12))

    file_path = f'/tmp/converter_django_project_tmp_files/'
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    file_path += f'{random_folder_name}/'
    folder_path = file_path
    os.mkdir(file_path)
    file_path += 'exported_file.xlsx'

    df.to_excel(file_path, index=False)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            filename = os.path.basename(file_path)
            response['Content-Disposition'] = 'inline; filename=' + filename
            remove_file_from_storage.apply_async(args=(folder_path,), countdown=15 )
            return response
    raise Http404

def import_file(request):
    """
    The column of the excel file should be part of
    [Username, Password, Email, First Name, Last Name]
    """
    form = FileInfoForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        print(form.instance.id)
        extract_file_and_save_info_into_db.delay(form.instance.id)
        messages.add_message(request, messages.INFO, 'File is Imported successfully..')
        return redirect('/')
    else:
        raise Http404


def get_progress_view(request):
    progress = Progress(request.GET.get("task_id"))
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')


def download_file_view(request):
    celery_result = AsyncResult(request.GET.get("task_id"))
    filepath = celery_result.result.get("data", {}).get("outfile")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/ms-excel")
            outfile = os.path.basename(filepath)
            response['Content-Disposition'] = "attachment; filename=%s" % outfile
            return response
    raise Http404
