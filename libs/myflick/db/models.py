from urlparse import urlparse
from datetime import datetime

from werkzeug.urls import url_quote
from jinja2 import escape as html_escape
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import func, and_

from myflick.db import BaseModel

class User(BaseModel):

    @staticmethod
    def save_g_data(session, profile_id, fullname, email):
        try:
            u = User.load(session, nickname = profile_id, service = 'gmail')

        except NoResultFound:
            u = User(nickname = profile_id, service = 'gmail',
                     fullname = fullname, email = email)
            session.add(u)
        else:
            u.fullname = fullname
            u.email = email

        session.flush()
        return u

    @property
    def alias(self):
        if self.service == 'gmail':
            return self.fullname

        raise NotImplementedError, ' for service ' + self.service

    @property
    def alias_repr(self):
        return url_quote(self.alias.replace(' ', '_'), safe='')

    def set_rating(self, movie, rating):
        try:
            r = Rating.load(self.session, user=self, movie=movie)
        except NoResultFound:
            self.session.add(Rating(user=self, movie=movie,
                                    rating=rating, rated=datetime.utcnow()))
            self.session.flush()
        else:
            r.rating = rating
            r.rated = datetime.utcnow()

    def drop_rating(self, movie):
        try:
            r = Rating.load(self.session, user=self, movie=movie)
        except NoResultFound:
            pass
        else:
            r.drop()

class Movie(BaseModel):
    pass

class Rating(BaseModel):
    pass
