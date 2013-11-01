from sqlalchemy.sql.expression import literal, and_, func

from myflick.controllers import BaseController
from myflick.db.models import Movie, Rating

class Controller(BaseController):

    def auto_movie(self, q):
        orig_q = q
        q = q.lstrip().lower().split(' ')
        full_words, q = q[:-1], q[-1]
        if 'the' in full_words:
            full_words.remove('the')

        target = literal(' ').op('||')(Movie.title)

        filters = []
        for word in full_words:
            filters.append(target.ilike('%% %s %%' % word))

        filters.append(target.ilike('%% %s%%' % q))
        if len(filters) > 1:
            filters = and_(*filters)
        else:
            filters = filters[0]


        res = self.session.query(Movie.id, Movie.title, Rating.rating)\
                  .outerjoin((Rating, and_(Rating.movie_id == Movie.id,
                                           Rating.user == self.user)))\
                  .filter(filters)\
                  .order_by(func.similarity(func.lower(target), orig_q).desc())\
                  .limit(7).all()
        self.return_json(res)
