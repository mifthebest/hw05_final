from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserCreation


class SignUp(CreateView):
    form_class = UserCreation
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
