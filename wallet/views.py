from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, WalletTransaction
from .serializers import WalletSerializer, WalletTransactionSerializer


class WalletView(generics.RetrieveAPIView):
    """GET /api/wallet/ — View own wallet."""
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class WalletTransactionHistoryView(generics.ListAPIView):
    """GET /api/wallet/transactions/ — View transaction history."""
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WalletTransaction.objects.filter(wallet__user=self.request.user)
