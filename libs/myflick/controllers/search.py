from sqlalchemy.sql.expression import literal, and_

from myflick.controllers import BaseController
from myflick.db.models import Movie, Rating

class Controller(BaseController):

    def auto_movie(self, q):
        # TODO : add db index
        res = self.session.query(Movie.id, Movie.title, Movie.url, Rating.rating)\
                  .outerjoin((Rating, and_(Rating.movie_id == Movie.id,
                                           Rating.user == self.user)))\
                  .filter(literal(' ').op('||')(Movie.title).ilike('%% %s%%' % q)).all()

        self.return_json(res)
