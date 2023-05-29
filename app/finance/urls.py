from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name="logout"),
    path('history_transactions', HistoryTransactionsView.as_view(), name="history_transactions"),
    path('expenses', ExpensesHistory.as_view(), name="history_transactions_expenses"),
    path('income', IncomeHistory.as_view(), name="history_transactions_income"),
    path('add_transaction/', AddTransactionView.as_view(), name="add_transaction"),
    path('detail_transaction/<int:pk>', DetailTransactionView.as_view(), name="detail_transaction"),
    path('edit_transaction/<int:pk>', EditTransactionView.as_view(), name="edit_transaction"),
    path('delete_transaction/<int:pk>', DeleteTransactionView.as_view(), name="delete_transaction"),
    path('converter/', exchange, name="converter"),
    path('edit_balance/<str:username>', edit_account_balance, name="edit_account_balance"),
]