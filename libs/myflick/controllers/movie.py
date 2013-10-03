from myflick.controllers import BaseController
from myflick.db.models import Movie
from sqlalchemy.orm.exc import NoResultFound

class Controller(BaseController):

    def partial(self, movie_id):
        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return

        meta = movie.get_meta()
        print type(meta), meta
        self.view.update({'movie': movie,
                          'meta': meta})
        self.template = 'partials/movie.phtml'
