# home/admin.py

from django.contrib import admin
from .models import Setting, ContactMessage, FAQ, SettingLang

# Register your models here.
class SettingAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'update_at']
    list_filter = ['status']

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'message', 'status']
    list_filter = ['status']

class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'ordernumber', 'status']
    list_filter = ['status']

admin.site.register(Setting, SettingAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(SettingLang)

