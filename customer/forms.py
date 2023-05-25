from django import forms
from .models import Contact, Customer, ResetPassword
from django.contrib.auth.models import User


class ContactForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Contact
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name', }),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Email', }),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject', }),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'rows': '8' }),
        }
        
        
class RegisterForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', }))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', }))
    password_again = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again', }))

    def save(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
        )
        customer = Customer.objects.create(user=user)
        
        return customer
    
    
class PasswordResetForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput())
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password_again = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again'}))
    
    def clean(self):
        cleaned_data = super().clean()
        token = cleaned_data['token']
        username = cleaned_data['username']
        password = cleaned_data['password']
        password_again = cleaned_data['password_again']
        rp = ResetPassword.objects.filter(token=token).first()
        user = User.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError('This username doesn\'t exists')
        if not rp or rp.user != user:
            raise forms.ValidationError('Process failed')
        if password and password_again and password != password_again:
            raise forms.ValidationError('Passwords are not same!')
        
        return cleaned_data
    
    def save(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data['username']
        password = cleaned_data['password']
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        rp = ResetPassword.objects.get(token=cleaned_data['token'])
        rp.used = True
        rp.save()
        return user