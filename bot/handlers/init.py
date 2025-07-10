from .user import register_user_handlers
from .admin import register_admin_handlers
from .generation import register_generation_handlers
from .payment import register_payment_handlers

def register_all_handlers(dp):
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_generation_handlers(dp)
    register_payment_handlers(dp)