DEPOSIT = 1
WITHDRAWAL = 2
LOAN = 3
LOAN_PAID = 4

# Tuple for model field choices
TRANSACTION_TYPES = (
    (DEPOSIT, 'Deposit'),
    (WITHDRAWAL, 'Withdrawal'),
    (LOAN, 'Loan'),
    (LOAN_PAID, 'Loan Repayment'),
)