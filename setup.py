from setuptools import setup

setup(name='myflick',
      version='1.0',
      description='OpenShift App for movie recommendations',
      author='Baze Petrushev',
      author_email='b.petrushev@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['psycopg2', 'Werkzeug', 'Jinja2', 'SQLAlchemy', 'oauth2']
)
