from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import UserAccount


class UserAccountAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'full_name', 'is_staff', 'is_active')
    search_fields = ['email', 'first_name', 'last_name', 'id']
    ordering = ['email',]

    def full_name(self, obj):
        return obj.get_full_name()

admin.site.register(UserAccount, UserAccountAdmin)
