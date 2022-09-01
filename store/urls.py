from re import search
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:category_slug>/', views.home, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('view_product/', views.view_product, name='view_product'),
    path('add_product/', views.add_product, name='add_product'),
    path('search/',views.search, name='search'),
]