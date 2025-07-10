from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_style = State()
    processing = State()
    payment = State()