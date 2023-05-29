from django import forms
from .models import *

class AddTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'category']

class EditTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'category']

class EditAccountBalanceForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['balance']