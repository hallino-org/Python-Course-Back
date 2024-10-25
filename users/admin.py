# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from . import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'full_name',
        'phone_number',
        'type',
        'level',
        'is_active',
        'is_staff',
        'created_at'
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_confirmed',
        'type',
        'level',
        'gender',
        'created_at',
    )

    search_fields = (
        'email',
        'username',
        'firstname',
        'lastname',
        'phone_number',
    )

    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': (
                'username',
                'firstname',
                'lastname',
                'gender',
                'phone_number',
                'birth_date',
            )
        }),
        (_('Status'), {
            'fields': (
                'type',
                'level',
                'is_confirmed',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'expire_date',
                'created_at',
                'updated_at',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'firstname',
                'lastname',
                'gender',
                'phone_number',
                'birth_date',
                'password1',
                'password2',
            ),
        }),
    )

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = _('Full Name')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('email', 'username')
        return self.readonly_fields


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name',
        'get_email',
        'total_courses',
        'get_user_type',
    )

    list_filter = (
        'total_courses',
        'user__type',
        'user__is_active',
    )

    search_fields = (
        'user__email',
        'user__username',
        'user__firstname',
        'user__lastname',
        'bio',
    )

    raw_id_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': ('user', 'bio')
        }),
        (_('Author Info'), {
            'fields': (
                'specializations',
                'total_courses',
            )
        }),
    )

    def get_full_name(self, obj):
        return obj.user.full_name

    get_full_name.short_description = _('Author Name')
    get_full_name.admin_order_field = 'user__firstname'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_user_type(self, obj):
        return obj.user.get_type_display()

    get_user_type.short_description = _('User Type')
    get_user_type.admin_order_field = 'user__type'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = models.User.objects.filter(
                is_active=True
            ).order_by('email')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
