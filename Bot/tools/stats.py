from Bot.database import db
from Bot.database.models import Users, Groups, Stats as St


class Stats:
    @staticmethod
    def update_stats(user:Users, group:Groups, points:int=0, win:int=0) -> None:
        stats = db.session.query(St).filter_by(
            group_id=group.id, user_id=user.id).first()
        
        if not stats:
            stats = St(group_id=group.id, user_id=user.id)
            db.session.add(stats)
            db.session.commit()
        
        stats = db.session.query(St).filter_by(
            group_id=group.id, user_id=user.id).first()
        
        stats.points += points
        stats.win += win

        db.session.commit()
    
    @staticmethod
    def get_stats(group:Groups) -> list:
        stats_points = db.session.query(St).filter_by(
            group_id=group.id).order_by(St.points.desc())[:5]
        stats_win = db.session.query(St).filter_by(
            group_id=group.id).order_by(St.win.desc())[:5]

        stats_points = ["{}{} {} punti".format(
            '🥇' if stats_points.index(stat) == 0 else '🥈' \
                if stats_points.index(stat) == 1 else '🥉' \
                    if stats_points.index(stat) == 2 else '',
            db.session.query(Users).get(stat.user_id).get_name(), stat.points)
        for stat in stats_points if stat.points]

        stats_win = ["{}{} {} {}".format(
            '🥇' if stats_win.index(stat) == 0 else '🥈' \
                if stats_win.index(stat) == 1 else '🥉' \
                    if stats_win.index(stat) == 2 else '',
            db.session.query(Users).get(stat.user_id).get_name(), 
            stat.win, "vittorie" if stat.win > 1 else "vittoria")
        for stat in stats_win if stat.win]

        points_message = "{}\n{}".format(
            "\n<b>Top 5 Classifica Punti: </b>" if stats_points else "",
            "\n".join(stats_points))

        win_message = "{}\n{}".format(
            "\n<b>Top 5 Classifica Vittorie: </b>" if stats_win else "",
            "\n".join(stats_win))
        
        return points_message, win_message

    @staticmethod
    def get_global_stat() -> list:
        stats_points = db.session.query(St).all()
        stats_win = db.session.query(St).all()
        
        stats_points_dict = dict()
        for stat in stats_points:
            if stat.user_id not in stats_points_dict.keys():
                stats_points_dict[stat.user_id] = stat.points
            else:
                stats_points_dict[stat.user_id] += stat.points
            
        stats_win_dict = dict()
        for stat in stats_win:
            if stat.user_id not in stats_win_dict.keys():
                stats_win_dict[stat.user_id] = stat.win
            else:
                stats_win_dict[stat.user_id] += stat.win

        stats_points_dict = {key: item for key, item in 
            sorted(stats_points_dict.items(), 
                key=lambda item: item[1], reverse=True)}

        stats_win_dict = {key: item for key, item in 
            sorted(stats_win_dict.items(), 
                key=lambda item: item[1], reverse=True)}

        stats_points = ["{}{} {} punti".format(
            '🥇' if list(stats_points_dict).index(user_id) == 0 else '🥈' \
                if list(stats_points_dict).index(user_id) == 1 else '🥉' \
                    if list(stats_points_dict).index(user_id) == 2 else '',
            db.session.query(Users).get(user_id).get_name(), 
            stats_points_dict[user_id]) for user_id in stats_points_dict \
                if stats_points_dict[user_id]][:5]

        stats_win = ["{}{} {} vittorie".format(
            '🥇' if list(stats_win_dict).index(user_id) == 0 else '🥈' \
                if list(stats_win_dict).index(user_id) == 1 else '🥉' \
                    if list(stats_win_dict).index(user_id) == 2 else '',
            db.session.query(Users).get(user_id).get_name(), 
            stats_win_dict[user_id]) for user_id in stats_win_dict if \
                stats_win_dict[user_id]][:5]

        points_message = "{}\n{}".format(
            "\n<b>Top 5 Classifica Punti: </b>" if stats_points else "",
            "\n".join(stats_points))

        win_message = "{}\n{}".format(
            "\n<b>Top 5 Classifica Vittorie: </b>" if stats_win else "",
            "\n".join(stats_win))
        
        return points_message, win_message