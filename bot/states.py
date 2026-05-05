from aiogram.fsm.state import State, StatesGroup

class FeedbackState(StatesGroup):
    waiting_for_message = State()

class ReviewStates(StatesGroup):
    reviewing = State()

class ReportStates(StatesGroup):
    waiting_for_report_text = State()