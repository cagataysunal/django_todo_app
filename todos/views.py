# todos/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserCreationForm, ProfileForm, TodoForm, UserForm
from .models import Profile, Todo


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("todo_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def home(request):
    return render(request, "home.html")


@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user)
    return render(request, "todos/todo_list.html", {"todos": todos})


@login_required
def todo_detail(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if todo.user != request.user:
        return HttpResponseForbidden(
            "You don't have permission to view this TODO item."
        )
    return render(request, "todos/todo_detail.html", {"todo": todo})


@login_required
def todo_create(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            return redirect("todo_list")
    else:
        form = TodoForm()
    return render(request, "todos/todo_form.html", {"form": form})


@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if todo.user != request.user:
        return HttpResponseForbidden(
            "You don't have permission to edit this TODO item."
        )
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("todo_list")
    else:
        form = TodoForm(instance=todo)
    return render(request, "todos/todo_form.html", {"form": form})


@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if todo.user != request.user:
        return HttpResponseForbidden(
            "You don't have permission to delete this TODO item."
        )
    if request.method == "POST":
        todo.delete()
        return redirect("todo_list")
    return render(request, "todos/todo_confirm_delete.html", {"todo": todo})


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        user_form = UserForm(instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(
        request, "profile.html", {"user_form": user_form, "profile_form": profile_form}
    )


@login_required
def profile(request):
    return render(request, "profile.html", {"user": request.user})
