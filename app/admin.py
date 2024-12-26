from django.contrib import admin
from .models import TelegramUser,Order,Category,Centers,Country,Role


# Register your models here.
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('pk','first_name','last_name', 'username', 'telegram_id', 'profile_photo')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('pk','name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk','name')

@admin.register(Centers)
class CentersAdmin(admin.ModelAdmin):
    list_display = ('pk','name','country')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('pk','name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk','user')