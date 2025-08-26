from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .constants import ACCOUNT_TYPES, GENDER_TYPES
from django import forms 
from django.contrib.auth.models import User
from .models import UserBankAccount, UserAddress


class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPES)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'account_type', 'birth_date', 'street_address', 'gender', 'postal_code', 'city', 'country']
        
    
    def save(self, commit=True):
        user = super().save(commit=False) 
        if commit == True:
            user.save()
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            birth_date = self.cleaned_data.get('birth_date')
            street_address = self.cleaned_data.get('street_address')
            city = self.cleaned_data.get('city')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            
            UserAddress.objects.create(
                user = user,
                street_address = street_address,
                city = city,
                postal_code = postal_code,
                country = country
            )
            
            UserBankAccount.objects.create(
                user = user,
                account_type = account_type,
                birth_date = birth_date,
                gender = gender,
                account_no = 100000 + user.id
            )
            
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-300 text-gray-700 border border-gray-300 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500'
                )
            })
            

class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPES)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-300 text-gray-700 border border-gray-300 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500'
                )
            })
        
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None
            
            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['gender'].initial = user_account.gender
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserBankAccount.objects.get_or_create(user=user)
            user_address, created = UserAddress.objects.get_or_create(user=user)
            
            user_account.account_type = self.cleaned_data.get('account_type')
            user_account.birth_date = self.cleaned_data.get('birth_date')
            user_account.gender = self.cleaned_data.get('gender')
            user_account.save()
            
            user_address.street_address = self.cleaned_data.get('street_address')
            user_address.city = self.cleaned_data.get('city')
            user_address.postal_code = self.cleaned_data.get('postal_code')
            user_address.country = self.cleaned_data.get('country')
            user_address.save()
        
        return user





# class UserUpdateForm(UserChangeForm):
#     birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     gender = forms.ChoiceField(choices=GENDER_TYPES)
#     account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)
#     street_address = forms.CharField(max_length=100)
#     city = forms.CharField(max_length=100)
#     postal_code = forms.IntegerField()
#     country = forms.CharField(max_length=100)

#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         for field in self.fields:
#             self.fields[field].widget.attrs.update({
#                 'class': (
#                     'appearance-none block w-full bg-gray-300 text-gray-700 border border-gray-300 '
#                     'rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500'
#                 )
#             })

#         if self.instance:
#             try:
#                 user_account = self.instance.account
#                 user_address = self.instance.address
#             except UserBankAccount.DoesNotExist:
#                 user_account = None
#                 user_address = None

#             if user_account:
#                 self.fields['account_type'].initial = user_account.account_type
#                 self.fields['birth_date'].initial = user_account.birth_date
#                 self.fields['gender'].initial = user_account.gender
#             if user_address:
#                 self.fields['street_address'].initial = user_address.street_address
#                 self.fields['city'].initial = user_address.city
#                 self.fields['postal_code'].initial = user_address.postal_code
#                 self.fields['country'].initial = user_address.country

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         if commit:
#             user.save()

#             user_account, _ = UserBankAccount.objects.get_or_create(user=user)
#             user_address, _ = UserAddress.objects.get_or_create(user=user)

#             user_account.account_type = self.cleaned_data.get('account_type')
#             user_account.birth_date = self.cleaned_data.get('birth_date')
#             user_account.gender = self.cleaned_data.get('gender')
#             user_account.save()

#             user_address.street_address = self.cleaned_data.get('street_address')
#             user_address.city = self.cleaned_data.get('city')
#             user_address.postal_code = self.cleaned_data.get('postal_code')
#             user_address.country = self.cleaned_data.get('country')
#             user_address.save()

#         return user

        
        

        
    