from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.http import JsonResponse
import json

# Create your views here.

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('staff_main')
            else:
                return redirect('main')
        return redirect('login')
    else:
        return render(request, 'login.html', {})
    
def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('main')
        else:
            return redirect('reg')
    else:
        form = UserCreationForm()
        return render(request, 'register.html', {'form': form,})
    
def main(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'main_new.html', context)

def staff_main(request):
    return render(request, 'staff_main.html', {})

def cart(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete = False)
    items = order.orderitem_set.all()
    context = {'items':items, 'order':order}
    if request.method == "POST":
        order.complete = True
        order.save()
        return redirect('main')
    # return render(request, 'cart.html', context)
    return render(request, 'about_us.html', context)

def profile(request):
    user = request.user
    context = {'user': user}
    return render(request, 'profile.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('ProductId:', productId)
    print('Action:', action)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete = False)
    print(order)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    print(orderItem)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)