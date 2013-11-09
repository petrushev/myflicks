from os import environ
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import relationship, backref, column_property
from sqlalchemy.sql.expression import and_
#from sqlalchemy.event import listen

from myflick.db import reflect
from myflick.db import models

conn_str = environ['OPENSHIFT_POSTGRESQL_DB_URL'] + '/' + environ['DBNAME']
engine = create_engine(conn_str)

## The commented lines provide hook for `connection_start` event
## Useful for patching custom composite types onto psycopg
#def connection_start_hook(dbapi_con, connection_record):
#    pass

#listen(engine, 'connect', connection_start_hook)

mappers, tables, Session = reflect(engine, models)

mappers['Rating'].add_properties({
    'movie': relationship(models.Movie,
                          backref=backref('ratings', order_by=models.Rating.rated.desc())),
    'user': relationship(models.User,
                         backref=backref('ratings', order_by=models.Rating.rated.desc()))})

mappers['User'].add_properties({
    'watchlist': relationship(models.Movie,
                              secondary=tables['watchlist'],
                              collection_class=set)})
