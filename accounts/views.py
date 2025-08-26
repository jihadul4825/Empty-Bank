from django.shortcuts import render
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth.models import User

from django.views.generic import FormView, UpdateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class UserRegistrationView(FormView):
    template_name = 'accounts/user_register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # print(user)
        return super().form_valid(form)
        

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')

class UserProfileUpdateView(UpdateView):
    template_name = 'accounts/profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    


    