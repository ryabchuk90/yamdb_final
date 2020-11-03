from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import ConfirmationCode

User = get_user_model()


class ConfirmationCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'confirmation_code', 'last_sent', 'confirmed')
    search_fields = ('email', )
    list_filter = ('confirmed', )
    empty_value_display = '-пусто-'


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name',
                    'username', 'bio', 'email', 'role')
    search_fields = ('username', )
    list_filter = ('role', )
    empty_value_display = '-пусто-'


admin.site.register(ConfirmationCode, ConfirmationCodeAdmin)
admin.site.register(User, UserAdmin)
