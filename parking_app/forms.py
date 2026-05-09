from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Client
from datetime import date
from django.contrib.auth.password_validation import validate_password


class ClientRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, label='ФИО')
    phone = forms.CharField(max_length=20, label='Телефон')
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone', 'birth_date', 'password1', 'password2']

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise forms.ValidationError('Возраст должен быть 18+')
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date']
            )
        return user
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        import re
        pattern = r'^\+\d{3}\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError('Телефон должен быть в формате: +375 (29) XXX-XX-XX')
        return phone

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password, self.instance)
        return password