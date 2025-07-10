import os
import requests
from aiogram import types
from tonconnect import TonConnect

class PaymentService:
    def __init__(self):
        self.ton_connect = TonConnect(
            manifest_url=os.getenv('TON_CONNECT_MANIFEST_URL'),
            secret=os.getenv('TON_CONNECT_SECRET')
        )
    
    async def create_ton_payment_link(self, user_id: int, amount: float) -> str:
        payment_data = {
            "user_id": user_id,
            "amount": amount,
            "currency": "TON",
            "description": "Платеж за генерации косплея"
        }
        return self.ton_connect.generate_link(payment_data)
    
    async def verify_ton_payment(self, payment_id: str) -> bool:
        return self.ton_connect.verify_payment(payment_id)

# Альтернативная реализация для Stripe
import stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')

class StripePayment:
    @staticmethod
    async def create_checkout_session(user_id: int) -> str:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': '10 AI Cosplay Generations',
                    },
                    'unit_amount': 500,  # $5.00
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={'user_id': user_id},
            success_url=f'https://{os.getenv("DOMAIN")}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{os.getenv("DOMAIN")}/payment/cancel',
        )
        return session.url

    @staticmethod
    async def verify_webhook(payload, sig_header):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
            )
            return event
        except ValueError as e:
            raise e
        except stripe.error.SignatureVerificationError as e:
            raise e