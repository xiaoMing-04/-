from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse, reverse_lazy
import stripe
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from games.models import Game
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def get_cart_game_ids(request):
    if request.user.is_authenticated:
        game_ids = list(
            Order.objects.filter(user=request.user).values_list('game_id', flat=True)
        )
        return JsonResponse({'game_ids': game_ids})
    
    return JsonResponse({'game_ids': []})


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        game_id = request.POST.get('game_id')

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Game not found.'})

        # Check if already in cart
        if Order.objects.filter(user=user, game=game).exists():
            return JsonResponse({
                'success': False,
                'already_in_cart': True,
                'message': 'Already in cart.'
            })

        # Add to cart
        Order.objects.create(user=user, game=game)
        return JsonResponse({'success': True, 'message': 'Game added to cart!'})

    return JsonResponse({'success': False, 'message': 'Invalid request or not authenticated.'})


def get_cart_count(request):
    user = request.user
    if user.is_authenticated:
        order_count = user.orders.count()  # Correct way to access related orders
    else:
        order_count = 0  # If not authenticated, set count to 0
    return JsonResponse({'order_count': order_count})


class CartView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'cart/cart.html'
    context_object_name = 'orders'
    login_url = '/login/'

    def get_queryset(self):
        # Return only the orders of the logged-in user
        return self.request.user.orders.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = context['orders']

        total_price = sum(order.game.price for order in orders)
        total_discounted_price = sum(order.game.discounted_price for order in orders)
        
        context['total_price'] = total_price
        context['total_discounted_price'] = total_discounted_price
        context['discount'] = total_price - total_discounted_price
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        return context
    

class CartDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        order.delete()
        return redirect('cart')
    

class CreateCheckoutSessionView(LoginRequiredMixin, View):
    login_url = '/login/'  # Redirect here if user is not logged in
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        orders = user.orders.all()
        
        line_items = []
        
        for order in orders:
            line_items.append({
                'price': order.game.stripe_price_id,
                'quantity': 1
            })
            
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                metadata = {
                    "user_id": str(request.user.id),
                    "order_ids": ",".join(str(order.id) for order in orders)
                },
                mode="payment",
                success_url=request.build_absolute_uri(reverse("success")),
                cancel_url=request.build_absolute_uri(reverse("cancel")),
            )
            return JsonResponse({'id': checkout_session.id})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
    

@login_required
def success(request):
    return render(request, "cart/success.html")


@login_required
def cancel(request):
    return render(request, "cart/cancel.html")


# @csrf_exempt
# def webhook_view(request):
#     payload = request.body
    
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None
    
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)
    
#     if event['type'] == 'checkout.session.completed' or event['type'] == 'checkout.session.async_payment_succeeded':
#         session = event['data']['object']
        
#         customer_email = session['customer_details']['email']
#         product_id = session['metadata']['product_id']
        
#         # mailjet.send_mailjet_email_purchase_success(customer_email, product_id, 'Outlast2')
    
#     return HttpResponse(status=200)