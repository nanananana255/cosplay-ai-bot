from aiogram import Dispatcher

def register_all_handlers(dp: Dispatcher):
    from .start import register_start_handlers
    from .image_processing import register_image_handlers
    from .payment import register_payment_handlers
    from .admin import register_admin_handlers
    from .sharing import register_sharing_handlers
    
    register_start_handlers(dp)
    register_image_handlers(dp)
    register_payment_handlers(dp)
    register_admin_handlers(dp)
    register_sharing_handlers(dp)