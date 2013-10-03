from datetime import datetime
from json import loads as json_loads
from json import dumps as json_dumps

from werkzeug.urls import url_quote
from sqlalchemy.orm.exc import NoResultFound
import requests

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

    def imdb_title_fetch(self):
        #http://www.omdbapi.com/?s=Star%20Wars&y=1977&r=JSON
        qtitle = self.title.lower()
        if '(' in qtitle:
            qtitle = qtitle.split('(')[0].strip()
        if qtitle.endswith(' the'):
            qtitle = qtitle[:-4]
        if qtitle.endswith(' a'):
            qtitle = qtitle[:-2]

        q = requests.get("http://www.omdbapi.com/?s=%s&y=%d&r=JSON" % (qtitle, self.year))
        try:
            q = json_loads(q.content)['Search']
        except KeyError:
            print "http://www.omdbapi.com/?s=%s&y=%d&r=JSON" % (qtitle, self.year)
            self.meta = json_dumps({})
            self.session.flush()
            return

        imdbid = q[0]['imdbID']
        self.imdbid = imdbid
        q = requests.get("http://www.omdbapi.com/?i=%s&r=JSON" % imdbid)
        self.meta = q.content
        self.session.flush()

    def get_meta(self):
        if self.meta is None:
            self.imdb_title_fetch()
            if self.meta is None:
                return {}

            return json_loads(self.meta)
        return self.meta

class Rating(BaseModel):
    pass
