from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone  # Thêm dòng này để nhập timezone

# Custom User Registration Form
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]


class Category(models.Model):
    sub_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="sub_categories",
        null=True,
        blank=True,
    )
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ManyToManyField(Category, related_name="products")
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    description = models.TextField(null=True, blank=True)
    specification = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    imgdes1 = models.ImageField(null=True, blank=True)
    imgdes2 = models.ImageField(null=True, blank=True)
    imgdes3 = models.ImageField(null=True, blank=True)
    imgdes4 = models.ImageField(null=True, blank=True)
    imgdes5 = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    # Helper methods to handle missing images
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ""
        return url

    @property
    def ImageURL1(self):
        try:
            url = self.imgdes1.url
        except:
            url = ""
        return url

    @property
    def ImageURL2(self):
        try:
            url = self.imgdes2.url
        except:
            url = ""
        return url

    @property
    def ImageURL3(self):
        try:
            url = self.imgdes3.url
        except:
            url = ""
        return url

    @property
    def ImageURL4(self):
        try:
            url = self.imgdes4.url
        except:
            url = ""
        return url

    @property
    def ImageURL5(self):
        try:
            url = self.imgdes5.url
        except:
            url = ""
        return url


class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    phonenum = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.customer.username} - {self.address}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("Accepted", "Accepted"),
        ("Packed", "Packed"),
        ("On The Way", "On The Way"),
        ("Delivered", "Delivered"),
        ("Cancel", "Cancel"),
        ("Pending", "Pending"),
    )

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Pending"
    )  # Trạng thái đơn hàng
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, blank=True, null=True
    )
    def __str__(self):
        return str(self.id)

    @property
    def get_cart_items(self):
        return sum([item.quantity for item in self.orderitem_set.all()])

    @property
    def get_cart_total(self):
        return sum([item.get_total for item in self.orderitem_set.all()])


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True
    )  # Sử dụng CASCADE để giữ dữ liệu
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.product.price * self.quantity


class Rating(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    content = models.TextField(null=True, blank=True)  # Thêm trường bình luận
    created_at = models.DateTimeField(default=timezone.now)  # Thêm trường thời gian tạo

    class Meta:
        unique_together = (
            "customer",
            "product",
        )  # Đảm bảo mỗi user chỉ đánh giá 1 sản phẩm 1 lần

    def __str__(self):
        # Kiểm tra nếu customer và product không phải là None
        customer_username = self.customer.username if self.customer else "Anonymous"
        product_name = self.product.name if self.product else "No Product"

        # Kiểm tra nếu content không phải là None
        if self.content:
            comment_preview = f"{self.content[:20]}{'...' if len(self.content) > 20 else ''}"  # Hiển thị 20 ký tự đầu tiên của bình luận
        else:
            comment_preview = "No Comment"

        return f"{customer_username} - {product_name} - {self.rating} - Comment: {comment_preview}"


class Contact(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )  # Khóa ngoại tới User
    full_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200, null=True)
    message = models.TextField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Lưu thời gian gửi liên hệ

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    class Meta:
        ordering = ["-created_at"]  # Sắp xếp theo thời gian gần nhất

STATUS_CHOICES = (
    ("Accepted", "Accepted"),
    ("Packed", "Packed"),
    ("On The Way", "On The Way"),
    ("Delivered", "Delivered"),
    ("Cancel", "Cancel"),
    ("Pending", "Pending"),
)

