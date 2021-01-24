from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django_backend.src.qazline.models import QazlineUser


class QazlineUserAdmin(UserAdmin):
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('email', 'first_name', 'last_name', 'is_active',)
    list_filter = ('email', 'first_name', 'last_name', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Permissions', {
            'fields': ('is_active', )
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2','is_active',)}
         ),
    )


admin.site.register(QazlineUser, QazlineUserAdmin)