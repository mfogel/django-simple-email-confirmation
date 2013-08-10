from django.contrib import admin

from .models import EmailAddress


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'key', 'set_at', 'confirmed_at')

admin.site.register((EmailAddress,), EmailAddressAdmin)
