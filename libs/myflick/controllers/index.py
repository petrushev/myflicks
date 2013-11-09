from operator import itemgetter
from random import shuffle

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import not_

from myflick.controllers import BaseController
from myflick.db.models import Rating, Movie, User

itemgetter0 = itemgetter(0)
itemgetter1 = itemgetter(1)

class Controller(BaseController):

    def index(self):
        self.template = 'index.phtml'

        # top rated
        top_rated = Rating.top_rated(self.session, limit=6)
        self.view['top_rated'] = top_rated

        # last rated
        last_rated = self.view['last_rated']
        shuffle(last_rated)
        last_rated[5:] = []
        ids = map(itemgetter1, self.view['last_rated'])
        movies = self.session.query(Movie).filter(Movie.id.in_(ids)).all()
        movies = dict((m.id, m)
                      for m in movies)
        self.view['movies'] = movies

        # recent users
        self.view['recent_users'] = User.recent(self.session, limit=8)

        # recent ratings
        already_shown = ids
        already_shown.extend(set(m.id for m, _ in top_rated))
        recent = self.session.query(Rating)\
                     .options(joinedload(Rating.movie))\
                     .options(joinedload(Rating.user))\
                     .filter(not_(Rating.movie_id.in_(already_shown)))\
                     .order_by(Rating.rated).limit(20).all()
        shuffle(recent)
        recent[10:] = []
        self.view['recent_ratings'] = recent


    def notfound(self):
        return BaseController.not_found(self, template = 'error/404.phtml')
