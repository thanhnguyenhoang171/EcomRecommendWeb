from rest_framework import serializers
from .models import (
    Product,
    User,
    Category,
    Order,
    OrderItem,
    Rating,
    Contact,
    ShippingAddress,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.StringRelatedField(many=True)  # Liên kết danh mục phụ

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "sub_categories"]


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)  # Liên kết danh mục sản phẩm

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "description",
            "specification",
            "category",
            "image",
            "imgdes1",
            "imgdes2",
            "imgdes3",
            "imgdes4",
            "imgdes5",
            "ImageURL",
            "ImageURL1",
            "ImageURL2",
            "ImageURL3",
            "ImageURL4",
            "ImageURL5",
        ]


# Shipping Address Serializer
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["id", "customer", "address", "city", "state", "phonenum"]


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer()  # Liên kết thông tin khách hàng
    shipping_address = ShippingAddressSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "date_order",
            "complete",
            "transaction_id",
            "status",
            "shipping_address",
            "get_cart_items",
            "get_cart_total",
        ]


# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "date_added", "get_total"]


# Rating Serializer
class RatingSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Rating
        fields = ["id", "customer", "product", "rating", "content", "created_at"]


# Contact Serializer
class ContactSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Contact
        fields = [
            "id",
            "user",
            "full_name",
            "email",
            "subject",
            "message",
            "phone",
            "created_at",
        ]
