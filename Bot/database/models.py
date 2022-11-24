from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

from Bot.tools.emoji import EmojiList


Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)

    name = Column(String(40))
    username = Column(String(40), unique=True)

    ban = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)

    currentstats = relationship('Stats', backref=backref('currentstats', uselist=False))

    def save(self):
        db.session.commit()
    
    def get_name(self):
        return '@' + self.username if self.username else self.name
        
    def __repr__(self):
        return "Users(chat_id={}, name={}, username={}, ban={}, admin={})".format(
            self.chat_id, self.name, self.username, self.ban, self.admin
        )
    
    def __str__(self):
        return "<code>{}</code> {} {}".format(
            self.chat_id, self.get_name(), "<b>ADMIN</b>" if self.admin else ""
        )


class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)

    # Settings #
    allow_reaction_lv1 = Column(Boolean, default=True)
    allow_reaction_lv3 = Column(Boolean, default=True)
    
    allow_duels = Column(Boolean, default=True)

    stats = relationship("Stats", backref='stats')

    def save(self):
        db.session.commit()

    def __repr__(self):
        return "Groups(chat_id={})".format(self.chat_id)


class Stats(Base):
    __tablename__ = "Stats"
    id = Column(Integer, primary_key=True)
    points = Column(Integer, default=0)
    win = Column(Integer, default=0)

    group_id = Column(Integer, ForeignKey('groups.id'))
    user_id = Column(Integer, ForeignKey('users.id'))


class Reaction(Base):
    __tablename__ = "Reaction"
    id = Column(Integer, primary_key=True)

    emoji = Column(Integer, nullable=False)
    value = Column(Integer, nullable=False)
    text = Column(String(256), nullable=False)
    
    @staticmethod
    def get_reaction(value:int, emoji:str, group:Groups) -> str:
        """
        very bad -> lv 1
        other results -> lv 2
        win -> lv 3

        0 🎲 -> 1 - very bad // 6 - win
        1 🎯 -> 1 - very bad // 6 - win
        2 🏀 -> 1, 2 - very bad // 4, 5 -> win
        3 ⚽️ -> 1, 2 - very bad // 4, 5 -> win
        """ 
        
        if emoji in EmojiList.emoji[:2]:
            level = 1 if value == 1 else 3 if value == 6 else 2
        elif emoji in EmojiList.emoji[2:]:
            level = 1 if value < 3 else 2 if value == 3 else 3
        else:
            level = None

        if level == 2 or (level == 3 and not group.allow_reaction_lv3) or (level == 1 and not group.allow_reaction_lv1):
            return None

        reaction = db.session.query(Reaction).filter_by(
            emoji=emoji, value=level).order_by(func.random()).first()
        return reaction.text if reaction else None


from Bot.database import db