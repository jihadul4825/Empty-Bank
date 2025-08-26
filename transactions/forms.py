from django import forms
from django.db.models import Sum
from .models import Transaction
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
    
class DipositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(f"You need to deposit at least {min_deposit_amount} $")
        return amount


class WithdrawalForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdrawal_amount = 500                                                        
        max_withdrawal_amount = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if amount < min_withdrawal_amount:
            raise forms.ValidationError(f"You need to withdraw at least {min_withdrawal_amount} $")
        if amount > max_withdrawal_amount:
            raise forms.ValidationError(f"You cannot withdraw more than {max_withdrawal_amount} $")
        if amount > balance:
            raise forms.ValidationError(f"You cannot withdraw more than {balance} $")
        
        return amount
    

class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        min_loan_amount = 2000
        max_loan_amount = 1000000
        amount = self.cleaned_data.get('amount')
        if amount < min_loan_amount:
            raise forms.ValidationError(f"You need to request at least {min_loan_amount} $")
        if amount > max_loan_amount:
            raise forms.ValidationError(f"You cannot request more than {max_loan_amount} $")
        
        return amount
    

        
# class LoanRepaymentForm(forms.ModelForm):
#     loan = forms.ModelChoiceField(
#         queryset=Transaction.objects.filter(transaction_type=LOAN),
#         label='Select Loan'
#     )

#     class Meta:
#         model = Transaction
#         fields = ['loan', 'amount', 'transaction_type']

#     def __init__(self, *args, **kwargs):
#         self.account = kwargs.pop('account', None)  # Avoid KeyError
#         super().__init__(*args, **kwargs)

#         # Set initial value and hide transaction type
#         self.fields['transaction_type'].initial = LOAN_PAID
#         self.fields['transaction_type'].widget = forms.HiddenInput()

#         # Limit loans to user's own active loans
#         if self.account:
#             self.fields['loan'].queryset = Transaction.objects.filter(
#                 account=self.account,
#                 transaction_type=LOAN,
#             )

#     def clean(self):
#         cleaned_data = super().clean()
#         loan = cleaned_data.get('loan')
#         amount = cleaned_data.get('amount')

#         if loan and amount:
#             # Total already paid
#             total_paid = Transaction.objects.filter(
#                 original_loan=loan,
#                 transaction_type=LOAN_PAID
#             ).aggregate(total=Sum('amount'))['total'] or 0

#             # Ensure total paid + new amount doesn't exceed loan amount
#             if total_paid + amount > loan.amount:
#                 raise forms.ValidationError("Repayment exceeds the original loan amount.")

#         return cleaned_data

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.account = self.account
#         instance.original_loan = self.cleaned_data['loan']
#         instance.balance_after_transaction = self.account.balance
#         if commit:
#             instance.save()
#         return instance