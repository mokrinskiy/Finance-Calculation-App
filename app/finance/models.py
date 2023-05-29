from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.user)


class Transaction(models.Model):
    TYPES_CHOICES = (
        ('Ex', 'Expenses'),
        ('In', 'Income')
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    previous_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type = models.CharField(max_length=8 ,choices=TYPES_CHOICES, default='Expenses')
    category = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.account.user} - {self.category} {self.amount}'
    
    def get_absolute_url(self):
        return reverse("detail_transaction", kwargs={"pk": self.pk})
    
    @classmethod
    def get_expenses_for_current_month(cls):
        current_month = timezone.now().month
        return cls.objects.filter(date__month=current_month, type='Ex')

    @classmethod
    def reset_expenses_for_new_month(cls):
        current_month = timezone.now().month
        cls.objects.filter(date__month=current_month, type='Ex').update(amount=0)
    
    class Meta:
        ordering = ['-pk']
    

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    limit = models.DecimalField(max_digits=10, decimal_places=2)


class Category(models.Model):
    name = models.CharField(max_length=100)


class RegularPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    due_date = models.DateField()