from django.contrib import admin
from .models import Transaction, LoanTransaction
from .constants import LOAN
from django.contrib import messages
from .views import send_transaction_email


# Admin for all transactions EXCEPT loans
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type' ,'timestamp']
    exclude = ['loan_approve']
    list_filter = ['transaction_type', 'timestamp', 'account', 'account__user__username']
    search_fields = ['account__user__username', 'account__account_number']
    list_per_page = 20
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(transaction_type=LOAN)  # Show non-loan transactions only


# Admin for LOAN transactions only
@admin.register(LoanTransaction)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve', 'timestamp'] 
    # list_editable = ['loan_approve']
    list_filter = ['loan_approve', 'timestamp', 'account', 'account__user__username']
    search_fields = ['account__user__username', 'account__account_number']
   

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(transaction_type=LOAN)  # Show only loan transactions


    def save_model(self, request, obj, form, change):
        account = obj.account
        is_approved = obj.loan_approve

        # print("=== Saving LoanTransaction ===")
        # print("Change detected:", change)
        # print("Loan approved now:", is_approved)

        if change:
            try:
                previous = Transaction.objects.get(pk=obj.pk)
            except Transaction.DoesNotExist:
                previous = None

            if previous:
                # print("Previous loan approved:", previous.loan_approve)

                # Approval Cancelled (True -> False)
                if previous.loan_approve and not is_approved:
                    if account.balance >= obj.amount:
                        account.balance -= obj.amount
                        obj.balance_after_transaction = account.balance
                        account.save()
                        # print(f"Loan reversed. New balance: {account.balance}")
                    else:
                        messages.warning(request, "Insufficient balance to reverse loan")
                        obj.loan_approve = True  # Revert back
                        return  # Don't save this object

                # New Approval (False -> True)
                elif not previous.loan_approve and is_approved:
                    account.balance += obj.amount
                    obj.balance_after_transaction = account.balance
                    account.save()
                    # print(f"Loan approved. New balance: {account.balance}")
        else:
            # Initial creation
            if is_approved:
                account.balance += obj.amount
                obj.balance_after_transaction = account.balance
                account.save()
                # print(f"Loan initially approved. New balance: {account.balance}")
            else:
                obj.balance_after_transaction = account.balance
                # print("Loan requested but not approved yet.")
            
        send_transaction_email(obj.account.user, obj.amount, "Loan Approval", "transactions/admin_email.html")
        super().save_model(request, obj, form, change)



