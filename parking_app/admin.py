from django.contrib import admin
from .models import (
    Client, Car, ParkingSpot, Invoice, Income,
    CompanyInfo, News, Term, Contact, Vacancy, Review, PromoCode, Payment
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'is_employee']   
    list_filter = ['is_employee']                         
    search_fields = ['full_name', 'phone']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'brand', 'model']
    list_filter = ['brand']
    search_fields = ['license_plate', 'brand', 'model']
    filter_horizontal = ['owners']

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ['spot_number', 'price_per_month', 'is_occupied', 'current_car']
    list_filter = ['is_occupied']
    search_fields = ['spot_number']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'car', 'date_incurred', 'amount', 'is_paid']
    list_filter = ['is_paid', 'date_incurred']
    search_fields = ['client__full_name', 'car__license_plate']

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'source']
    list_filter = ['date']

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['id']  # ← убрал updated_at
    list_filter = []

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['term', 'added_date']
    search_fields = ['term']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'phone', 'email']
    list_filter = ['position']
    search_fields = ['full_name']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary']
    search_fields = ['title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['author_name']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'is_active', 'valid_from', 'valid_to']
    list_filter = ['is_active']
    search_fields = ['code']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'amount', 'payment_date', 'invoice']
    list_filter = ['payment_date']
    search_fields = ['client__full_name']
    raw_id_fields = ['client', 'invoice'] 