from django.db import models
from core.models import BaseModel


class Wallet(BaseModel):
    """User wallet for credits and payouts."""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet: {self.user.email} (Bal: {self.balance})"


class WalletTransaction(BaseModel):
    """Transaction log for a wallet."""
    TRANSACTION_TYPES = [
        ('top_up', 'Top Up'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('earnings', 'Earnings'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} for {self.wallet.user.email}"
