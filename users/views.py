from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import User

# Create your views here.
def signup_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        birthday = request.POST['birthday']
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                birthday=birthday
            )
            login(request,user)
            messages.success(request,f'Bun venit, {user.username}!')
            return redirect('user_profile',username=username)
        except Exception as e:
            messages.error(request,f'Error :{str(e)}')
        messages.success(request, 'Cont creat!')
        return redirect('user_login')

    return render(request, 'html/signup.html')
@login_required
def acces_profile(request,username):
    user = get_object_or_404(User,username=username)
    context = {
        "username":user.username,
        "email":user.email,
        "user":user
    }
    return render(request, "html/profile.html", context)
def login_page(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user:
            login(request, user)
            return redirect('users:profile-path', username=username)
        else:
            messages.error(request,'Date incorecte')
            return redirect('user_login')
    else:
        if request.user.is_authenticated:
            logout(request)
        return render(request, "html/login.html")