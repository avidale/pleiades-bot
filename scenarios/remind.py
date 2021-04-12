import os
import random

from core.dm import csc, Pr, PTurn
from core.reminder import REMINDER


CODEWORD = os.environ.get('CODEWORD') or str(random.random())


@csc.add_handler(priority=Pr.STRONG_INTENT, regexp='.*выслать напоминание.*')
def ask_for_reminders(turn: PTurn):
    turn.response_text = 'Чтобы разослать напоминания, пожалуйста, назовите кодовое слово.'
    turn.next_stage = 'send_reminders'


@csc.add_handler(priority=Pr.STAGE, regexp=CODEWORD, stages=['send_reminders'])
def send_reminders(turn: PTurn):
    if not REMINDER.bot:
        turn.response_text = 'У ремайндера не настроен бот, к сожалению.'
        return
    if not REMINDER.users_collection:
        turn.response_text = 'У ремайндера не настроена база данных, к сожалению.'
        return
    result = REMINDER.iterate_users()
    turn.response_text = f'Разослал уведомления! ' \
                         f'{result["half_forms"]} - о незавершенных анкетах, {result["new_forms"]} - о новых.'


@csc.add_handler(priority=Pr.STRONG_INTENT, regexp='.*массов.. рассылк.*')
def ask_for_sendout(turn: PTurn):
    turn.response_text = 'Чтобы сделать массовую рассылку, пожалуйста, назовите кодовое слово.'
    turn.next_stage = 'ask_sendout_codeword'


@csc.add_handler(priority=Pr.STAGE, regexp=CODEWORD, stages=['ask_sendout_codeword'])
def ask_sendout_codeword(turn: PTurn):
    turn.response_text = 'Кодовое слово принято! Теперь отправьте мне сообщение, которое вы хотите разослать ' \
                         'ВСЕМ ПОДПИСЧИКАМ БОТА. Если вы передумали, скажите "нет".'
    turn.suggests.append('нет')
    turn.next_stage = 'sendout'


@csc.add_handler(priority=Pr.STRONG_INTENT, stages=['sendout'], regexp='нет')
def sendout_cancel(turn: PTurn):
    turn.next_stage = None
    turn.response_text = 'Окей, я не буду делать рассылку.'


@csc.add_handler(priority=Pr.WEAK_STAGE, stages=['sendout'])
def sendout(turn: PTurn):
    turn.next_stage = None
    if not REMINDER.bot:
        turn.response_text = 'У ремайндера не настроен бот, к сожалению.'
        return
    if not REMINDER.users_collection:
        turn.response_text = 'У ремайндера не настроена база данных, к сожалению.'
        return
    result = REMINDER.send_to_everyone(text=turn.text)
    turn.response_text = f'Разослал ваше сообщение! ' \
                         f'Оно было отправлено всем {result} пользователям (кроме тех, которые заблокировали бота). '
