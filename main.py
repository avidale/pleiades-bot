import os
import logging

import sentry_sdk
import dialogic


from core.dm import make_dm
from core.reminder import REMINDER
from misc.vk import VA
from scenarios import *


if os.getenv('SENTRY_DSN', None) is not None:
    sentry_sdk.init(os.environ['SENTRY_DSN'])


logging.basicConfig(level=logging.DEBUG)


if os.environ.get('MONGODB_URI'):
    db = dialogic.storage.database_utils.get_mongo_or_mock()
    forms_collection = db.get_collection('forms')
    polylogs_collection = db.get_collection('polylogs')
    users_collection = db.get_collection('sessions')
    storage = dialogic.session_storage.MongoBasedStorage(database=db)
    log_storage = dialogic.storage.message_logging.MongoMessageLogger(database=db, detect_pings=True)
else:
    storage = dialogic.storage.session_storage.FileBasedStorage(path='_tmp/sessions')
    log_storage = None
    forms_collection = None
    polylogs_collection = None
    users_collection = None


manager = make_dm(
    forms_collection=forms_collection,
    polylogs_collection=polylogs_collection,
)


connector = dialogic.dialog_connector.DialogConnector(
    dialog_manager=manager,
    storage=storage,
    log_storage=log_storage,
    alice_native_state=False,
)
connector.adapters[dialogic.SOURCES.VK] = VA(
    suggest_cols='auto',
    suggest_margin=2,
)


handler = connector.serverless_alice_handler
server = dialogic.server.flask_server.FlaskServer(connector=connector)
app = server.app

REMINDER.bot = server.vk_bot
REMINDER.users_collection = users_collection


if __name__ == '__main__':
    server.parse_args_and_run()
