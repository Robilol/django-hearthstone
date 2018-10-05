from django.http import HttpResponse
from django.shortcuts import render



def index(request):
    context = {'test': 'yolo'}
    return render(request, 'hearthstone/index.html', context)

def login(request):
    return HttpResponse("Hello, world. You're at the login.")
