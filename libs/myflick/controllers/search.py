from sqlalchemy.sql.expression import literal, and_, func

from myflick.controllers import BaseController
from myflick.db.models import Movie, Rating

class Controller(BaseController):

    def auto_movie(self, q):
        q = q.lstrip().lower()
        if q.startswith('the '):
            q = q[4:]
        target = literal(' ').op('||')(Movie.title)
        res = self.session.query(Movie.id, Movie.title, Rating.rating)\
                  .outerjoin((Rating, and_(Rating.movie_id == Movie.id,
                                           Rating.user == self.user)))\
                  .filter(target.ilike('%% %s%%' % q))\
                  .order_by(func.similarity(func.lower(target), q).desc())\
                  .limit(7).all()
        self.return_json(res)
