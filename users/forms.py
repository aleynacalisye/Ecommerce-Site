from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # E-posta adresinin belirli bir domaine sahip olmasını kontrol edin
        if not email.endswith('@example.com'):
            raise ValidationError("Lütfen geçerli bir e-posta adresi girin.")
        # Daha önce kullanılan bir e-posta adresi olup olmadığını kontrol edin
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu e-posta adresi zaten kullanılmış.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        # Şifrenin belirli bir uzunluğa veya karmaşıklığa sahip olmasını kontrol edin
        if len(password1) < 8:
            raise ValidationError("Şifreniz en az 8 karakter uzunluğunda olmalıdır.")
        return password1


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)