from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    OrderViewSet,
    CategoryViewSet,
    OrderItemViewSet,
    ContactViewSet,
    RatingViewSet,
    ShippingAddressViewSet,
)


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"orderitems", OrderItemViewSet, basename="orderitem")
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"ratings", RatingViewSet, basename="rating")
router.register(r"shippingaddress", ShippingAddressViewSet, basename="shippingaddress")

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart, name="cart"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutPage, name="logout"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("register/", views.register, name="register"),
    path("search/", views.search, name="search"),
    path("category/", views.category, name="category"),
    path("detail/", views.detail, name="detail"),
    path("contact/", views.contact, name="contact"),
    path("aboutus/", views.aboutus, name="aboutus"),
    path("info/", views.info, name="info"),
    path("process_payment/", views.process_payment, name="process_payment"),
    path("evaluate/", views.evaluate, name="evaluate"),
    path("api/", include(router.urls)),
]
