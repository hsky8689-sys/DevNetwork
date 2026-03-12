from django.shortcuts import render
from chat.models import Message
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def index(request):
    return render(request, "html/index.html")
def register_view(request):
    form = UserCreationForm()
    return render(request,
                  "html/signup.html",
                  {"form":form})
def show_all_messages(request):
    messages = Message.objects.all()
    return render(request, 'html/messages.html', {'messages':messages})
def room(request,room_name):
    return render(request, "html/room.html", {"room_name":room_name})
def signup(request):
    return render(request, "html/signup.html")