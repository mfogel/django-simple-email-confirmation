from django.contrib import admin

from simple_email_confirmation import get_email_address_model


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'key', 'set_at', 'confirmed_at')
    search_fields = ('email', 'key')


admin.site.register(get_email_address_model(), EmailAddressAdmin)
