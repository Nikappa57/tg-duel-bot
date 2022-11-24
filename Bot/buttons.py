import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from Bot.decorator import checkuser
from Bot.database import db
from Bot.database.models import Users, Reaction
from Bot.tools.groups import checkgroups
from Bot.tools.duel import Duel
from Bot.tools.emoji import EmojiList


@checkuser.check()
def button(update, context, currentuser):
    query = update.callback_query
    data = query.data

    if data[:4] == 'duel':
        if data[:13] == 'duel-request-':
            user_id = data[13:]
            if '-' in user_id:
                user_id, currentuser_id = user_id.split('-')
                if int(currentuser_id) != currentuser.chat_id:
                    return query.answer('The duel was not sent to you.')

            user = db.session.query(Users).filter_by(chat_id=user_id).first()

            if currentuser.chat_id == int(user_id):
                return query.answer('You can’t challenge yourself.', 
                    show_alert=True)

            if currentuser.chat_id in Duel.duel_data.keys():
                return query.answer('You’re already in another duel.', 
                    show_alert=True)

            if user.chat_id in Duel.duel_data.keys():
                return query.answer('The user is already in another duel.', 
                    show_alert=True)

            Duel.duel_data[currentuser.chat_id] = Duel(currentuser, user)
            duel = Duel.duel_data[currentuser.chat_id]
            Duel.duel_data[user.chat_id] = duel

            message = '<b>{0} has accepted the challenge.</b>\n\n{0} '.format(
                currentuser.get_name()) + 'It’s your turn, send this ' + \
                    'emoji: <code>{}</code>'.format(duel.emoji)

            keyboard = [
                [
                    InlineKeyboardButton('❌ Give up ❌', 
                    callback_data='duel-giveup-{}-{}'.format(
                        currentuser.chat_id, user.chat_id))
                ]
            ]

            query.edit_message_text(message, 
                reply_markup=InlineKeyboardMarkup(keyboard))

        elif data[:12] == 'duel-giveup-':
            users = data[12:].split('-')
            user_1 = db.session.query(Users).filter_by(
                chat_id=users[0]).first()
            user_2 = db.session.query(Users).filter_by(
                chat_id=users[1]).first()

            if currentuser not in [user_1, user_2]:
                return query.answer('You’re not this duel')
            try:
                del Duel.duel_data[user_1.chat_id]
                del Duel.duel_data[user_2.chat_id]
            except KeyError:
                pass

            winner = user_1 if user_1 != currentuser else user_2
            
            query.edit_message_text(
                '<i>I’m sorry {} but {} has given up!</i>'.format(
                    winner.get_name(), currentuser.get_name()))

    elif data[:8] == 'settings':
        if data == 'settings-close':
            context.bot.delete_message(currentuser.chat_id, 
                query.message.message_id)
            return query.answer('⚙️ Settings have been closed ⚙️')

        elif data[:18] == 'settings-reaction-':
            if 'range' in data:
                group_id, reaction_range = re.match(
                    '^settings-reaction-(-\d+)-range-(\d)$', data).groups()
                
                group = checkgroups(group_id)

                if reaction_range == "1":
                    group.allow_reaction_lv1 = not group.allow_reaction_lv1
                
                elif reaction_range == "2":
                    group.allow_reaction_lv2 = not group.allow_reaction_lv2
                
                else:
                    if group.allow_reaction_lv1 or group.allow_reaction_lv2:
                        group.allow_reaction_lv1, group.allow_reaction_lv2 = False, False
                    else:
                        group.allow_reaction_lv1, group.allow_reaction_lv2 = True, True

                db.session.commit()
            else:
                group_id = data[18:]
                group = checkgroups(group_id)
                
            lv = 3 if group.allow_reaction_lv1 and group.allow_reaction_lv2 \
                else 1 if group.allow_reaction_lv1 else 2 if \
                    group.allow_reaction_lv2 else 4

            message = '<b>Settings Reactions Group</b>\n\n<i>Choose ' + \
                'which reactions to keep activated</i>\n\n' + \
                    '<b>Range 1:</b> The user makes little mistake' + \
                        '\n<b>Range 2:</b> The user makes maximum points'
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text='➡️ None ⬅️' if lv == 4 else 'None', 
                        callback_data='settings-reaction-' + \
                            f'{group.chat_id}-range-3')
                ],
                [
                    InlineKeyboardButton(
                        text='➡️ Range 1 ⬅️' if lv == 1 or lv == 3 \
                            else 'Range 1', callback_data='settings-' + \
                                f'reaction-{group.chat_id}-range-1'),
                    InlineKeyboardButton(
                        text='➡️ Range 2 ⬅️' if lv == 2 or lv == 3 \
                            else 'Range 2', callback_data='settings-' + \
                                f'reaction-{group.chat_id}-range-2')
                ],
                [
                    InlineKeyboardButton(
                        text='◀️ Back ◀️', 
                        callback_data=f'settings-{group.chat_id}')
                ]
            ]

            query.edit_message_text(message, 
                reply_markup=InlineKeyboardMarkup(keyboard))

        elif data[:14] == 'settings-duel-':
            if 'modify' in data:
                group_id, allow_duel = re.match(
                    '^settings-duel-(-\d+)-modify-(\d)', data).groups()
                
                group = checkgroups(group_id)
                allow_duel = bool(int(allow_duel))

                if allow_duel == group.allow_duels:
                    group.allow_duels = not allow_duel
                else:
                    group.allow_duels = allow_duel

                db.session.commit()
            
            else:
                group_id = data[14:]
                group = checkgroups(group_id)

            message = '<b>Settings of the group duels</b>\n\n<i>Choose ' + \
                    'whether to keep duels activated in your group</i>\n\n'

            keyboard = [
                [
                    InlineKeyboardButton(
                        text='➡️ Active ⬅️' if group.allow_duels \
                            else 'Active', callback_data='settings-' + \
                                f'duel-{group.chat_id}-modify-1'),
                    InlineKeyboardButton(
                        text='➡️ Disable ⬅️' if not group.allow_duels \
                            else 'Disattivati', callback_data='settings-' + \
                                f'duel-{group.chat_id}-modify-0')
                ],
                [
                    InlineKeyboardButton(
                        text='◀️ Back ◀️', 
                        callback_data=f'settings-{group.chat_id}')
                ]
            ]

            query.edit_message_text(message,
                reply_markup=InlineKeyboardMarkup(keyboard))
                

        elif data[:9] == 'settings-':
                group_id = data[9:]
                group = checkgroups(group_id)

                message = '<b>Group setting</b>\n\n' + \
                        '<i>Choose whether to disable reactions or duels.</i>'
                    
                keyboard = [
                    [
                        InlineKeyboardButton('🤪 Reactions 🤪', 
                            callback_data=f'settings-reaction-{group.chat_id}'),
                        InlineKeyboardButton('🏀 Duels 🏀', 
                            callback_data=f'settings-duel-{group.chat_id}')
                    ],
                    [
                        InlineKeyboardButton('✖️ Close Settings ✖️', 
                            callback_data=f'settings-close')
                    ]
                ]

                query.edit_message_text(message, 
                    reply_markup=InlineKeyboardMarkup(keyboard))

    elif data[:8] == 'reaction' and currentuser.admin:
        if '-' not in data:    
            message = "<b>List of saved reactions</b>"

            keyboard = [
                [InlineKeyboardButton(emoji, 
                    callback_data='reaction-{}'.format(emoji))
                for emoji in EmojiList.emoji]
            ]

            query.edit_message_text(message, 
                reply_markup=InlineKeyboardMarkup(keyboard))

        elif data[:9] == 'reaction-':
            if '-' not in data[9:]:
                emoji = data[9:]
                reaction_list = db.session.query(
                    Reaction).filter_by(emoji=emoji).all()

                if not reaction_list:
                    return query.answer('There are no reactions for this emoji yet')

                message = '<b>List of reactions saved for {}</b>'.format(emoji)
                keyboard = [[InlineKeyboardButton(reaction.text, 
                    callback_data='reaction-{}-{}'.format(
                        emoji, reaction.id))] for reaction in reaction_list]

                keyboard.append([
                    InlineKeyboardButton(
                        '◀️ Back ◀️', 
                        callback_data='reaction'.format(emoji))
                ])

                query.edit_message_text(message, 
                    reply_markup=InlineKeyboardMarkup(keyboard))

            elif '-delete' not in data:
                reaction_id = data[11:]
                reaction = db.session.query(Reaction).get(reaction_id)
                message = '<b>Change Reaction</b>\n\n<b>Reaction</b>: ' + \
                    '{}\n<b>Emoji</b>: {}\n<b>Range</b>: {}'.format(
                    reaction.text, reaction.emoji, reaction.value)

                keyboard = [
                    [
                        InlineKeyboardButton('❌ Delete ❌', 
                        callback_data='reaction-{}-{}-delete'.format(
                            reaction.emoji, reaction.id))
                    ],
                    [
                        InlineKeyboardButton('◀️ Back ◀️', 
                        callback_data='reaction-{}'.format(reaction.emoji))
                    ]
                ]

                query.edit_message_text(message, 
                    reply_markup=InlineKeyboardMarkup(keyboard))

            else:
                emoji, reaction_id, _ = data[9:].split('-')
                reaction = db.session.query(Reaction).get(reaction_id)
                db.session.delete(reaction)
                db.session.commit()

                reaction_list = db.session.query(
                    Reaction).filter_by(emoji=emoji).all()

                if not reaction_list:
                    message = "<b>List of saved reactions</b>"

                    keyboard = [
                        [InlineKeyboardButton(emoji, 
                            callback_data='reaction-{}'.format(emoji))
                        for emoji in EmojiList.emoji]
                    ]

                    query.edit_message_text(message, 
                        reply_markup=InlineKeyboardMarkup(keyboard))
            
                    return query.answer(
                        'There are no reactions for this emoji yet')

                message = '<b>List of reactions saved for {}</b>'.format(emoji)
                keyboard = [[InlineKeyboardButton(reaction.text, 
                    callback_data='reaction-{}-{}'.format(
                        emoji, reaction.id))] for reaction in reaction_list]

                keyboard.append([InlineKeyboardButton(
                    '◀️ Back ◀️', callback_data='reaction')])

                query.edit_message_text(message, 
                    reply_markup=InlineKeyboardMarkup(keyboard))
            
    query.answer()