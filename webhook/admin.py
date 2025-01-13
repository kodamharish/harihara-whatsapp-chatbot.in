from django.contrib import admin

# Register your models here.

# webhook/admin.py

from django.contrib import admin
from .models import *

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'message_body', 'timestamp')
    search_fields = ('phone_number', 'message_body')
    list_filter = ('timestamp',)

admin.site.register(Template)

