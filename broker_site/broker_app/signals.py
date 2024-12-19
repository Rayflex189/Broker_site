from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import *

from django.core.mail import send_mail

@receiver(post_save, sender=Investment)
def update_investment_totals(sender, instance, created, **kwargs):
    if created:
        # If it's a new instance, initialize totals
        instance.total_amount = instance.amount
        instance.profit = instance.calculate_profit()
    else:
        # If it's an update, increment the totals
        original = sender.objects.get(pk=instance.pk)
        instance.total_amount = original.total_amount + instance.amount
        instance.profit = original.profit + instance.calculate_profit()

    # Save the instance with updated values
    instance.save(update_fields=['total_amount', 'profit'])


@receiver(post_save, sender=UserProfile)
def send_balance_update_notification(sender, instance, **kwargs):
    # Check if this is an update (not a new instance creation)
    if not kwargs.get('created', False):
        # Get the previous balance value
        old_balance = sender.objects.get(pk=instance.pk).main_balance
        new_balance = instance.main_balance
        
        if new_balance != old_balance:
            # Determine transaction type
            transaction_type = "Credit" if new_balance > old_balance else "Debit"
            difference = abs(new_balance - old_balance)
            
            # Prepare email content
            subject = f"Your Account Balance Has Been Updated"
            message = (
                f"Dear {instance.user.first_name},\n\n"
                f"There has been a {transaction_type} of {difference} in your account.\n"
                f"Your new balance is {new_balance}.\n\n"
                f"Thank you for banking with us.\n\n"
                f"Heritage Online Banking"
            )
            recipient_email = instance.user.email
            
            # Send the email
            send_mail(
                subject,
                message,
                'skylinebank059@gmail.com',  # Replace with your sender email
                [recipient_email],
                fail_silently=False,
            )

@receiver(pre_save, sender=UserProfile)
def track_balance_changes(sender, instance, **kwargs):
    """
    Before saving, fetch the old balance for comparison.
    """
    if not instance.pk:
        # This is a new instance, skip tracking
        instance._old_balance = None
    else:
        try:
            old_instance = UserProfile.objects.get(pk=instance.pk)
            instance._old_balance = old_instance.main_balance
        except UserProfile.DoesNotExist:
            instance._old_balance = None


@receiver(post_save, sender=UserProfile)
def create_transaction_on_balance_update(sender, instance, created, **kwargs):
    """
    After saving, create a transaction if the balance changed.
    """
    # Skip processing for newly created profiles
    if created or instance._old_balance is None:
        return

    # Check if the balance has changed
    if instance._old_balance != instance.main_balance:
        # Calculate the transaction amount
        amount = instance.main_balance - instance._old_balance
        description = 'Credit' if amount > 0 else 'Debit'

        # Create a transaction record
        Transaction.objects.create(
            user=instance.user,
            amount=abs(amount),  # Always positive
            balance_after=instance.main_balance,
            description=description
        )