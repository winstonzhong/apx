from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.

def test2(request):
    return HttpResponse('ok')