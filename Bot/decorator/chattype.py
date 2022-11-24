from Bot import errors

from Bot.database.models import db
from Bot.database.models import Groups, Stats


def group(fun):
    def wrapper(update, *args):
        data = update.message if update.message else update.edited_message

        if data.chat.type in ['group', 'supergroup']:
            group = db.session.query(Groups).filter_by(
                chat_id=data.chat.id).first()
            if not group:
                group = Groups(chat_id=data.chat.id)
                db.session.add(group)
                db.session.commit()
            
            fun(update, *args, group)
        else:
            errors.chat_groups(update, *args)
    return wrapper

def private(fun):
    def wrapper(update, *args):
        data = update.message if update.message else update.callback_query \
                if update.callback_query else update.edited_message
        if data:
            if not update.callback_query:
                if data.chat.type == 'private':
                    fun(update, *args)
            else:
                fun(update, *args)
    return wrapper