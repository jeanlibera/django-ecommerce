from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    # create a link on first_name or last_name
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    # order entries by date_joined in descending order
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    # don't allow the user specify read-only fields
    fieldsets = ()

admin.site.register(Account, AccountAdmin)