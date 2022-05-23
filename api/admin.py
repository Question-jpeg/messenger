from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Category, Listing, ListingImage, Message, MessageFile, SentOnMessage, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Services'), {'fields': ('expoPushToken',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name'),
        }),
    )
    list_display = ('email', 'name', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)


class ListingImageInLine(admin.TabularInline):
    model = ListingImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img width="100" src="{instance.image.url}" class="thumbnail" />')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'category', 'user']
    inlines = [ListingImageInLine]


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'image']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class SentOnMessageInLine(admin.TabularInline):
    model = SentOnMessage
    fk_name = "message_parent"

class MessageFileInLine(admin.TabularInline):
    model = MessageFile

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user', 'text']
    inlines = [SentOnMessageInLine, MessageFileInLine]

@admin.register(SentOnMessage)
class SentOnMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_parent', 'message']
