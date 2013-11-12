from operator import attrgetter

from myflick.controllers import BaseController
from myflick.db.models import Rating, Movie, User

from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound

getter_id = attrgetter('id')

class Controller(BaseController):

    def init(self):
        if self.user is None:
            self.not_authorized('error/401.phtml')
            self.action_name = None
            return

    def watchlist(self):
        watchlist_ids = map(getter_id, self.user.watchlist)

        avg_rating = self.session.query(Rating.movie_id, func.avg(Rating.rating))\
                         .filter(Rating.movie_id.in_(watchlist_ids))\
                         .group_by(Rating.movie_id).all()
        avg_rating = dict(avg_rating)
        self.view['avg_rating'] = avg_rating
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
