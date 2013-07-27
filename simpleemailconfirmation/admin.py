from django.contrib import admin

from .models import EmailAddress, EmailConfirmation


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'is_primary')

class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'key', 'created_at', 'confirmed_at')

admin.site.register((EmailAddress,), EmailAddressAdmin)
admin.site.register((EmailConfirmation,), EmailConfirmationAdmin)
