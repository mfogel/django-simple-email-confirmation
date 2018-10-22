from django.contrib import admin

from .settings import EmailAddressModel


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'key', 'set_at', 'confirmed_at')
    search_fields = ('email', 'key')


admin.site.register(EmailAddressModel, EmailAddressAdmin)
