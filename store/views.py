from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        try:
             cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}
        print("Cart: ",cart)
        items=[]
        order={"get_cart_total":0,'get_cart_items':0}
        cartItems=order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']

            product=Product.objects.get(id=i)
            total=(product.price * cart[i]['quantity'])

            order['get_cart_total'] +=total
            order['get_cart_items'] +=cart[i]['quantity']
            print('cartitems: ',cartItems)
            print(order['get_cart_items'])
        

            item={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageUrl
                },
                'quantity': cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)
    popular=Product.objects.filter(top_product=True).order_by('price')
    search=request.GET.get('search')
    if search:
        products=Product.objects.filter(category=search)
    else:
        products=Product.objects.all()
    context={'items':items,'order':order,'products':products,'cartItems':cartItems,'shipping':False,'popular':popular}
    return render(request,'store/store.html',context)
def cart(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
        
    else:
        try:
             cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}
        print("Cart: ",cart)
        items=[]
        order={"get_cart_total":0,'get_cart_items':0}
        cartItems=order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']

            product=Product.objects.get(id=i)
            total=(product.price * cart[i]['quantity'])

            order['get_cart_total'] +=total
            order['get_cart_items'] +=cart[i]['quantity']

            item={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageUrl
                },
                'quantity': cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)

    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/cart.html',context)
def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={"get_cart_total":0,'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    # print(request.body)
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']
    print(action)
    print(productId)

    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order,created=Order.objects.get_or_create(customer=customer,complete=False)
    orderItem,created=OrderItem.objects.get_or_create(order=order,product=product)

    if action=='add':
        orderItem.quantity=(orderItem.quantity+1)
    elif action=='remove':
        orderItem.quantity=(orderItem.quantity-1)
    orderItem.save()
    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse("Item was added",safe=False)

def processOrder(request):
    print("data: ",request.body)
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        total=float(data['form']['total'])
        order.transaction_id=transaction_id
        if total==float(order.get_cart_total):
            order.complete=True
        order.save()

        if order.shipping==True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode']

            )
        
    else:
        print("user is not logged in")
    return JsonResponse("payment successful",safe=False)

def signupaccount(request):
    if request.method == 'GET':
        return render(request, 'store/signupaccount.html', {'form':UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password= request.POST['password1']) 
                user.save()
                customer = Customer.objects.create(user=user)
                # Add additional customer information if needed
                customer.name = request.POST['username']  # Replace with actual name
                customer.email = 'johndoe@example.com'  # Replace with actual email
                customer.save()
                login(request, user)
                return redirect('store')
            except IntegrityError:
                return render(request,'store/signupaccount.html', {'form':UserCreationForm,'error':'Username already taken. Choose new username.'})
        else:
            return render(request, 'store/signupaccount.html', {'form':UserCreationForm, 'error':'Passwords do not match'})
        

def logoutaccount(request):
    logout(request)
    return redirect('store')

def loginaccount(request): 
    if request.method == 'GET':
        return render(request, 'store/loginaccount.html', {'form':AuthenticationForm})
    else:
        user = authenticate(request,
        username=request.POST['username'], password=request.POST['password']) 
        if user is None:
            return render(request,'store/loginaccount.html', {'form': AuthenticationForm(), 'error': 'username and password donot match'})
        else: 
            login(request,user)
            return redirect('store')
        
def detail(request,product_id):
    product=get_object_or_404(Product,pk=product_id)
    recomend=Product.objects.filter(subcategory=product.subcategory)
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={"get_cart_total":0,'get_cart_items':0}
        cartItems=order['get_cart_items']
    context={'items':items,'order':order,'cartItems':cartItems,'product':product,'Recomend':recomend}
    
    return render(request,'store/detail.html',context)

def women(request,sub=None):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        try:
             cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}
        print("Cart: ",cart)
        items=[]
        order={"get_cart_total":0,'get_cart_items':0}
        cartItems=order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']

            product=Product.objects.get(id=i)
            total=(product.price * cart[i]['quantity'])

            order['get_cart_total'] +=total
            order['get_cart_items'] +=cart[i]['quantity']

            item={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageUrl
                },
                'quantity': cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)
    if sub=='Jeans':
        product=Product.objects.filter(subcategory='Jeans').filter(gender='Female')
    elif sub=='T-shirt':
        product=Product.objects.filter(subcategory='T-shirt').filter(gender='Female')
    elif sub=='Shirt':
        product=Product.objects.filter(subcategory='Shirt').filter(gender='Female')
    else:
        product=Product.objects.filter(gender='Female').filter(category='Clothing')
        print("entered else")
        print(sub)
    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False,'products':product}
    return render(request,'store/Women.html',context)

def men(request,sub=None):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        try:
             cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}
        print("Cart: ",cart)
        items=[]
        order={"get_cart_total":0,'get_cart_items':0}
        cartItems=order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']

            product=Product.objects.get(id=i)
            total=(product.price * cart[i]['quantity'])

            order['get_cart_total'] +=total
            order['get_cart_items'] +=cart[i]['quantity']

            item={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageUrl
                },
                'quantity': cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)
    if sub=='Jeans':
        product=Product.objects.filter(gender='Male').filter(subcategory='Jeans')
    elif sub=='T-shirt':
        product=Product.objects.filter(subcategory='T-shirt').filter(gender='Male')
    elif sub=='Shirt':
        product=Product.objects.filter(subcategory='Shirt').filter(gender='Male')
    else:
        product=Product.objects.filter(gender='Male').filter(category='Clothing')
        print("entered else")
        print(sub)
    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False,'products':product}
    return render(request,'store/Men.html',context)

def shoes(request,gender=None):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        try:
             cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}
        print("Cart: ",cart)
        items=[]
        order={"get_cart_total":0,'get_cart_items':0}
        cartItems=order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']

            product=Product.objects.get(id=i)
            total=(product.price * cart[i]['quantity'])

            order['get_cart_total'] +=total
            order['get_cart_items'] +=cart[i]['quantity']

            item={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageUrl
                },
                'quantity': cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)
    if gender=='Male':
        product=Product.objects.filter(gender='Male').filter(category='Shoes')
    elif gender=='Female':
        product=Product.objects.filter(gender='Female').filter(category='Shoes')
    else:
        product=Product.objects.filter(category='Shoes')
    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False,'products':product}
    return render(request,'store/Shoes.html',context)

@login_required
def user_profile_view(request):
    # try:
    #     profile = request.user.userprofile
    #     customer=request.user.customer
    #     order,created=Order.objects.get_or_create(customer=customer,complete=False)
    #     items=order.orderitem_set.all()
    #     cartItems=order.get_cart_items
    # except UserProfile.DoesNotExist:
    #     profile = UserProfile(user=request.user)
    #     profile.save()

    # if request.method == 'POST':
    #     form = UserProfileForm(request.POST, request.FILES, instance=profile)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('userProfile')
    # else:
    #     form = UserProfileForm(instance=profile)
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        customer='null2'
        items=[]
        order={"get_cart_total":0,'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']
    context={'items':items,'order':order,'cartItems':cartItems,'customer':customer}
    return render(request,'store/userProfile.html',context)
def all(request):
    products=Product.objects.all()
    return render(request,'store/all.html',{'products':products})

