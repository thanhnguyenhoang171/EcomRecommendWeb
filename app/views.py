from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    categories = Category.objects.filter(is_sub=False)
    context = {
        "products": products,
        "cartItems": cartItems,
        "categories": categories,
    }
    return render(request, "app/home.html", context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub=False)
    
    context = {"items": items, "order": order, "cartItems": cartItems, "categories":categories}
    return render(request, "app/cart.html", context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "app/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Xử lý từng item trong giỏ hàng
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity += 1
    elif action == "remove":
        orderItem.quantity -= 1

    orderItem.save()
    
    if action == "removefromcart":
        # Xóa toàn bộ đơn hàng và các item
        orderItem.delete()
        # Kiểm tra nếu không còn item nào trong giỏ hàng thì xóa đơn hàng
        if not order.orderitem_set.exists():
            order.delete()

    # Nếu số lượng của một item <= 0 thì cũng xóa nó
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item updated", safe=False)


def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            messages.info(request, "Nhập lại mật khẩu chưa chính xác!")
    context = {"form": form}
    return render(request, "app/register.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Tên đăng nhập hoặc mật khẩu chưa đúng!")
    context = {}
    return render(request, "app/login.html", context)


def logoutPage(request):
    logout(request)
    return redirect("login")


def search(request):
    if request.method == "POST":
        searched = request.POST["searched"]
        keys = Product.objects.filter(name__contains=searched)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'order.get_cart_total': 0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()

    return render(
        request,
        "app/search.html",
        {
            "searched": searched,
            "keys": keys,
            "products": products,
            "cartItems": cartItems,
        },
    )


def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get("category", "")
    products = (
        Product.objects.filter(category__slug=active_category)
        if active_category
        else None
    )

    # # Fetch subcategories linked to each category
    subcategories = Category.objects.filter(is_sub=True)

    context = {
        "categories": categories,
        "products": products,
        "active_category": active_category,
        "subcategories": subcategories,
    }
    return render(request, "app/category.html", context)


def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0}
        cartItems = order["get_cart_items"]
    categories = Category.objects.filter(is_sub=False)

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "categories": categories,
    }
    return render(request, "app/detail.html", context)
