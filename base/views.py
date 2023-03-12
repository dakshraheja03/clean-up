from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Location,Category,Tasks
from .forms import TaskImageForm,ApproveForm,TaskForm
from datetime import datetime
from django.db.models import Q

def loginPage(request):
    if(request.user.is_authenticated):
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, 'User doesnt exist')

        user= authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"incorrect password")
        
    return render(request,"base/login_registration.html")

def logoutPage(request):

    logout(request)
    return redirect("home")

@login_required(login_url='loginPage')
def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    if request.user.is_staff:
        tasks = Tasks.objects.filter(
            Q(location__name__icontains = q) |
            Q(category__name__icontains = q)
        )
    else:
        tasks = request.user.tasks_set.filter(
            Q(location__name__icontains = q) |
            Q(category__name__icontains = q)
        )
    print(tasks)
    location = Location.objects.all()
    category = Category.objects.all()
    context = {'tasks':tasks,'locations':location, "categories":category}
    return render(request,"base/home.html",context)

@login_required(login_url='loginPage')
def task_image(request,pk):
# room=Room.objects.get(id=pk)
    task=Tasks.objects.get(id=pk)
    if(request.user == task.assigned):
        form=TaskImageForm(instance=task)
        if request.method == "POST":
            form = TaskImageForm(request.POST,request.FILES,instance=task)
            if form.is_valid():
                temp = form.save(commit=False)
                temp.completed = datetime.now()
                temp.save()
                # messages.SUCCESS(request,"Successfully uploaded")
                return redirect('home')
        context = {"form":form}
        return render(request,'base/task_image.html',context)
    else:
        return HttpResponse("you arent allowed here")
    


@login_required(login_url='loginPage')
def task_approve(request,pk):
# room=Room.objects.get(id=pk)
    task=Tasks.objects.get(id=pk)
    if(request.user.is_staff):
        form=ApproveForm(instance=task)
        if request.method == "POST":
            form = ApproveForm(request.POST,instance=task)
            if form.is_valid():
                temp = form.save(commit=False)
                temp.approved_time = datetime.now()
                temp.save()
                return redirect("home")
        context = {"form":form,"task":task}
        return render(request,'base/task_approve.html',context)
    else:
        return HttpResponse("login as ADMIN user")
    

@login_required(login_url='loginPage')
def task_form(request):
# room=Room.objects.get(id=pk)
    # task=Tasks.objects.get(id=pk)
    if(request.user.is_staff):
        form=TaskForm()
        if request.method == "POST":
            form = TaskForm(request.POST)
            if form.is_valid():
                temp = form.save(commit=False)
                # temp.approved_time = datetime.now()
                temp.save()
                return redirect("home")
        context = {"form":form}
        return render(request,'base/task_form.html',context)
    else:
        return HttpResponse("Login as ADMIN user")