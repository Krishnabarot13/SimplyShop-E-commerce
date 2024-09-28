from django.urls import path
from . import views

urlpatterns=[
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('update_item/',views.updateItem,name="update_item"),
    path("process_order/",views.processOrder,name="process_order"),

    
     path('signupaccount/', views.signupaccount, name='signupaccount'),
    path('logout/', views.logoutaccount,name='logoutaccount'),
    path('login/', views.loginaccount, name='loginaccount'),

    path('<int:product_id>',views.detail,name='detail'),
    path('women/',views.women,name='women'),
    path('men/',views.men,name='men'),
    path('women/<str:sub>',views.women,name='wfilter'),
    path('men/<str:sub>',views.men,name='mfilter'),
    path('shoes/',views.shoes,name='shoes'),
    path('shoes/<str:gender>',views.shoes,name='sfilter'),

    path('UserProfile/',views.user_profile_view,name='userProfile'),
    path('all/',views.all,name='all')
]