from django.urls import path
from .views import WalletView, WalletTransactionHistoryView

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet-detail'),
    path('wallet/transactions/', WalletTransactionHistoryView.as_view(), name='wallet-transactions'),
]
