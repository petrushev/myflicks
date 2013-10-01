from myflick.controllers import BaseController
from myflick.app import project_path

from myflick.db.models import Movie

class Controller(BaseController):

    def update_movies(self):
        with open(project_path + '/data/movies', 'r') as movies:
            while True:
                batch = [line.strip() for _, line in zip(range(100), movies)
                         if line.strip() != '']
                if batch == []: break

                batch = set(batch)
                existing = self.session.query(Movie.title).filter(Movie.title.in_(batch)).all()
                existing = [r[0] for r in existing]
                new_ = batch.difference(existing)
                new_ = [Movie(title=title, url='http://' + title) for title in new_]
                self.session.add_all(new_)
                self.session.commit()

        self.redirect('/')
