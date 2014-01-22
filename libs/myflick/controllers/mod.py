#from operator import itemgetter, attrgetter

import json

from sqlalchemy.orm.exc import NoResultFound
#from sqlalchemy.sql.expression import and_

from myflick.controllers import BaseController
from myflick.db.models import Movie, User

#key1 = itemgetter(1)
#getter_title = attrgetter('title')

def reformat_cast(cast):
    return ', '.join([item.strip() for item in cast.split(',')])

class Controller(BaseController):

    def init(self):
        if self.user is None or not self.user.is_mod():
            self.template = 'error/401.phtml'
            self.action = 'not_authorized'

    def movie(self, movie_id):
        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return self.not_found('error/404.phtml')

        self.view['movie'] = movie
        self.view['meta'] = movie.get_meta()
        self.template = 'mod/movie.phtml'

    def update_movie(self, movie_id):
        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return self.not_found('error/404.phtml')


        title, year, poster, director, screenwriter, actors, imdbid = [self.request.form[key]
            for key in 'title, year, poster, director, screenwriter, actors, imdbid'.split(', ')]

        year = int(year)

        movie.title = title
        movie.year = year
        movie.img = poster

        if imdbid==movie.imdbid:
            meta = movie.get_meta()
            meta['Director'] = reformat_cast(director)
            meta['Screenwriter'] = reformat_cast(screenwriter)
            meta['Actors'] = reformat_cast(actors)
            movie.meta = meta

        else:
            imdbid = imdbid.strip()
            if 'imdb.com' in imdbid:
                imdbid = imdbid.split("title/")[1].split("/")[0]

            movie.imdbid = imdbid
            movie.meta = None
            movie.get_meta()

        return self.redirect('/mod/movie/%d' % movie_id)
