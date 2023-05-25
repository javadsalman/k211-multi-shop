from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm, RegisterForm, PasswordResetForm
from shop.models import Product
from .models import WishtItem, BasketItem, ResetPassword
from payment.models import Coupon
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F
from django.core.mail import send_mail
from django.conf import settings
from os import getenv
import requests
# Create your views here.

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        recaptcha_response = request.POST.get('g-recaptcha-response')
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': getenv('RECAPTCHA_SECRET_KEY'),
            'response': recaptcha_response,
        })
        response_data = response.json()
        if form.is_valid() and response_data['success'] and response_data['score'] > 0.7:
            form.save()
            return render(request, 'contact.html', {'form': form, 'result': 'success'})
        return render(request, 'contact.html', {'form': form, 'result': 'fail'})
    return render(request, 'contact.html', {'form': form})

@login_required
def wishlist_view(request):
    wishlist = request.user.customer.wishlist.all()
    total_price = wishlist.aggregate(total_price = Sum('product__price'))['total_price']
    # Author.objects.annotate(total_pages=Sum("book__pages"))
    return render(request, 'wishlist.html', {'wishlist': wishlist, 'total_price': total_price})

@login_required
def wish_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    customer = request.user.customer
    WishtItem.objects.create(product=product, customer=customer)
    return redirect(request.META.get('HTTP_REFERER'))
    
@login_required
def unwish_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    customer = request.user.customer
    WishtItem.objects.filter(product=product, customer=customer).delete()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def basket(request):
    basketlist = request.user.customer.basketlist.all().annotate(total_price=F('count') * F('product__price'))
    all_price = basketlist.aggregate(all_price=Sum('total_price'))['all_price'] or 0
    shipping_price = all_price * 0.07
    final_price = all_price + shipping_price
    
    coupon_code = request.GET.get('coupon', '')
    coupon_message = None
    coupon_status = None
    coupon_discount = 0
    coupon_discount_amount = 0
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code).first()
        if coupon:
            is_valid, message = coupon.is_valid(request.user.customer)
            if is_valid:
                coupon_status = 'valid'
                coupon_message = message
                coupon_discount = coupon.discount
                coupon_discount_amount = final_price * coupon_discount / 100
                final_price -= coupon_discount_amount
            else:
                coupon_status = 'invalid'
                coupon_message = message
        else:
            coupon_status = 'invalid'
            coupon_message = 'Bele bir kupon yoxdur'
        
        
        
    return render(request, 'basket.html', {
        'basketlist': basketlist,
        'all_price': round(all_price, 2),
        'shipping_price': round(shipping_price, 2),
        'final_price': round(final_price, 2),
        'coupon_code': coupon_code,
        'coupon_message': coupon_message,
        'coupon_status': coupon_status,
        'coupon_discount': coupon_discount,
        'coupon_discount_amount': round(coupon_discount_amount, 2),
    })

@login_required
def add_basket(request, product_pk):
    if request.method == 'POST':
        size_pk = request.POST.get('size')
        color_pk = request.POST.get('color')
        count = request.POST.get('count')
        customer = request.user.customer
        basket = BasketItem.objects.create(product_id=product_pk, size_id=size_pk, color_id=color_pk, count=count, customer=customer)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('shop:home')
    
    
def increase_basket_item(request, basket_pk):
    basket = get_object_or_404(BasketItem, pk=basket_pk)
    basket.count = F('count') + 1
    basket.save()
    return redirect('customer:basket')

def decrease_basket_item(request, basket_pk):
    basket = get_object_or_404(BasketItem, pk=basket_pk)
    if basket.count == 1:
        basket.delete()
    else:
        basket.count = F('count') - 1
        basket.save()
    return redirect('customer:basket')

@login_required
def remove_basket(request, basket_pk):
    basket = get_object_or_404(BasketItem, pk=basket_pk)
    basket.delete()
    return redirect('customer:basket')

def login_view(request):
    if request.method == 'POST':
        print('SHOW', request.POST)
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember', False)
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            return redirect('shop:home')
        return render(request, 'login.html', {'fail': True})
        
    return render(request, 'login.html', {})

def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect('customer:login')
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('customer:login')

usd_eq = {'AZN': 1.7, 'TRY': 19.56, 'EUR': 0.91, 'USD': 1}
def change_currency(request):
    currency = request.GET.get('currency')
    currency_ratio = usd_eq[currency]
    request.session['currency'] = currency
    request.session['currency_ratio'] = currency_ratio
    return redirect(request.META.get('HTTP_REFERER'))


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            ResetPassword.objects.filter(user=user).update(used=True)
            rp = ResetPassword.objects.create(user=user)
            url = request.build_absolute_uri(rp.get_absolute_url())
            message = f'Please renew your password from this link: {url}'
            subject = 'Renew Password'
            sender = settings.EMAIL_HOST_USER
            send_mail(subject, message, sender, [email])
            return redirect('customer:reset-password-result', color='success', message='Mail sent successfuly')
        else:
            return render(request, 'forgot_password.html', {'status': 'invalid_user'})
    return render(request, 'forgot_password.html')

def reset_password_view(request, token):
    rp = ResetPassword.objects.filter(token=token).first()
    if rp and rp.is_valid():
        if request.method == 'GET':
            form = PasswordResetForm(initial={'token': token})
            return render(request, 'reset-password.html', {'form': form})
        else:
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('customer:reset-password-result', color='success', message='Password reset successfuly!')
            return render(request, 'reset-password.html', {'form': form}) 
    else:
        return redirect('customer:reset-password-result', color='danger', message='The reset password reference you entered is invalid')

def reset_password_result_view(request, color, message):
    return render(request, 'reset-password-result.html', {'color': color, 'message': message})