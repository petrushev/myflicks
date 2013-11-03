from operator import itemgetter

from myflick.controllers import BaseController
from myflick.db.models import Rating, Movie

itemgetter1 = itemgetter(1)

class Controller(BaseController):

    def index(self):
        self.template = 'index.phtml'

        # top rated
        self.view['top_rated'] = Rating.top_rated(self.session, limit=5)

        # last rated
        ids = map(itemgetter1, self.view['last_rated'])
        movies = self.session.query(Movie).filter(Movie.id.in_(ids)).all()
        movies = dict((m.id, m)
                      for m in movies)
        self.view['movies'] = movies

    def notfound(self):
        return BaseController.not_found(self, template = 'error/404.phtml')
