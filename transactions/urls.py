from django.urls import path
from .views import DipositView, WithdrawalView, LoanRequestView, LoanListView, PayLoanView, TransactionReportView

urlpatterns = [
    path("deposit/", DipositView.as_view(), name="deposit"),
    path("withdrawal/", WithdrawalView.as_view(), name="withdrawal"),
    path("loan_request/", LoanRequestView.as_view(), name="loan_request"),
    path("loan_list/", LoanListView.as_view(), name="loan_list"),
    path("pay_loan/<int:loan_id>/", PayLoanView.as_view(), name="pay_loan"),
    path("transaction_report/", TransactionReportView.as_view(), name="transaction_report"),
]
    