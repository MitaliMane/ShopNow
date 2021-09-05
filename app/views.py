from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q



class ProductView(View):
     def get(self, request):
          topwears = Product.objects.filter(category='TW')
          bottomwears = Product.objects.filter(category='BW')
          mobiles = Product.objects.filter(category='M')
          laptops = Product.objects.filter(category='L')
          return render(request, 'app/home.html', {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles, 'laptops': laptops})

class ProductDetailView(View):
     def get(self, request, pk):
          product = Product.objects.get(pk=pk)
          return render(request, 'app/productdetail.html', {'product':product})

def add_to_cart(request):
     user = request.user
     item_already_in_cart1 = False
     product = request.GET.get('prod_id')
     item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
     if item_already_in_cart1 == False:
          product_title = Product.objects.get(id=product)
          Cart(user=user, product=product_title).save()
          messages.success(request, 'Product Added to Cart Successfully !!' )
          return redirect('/cart')
     else:
          return redirect('/cart')



def show_cart(request):
     if request.user.is_authenticated:
          user = request.user
          cart = Cart.objects.filter(user=user)
          amount = 0.0
          shipping_amount = 70.0
          amount = 0.0
          cart_product = [p for p in Cart.objects.all() if p.user == user]
          if cart_product:
               for p in cart_product:
                    tempamount = (p.quantity * p.product.discounted_price)
                    amount += tempamount
                    totalamount = amount + shipping_amount
                    return render(request, 'app/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount})
          else:
               return render(request, 'app/emptycart.html')
     else:
          return render(request, 'app/emptycart.html', {'totalitem':totalitem})


def plus_cart(request):
     if request.method == 'GET':
          prod_id = request.GET['prod_id']
          c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
          c.quantity+=1
          c.save()
          amount = 0.0
          shipping_amount= 70.0
          cart_product = [p for p in Cart.objects.all() if p.user == request.user]
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               data = {
                    'quantity':c.quantity,
                    'amount':amount,
                    'totalamount':amount+shipping_amount
                    }
               return JsonResponse(data)
     else:
               return HttpResponse("")

def minus_cart(request):
     if request.method == 'GET':
          prod_id = request.GET['prod_id']
          c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
          c.quantity-=1
          c.save()
          amount = 0.0
          shipping_amount= 70.0
          cart_product = [p for p in Cart.objects.all() if p.user == request.user]
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               data = {
                    'quantity':c.quantity,
                    'amount':amount,
                    'totalamount':amount+shipping_amount
                    }
               return JsonResponse(data)
     else:
               return HttpResponse("")



def remove_cart(request):
     if request.method == 'GET':
          prod_id = request.GET['prod_id']
          c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
          c.delete()
          amount = 0.0
          shipping_amount= 70.0
          cart_product = [p for p in Cart.objects.all() if p.user == request.user]
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               data = {
                    'amount':amount,
                    'totalamount':amount+shipping_amount
                    }
               return JsonResponse(data)
     else:
               return HttpResponse("")


def checkout(request):
     user = request.user
     add = Customer.objects.filter(user=user)
     cart_items = Cart.objects.filter(user=request.user)
     amount = 0.0
     shipping_amount = 70.0
     
     cart_product = [p for p in Cart.objects.all() if p.user == request.user]
     if cart_product:
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               
     return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items})


def payment_done(request):
     custid = request.GET.get('custid')
     print("Customer ID", custid)
     user = request.user
     cartid = Cart.objects.filter(user = user)
     customer = Customer.objects.get(id=custid)
     print(customer)
     for cid in cartid:
          OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
          print("Order Saved")
          cid.delete()
          print("Cart Item Deleted")
          return redirect("orders")


def address(request):
     totalitem = 0
     if request.user.is_authenticated:
          totalitem = len(Cart.objects.filter(user=request.user))
          add = Customer.objects.filter(user=request.user)
          return render(request, 'app/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})

def orders(request):
     op = OrderPlaced.objects.filter(user=request.user)
     return render(request, 'app/orders.html', {'order_placed':op})

def password_change(request):
     return render(request, 'app/passwordchange.html')

def mobile(request, data=None):
     if data == None:
          mobiles = Product.objects.filter(category='M')
     elif data =='Redmi' or data == 'SamSung' or data =='OnePlus':
          mobiles = Product.objects.filter(category='M').filter(brand=data)
     elif data =='below':
          mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=25000)
     elif data =='above':
          mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=25000)
     return render(request, 'app/mobile.html', {'mobiles':mobiles})

def laptop(request, data=None):
     if data == None:
          laptops = Product.objects.filter(category='L')
     elif data =='Asus' or data == 'Acer' or data =='Legion':
          laptops = Product.objects.filter(category='L').filter(brand=data)
     elif data =='below':
          laptops = Product.objects.filter(category='L').filter(discounted_price__lt=40000)
     elif data =='above':
          laptops = Product.objects.filter(category='L').filter(discounted_price__gt=40000)
     return render(request, 'app/laptop.html', {'laptops':laptops})

def top_wear(request, data=None):
     if data == None:
          top_wears = Product.objects.filter(category='TW')
     elif data =='Polo' or data == 'Calvin' or data =='Park':
          top_wears = Product.objects.filter(category='TW').filter(brand=data)
     elif data =='below':
          top_wears = Product.objects.filter(category='TW').filter(discounted_price__lt=500)
     elif data =='above':
          top_wears = Product.objects.filter(category='TW').filter(discounted_price__gt=500)
     return render(request, 'app/top wear.html', {'top wears':top_wears})

def bottom_wear(request, data=None):
     if data == None:
          bottom_wears = Product.objects.filter(category='BW')
     elif data =='Levis' or data == 'Lee' or data =='Roadster':
          bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
     elif data =='below':
          bottom_wears = Product.objects.filter(category='BW').filter(discounted_price__lt=1000)
     elif data =='above':
          bottom_wears = Product.objects.filter(category='BW').filter(discounted_price__gt=1000)
     return render(request, 'app/bottom wear.html', {'bottom wear':bottom_wears})
      

class CustomerRegistrationView(View):
     def get(self, request):
          form = CustomerRegistrationForm()
          return render(request, 'app/customerregistration.html', {'form':form})
     def post(self, request):
          form = CustomerRegistrationForm(request.POST)
          if form.is_valid():
               messages.success(request,'Registered Successfully')
               form.save()
          return render(request, 'app/customerregistration.html', {'form':form})
     


class ProfileView(View):
     def get(self, request):
          totalitem = 0
          if request.user.is_authenticated:
               totalitem = len(Cart.objects.filter(user=request.user))
               form = CustomerProfileForm()
               return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
               
     def post(self, request):
          totalitem = 0
          if request.user.is_authenticated:
               totalitem = len(Cart.objects.filter(user=request.user))
               form = CustomerProfileForm(request.POST)
               if form.is_valid():
                    usr = request.user
                    name  = form.cleaned_data['name']
                    locality = form.cleaned_data['locality']
                    city = form.cleaned_data['city']
                    state = form.cleaned_data['state']
                    zipcode = form.cleaned_data['zipcode']
                    reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
                    reg.save()
                    messages.success(request, 'Congratulations!! Profile Updated Successfully.')
                    return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
