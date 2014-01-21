from operator import itemgetter, attrgetter

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from myflick.controllers import BaseController
from myflick.db.models import Movie, Rating, User

key1 = itemgetter(1)
getter_title = attrgetter('title')

class Controller(BaseController):

    def show(self, user_id, dummy):
        if self.user:
            if self.user.id==user_id:
                pass # TODO :remove this
                #return self.home()

        try:
            user_ = User.load(self.session, id=user_id)
        except NoResultFound:
            return self.not_found('error/404.phtml')

        ratings = self.session.query(Movie, Rating.rating)\
                      .join((Rating, and_(Rating.movie_id==Movie.id,
                                          Rating.user_id==user_.id)))\
                      .order_by(Rating.rated.desc()).all()

        watchlist = sorted(user_.watchlist, key=getter_title)

        self.view.update({'user_': user_,
                          'ratings1': ratings,
                          'ratings2': sorted(ratings, key=key1, reverse=True),
                          'watchlist': watchlist})
        self.template = 'user.phtml'

    def home(self):
        if self.user is None:
            return self.not_authorized('error/401.phtml')
        self.template = 'home.phtml'
