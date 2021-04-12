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
