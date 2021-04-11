from datetime import datetime
import os

from dialogic import SOURCES
from dialogic.interfaces.vk import VKMessage

from core.dm import csc, Pr, PTurn


@csc.add_handler(priority=Pr.CRITICAL)
def log_polylog(turn: PTurn):
    if turn.ctx.source != SOURCES.VK:
        return
    m: VKMessage = turn.ctx.raw_message
    if not isinstance(m, VKMessage):
        return
    # we are interested only in group chats
    if m.peer_id == m.user_id or not m.peer_id:
        return

    bot_id = os.environ.get('VK_GROUP_ID', '203824813')

    need_to_respond = False
    # if m.action and m.action.get('type') == 'chat_invite_user':
    #    need_to_respond = True
    if f'[club{bot_id}|' in m.text:
        # send the message if the bot was explicitly tagged
        need_to_respond = True
    elif turn.polylogs_collection:
        # send the message if the chat is unfamiliar to the bot
        one = turn.polylogs_collection.find_one({'peer_id': m.peer_id})
        if one is None:
            need_to_respond = True

    if need_to_respond:
        turn.response_text = 'Привет! Я бот Плеяд. ' \
                             'Я отслеживаю активность в беседе, но по-хорошем отвечаю только в личке. ' \
                             'Чтобы заполнить анкеты, напишите мне в личку. ' \
                             'Чтобы я мог учитывать статистику сообщений в беседе, ' \
                             'выберите меня в списке участников беседы, нажмите на галочку, ' \
                             'и выберите "Дать доступ ко всей переписке".'
    else:
        turn.response_text = 'Это сообщение вы не должны были увидеть. Если оно пришло, Давид посадил багу.'
        turn.no_response = True

    if turn.polylogs_collection:
        mdata = m.data or {}
        turn.polylogs_collection.insert_one({
            'peer_id': m.peer_id,
            'user_id': m.user_id,
            'time': datetime.now(),
            'text': m.text,
            'reply_id': (mdata.get('reply_message') or {}).get('id'),
            'id': mdata.get('id'),
        })
