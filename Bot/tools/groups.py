from Bot.database import db
from Bot.database.models import Groups


def checkgroups(chat_id:int) -> Groups:
    group = db.session.query(Groups).filter_by(
        chat_id=chat_id).first()
    if not group:
        group = Groups(chat_id=chat_id)
        db.session.add(group)
        db.session.commit()

    return group