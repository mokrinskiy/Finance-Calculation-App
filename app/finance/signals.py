from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_account(sender, instance, **kwargs):
    instance.account.save()

# После сохранения 
@receiver(post_save, sender=Transaction)
def update_budget_on_transaction_save(sender, instance, created, **kwargs):
    account = instance.account
    amount = instance.amount

    if created:
        if instance.type == 'Ex':
            account.balance -= amount
        else:
            account.balance += amount
    else:
        if instance.type == 'Ex':
            account.balance -= amount - instance.previous_amount
        else:
            account.balance += amount - instance.previous_amount

    account.save()

# После удаления
@receiver(post_delete, sender=Transaction)
def update_budget_on_transaction_delete(sender, instance, **kwargs):
    account = instance.account
    amount = instance.amount

    if instance.type == 'Ex':
        account.balance += amount
    else:
        account.balance -= amount

    account.save()

# Перед сохранением объекта
@receiver(pre_save, sender=Transaction)
def store_previous_amount(sender, instance, **kwargs):
    if instance.pk:
        # Если объект уже существует (редактирование транзакции)
        old_instance = Transaction.objects.get(pk=instance.pk)
        instance.previous_amount = old_instance.amount
    else:
        # Если объект новый (создание транзакции)
        instance.previous_amount = 0  # Или любое другое начальное значение