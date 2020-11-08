from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, f"Account successfully created, {form.cleaned_data.get('username')}")
            form.save()
            return redirect('user-login')
    else:
        form = UserRegistrationForm()
    context = {'form': form}
    return render(request, 'users/register.html', context)
