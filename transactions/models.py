from django.db import models

from accounts.models import UserBankAccount
from django.contrib.auth.models import User
from .constants import TRANSACTION_TYPES


class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPES, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(null=True, default=False)
    
    # This line allows a loan repayment to reference the original loan
    # original_loan = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='repayments')
    
    class Meta:
        ordering = ['-timestamp']
    
        indexes = [
                models.Index(fields=['account', 'transaction_type']),
                models.Index(fields=['transaction_type']),
                models.Index(fields=['timestamp'])
            ]


class LoanTransaction(Transaction):
    class Meta:
        proxy = True
        verbose_name = 'Loan Request'
        verbose_name_plural = 'Loan Requests'
