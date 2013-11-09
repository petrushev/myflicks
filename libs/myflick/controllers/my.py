from myflick.controllers import BaseController
from myflick.db.models import Rating, Movie, User

from sqlalchemy.orm.exc import NoResultFound

class Controller(BaseController):

    def init(self):
        if self.user is None:
            self.not_authorized('error/401.phtml')
            self.action_name = None
            return

    def watchlist(self):
        self.template = 'my/watchlist.phtml'

    def togglewatchlist(self):
        movie_id = int(self.request.form['movie_id'])
        movie = Movie.load(self.session, id=movie_id)
        if movie in self.user.watchlist:
            self.user.watchlist.remove(movie)
        else:
            # checked if already seen
            try:
                Rating.load(self.session, movie=movie, user=self.user)
            except NoResultFound:
                self.user.watchlist.add(movie)
