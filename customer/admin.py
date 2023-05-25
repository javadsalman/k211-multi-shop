from django.contrib import admin
from .models import Contact, ResetPassword

# Register your models here.

admin.site.register(Contact)
admin.site.register(ResetPassword)