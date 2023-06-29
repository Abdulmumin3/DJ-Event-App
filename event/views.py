from django.shortcuts import render, redirect
from .models import User, Event, Submission
from .forms import SubmissionForm, CustomUserCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
# from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def login_page(request):
    page = 'login'
    
    if request.method == 'POST':
        user = authenticate(
            email = request.POST['email'],
            password = request.POST['password']
        )
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'event\login_register.html', {'page':page})

def logout_user(request):
    logout(request)
    return redirect('login')
    
def register_page(request):
    page = 'register'
    form = CustomUserCreateForm()
    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        
    return render(request, 'event\login_register.html', {'page':page, 'form':form})

def home_page(request):
    users = User.objects.filter(hackathon_participant=True)
    users = users[0:20]
    events = Event.objects.all()
    return render(request, 'event\home.html', {'users':users, 'events':events})

def user_page(request, pk):
    user = User.objects.get(id=pk)
    return render(request, 'event\profile.html', {'user':user})

@login_required(login_url='login')
def account_page(request):
    user = request.user
    return render(request, 'event\my_account.html', {'user':user})


def event_page(request, pk):
    event = Event.objects.get(id=pk)
    
    registered = False
    submitted = False

    if request.user.is_authenticated:
        registered = request.user.events.filter(id=event.id).exists()
        submitted = Submission.objects.filter(participant=request.user, event=event).exists()
        
    return render(request, 'event\event.html', {'event':event, 'registered':registered, 'submitted':submitted})

@login_required(login_url='login')   
def registration_confirmation(request, pk):
    event = Event.objects.get(id=pk)
    if request.method == 'POST':
        event.participants.add(request.user)
        return redirect('event', pk=event.id)
    return render(request, 'event\event_confirmation.html', {'event':event})

@login_required(login_url='login')
def project_submission(request, pk):
    event = Event.objects.get(id=pk)
    form = SubmissionForm()
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.event = event
            instance.participant = request.user
            instance.save()
            return redirect('my_account')
    return render(request, 'event\submit_form.html', {'event':event, 'form':form})

@login_required(login_url='login')
def update_submission(request, pk):
    submission = Submission.objects.get(id=pk)
    
    if request.user != submission.participant:
        raise Http404
    
    event = submission.event
    form = SubmissionForm(instance=submission)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.event = event
            instance.participant = request.user
            instance.save()
            return redirect('my_account')
    return render(request, 'event\submit_form.html', {'event':event, 'form':form})
