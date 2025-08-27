from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q, Sum
from django.db import transaction as db_transaction

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from datetime import datetime
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string


from .forms import (
    DipositForm, 
    WithdrawalForm, 
    LoanRequestForm
)
from accounts.models import UserBankAccount
from .models import Transaction
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID


# def send_transaction_email(user, amount, subject, template):
#     message = render_to_string(template, {
#         'user': user,
#         'amount': amount,
#     })
#     send_email = EmailMultiAlternatives(subject, '', to=[user.email])
#     send_email.attach_alternative(message, 'text/html')
#     send_email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title':self.title
        })
        return context


class DipositView(TransactionCreateMixin):
    form_class = DipositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        
        account.balance += amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"{amount:.2f} $ was deposited successfully")
        # Send email notification
        # send_transaction_email(
        #     user=self.request.user,
        #     amount=amount,
        #     subject='Deposit Successful',
        #     template='transactions/deposit_email.html'
        # )
        return super().form_valid(form)


class WithdrawalView(TransactionCreateMixin):
    form_class = WithdrawalForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial
    
     # Check if user has any active (unpaid) approved loans
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= amount
        self.request.user.account.save(
            update_fields = ['balance']
        )

        # messages.success(self.request ,f"{amount:.2f} $ was withdrawn from your account successfully")
        # send_transaction_email(self.request.user, amount, "Withdrawal Message", "transactions/withdrawal_email.html")
        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'
    success_url = reverse_lazy('loan_request')

    def get_initial(self):
        return {'transaction_type': LOAN}

    def form_valid(self, form):
        account = self.request.user.account
        amount = form.cleaned_data['amount']
        today = now().date()
        
        # Reset loan count if month changed
        if account.last_loan_date and account.last_loan_date.month != today.month:
            account.loan_count = 0
            account.save()
            
        # Check monthly loan limit
        if account.loan_count >= 3:
            form.add_error('amount', "You can't take more than 3 loans in a month.")
            return self.form_invalid(form)
        
        # Rule 1: Check for any pending loan (requested but not approved yet)
        pending_loans = Transaction.objects.filter(
            account=account,
            transaction_type=LOAN,
            loan_approve=False
        )
        if pending_loans.exists():
            form.add_error('amount', "Admin has not approved your previous loan request yet. Please wait.")
            return self.form_invalid(form)
        

         # Rule 2: Check for any approved but unpaid loan
        loan_status = Transaction.objects.filter(
            account=account,
            transaction_type=LOAN,
            loan_approve=True
        ).exclude(transaction_type=LOAN_PAID).exists()
        if loan_status:
            form.add_error('amount', "You have an approved loan that you haven't paid yet. Please pay it first.")
            return self.form_invalid(form)
        
        # Update loan count and date
        account.loan_count += 1
        account.last_loan_date = today
        account.save()

        messages.success(self.request, f"{amount:.2f} $ was requested for loan successfully")
        # send_transaction_email(self.request.user, amount, "Loan Request Message", "transactions/loan_email.html")
        return super().form_valid(form)

        


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    # paginate_by = 10
    # context_object_name = 'transactions'
    #** if you don't want to use default context object name then you have to write in template:  object_list **#

    def get_queryset(self):
        self.account = UserBankAccount.objects.get(user=self.request.user) #Always get fresh account
        queryset = super().get_queryset().filter(
            account = self.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

            # When filtered, get balance from latest filtered transaction
            last_txn = queryset.order_by('-timestamp').first()
            self.filtered_balance = last_txn.balance_after_transaction if last_txn else 0
            
            return queryset.distinct().order_by('-timestamp')

        else:
            # Get latest actual account balance        
            self.filtered_balance = self.account.balance
        
        return queryset.distinct().order_by('-timestamp')[:10] # Most recent 10
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.account,
            'balance': self.filtered_balance,
            'start_date': self.request.GET.get('start_date'),
            'end_date': self.request.GET.get('end_date'),
        })
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(
            Transaction,
            id=loan_id,
            account=request.user.account,
            transaction_type=LOAN,
            loan_approve=True
        )
        
        account = request.user.account
        
        if loan.amount > account.balance:
            messages.error(request, "Insufficient balance to pay loan")
            return redirect('loan_list')
        
        # Process payment
        account.balance -= loan.amount
        loan.transaction_type = LOAN_PAID
        loan.balance_after_transaction = account.balance
        
        with db_transaction.atomic():
            account.save(update_fields=['balance'])
            loan.save(update_fields=[
                'transaction_type', 
                'balance_after_transaction'
            ])
        
        messages.success(request, "Loan paid successfully")
        return redirect('loan_list')
        




class LoanListView(LoginRequiredMixin, ListView):
    template_name = 'transactions/loan_request.html' 
    model = Transaction
    context_object_name = 'loans'
    
    # def get_queryset(self):
    #     user_account = self.request.user.account
    #     queryset = Transaction.objects.filter(
    #         account=user_account,
    #         transaction_type=LOAN
    #     )
    #     return queryset
    
    def get_queryset(self):
        user_account = self.request.user.account
        return Transaction.objects.filter(
            account=user_account,
            transaction_type=LOAN
        )


    