from django.shortcuts import render, redirect
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth import logout, login
from users.firebase_helpers import firebase_config
from users.utils import sync_firebase_users
import requests
# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = UserRegisterForm()
        
    return render(request, 'users/signup.html', {'form': form})


def profile(request):
    return render(request, 'users/profile.html')


def logout_view(request):
    logout(request)
    return redirect('login')





def forgot_password(request):
    firebase_config()

    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'users/forgot_pw.html', {'error': 'Email is required.'})

        API_KEY = "AIzaSyC0d3a8cnrFZIG9tXeEMINjeBzkZKyIvIw"
        reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        data = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        try:
            response = requests.post(reset_url, json=data)
            if response.status_code == 200:
                # đồng bộ từ firebase về database của django
                sync_firebase_users(email=email)
                return render(request, 'users/forgot_pw.html', {'success': 'Password reset email sent.'})
            else:
                error_message = response.json().get('error', {}).get('message', 'An error occurred.')
                return render(request, 'users/forgot_pw.html', {'error': error_message})
        except Exception as e:
            return render(request, 'users/forgot_pw.html', {'error': f'Error: {e}'})

    return render(request, 'users/forgot_pw.html')