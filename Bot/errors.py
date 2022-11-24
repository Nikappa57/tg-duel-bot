def chat_groups(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "Use this command in a group."
    )


def unknown(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "Command not found."
    )


def admin_required_error(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "Only admins can access this feature."
    )


def ban_error(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "You were banned from this bot."
    )


def user_dont_exist(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "The user does not exist."
    )


def syntax_error(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "Use this command to reply to a message" + \
            " or use /<command> @Username"
    )


def yourself_error(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "You can’t change yourself."
    )


def mod_bot_error(update, context):
    context.bot.send_message(
        update.effective_chat.id, 
        "You can’t edit a bot."
    )