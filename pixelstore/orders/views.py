import datetime
from urllib import request
from django.shortcuts import render,redirect
from carts.models import Cart, CartItem
from store.models import Product
from .forms import OrderForm,PaymentForm
from . models import Order, OrderProduct, Payment
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# Create your views here.

def payments(request, order_numbers):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    #tax = (2 *total)/100

    processing_fee = 2/100 * total
    grand_total = int(total)*100 + int(processing_fee)*100 #+ tax
    sub_total = total

    cart_items = CartItem.objects.filter(user=current_user)
    order = Order.objects.get(user=current_user, is_ordered=True, order_number=order_numbers)

    # move the cart products to the Order Products
    cart_items = CartItem.objects.filter(user=current_user)
    payments = Payment.objects.get(user=current_user, order_id=order_numbers)
    
   

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.product_id = item.product_id
        order_product.user_id = request.user.id
        order_product.payment = payments
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # reduce the quntity of items
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear cart
    CartItem.objects.filter(user=request.user).delete()

def place_order(request,total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('home')

    grand_total = 0 
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        formvalid = form.is_valid()
        print(formvalid, 'formvalid')

        if form.is_valid():
            # store the all billing information inside order table
            data = Order()
            data.user           = current_user
            data.first_name     = form.cleaned_data['first_name']
            data.last_name      = form.cleaned_data['last_name']
            data.phone          = form.cleaned_data['phone']
            data.email          = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country        = form.cleaned_data['country']
            data.state          = form.cleaned_data['state']
            data.city           = form.cleaned_data['city']
            data.order_note     = form.cleaned_data['order_note']
            data.order_total    = grand_total
            data.tax            = tax
            data.ip             = request.META.get('REMOTE_ADDR')
            data.save()
            print(data)

            # genarate order number

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            print(data)
            
            rz_total = int(total) + int(tax)
            rz_total = int(rz_total * 100)

            # print (rz_total,"-----------------------------")
    

            # Create Razorpay client

            client = razorpay.Client(
                auth=('rzp_test_RinWoQfRYdS3Iq', 'RFd2kCbkfgsYY1WIGCPKeIX8')
                
                )

            # create order 

            response_payment = client.order.create(dict(amount=rz_total, currency="INR"))

            order_response_id = response_payment["id"]
            # print (response_payment,"______")
            order_status = response_payment["status"]
            if order_status == "created":
                payment = Payment(
                    user=request.user,
                    amount=rz_total,
                    order_id = order_number,
                    razorpay_payment_id=order_response_id ,
                    paid=True,
                )
                # payment.paid = True
                
                payment.save()
                data.is_ordered=True
                data.payment=payment
                data.save()


                payments(request, order_number)

            order = Order.objects.get(user=current_user, is_ordered=True, order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                'payment':response_payment,
            }
            return render(request, 'orders/payments.html', context)

    else:
        return redirect('checkout')

@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id' : response[ 'razorpay_order_id'],
        'razorpay_payment_id' : response ['razorpay_payment_id'],
        'razorpay_signature' : response ['razorpay_signature']
    }

    # client instance
    client = razorpay.Client(auth=('rzp_test_RinWoQfRYdS3Iq', 'RFd2kCbkfgsYY1WIGCPKeIX8' ))

    try:
        status = client.utility.verify_payment_signature(params_dict)
        products = Payment.objects.get(order_id=response['razorpay_order_id'])
        products.razorpay_payment_id = response ['razorpay_payment_id']
        products.paid = True
        products.save()
        return render(request, 'orders/payment_status.html', {'status' : True})
    except:
        return render(request, 'orders/payment_status.html', {'status': False})


    

    # try:
    #     order = Order.objects.get(order_number=order_number, is_ordered=True)
    #     ordered_products = OrderProduct.objects.filter(order_id=order.id)

    #     context = { 
    #         'order' : order,
    #         'ordered_products' : ordered_products,
    #     }

    #     return render(request, 'orders/payment_status.html',context)
    # except (Payment.DoesNotExist, Order.DoesNotExist):
    #     return redirect('home')