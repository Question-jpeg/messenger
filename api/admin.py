from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Category, Listing, ListingImage, ListingLocation, User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2', 'email', 'name')
        }),
    )
    list_display = ['username', 'email', 'name', 'is_staff']

class ListingImageInLine(admin.TabularInline):
    model = ListingImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'user', 'location']
    inlines = [ListingImageInLine]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(ListingLocation)
class ListingLocationAdmin(admin.ModelAdmin):
    list_display = ['listing', 'latitude', 'longitude']
