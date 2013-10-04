from myflick.controllers import BaseController
from myflick.db.models import Movie, Rating, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

class Controller(BaseController):

    def partial(self, movie_id):
        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return

        self.view.update({'movie': movie,
                          'meta': movie.get_meta()})
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

        self.view.update({'movie': movie,
                          'meta': movie.get_meta(),
                          'last_ratings': last_ratings,
                          'avg_rating': avg_rating})
        self.template = 'movie.phtml'
