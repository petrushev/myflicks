import requests
from json import loads as json_loads
from werkzeug.urls import url_quote

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from myflick.controllers import BaseController
from myflick.db.models import Movie, Rating, User

class Controller(BaseController):

    def partial(self, movie_id):
        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return

        meta = movie.get_meta()
        self.view.update({'movie': movie,
                          'meta': meta})
        self.template = 'partials/movie.phtml'

    def show(self, movie_id, dummy):
        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return self.not_found('error/404.phtml')

        # last ratings
        last_ratings = self.session.query(Rating.rating, User)\
                           .join((User, and_(User.id == Rating.user_id,
                                             Rating.movie == movie)))\
                           .order_by(Rating.rated.desc()).all()

        if len(last_ratings) == 0:
            avg_rating = None
        else:
            avg_rating = sum(r.rating for r in last_ratings) * .5 / len(last_ratings)

        # user rating
        if self.user is not None:
            try:
                self.view['rating'] = Rating.load(self.session, movie=movie, user=self.user)
            except NoResultFound:
                pass

        self.view.update({'movie': movie,
                          'meta': movie.get_meta(),
                          'last_ratings': last_ratings,
                          'avg_rating': avg_rating})
        self.template = 'movie.phtml'

    def missing(self):
        self.template = 'missing.phtml'

    def fill_missing(self):
        imdb_link = self.request.form['imdb'].lower()
        if 'imdb.com' not in imdb_link:
            return self.redirect('/movie/missing')

        try:
            imdbid = imdb_link.split("title/")[1].split("/")[0]
            q = requests.get("http://www.omdbapi.com/?i=%s&r=JSON" % imdbid)
            content = q.content
            del q
            content_json = json_loads(content)
            title = content_json['Title']
            year = int(content_json['Year'].strip())

        except Exception, _:
            return self.redirect('/movie/missing')

        try:
            movie = Movie.load(self.session, title=title, year=year)
        except NoResultFound:
            movie = Movie(title=title, year=year, meta=content, imdbid=imdbid)
            self.session.add(movie)
            self.session.flush()
        else:
            movie.meta=content
            movie.imdbid=imdbid

        return self.redirect('/movie/%d-%s' % (movie.id, url_quote(movie.title)))
