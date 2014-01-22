from datetime import datetime
from sys import stderr
from json import loads as json_loads
from json import dumps as json_dumps
from random import shuffle
from os import environ

from werkzeug.urls import url_quote, url_quote_plus
from sqlalchemy.sql.expression import func, and_
from sqlalchemy.orm.exc import NoResultFound
import requests

from myflick.db import BaseModel

forbidden_domains = ('collider', 'impawards', 'imdb', 'dbcovers', 'turkcealtyazi', 'ebayimg',
                     'iceposter', 'beyondhollywood', 'examiner', 'bigcommerce', 'thisdistractedglobe',
                     'bdbphotos', 'mposter', 'images-amazon', 'audiorushes', 'movieposterdb')

MODS = environ['MODS']

class User(BaseModel):

    @staticmethod
    def save_g_data(session, profile_id, fullname, email):
        try:
            u = User.load(session, nickname = profile_id, service = 'gmail')

        except NoResultFound:
            u = User(nickname = profile_id, service = 'gmail',
                     fullname = fullname, email = email)
            session.add(u)
            session.flush()
        else:
            u.fullname = fullname
            u.email = email

        return u

    @staticmethod
    def save_twitter_data(session, nickname, fullname, email):
        try:
            u = User.load(session, nickname = nickname, service = 'twitter')

        except NoResultFound:
            u = User(nickname = nickname, service = 'twitter',
                     fullname = fullname, email = email)
            session.add(u)
            session.flush()
        else:
            u.fullname = fullname
            u.email = email

        return u

    @staticmethod
    def save_fb_data(session, nickname, fullname, email):
        try:
            u = User.load(session, nickname = nickname, service = 'fb')

        except NoResultFound:
            u = User(nickname = nickname, service = 'fb',
                     fullname = fullname, email = email)
            session.add(u)
            session.flush()
        else:
            u.fullname = fullname
            u.email = email

        return u

    @property
    def alias(self):
        if self.service in ('gmail', 'twitter', 'fb'):
            return self.fullname

        raise NotImplementedError, ' for service ' + self.service

    @property
    def home_url(self):
        if self.service=='fb':
            return "https://www.facebook.com/profile.php?id=%s" % self.nickname
        if self.service=='twitter':
            return "http://twitter.com/%s" % self.fullname

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

        # drop from watchlist
        if movie in self.watchlist:
            self.watchlist.remove(movie)
            self.session.flush()

    def drop_rating(self, movie):
        try:
            r = Rating.load(self.session, user=self, movie=movie)
        except NoResultFound:
            pass
        else:
            r.drop()
            self.session.flush()

    @staticmethod
    def recent(session, limit=5):
        sq = session.query(Rating.user_id, func.max(Rating.rated).label('max_rated'))\
                    .group_by(Rating.user_id).subquery()
        res = session.query(User)\
                     .join((sq, sq.c.user_id==User.id))\
                     .order_by(sq.c.max_rated.desc()).limit(limit).all()
        return res

    def is_mod(self):
        modlist = MODS.split(';')
        return ('%s|%s' % (self.nickname, self.service)) in modlist


class Movie(BaseModel):

    def __repr__(self):
        return "<Movie: %s (%d)>" % (self.title, self.year)

    def imdb_title_fetch(self):
        if self.imdbid is None:
            qtitle = self.title.lower()
            if '(' in qtitle:
                qtitle = qtitle.split('(')[0].strip()
            if qtitle.endswith(' the'):
                qtitle = qtitle[:-4]
            if qtitle.endswith(' a'):
                qtitle = qtitle[:-2]

            #                 http://www.omdbapi.com/?s=Star%20Wars&y=1977&r=JSON
            q = requests.get("http://www.omdbapi.com/?s=%s&y=%d&r=JSON" % (qtitle, self.year))
            try:
                q = json_loads(q.content)['Search']

            except KeyError:
                stderr.write("Error fetching: http://www.omdbapi.com/?s=%s&y=%d&r=JSON \n" % (qtitle, self.year))
                return

            self.imdbid = q[0]['imdbID']

        q = requests.get("http://www.omdbapi.com/?i=%s&r=JSON" % self.imdbid)
        self.meta = json_loads(q.content)
        self.session.flush()

    def get_meta(self):
        if self.meta is None or self.meta=={} or self.meta=='{}':
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
            if all(cond):
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
        sq = session.query(Rating.movie_id.label('movie_id'),
                           func.min(Rating.rated).label('min_rated'))\
                    .group_by(Rating.movie_id).subquery()

        res = session.query(User, Movie.id, Movie.title, Rating.rating)\
                     .join((Rating, Rating.user_id==User.id))\
                     .join((Movie, Movie.id==Rating.movie_id))\
                     .join((sq, and_(sq.c.movie_id==Movie.id,
                                     sq.c.min_rated==Rating.rated)))\
                     .order_by(sq.c.min_rated.desc()).limit(limit).all()
        return res

    @staticmethod
    def _top_rated(session, limit, offset=9.90, appendto=tuple()):
        # select movie_id, avg(rating) from rating group by movie_id
        # having (avg(rating) > 9.90 and avg(rating) <=10.0);
        top_offset = min([offset + .1, 10.0])
        avg_ = func.avg(Rating.rating)
        cnt_ = func.count(Rating.user_id)
        res = session.query(Rating.movie_id, avg_)\
                     .group_by(Rating.movie_id)\
                     .having(and_(cnt_ > 1, avg_ > offset, avg_ <= top_offset))\
                     .all()

        if len(res) > 0 or offset < 1.0:
            res = tuple(res)
            appendto = appendto + res
            if len(appendto) >= limit or offset < 1.0:
                appendto = list(appendto)
                shuffle(appendto)
                if len(appendto) > limit:
                    appendto[limit:] = []
                return appendto

        return Rating._top_rated(session, limit=limit, offset=offset-0.1, appendto=appendto)

    @staticmethod
    def top_rated(session, limit=5):
        res = Rating._top_rated(session, limit)
        ids = [r.movie_id for r in res]
        movies = session.query(Movie).filter(Movie.id.in_(ids)).all()
        movies = dict((m.id, m)
                      for m in movies)

        return tuple((movies[id_], avg_)
                     for id_, avg_ in res)

class Watchlist(BaseModel):
    pass
