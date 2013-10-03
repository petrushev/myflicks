from myflick.controllers import BaseController
from myflick.db.models import Movie
from sqlalchemy.orm.exc import NoResultFound

class Controller(BaseController):

    def user_rate(self):
        if self.user is None:
            return self.not_authorized('error/401.phtml')

        try:
            movie_id = int(self.request.form['movie_id'])
            rating = int(self.request.form['rating'])
        except (KeyError, ValueError):
            return self.bad_request('error/400.phtml')

        try:
            movie = Movie.load(self.session, id=movie_id)
        except NoResultFound:
            return self.not_found('error/404.phtml')

        if rating == 0:
            self.user.drop_rating(movie)
        else:
            self.user.set_rating(movie, rating)
        self.template = None
