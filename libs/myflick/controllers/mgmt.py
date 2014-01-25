from myflick.controllers import BaseController
from myflick.app import project_path

from myflick.db.models import Movie
from sqlalchemy.sql.expression import tuple_

class Controller(BaseController):

    def update_movies(self):
        with open(project_path + '/data/movies', 'r') as movies:
            while True:
                batch = (line.decode('utf-8').strip().split('(') for _, line in zip(range(100), movies)
                         if line.strip() != '')
                batch = [('('.join(parts[:-1]).strip(), int(parts[-1][:-1]))
                         for parts in batch]

                if batch == []: break

                batch = set(batch)
                existing = self.session.query(Movie.title, Movie.year)\
                               .filter(tuple_(Movie.title, Movie.year).in_(batch)).all()
                new_ = batch.difference(existing)
                new_ = [Movie(title=title, year=year, meta={}) for title, year in new_]
                self.session.add_all(new_)
                self.session.commit()

        self.redirect('/')
