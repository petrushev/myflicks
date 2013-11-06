from operator import itemgetter

from myflick.controllers import BaseController
from myflick.db.models import Rating, Movie, User

from sqlalchemy.sql.expression import func

itemgetter0 = itemgetter(0)

class Controller(BaseController):

    def show(self, fullname, crew):

        self.view['fullname'] = fullname

        sql = """
        select id from movie
        where meta is not null
              and btrim(json_select(meta, '{"%s"}')::text, '"') like :fullname """

        if crew == 'director':
            sql = sql % 'Director'

        elif crew == 'screenwriter':
            sql = sql % 'Writer'

        elif crew == 'actor':
            sql = sql % 'Actors'

        else:
            raise RuntimeError, 'routing for crew:%s not provided' % crew

        fullname_ = fullname.encode('ascii', 'replace').replace('?','%')
        movie_ids = self.session.execute(sql, {'fullname': '%'+fullname_+'%'}).fetchall()
        movie_ids = map(itemgetter0, movie_ids)

        sq = self.session.query(Rating.movie_id,
                                func.avg(Rating.rating).label('avg_rating'),
                                func.count(Rating.user_id).label('rev_cnt'))\
                 .group_by(Rating.movie_id).subquery()

        movies = self.session.query(Movie, sq.c.avg_rating, sq.c.rev_cnt)\
                    .outerjoin((sq, sq.c.movie_id==Movie.id))\
                    .filter(Movie.id.in_(movie_ids))\
                    .order_by(Movie.year.desc()).all()

        self.view.update({'crew': crew,
                          'movies': movies})
        self.template = 'cast.phtml'
