from django.db.models.signals import pre_save, post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from .models import Investment, UserProfile, Transaction


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    """
    Creates a permanent superuser after migrations.
    """
    if sender.name == "auth":  # Ensures it runs only for the auth app
        User = get_user_model()
        superuser_username = settings.SUPERUSER_USERNAME
        superuser_email = settings.SUPERUSER_EMAIL
        superuser_password = settings.SUPERUSER_PASSWORD

        if not User.objects.filter(username=superuser_username).exists():
            User.objects.create_superuser(
                username=superuser_username,
                email=superuser_email,
                password=superuser_password
            )
            print(f"Superuser '{superuser_username}' created.")
        else:
            print(f"Superuser '{superuser_username}' already exists.")


@receiver(post_save, sender=Investment)
def update_investment_totals(sender, instance, created, **kwargs):
    """
    Updates total amount and profit for an investment.
    """
    if created:
        instance.total_amount = instance.amount
        instance.profit = instance.calculate_profit()
        instance.save(update_fields=['total_amount', 'profit'])


@receiver(pre_save, sender=UserProfile)
def track_balance_changes(sender, instance, **kwargs):
    """
    Tracks previous balance before saving.
    """
    if instance.pk:
        try:
            old_instance = UserProfile.objects.get(pk=instance.pk)
            instance._old_balance = old_instance.main_balance
        except UserProfile.DoesNotExist:
            instance._old_balance = None
    else:
        instance._old_balance = None


@receiver(post_save, sender=UserProfile)
def send_balance_update_notification(sender, instance, created, **kwargs):
    """
    Sends email notification when user balance changes.
    """
    if created or instance._old_balance is None:
        return

    old_balance = instance._old_balance
    new_balance = instance.main_balance

    if new_balance != old_balance:
        transaction_type = "Credit" if new_balance > old_balance else "Debit"
        difference = abs(new_balance - old_balance)

        subject = "Your Account Balance Has Been Updated"
        message = (
            f"Dear {instance.user.first_name},\n\n"
            f"There has been a {transaction_type} of {difference} in your account.\n"
            f"Your new balance is {new_balance}.\n\n"
            f"Thank you for banking with us.\n\n"
            f"Merchant First Bank"
        )
        recipient_email = instance.user.email

        send_mail(
            subject,
            message,
            'skylinebank059@gmail.com',
            [recipient_email],
            fail_silently=False,
        )


@receiver(post_save, sender=UserProfile)
def create_transaction_on_balance_update(sender, instance, created, **kwargs):
    """
    Creates a transaction record if balance has changed.
    """
    if created or instance._old_balance is None:
        return

    if instance._old_balance != instance.main_balance:
        amount = instance.main_balance - instance._old_balance
        description = 'Credit' if amount > 0 else 'Debit'

        Transaction.objects.create(
            user=instance.user,
            amount=abs(amount),
            balance_after=instance.main_balance,
            description=description
        )
