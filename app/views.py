from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    Category,
    Product,
    ShippingAddress,
    Order,
    OrderItem,
    Rating,
    Contact,
)
from .recommendation import CFRecommender
from django.db.models import Avg
from .evaluate import Evaluator
from rest_framework import viewsets
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ShippingAddressSerializer,
    OrderSerializer,
    OrderItemSerializer,
    RatingSerializer,
    ContactSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.filter(
            customer=customer, complete=False
        ).first()  # Lấy order nếu đã tồn tại
        if order:
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        else:
            items = []
            cartItems = 0
    else:
        items = []
        cartItems = 0

    products = Product.objects.all().order_by("?")
    categories = Category.objects.filter(is_sub=False)

    # Pagination
    paginator = Paginator(products, 20)  # Hiển thị 20 sản phẩm mỗi trang
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "cartItems": cartItems,
        "categories": categories,
    }
    return render(request, "app/home.html", context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        try:
            # Chỉ tìm đơn hàng chưa hoàn thành thay vì tạo mới
            order = Order.objects.get(customer=customer, complete=False)
        except Order.DoesNotExist:
            # Không có đơn hàng chưa hoàn thành, không tạo mới
            order = None

        items = order.orderitem_set.all() if order else []
        cartItems = order.get_cart_items if order else 0
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
    return render(request, "app/cart.html", context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0}
        cartItems = order["get_cart_items"]

    # Lấy thông tin địa chỉ giao hàng của khách hàng
    shipping_infos = ShippingAddress.objects.filter(customer=request.user)

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "shipping_infos": shipping_infos,
    }

    return render(request, "app/checkout.html", context)


def updateItem(request):
    if request.user.is_authenticated:  # Kiểm tra nếu người dùng đã đăng nhập
        data = json.loads(request.body)
        productId = data.get("productId")
        action = data.get("action")

        if not productId or not action:
            return JsonResponse({"error": "Invalid data"}, status=400)

        try:
            product = Product.objects.get(id=productId)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)

        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Xử lý từng item trong giỏ hàng
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product
        )

        if action == "add":
            orderItem.quantity += 1
        elif action == "remove":
            orderItem.quantity -= 1
        orderItem.save()

        # Nếu số lượng <= 0, xóa item khỏi giỏ hàng
        if orderItem.quantity <= 0:
            orderItem.delete()

        # Nếu xóa item khỏi giỏ hàng mà không còn item nào, xóa luôn đơn hàng
        if action == "removefromcart":
            orderItem.delete()
            if not order.orderitem_set.exists():  # Không còn item nào trong đơn hàng
                order.delete()

        return JsonResponse("Item updated", safe=False)

    else:
        return redirect("login")  # Chuyển hướng đến trang đăng nhập nếu chưa đăng nhập


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
            messages.error(
                request, "Tên đăng nhập hoặc mật khẩu chưa đúng!"
            )  # Chỉ hiển thị thông báo lỗi đăng nhập

    context = {}
    return render(request, "app/login.html", context)


def logoutPage(request):
    logout(request)
    return redirect("login")


def search(request):
    searched = request.POST.get("searched", "")
    keys = Product.objects.filter(name__contains=searched) if searched else []

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0}
        cartItems = order["get_cart_items"]

    products = Product.objects.all()
    categories = Category.objects.filter(is_sub=False)
    return render(
        request,
        "app/search.html",
        {
            "searched": searched,
            "keys": keys,
            "products": products,
            "cartItems": cartItems,
            "categories": categories,
        },
    )


def category(request):
    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.filter(
            customer=customer, complete=False
        ).first()  # Change here
        items = order.orderitem_set.all() if order else []
        cartItems = order.get_cart_items if order else 0  # Update to handle None

    else:
        items = []
        cartItems = 0  # Directly set to 0 since there's no order

    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get("category", "")
    products = (
        Product.objects.filter(category__slug=active_category).order_by("?")
        if active_category
        else Product.objects.all().order_by("?")
    )

    subcategories = Category.objects.filter(is_sub=True)

    context = {
        "categories": categories,
        "products": products,
        "active_category": active_category,
        "subcategories": subcategories,
        "cartItems": cartItems,
    }
    return render(request, "app/category.html", context)


def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.filter(customer=customer, complete=False).first()
        cartItems = order.get_cart_items if order else 0

        recommender = CFRecommender(k=5)

        try:
            recommender.fit()  # Huấn luyện mô hình
            recommended_products = recommender.recommend(customer.id)
        except ValueError as e:
            if str(e) == "Không có dữ liệu đánh giá để huấn luyện mô hình.":
                recommended_products = []
                print("Không có dữ liệu đánh giá để tạo gợi ý sản phẩm.")
            else:
                recommended_products = []
                print(f"Error fetching recommendations: {e}")

        # Lấy danh sách sản phẩm mà người dùng đã đánh giá
        existing_product_ids = Rating.objects.filter(customer=customer).values_list(
            "product_id", flat=True
        )

        # Lọc ra sản phẩm đã đánh giá
        recommended_products = [
            p for p in recommended_products if p.id not in existing_product_ids
        ]

        if request.method == "POST":
            comment_content = request.POST.get("comment")
            rating_value = request.POST.get("rating")

            existing_rating = Rating.objects.filter(
                customer=customer, product__id=request.GET.get("id")
            ).first()

            if existing_rating:
                existing_rating.rating = float(rating_value)
                existing_rating.content = comment_content
                existing_rating.save()
                messages.success(request, "Đánh giá của bạn đã được cập nhật!")
            else:
                Rating.objects.create(
                    customer=customer,
                    product=Product.objects.get(id=request.GET.get("id")),
                    rating=float(rating_value),
                    content=comment_content,
                )
                messages.success(request, "Đánh giá của bạn đã được lưu!")

    else:
        return redirect("login")

    id = request.GET.get("id", "")
    products = Product.objects.filter(id=id)

    if not products.exists():
        messages.error(request, "Sản phẩm không tồn tại.")
        return render(request, "app/detail.html", {})

    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.filter(customer=customer, complete=False).first()
        if order:
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        else:
            items = []
            cartItems = 0
    else:
        items = []
        cartItems = 0

    categories = Category.objects.filter(is_sub=False)
    product = products.first()
    ratings = Rating.objects.filter(product=product).order_by("-created_at")
    star_range = range(1, 6)
    total_reviews = ratings.count()
    avg_rating = ratings.aggregate(Avg("rating"))["rating__avg"] or 0.0

    context = {
        "products": products,
        "cartItems": cartItems,
        "categories": categories,
        "ratings": ratings,
        "star_range": star_range,
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
        "recommended_products": recommended_products,
    }
    return render(request, "app/detail.html", context)


def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Kiểm tra xem các trường có giá trị hợp lệ không
        if full_name and email and subject and message:
            # Tạo một instance của Contact nhưng chưa lưu vào cơ sở dữ liệu
            contact = Contact(
                full_name=full_name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
            )

            # Nếu người dùng đã đăng nhập, gán họ vào trường user
            if request.user.is_authenticated:
                contact.user = request.user

            # Lưu vào cơ sở dữ liệu
            contact.save()

            # Thông báo thành công và chuyển hướng
            messages.success(request, "Tin nhắn của bạn đã được gửi thành công!")
            return redirect(
                "contact"
            )  # Redirect về trang liên hệ hoặc bất kỳ trang nào bạn muốn

        else:
            # Nếu có trường bắt buộc nào thiếu, thông báo lỗi
            messages.error(request, "Vui lòng điền đầy đủ thông tin bắt buộc!")

    return render(request, "app/contact.html")  # Render lại trang liên hệ


def aboutus(request):
    context = {}
    return render(request, "app/aboutus.html", context)  # Render lại trang liên hệ


def info(request):
    if request.method == "POST":
        # Lưu thông tin vận chuyển
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        phonenum = request.POST.get("phonenum")

        if address and city and state and phonenum:
            shipping_info, created = ShippingAddress.objects.get_or_create(
                customer=request.user
            )
            shipping_info.address = address
            shipping_info.city = city
            shipping_info.state = state
            shipping_info.phonenum = phonenum
            shipping_info.save()

            messages.success(request, "Thông tin vận chuyển đã được lưu!")
            return redirect("info")  # Redirect để hiển thị thông tin mới đã lưu
        else:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin!")

    # Handle GET request: hiển thị thông tin vận chuyển đã lưu
    shipping_infos = ShippingAddress.objects.filter(customer=request.user)

    if request.user.is_authenticated:
        customer = request.user

        # Fetch all orders for the user
        orders = Order.objects.filter(customer=customer)

        # Try to get current incomplete order, but do not create it
        order = Order.objects.filter(customer=customer, complete=False).first()

        # If an order exists, fetch its items, otherwise set empty items and cart
        if order:
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        else:
            items = []
            cartItems = 0
    else:
        items = []
        orders = []  # No orders if user is not authenticated
        order = None
        cartItems = 0

    categories = Category.objects.filter(is_sub=False)

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "categories": categories,
        "shipping_infos": shipping_infos,
        "orders": orders,  # Add orders to context
    }

    return render(request, "app/info.html", context)


def process_payment(request):
    if request.method == "POST":
        # Simulate successful payment (replace with actual payment logic)
        payment_success = True

        if payment_success:
            # Tìm đơn hàng chưa hoàn thành của người dùng
            try:
                order = Order.objects.get(customer=request.user, complete=False)
            except Order.DoesNotExist:
                messages.error(request, "Không tìm thấy đơn hàng chưa hoàn thành.")
                return redirect(
                    "checkout"
                )  # Quay lại trang checkout nếu không tìm thấy đơn hàng

            # Kiểm tra xem đơn hàng đã hoàn thành trước đó hay chưa
            if order.complete:
                messages.warning(request, "Đơn hàng đã được thanh toán trước đó.")
                return redirect(
                    "checkout"
                )  # Quay lại trang checkout nếu đơn hàng đã hoàn thành

            # Kiểm tra xem người dùng đã có địa chỉ giao hàng chưa
            shipping_address = ShippingAddress.objects.filter(
                customer=request.user
            ).first()

            if not shipping_address:
                # Nếu không có địa chỉ, yêu cầu người dùng tạo địa chỉ giao hàng
                messages.error(
                    request, "Vui lòng tạo địa chỉ giao hàng trước khi thanh toán."
                )
                return redirect("info")  # Chuyển hướng đến trang tạo địa chỉ giao hàng

            # Cập nhật trạng thái đơn hàng thành đã hoàn thành và thêm thông tin địa chỉ giao hàng
            order.complete = True
            order.shipping_address = (
                shipping_address  # Gán địa chỉ giao hàng vào đơn hàng
            )
            order.save()

            # Thông báo thanh toán thành công
            messages.success(request, "Thanh toán thành công!")
            return redirect(
                "cart"
            )  # Quay lại trang checkout sau khi thanh toán thành công

        else:
            # Nếu thanh toán thất bại
            messages.error(
                request, "Có lỗi xảy ra trong quá trình thanh toán. Vui lòng thử lại."
            )
            return redirect("checkout")

    # Nếu không phải phương thức POST, quay lại trang checkout
    return redirect("checkout")


def evaluate(request):
    # Khởi tạo mô hình và huấn luyện
    recommender = CFRecommender(k=30, CF=1)
    recommender.fit()

    # Khởi tạo evaluator
    evaluator = Evaluator(recommender)

    # Gọi phương thức đánh giá
    SE, RMSE = (
        evaluator.evaluate()
    )  # Lưu ý: đảm bảo phương thức evaluate() trả về SE và RMSE

    # Kiểm tra kết quả
    if SE is None or RMSE is None:
        # Xử lý trường hợp không có dữ liệu
        return HttpResponse("Không có dữ liệu để đánh giá.")

    # Xử lý và trả về phản hồi bình thường
    return HttpResponse(f"SE: {SE}, RMSE: {RMSE}")


# Tạo API
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
