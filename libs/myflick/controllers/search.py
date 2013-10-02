from sqlalchemy.sql.expression import literal

from myflick.controllers import BaseController
from myflick.db.models import Movie

class Controller(BaseController):

    def auto_movie(self, q):
        # TODO : add db index
        res = self.session.query(Movie)\
                  .filter(literal(' ').op('||')(Movie.title).ilike('%% %s%%' % q)).all()
        res = [(m.id, m.title, m.url)
               for m in res]

        self.return_json(res)
