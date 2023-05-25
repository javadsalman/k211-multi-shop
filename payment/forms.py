from django import forms
from .models import Order, OrderedProduct


class OrderForm(forms.ModelForm):
    
    class Meta:
        exclude = ['customer', 'coupon_code', 'coupon_discount', 'accepted', 'delivered', 'created']
        model = Order
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+994123456789'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Baku'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filankes Filankesov 15 17'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AZ1234'}),
            'country': forms.Select(attrs={'class': 'custom-select'})
        }
        
    def save(self, customer, basketlist, coupon):
        data = self.cleaned_data.copy()
        data['customer'] = customer
        if coupon and coupon.is_valid(customer)[0]:
            data['coupon_code'] = coupon.code
            data['coupon_discount'] = coupon.discount
        
        order = Order.objects.create(**data)
        
        ordered_products = []
        for basketitem in basketlist:
            op = OrderedProduct(
                order=order,
                title=basketitem.product.title,
                count=basketitem.count,
                price=basketitem.product.price,
                size=basketitem.size.title,
                color=basketitem.color.title,
            )
            ordered_products.append(op)
        OrderedProduct.objects.bulk_create(ordered_products)
        basketlist.delete()
        return order

        