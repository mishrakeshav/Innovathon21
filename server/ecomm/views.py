from django.db import models
from django.shortcuts import get_object_or_404, render
from django.views import generic
from rest_framework import generics, permissions, filters
from rest_framework import response
from rest_framework.response import Response
import django_filters.rest_framework

from .models import (Category, Product, Order, OrderItem, Cart)
from .serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderItemCreateSerializer,
    CategorySerializer
)


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = {
        'name': ['contains'],
        'price': ['exact', 'gte', 'lte'],
        'category': ['exact'],
        'model_number': ['contains'],
        'other': ['contains']
    }
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter, filters.OrderingFilter
    ]
    search_fields = ['$name', '$category',
                     '$model_number', '$other']
    ordering_fields = ['price', ]


class OrderDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        orders = Order.objects.filter(user=user_id)
        return orders

    def post(self, request, *args, **kwargs):
        data = request.data
        order = Order.objects.create(
            user=request.user,
            shipping_address=data.get('shipping_address'),
        )

        orderitem_list = data.get('order_item')
        for id in orderitem_list:
            orderitem = get_object_or_404(OrderItem, pk=id)

            cart_item = Cart.objects.filter(order_item=orderitem)
            cart_item.delete()

            orderitem.order = order
            orderitem.save()

        return Response(
            data=OrderSerializer(order).data
        )


class OrderItemList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        order_item = list(map(
            lambda cart: cart.order_item,
            Cart.objects.filter(user=user).all()
        ))
        return order_item


class OrderItemCreate(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemCreateSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        product = get_object_or_404(Product, pk=data.get('product'))

        order_item = OrderItem.objects.create(
            product=product,
            quantity=int(data.get('quantity')),
            price=product.price,
        )

        Cart.objects.create(user=request.user, order_item=order_item)

        return Response(
            data=OrderItemCreateSerializer(order_item).data
        )


class OrderItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    # TODO: Updates for the price


class CategoryList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


def home(request):
    context = {}
    return render(request, 'ecomm/home.html', context)
