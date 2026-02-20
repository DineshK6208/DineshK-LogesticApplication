from rest_framework import serializers
from .models import Wallet, WalletTransaction


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'description', 'created_at']


class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'transactions']
        read_only_fields = ['id', 'balance']
