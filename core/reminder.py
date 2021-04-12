import time
from datetime import datetime, timedelta
from typing import Optional, Dict

from dialogic.interfaces.vk import VKBot


class Reminder:
    def __init__(self, users_collection=None, bot=None):
        self.users_collection = users_collection
        self.bot: Optional[VKBot] = bot

    def iterate_users(self) -> Dict:
        users = list(self.users_collection.find({}))
        now = datetime.now()
        half_forms = 0
        new_forms = 0
        for u in users:
            dt = u.get('last_time')
            if dt is not None and dt > str(now - timedelta(hours=12)):
                continue

            uid = u['key'].lstrip('vk__')
            if not uid.isdigit():
                continue
            uid = int(uid)
            forms = u['value'].get('forms') or {}
            has_active_forms = sum(1 for f in forms.values() if f.get('is_active')) > 0

            if has_active_forms:
                self.remind(
                    user_id=uid,
                    text='Привет! У вас есть недозаполненная анкета. Вы готовы завершить её?',
                    suggests=['окей', 'ладно'],
                )
                half_forms += 1
            elif len(forms) < 2:
                self.remind(
                    user_id=uid,
                    text='Привет! У меня есть анкета для вас. Вы готовы заняться ею?',
                    suggests=['хорошо', 'давайте'],
                )
                new_forms += 1
            else:
                continue

        return {'half_forms': half_forms, 'new_forms': new_forms}

    def remind(self, user_id, text, suggests=None):
        if suggests:
            keyboard = {
                'one_time': True,
                'buttons': [[{'action': {'type': 'text', 'label': s}} for s in suggests]],
            }
        else:
            keyboard = None
        self.bot.send_message(
            peer_id=user_id,
            text=text,
            keyboard=keyboard,
        )
        time.sleep(0.1)

    def send_to_everyone(self, text):
        users = list(self.users_collection.find({}))
        for u in users:
            uid = u['key'].lstrip('vk__')
            if not uid.isdigit():
                continue
            self.remind(user_id=uid, text=text)
        return len(users)


REMINDER = Reminder()
