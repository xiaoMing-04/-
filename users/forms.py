from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import requests
from users.firebase_helpers import firebase_config
from firebase_admin import auth
from users.utils import sync_firebase_users

User = get_user_model()

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password'
    }))
    
    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        
        if not email or not password:
            raise forms.ValidationError("Email and password are required.")

        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }


        API_KEY = "AIzaSyC0d3a8cnrFZIG9tXeEMINjeBzkZKyIvIw"
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        response = requests.post(url, json=data)

        if response.status_code == 200:
            res_data = response.json()
            firebase_uid = res_data['localId']

            # Đồng bộ user từ Firebase về Django
            user_obj = sync_firebase_users(email=email)
            if not user_obj:
                raise forms.ValidationError("Không thể đồng bộ người dùng từ Firebase.")
            self.user = user_obj
        else:
            error_message = response.json().get('error', {}).get('message', 'Email hoặc mật khẩu không đúng.')
            raise forms.ValidationError(error_message)


    def get_user(self):
        return self.user  
    
    
    
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput({
        'placeholder': 'Email address'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput({
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput({
        'placeholder': 'Confirm Password'
    }))
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
        

    def save(self, commit=True):
        firebase_config()

        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        display_name = email.split('@')[0]  # hoặc cho người dùng nhập tên

        # 1. Tạo user trên Firebase Authentication
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )

            # 2. Gán custom claims mặc định (ví dụ: role='user')
            auth.set_custom_user_claims(user_record.uid, {'role': 'user'})

        except Exception as e:
            print(f"Firebase error: {e}")
            raise forms.ValidationError("Không thể tạo tài khoản Firebase.")

        # 3. Lưu vào local database (Django)
        user = super().save(commit=False)
        user.username = display_name
        user.email = email
        user.id = user_record.uid  # nếu model có field này
        user.set_password(password)

        if commit:
            user.save()

        return user
    