from atexit import register
from django.urls import path
from .import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('', views.user_dashboard, name='user_dashboard'),
    
    # user dashboard
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    # admin dashboard
    path('product_management/', views.product_management, name='product_management'),
    path('add_product/', views.add_product, name='add_product'),
    path('user_management', views.user_management, name='user_management'),
    path('user_ban/<int:user_id>/',views.user_ban,name='user_ban'),
    path('user_unban/<int:user_id>/',views.user_unban,name='user_unban'),
    path('delete_product/<int:product_id>/',views.delete_product,name='delete_product'),
    path('edit_product/<int:product_id>/',views.edit_product,name='edit_product'),
    path('admin_change_password/', views.admin_change_password, name='admin_change_password'),
    path('order_management/',views.order_management,name='order_management'),
    path('accept_order/<int:order_number>/', views.accept_order, name='accept_order'),
    path('complete_order/<int:order_number>/', views.complete_order, name='complete_order'),
    path('admin_cancel_order/<int:order_number>/', views.admin_cancel_order, name='admin_cancel_order'),
    path('category_management/',views.category_management,name='category_management'),
    path('add_category',views.add_category,name='add_category'),
    path('delete_category/<int:category_id>/',views.delete_category,name='delete_category'),
    path('update_category/<int:category_id>/', views.update_category, name='update_category'),
    path('admin_orders/', views.admin_order, name='admin_orders'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]