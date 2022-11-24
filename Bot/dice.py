from Bot.decorator import checkuser
from Bot.tools.duel import Duel
from Bot.tools.stats import Stats
from Bot.tools.groups import checkgroups
from Bot.database.models import Reaction

@checkuser.check()
def dice(update, context, currentuser):
    points = update.message.dice.value
    emoji = update.message.dice.emoji

    if not update.message.chat.type in ['group', 'supergroup']:
        return
    
    group = checkgroups(update.message.chat.id)
    
    if currentuser.chat_id in Duel.duel_data.keys():
        duel = Duel.duel_data[currentuser.chat_id]

        if duel.turn != currentuser:
            return update.message.reply_text('It’s not your turn!')

        if duel.emoji != emoji:
            return update.message.reply_text(
                'You’re using the wrong emoji, use <code>{}</code>'.format(
                    duel.emoji
                ))

        duel.update_points(currentuser, points)

        if duel.step == 6:
            sent = update.message.reply_text(
                    '<b>The duel is over</b>\n\n<i>The winner is...</i>'.format(
                        duel.turn.get_name()
                ))

            winner = duel.get_winner()
            
            if not winner:
                del Duel.duel_data[duel.user_1.chat_id]
                del Duel.duel_data[duel.user_2.chat_id]

                return context.job_queue.run_once(lambda x=None: context.bot.edit_message_text(
                    '<b>The duel ended in a tie!</b>\n\n{} {} points\n{} {} points'.format(
                        duel.user_1.get_name(), duel.user_1_points, 
                        duel.user_2.get_name(), duel.user_2_points
                    ), 
                    sent.chat.id, 
                    sent.message_id
                ), 3 if emoji == '🎯' else 4)


            context.job_queue.run_once(lambda x=None: context.bot.edit_message_text(
                    '<b>{} won the duel</b>\n\n<i>{} {} points\n{} {} points</i>'.format(
                    winner.get_name(), duel.user_1.get_name(), duel.user_1_points,
                    duel.user_2.get_name(), duel.user_2_points), 
                    sent.chat.id, 
                    sent.message_id
                ), 3 if emoji == '🎯' else 4)

            del Duel.duel_data[duel.user_1.chat_id]
            del Duel.duel_data[duel.user_2.chat_id]

            Stats.update_stats(winner, group, win=1)
        else:
            sent = update.message.reply_text(
            '<b>You scored ? points</b>\n\n<i>Now it is the turn of {}</i>'.format(
                duel.turn.get_name()
            ))

            context.job_queue.run_once(lambda x=None: context.bot.edit_message_text(
                sent.text.replace("?", str(points)), 
                sent.chat.id, 
                sent.message_id
            ), 3 if emoji == '🎯' else 4)

    else:
        message = Reaction.get_reaction(value=points, emoji=emoji, group=group)

        if message:
            context.job_queue.run_once(lambda x=None: 
                update.message.reply_text(message), 3 if emoji == '🎯' else 4)
            
    
    Stats.update_stats(currentuser, points=points, group=group)