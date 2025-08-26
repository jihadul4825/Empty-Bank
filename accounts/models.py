from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPES, GENDER_TYPES

# Create your models here.


class UserBankAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    account_type = models.CharField(choices=ACCOUNT_TYPES)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_TYPES)
    initial_deposit_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    last_loan_date = models.DateField(blank=True, null=True)
    loan_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return str(self.account_no)


class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.email
