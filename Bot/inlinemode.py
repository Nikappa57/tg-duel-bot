from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent

from Bot.decorator import checkuser
from Bot.tools.stats import Stats


@checkuser.check()
def inline_mode(update, context, currentuser):
    stats_points, stats_win = Stats.get_global_stat()
    message = "<b>Global Statistics</b>{}{}".format(
        "\n" + stats_points, "\n" + stats_win) \
            if stats_points or stats_win else None

    update.inline_query.answer([
        InlineQueryResultArticle(
            id=uuid4(),
            title='Global Stats',
            description='global statistics',
            input_message_content=InputTextMessageContent(
                message if message else "There are no statistics yet")
            )
    ], cache_time=0)