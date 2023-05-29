from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, View, TemplateView, ListView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
import plotly.graph_objects as go
from .forms import *
import pandas as pd
from django.db.models import Sum
from datetime import datetime
from django.utils.timezone import now
import requests


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_account = Account.objects.get(user=self.request.user)
        current_month = datetime.now().strftime('%B')

        start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        summ_current_month = Transaction.objects.filter(type='Ex', date__gte=start_of_month).aggregate(Sum('amount'))

        if summ_current_month['amount__sum']:
            total_amount = summ_current_month['amount__sum']
        else:
            total_amount = 0

        data = Transaction.objects.filter(type="Ex")

        #
        if len(data) > 0:
            df = pd.DataFrame(list(data.values()))
            fig = go.Figure(data=[go.Pie(labels=df['category'], values=df['amount'])])

            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(width=350, height=250, margin=dict(l=0, r=0, t=25, b=0))
            fig.update_layout(title=f"Траты за {current_month}: {round(total_amount, 2)} руб")
            fig.update_layout(paper_bgcolor='#D9D9D9')

            div = fig.to_html(full_html=True)
        else:
            div = "Add your first transaction!"

        context["transaction_history_ex"] = Transaction.objects.filter(account=user_account, type='Ex')[:4]
        context["transaction_history_in"] = Transaction.objects.filter(account=user_account, type='In')[:5]
        context["transaction_history"] = Transaction.objects.filter(account=user_account)[:10]

        context["user_balance"] = Account.objects.get(user=self.request.user).balance
        context["plot_div"] = div
        context["title"] = f"{self.request.user}'s finance"
        return context

@login_required
def edit_account_balance(request, username):
    user = User.objects.get(username=username)
    account = Account.objects.get(user=user)

    if request.method == 'POST':
        form = EditAccountBalanceForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EditAccountBalanceForm(instance=account)

    return render(request, 'edit_account_balance.html', {'form': form, 'title': 'Edit balance'})


# Representation classes for transactions
class BaseTransactionView(LoginRequiredMixin):
    model = Transaction
    success_url = reverse_lazy('home')
    template_name = None


class HistoryTransactionsView(BaseTransactionView ,ListView):
    template_name = 'history_transactions.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_transactions"] = Transaction.objects.all()
        context["title"] = "Transactions History"
        return context


class ExpensesHistory(BaseTransactionView ,ListView):
    template_name = 'history_expenses.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(type='Ex')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["expenses_transactions"] = self.get_queryset()
        context["title"] = "Expenses"
        return context


class IncomeHistory(BaseTransactionView, ListView):
    template_name = 'history_income.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(type='In')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["income_transactions"] = self.get_queryset()
        context["title"] = "Income"
        return context


class AddTransactionView(BaseTransactionView, CreateView):
    form_class = AddTransactionForm
    template_name = 'add_transaction.html'

    def form_valid(self, form):
        account = Account.objects.get(user=self.request.user)
        form.instance.account = account
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add transaction"
        return context


class DetailTransactionView(BaseTransactionView, DetailView):
    context_object_name = "transaction"
    template_name = 'detail_transaction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "About Transaction"
        return context


class EditTransactionView(BaseTransactionView, UpdateView):
    form_class = EditTransactionForm
    template_name = 'edit_transaction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Transaction"
        return context



class DeleteTransactionView(BaseTransactionView, DeleteView):
    template_name = 'delete_transaction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Delete Transaction"
        return context



class RegisterUser(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Registration"
        return context


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Login"
        return context


def logout_user(request):
    logout(request)
    return redirect('login')


def exchange(request):
    response = requests.get(url='https://v6.exchangerate-api.com/v6/3159abda207368bd8f76fb3e/latest/USD').json()
    currencies = response.get('conversion_rates')

    if request.method == 'GET':
        context = {
            'currencies': currencies,
            'title': 'Convertor'
        }
        return render(request, 'converter.html', context=context)

    if request.method == 'POST':
        from_amount = float(request.POST.get('from-amount'))
        from_curr = request.POST.get('from-curr')
        to_curr = request.POST.get('to-curr')

        converted_amount = round((currencies[to_curr] / currencies[from_curr]) * float(from_amount), 2)

        context = {
            'from_amount': from_amount,
            'from_curr': from_curr,
            'to_curr': to_curr,
            'currencies': currencies,
            'converted_amount': converted_amount,
            'title': 'Convertor'
        }
        return render(request, 'converter.html', context=context)