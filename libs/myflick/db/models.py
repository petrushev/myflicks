from datetime import datetime
from sys import stdout
from json import loads as json_loads
from json import dumps as json_dumps
from operator import and_

from werkzeug.urls import url_quote, url_quote_plus
from sqlalchemy.orm.exc import NoResultFound
import requests

from myflick.db import BaseModel

forbidden_domains = ('collider', 'impawards', 'imdb')

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
            self.session.flush()

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
            stdout.write("Error fetching: http://www.omdbapi.com/?s=%s&y=%d&r=JSON \n" % (qtitle, self.year))
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

        if type(self.meta) is dict:
            return self.meta

        return json_loads(self.meta)

    def image_fetch(self):
        q = '"%s" %d poster' % (self.title, self.year)
        q = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + url_quote_plus(q)
        q = requests.get(q)
        q = json_loads(q.content)
        try:
            q = q['responseData']['results']
        except (TypeError, KeyError):
            return
        for item in q:
            img = item['url']
            img_lower = img.lower()
            cond = [forbidden not in img_lower
                    for forbidden in forbidden_domains]
            if reduce(and_, cond):
                self.img = img
                return

    def get_image(self):
        if self.img is None:
            self.image_fetch()
            if self.img is None:
                return ''

        return self.img

class Rating(BaseModel):

    @staticmethod
    def last_rated(session, limit=10):
        # TODO add rating.rated index
        res = session.query(User, Movie.id, Movie.title, Rating.rating)\
                     .join(Rating).join(Movie)\
                     .order_by(Rating.rated.desc()).limit(limit).all()
        return res
