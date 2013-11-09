My Flicks
=========

Platform for movie recommendations and ranking

Staging version is on `openshift <http://movie-words.rhcloud.com/>`_.


Requirements
------------

* python==2.7
* postgresql>=9.2
* psycopg2
* SQLAlchemy
* Werkzeug
* Jinja2
* requests
* oauth2

Installation
------------

#. Fetch the repository
#. Create data folder
#. Create database and run ``db/snapshot.schema.sql``
#. Start static content server for path ``wsgi/static``
#. (optional) Register applications on google console, facebook and twitter, for consumer-key purposes
#. Fill the ``environ`` values in ``libs/run.py``
