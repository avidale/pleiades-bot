import os
import random

from core.dm import csc, Pr, PTurn


from hashlib import md5
import pandas as pd
from collections import defaultdict


def do_hash(s, salt=os.environ.get('HASH_SALT') or 'uid_'):
    return md5(f'{salt}_{s}'.encode()).hexdigest()


def forms2excel(forms, filename='forms.xlsx'):
    dd = defaultdict(list)
    for f in forms:
        if not f.get('name'):
            continue
        dd[f['name']].append(
            dict(
                name=f['name'],
                timestamp=f['timestamp'],
                uid_hash=do_hash(f['user_id']),
                **f['fields']
            )
        )

    writer = pd.ExcelWriter(filename)
    for k, v in dd.items():
        pd.DataFrame(v).to_excel(writer, sheet_name=k)
    writer.save()


CODEWORD = os.environ.get('CODEWORD') or str(random.random())


@csc.add_handler(priority=Pr.STRONG_INTENT, regexp='.*результат.*')
def ask_for_results(turn: PTurn):
    turn.response_text = 'Чтобы выгрузить результаты опросов, пожалуйста, назовите кодовое слово.'
    turn.next_stage = 'get_results'


@csc.add_handler(priority=Pr.STAGE, regexp=CODEWORD, stages=['get_results'])
def get_results(turn: PTurn):
    coll = turn.forms_collection
    if not coll:
        turn.response_text = 'Таблица для сбора данных не настроена, простите.'
        return
    forms = list(coll.find({}))
    fn = 'forms.xlsx'
    forms2excel(forms, fn)
    turn.response_text = 'Отправляю вам файл с результатами!'
    turn.upload_filename = fn
