import copy
import os
from datetime import datetime

import dialogic
import attr
from dialogic.cascade import Cascade, Pr, DialogTurn
from dialogic.dialog import Context, Response
from dialogic.dialog_manager import TurnDialogManager


csc = Cascade()


@attr.s
class PTurn(DialogTurn):
    forms_collection = attr.ib(default=None)
    polylogs_collection = attr.ib(default=None)
    no_response: bool = attr.ib(default=False)
    upload_filename: str = attr.ib(default=None)


class PleyadeDM(TurnDialogManager):
    def __init__(self, *args, forms_collection=None, polylogs_collection=None, **kwargs):
        super(PleyadeDM, self).__init__(*args, **kwargs)
        self.polylogs_collection = polylogs_collection
        self.forms_collection = forms_collection

    def preprocess_turn(self, turn: PTurn):
        if not turn.user_object:
            turn.user_object = {}
        # turn.stage = None  # the old stage will be left intact
        turn.polylogs_collection = self.polylogs_collection
        turn.forms_collection = self.forms_collection

    def postprocess_response(self, response: Response, turn: PTurn):
        response.no_response = turn.no_response
        response.updated_user_object['last_time'] = str(datetime.now())
        # todo: add filename to response


class FFDM(dialogic.dialog_manager.FormFillingDialogManager):
    def __init__(self, *args, forms_collection=None, **kwargs):
        super(FFDM, self).__init__(*args, **kwargs)
        self.forms_collection = forms_collection

    def handle_completed_form(self, form, user_object, ctx: Context):
        document = copy.deepcopy(form)
        document['user_id'] = ctx.user_id
        document['timestamp'] = datetime.now()

        if self.forms_collection:
            self.forms_collection.insert_one(document)
        return Response(
            text=self.config.finish_message,
            user_object=user_object,
            suggests=self.config.finish_suggests or [],
        )


forms_root = 'data/forms'

form_dms = [
    FFDM(os.path.join(forms_root, fn))
    for fn in os.listdir(forms_root)
]


@csc.add_handler(priority=Pr.STAGE)
def try_forms(turn: DialogTurn):
    for dm in form_dms:
        form_response = dm.try_to_respond(turn.ctx)
        if form_response:
            turn.response = form_response
            return


def make_dm(forms_collection=None, polylogs_collection=None) -> PleyadeDM:
    dm = PleyadeDM(
        csc,
        turn_cls=PTurn,
        polylogs_collection=polylogs_collection,
        forms_collection=forms_collection,
    )
    for m in form_dms:
        m.forms_collection = forms_collection
    return dm
