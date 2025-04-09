from django.contrib import admin
from .models import *

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'option', 'amount', 'profit', 'total_amount', 'status']
    list_editable = ['profit', 'total_amount', 'amount']
    search_fields = ['user__username', 'option__name']
    list_filter = ['status', 'option']
    ordering = ['-id']

admin.site.register(InvestmentOption)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'MID_CODE', 'main_balance', 'card_number', 'cvv',
        'expiry_date', 'profit', 'total_amount', 'get_total_balance'
    ]
    search_fields = ['user__username']
    list_editable = ['profit', 'total_amount']

    def get_total_balance(self, obj):
        return obj.total_balance
    get_total_balance.short_description = 'Total Balance'  # This must be set after method definition

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_instance = UserProfile.objects.get(pk=obj.pk)
                if old_instance.main_balance != obj.main_balance:
                    amount = obj.main_balance - old_instance.main_balance
                    description = 'Credit' if amount > 0 else 'Debit'

                    print(f"Admin updated balance for user: {obj.user.username}")
                    print(f"Old balance: {old_instance.main_balance}, New balance: {obj.main_balance}")
                    print(f"Transaction type: {description}, Amount: {abs(amount)}")

                    Transaction.objects.create(
                        user=obj.user,
                        amount=abs(amount),
                        balance_after=obj.main_balance,
                        description=description
                    )
            except UserProfile.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'amount', 'balance_after', 'timestamp', 'description', 'status'
    ]
    search_fields = ['user__username', 'description', 'status']
    list_filter = ['timestamp', 'user', 'status']
    ordering = ['-timestamp']

class YourModelAdmin(admin.ModelAdmin):
    list_display = ('image_display',)

    def image_display(self, obj):
        return obj.image.url if obj.image else None
