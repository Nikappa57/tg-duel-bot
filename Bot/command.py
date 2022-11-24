from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from Bot.decorator import chattype, checkuser
from Bot.database.models import Reaction, Users
from Bot.database import db
from Bot.tools.groups import checkgroups
from Bot.tools.duel import Duel
from Bot.tools.stats import Stats
from Bot.tools.emoji import EmojiList


# start #
@checkuser.check()
def start(update, context, currentuser):
    data = update.message if update.message else update.edited_message
    
    if data.chat.type in ['group', 'supergroup']:
        group = checkgroups(data.chat.id)

        message = "<b>Hey!</b> 👋Thanks for putting me in this group\n\n" + \
            "<b>Remember to put me as group manager!</b> 🚨\n" + \
            "<i>To know how the bot works click the button below!</i>"

        keyboard = [
            [InlineKeyboardButton('ℹ️ Tutorial ℹ️', 
                url=f't.me/{context.bot.username}?start=tutorial')]
        ]

    else:
        arg = data.text[7:]
        if arg:
            if arg == 'tutorial':
                message = f"<b>Tutorial @{context.bot.username}</b> ℹ️\n\n" + \
                    "<i>Challenge a person by responding to a user’s message with " + \
                        "/duel or use the command /duel to ask everyone who wants to challenge you." + \
                            "\n\nUse /stats to see group statistics.\n" + \
                                "Use /globalstats to see global statistics, or use inlinemode\n" + \
                                    "Use /settings in group to open private settings (admin).</i>\n" + \
                                        "\n\n<b>Remember to put me as group manager</b>"
                
                keyboard = [
                    [InlineKeyboardButton('🔗 GitHub repo 🔗', 
                        url='https://github.com/Nikappa57/tg-duel-bot')]
                ]

            elif arg[:9] == 'settings_':
                group_id, chat_id = list(map(int, arg[9:].split('_')))

                if currentuser.chat_id != chat_id:
                    return update.message.reply_text(
                        'Settings have been opened by another person'
                    )

                message = '<b>Group settings</b>\n\n<i>Choose whether to </i>' + \
                    'disable reactions or duels.'
                
                keyboard = [
                    [
                        InlineKeyboardButton('🤪 Reactions 🤪', callback_data=f'settings-reaction-{group_id}'),
                        InlineKeyboardButton('🏀 Duels 🏀', callback_data=f'settings-duel-{group_id}')
                    ],
                    [
                        InlineKeyboardButton('✖️ Close Settings ✖️', callback_data=f'settings-close')
                    ]
                ]
        
        else:
            message = f"<b>Welcome {currentuser.get_name()}</b> 👋\n\n" + \
                "<i>Add me to your group to make it more active and fun " + \
                    "\n\nUsers can challenge each other, " + \
                        "more will win more will rise in the group and global ranking! 👍</i>"

            keyboard = [
                [InlineKeyboardButton('✅ Add me to your group ✅', 
                    url=f't.me/{context.bot.username}?startgroup=True')],
                [InlineKeyboardButton('🔗 GitHub repo 🔗', 
                        url='https://github.com/Nikappa57/tg-duel-bot')],
                [InlineKeyboardButton('Dice icons created by Freepik - Flaticon', 
                        url='https://www.flaticon.com/free-icons/dice')],
            ]
    update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


# Duel #
@chattype.group
@checkuser.check()
def duel(update, context, currentuser, group):
    if not group.allow_duels:
        return update.message.reply_text(
            '<i>I’m sorry, but the group administrator disabled the duels.</i>')

    data = update.message if update.message else update.edited_message
    
    bot_info = context.bot.get_chat_member(data.chat.id, context.bot.id)

    if bot_info.status not in ['creator', 'administrator']:
        return update.message.reply_text(
            '<i>I’m sorry 😔, but before you can have a duel you must ' + \
                'set me up as group administrator</i>')

    if currentuser.chat_id in Duel.duel_data.keys():
        return update.message.reply_text(
            "<i>You’re already in another duel.</i>"
        )

    if data.reply_to_message:
        user_data = data.reply_to_message.from_user
        user = db.session.query(Users).filter_by(chat_id=user_data.id).first()

        if not user:
            user = Users(chat_id=user_data.id, 
                username=user_data.username, name=user_data.chat_id)
            db.session.add(user)
            db.session.commit()

        if user.chat_id in Duel.duel_data.keys():
            return update.message.reply_text(
                "{} is already engaged in another duel.".format(user.get_name())
            )
            
        keyboard = [[InlineKeyboardButton('✅', 
            callback_data=f'duel-request-{currentuser.chat_id}-{user.chat_id}')]]

        return update.message.reply_text("{} you were challenged by {}\n\n".format(
                user.get_name(), currentuser.get_name()
            ) + "<i>You dare to accept?</i>",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    keyboard = [[InlineKeyboardButton("✅ Duel ✅", 
        callback_data=f'duel-request-{currentuser.chat_id}')]]

    update.message.reply_text(
        "<b>Who has the courage to challenge {}?</b>".format(
            currentuser.get_name()), reply_markup=InlineKeyboardMarkup(
                keyboard))


# settings #
@chattype.group
@checkuser.check()
def settings(update, context, currentuser, group):
    data = update.message if update.message else update.edited_message
    
    user = context.bot.get_chat_member(data.chat.id, data.from_user.id)
        
    if not data.chat.all_members_are_administrators and \
        user.status not in ['creator', 'administrator']:
        return update.message.reply_text(
            '✋ You are not a group administrator!')
            

    message = "<i>Click the button to open private settings</i>"

    keyboard = [
        [InlineKeyboardButton('⚙️ Settings ⚙️', 
            url=f't.me/{context.bot.username}?start=' + \
                f'settings_{group.chat_id}_{currentuser.chat_id}')]
    ]

    update.message.reply_text(message, 
        reply_markup=InlineKeyboardMarkup(keyboard))


# stats #
@chattype.group
@checkuser.check()
def stats(update, context, currentuser, group):
    stats_points, stats_win = Stats.get_stats(group)
    message = "<b>Group statistics</b>{}{}".format(
        "\n" + stats_points, "\n" + stats_win) \
            if stats_points or stats_win else None
    
    update.message.reply_text(
        message if stats_points and stats_win \
            else "There are no statistics for this group yet")
    

@checkuser.check()
def globalstats(update, context, currentuser):
    stats_points, stats_win = Stats.get_global_stat()
    message = "<b>Global statistics</b>{}{}".format(
        "\n" + stats_points, "\n" + stats_win) \
            if stats_points or stats_win else None
    
    update.message.reply_text(
        message if message else "There are no statistics yet")


# admin #
@chattype.private
@checkuser.check(adminrequired=True)
def reaction(update, context, currentuser):
    message = "<b>List of saved reactions</b>"

    keyboard = [
        [InlineKeyboardButton(emoji, 
            callback_data='reaction-{}'.format(emoji))
        for emoji in EmojiList.emoji]
    ]

    update.message.reply_text(message, 
        reply_markup=InlineKeyboardMarkup(keyboard))


@chattype.private
@checkuser.check(adminrequired=True)
def addreaction(update, context, currentuser):
    args = update.message.text.split(' ', 3)[1:]

    if len(args) != 3:
        return update.message.reply_text(
            'Syntax error, use /addreaction emoji value reaction')

    emoji, value, reaction = args
    if value not in ('1', '2'):
        return update.message.reply_text(
            'Level not allowed, choose between 1 and 2')
    liv = 1 if value == '1' else 3
    new_reaction = Reaction(emoji=emoji, 
        value=liv, text=reaction)
    db.session.add(new_reaction)
    db.session.commit()

    update.message.reply_text('Reaction added')


@chattype.private
@checkuser.check(adminrequired=True)
@checkuser.user_arg
def ban(update, context, currentuser, user):
    user.ban = True
    user.save()

    update.message.reply_text(
        'The user has been banned.'
    )



@chattype.private
@checkuser.check(adminrequired=True)
@checkuser.user_arg
def unban(update, context, currentuser, user):
    user.ban = False
    user.save()

    update.message.reply_text(
        'User unban with success.'
    )


@chattype.private
@checkuser.check(adminrequired=True)
def users(update, context, currentuser):
    update.message.reply_text('Users:\n{}'.format(
        "\n".join(f"{number} - {user}" for number, user in enumerate(db.session.query(Users).all()))))


@chattype.private
@checkuser.check(adminrequired=True)
@checkuser.user_arg
def admin(update, context, currentuser, user):
    user.admin = True
    user.save()
    
    update.message.reply_text(
        "The user has become an admin."
    )


@chattype.private
@checkuser.check(adminrequired=True)
@checkuser.user_arg
def unadmin(update, context, currentuser, user):
    user.admin = False
    user.save()

    update.message.reply_text(
        "The user has been demoted."
    )


@chattype.private
@checkuser.check(adminrequired=True)
@checkuser.user_arg
def info(update, context, currentuser, user):
    update.message.reply_text(
        str(user)
    )