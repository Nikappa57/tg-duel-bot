from Bot.database.models import Users
from Bot.database import db

from Bot import errors


def check(adminrequired=False):
    def fuction(fun):
        """
        Check if the user is new, if he is banned, if he has changed his name and username, if you update them in the database
        IMPORTANT TO PLACE IT ON ALL CONTROLS AS FIRST DECORATOR
        
        adminrequired=True 

        Check if the user is admin, 
        if not send an error message in chat 
        (Bot.errors.admin_required_error)
        """
        def wrapper(update, context, *args):
            data = update.message if update.message else update.callback_query \
                if update.callback_query else update.edited_message if update.edited_message \
                    else update.inline_query
            username = data.from_user.username
            name = data.from_user.name
            chat_id = data.from_user.id

            user = db.session.query(Users).filter_by(chat_id=chat_id).first()

            if not user:
                user = Users(chat_id=chat_id, username=username, name=name)
                db.session.add(user)
                db.session.commit()

            elif user.ban:
                errors.ban_error(update, context)

            elif user.username != username and user.username:
                user.username = username
            
            elif user.name != name:
                user.name = name

            db.session.commit()

            if not user.ban or not user:
                if not adminrequired:
                    fun(update, context, user, *args)
                elif db.session.query(Users).filter_by(chat_id=chat_id).first().admin:
                    fun(update, context, user, *args)
                else:
                    errors.admin_required_error(update, context)
        return wrapper
    return fuction

def user_arg(fun):
    """
    Serves in all commands where you need to edit/recall another user
    Supports the syntax "/<command> chat_id" and "/<command> @username"
    Also supports reply_to_message
    
    If syntax is wrong by a chat error (Bot.errors.syntax_error)
    If the user is not present in the database by a chat error (Bot.errors.user_dont_exist)
    If you try to recall/edit yourself from a chat error (Bot.errors.yourself_error)

    When you put as a decorator it is IMPORTANT to add the user argument to the function
    where the object of the User class referred to the called user will be passed by user_arg itself
    """
    def wrapper(update, context, currentuser, *args):
        data = update.message if update.message else update.edited_message
        message = data.text
        chat_id = data.from_user.id
        reply_message = data.reply_to_message
        user = message.split(" ")

        if (len(user) == 1 or (not user[-1].isdecimal() and "@" not in message)) and not reply_message:
            errors.syntax_error(update, context, *args)
            return

        user = user[-1] if not reply_message else str(reply_message.from_user.id)

        check = db.session.query(Users).filter_by(chat_id=int(user)).first() if user.isdecimal() or reply_message \
            else db.session.query(Users).filter_by(username=user.replace("@", "")).first()

        if reply_message and reply_message.from_user.is_bot:
            errors.mod_bot_error(update, context, *args)
            return

        if not check:
            errors.user_dont_exist(update, context, *args)
            return

        if check.chat_id == chat_id:
            errors.yourself_error(update, context, *args)
            return

        fun(update, context, currentuser, check, *args)

    return wrapper