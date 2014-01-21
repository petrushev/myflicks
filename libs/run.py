from os import environ

# see doc/deployment.rst for more info
environ['CDN_PREFIX'] = 'http://myflick.cdn' # 'wsgi/static' served by external server
environ['OPENSHIFT_DATA_DIR'] = "~/myflick_data/"
environ['OPENSHIFT_POSTGRESQL_DB_URL'] = 'postgresql://myflick:myflickpass@localhost:5432'
environ['DBNAME'] = 'myflick'
environ['TEMPLATES_AUTORELOAD'] = '1'

environ['MYFLICK_G_CLIENTID'] = ""
environ['MYFLICK_G_SECRET'] = ""

environ['MYFLICK_TWITTER_CONSUMER_KEY'] = ""
environ['MYFLICK_TWITTER_CONSUMER_SECRET'] = ""

environ['MYFLICK_FB_CONSUMER_KEY'] = ""
environ['MYFLICK_FB_CONSUMER_SECRET'] = ""

from myflick.app import application

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    environ['OAUTH_BASE'] = 'http://localhost:8090/login'
    run_simple("localhost", 8090,
               application, use_reloader = True, threaded = False, processes = 1)
