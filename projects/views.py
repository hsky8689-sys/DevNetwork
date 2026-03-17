from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

@login_required
def create_project(request):
    if request.method == 'POST':
        pass
    else:
        JsonResponse({'status': 'error',
                      'code' : 404
                      })