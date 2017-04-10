# -*- coding: UTF-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User, Organisation

from .forms import UserChangeForm, UserCreationForm
from django.contrib.auth.forms import AdminPasswordChangeForm


class UserInline(admin.TabularInline):
    model = User
    extra = 1
    suit_classes = 'suit-tab suit-tab-user'


class OrganisationInline(admin.TabularInline):
    model = Organisation
    extra = 1
    suit_classes = 'suit-tab suit-tab-Organisation'


class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            qs = kwargs.get('queryset', db_field.rel.to.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs['queryset'] = qs.select_related('content_type')
        return super(GroupAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)


class UserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_admin',
                    'organisation', 'operator')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password',
                           'username', 'first_name', 'last_name',)}),
        ('permissions', {
         'fields': ('is_admin', 'groups', 'user_permissions')}),
        ('organisation', {'fields': ('organisation', 'operator', 'manager')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'organisation')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


class OrganisationAdmin(admin.ModelAdmin):

    list_display = ('name', 'operator', )

    inlines = (UserInline,)

admin.site.register(Organisation, OrganisationAdmin)

