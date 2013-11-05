from os import environ
from sys import stderr
from json import loads

from werkzeug.urls import url_encode, url_quote, url_decode
import requests
import oauth2

from myflick.controllers import BaseController, prepare_cookie
from myflick.db.models import User

conf = {
  'g': {
    'client_id': environ['MYFLICK_G_CLIENTID'],
    'client_secret': environ['MYFLICK_G_SECRET'],
    'token_url': 'https://accounts.google.com/o/oauth2/auth',
    'access_url': 'https://accounts.google.com/o/oauth2/token'
  },
  'twitter': {
    'token_url':'https://api.twitter.com/oauth/request_token',
    'consumer_key': environ['MYFLICK_TWITTER_CONSUMER_KEY'],
    'callback_base': '/callback/twitter/',
    'consumer_secret': environ['MYFLICK_TWITTER_CONSUMER_SECRET'],
    'authenticate': 'https://api.twitter.com/oauth/authenticate',
    'authorize_url': 'https://api.twitter.com/oauth/authorize',
    'access_token': 'https://api.twitter.com/oauth/access_token'
  },
  'fb': {
    'consumer_key': environ['MYFLICK_FB_CONSUMER_KEY'],
    'consumer_secret': environ['MYFLICK_FB_CONSUMER_SECRET'],
    'callback_base': '/callback/fb/',
    'token_url': 'https://www.facebook.com/dialog/oauth/'
  }
}

oauth_base = environ['OAUTH_BASE']
oauth_secrets_path_prefix = environ['OPENSHIFT_DATA_DIR'] + '/oauth_secret_'

class Controller(BaseController):

    def g_request(self, original_url):
        conf_ = conf['g']
        query_string = url_encode({'client_id': conf_['client_id'],
                                   'response_type': 'code',
                                   'scope': 'openid email profile',
                                   'redirect_uri': oauth_base + '/callback/g',
                                   'state': original_url,
                                   'access_type': 'online'})
        # redirects to 'login with google+' page
        self.redirect(conf_['token_url'] + '?' + query_string)

    def g_callback(self):
        # parse the original url from the google+ redirect state param
        original_url = self.request.args.get('state', '')
        code = self.request.args['code']
        conf_ = conf['g']

        # authenticate the passed code
        q = requests.post(conf_['access_url'],
                          data = {'code': code,
                                 'client_id': conf_['client_id'], 'client_secret': conf_['client_secret'],
                                 'redirect_uri': oauth_base + '/callback/g',
                                 'grant_type': 'authorization_code'})

        if q.status_code != 200:
            stderr.write("Login error:\n    %s\n" % q.content)
            return self.redirect('/?msg=AUTH_ERROR')

        content = loads(q.content)
        access_token = content['access_token']
        del content

        # get userinfo
        q = requests.get('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token)
        content = loads(q.content)

        profile_id = content['id']

        # save userinfo by id
        User.save_g_data(self.session, profile_id, fullname=content['name'], email=content['email'])

        # set redirect with cookie
        self.redirect('/' + original_url)
        cookie_val = prepare_cookie('gmail', str(profile_id))
        self._response.set_cookie('logged', cookie_val)

    def logout(self, original_url):
        self.redirect('/' + original_url)
        self.response.delete_cookie('logged')


    def twitter_request(self, original_url):
        conf_ = conf['twitter']
        original_url = oauth_base + conf_['callback_base'] + url_quote(original_url)

        consumer = oauth2.Consumer(conf_['consumer_key'], conf_['consumer_secret'])
        client = oauth2.Client(consumer)

        q, content = client.request(conf_['token_url'], "POST",
                                    body = url_encode({'oauth_callback':original_url}))

        if q['status'] != "200":
            stderr.write("Login error twitter auth:\n    %s\n" % q.content)
            return self.redirect('/?msg=2')
        del q

        oauth_data = url_decode(content)
        oauth_token = oauth_data['oauth_token']
        oauth_token_secret = oauth_data['oauth_token_secret']

        del content
        del oauth_data

        f = open(oauth_secrets_path_prefix + oauth_token, 'w')
        f.write(oauth_token_secret)
        f.close()

        self.redirect(conf_['authenticate'] + "?oauth_token=" + oauth_token)

    def twitter_callback(self, original_url):
        oauth_token = self.request.args['oauth_token']

        try:
            f = open(oauth_secrets_path_prefix + oauth_token, 'r')
        except IOError, exc:
            stderr.write("Login error (token not found):\n    %s\n" % str(exc))
            return self.redirect('/?msg=2')

        oauth_token_secret = f.read()
        f.close()

        oauth_verifier = self.request.args['oauth_verifier']
        token = oauth2.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_verifier)

        conf_ = conf['twitter']
        consumer = oauth2.Consumer(conf_['consumer_key'], conf_['consumer_secret'])

        client = oauth2.Client(consumer, token)
        q, content = client.request(conf_['access_token'], method = 'POST')

        if q['status'] != "200":
            stderr.write("Login error:\n    %s\n" % q.content)
            return self.redirect('/?msg=2')

        del q
        content = url_decode(content)
        oauth_token = content['oauth_token']
        oauth_token_secret = content['oauth_token_secret']

        user_id = content['user_id']
        username = content['screen_name']
        User.save_twitter_data(self.session, user_id, fullname=username, email='')
        del content

        f = open(oauth_secrets_path_prefix + oauth_token, 'w')
        f.write(oauth_token_secret)
        f.close()

        # set redirect to callback
        original_url = '/' + original_url
        self.redirect(original_url)

        cookie_val = prepare_cookie('twitter', user_id)
        self._response.set_cookie('logged', cookie_val)

    def fb_request(self, original_url):
        conf_ = conf['fb']

        original_url = oauth_base + conf_['callback_base'] + url_quote(original_url)
        uri = conf_['token_url'] + '?' + url_encode({'client_id': conf_['consumer_key'],
                                                     'redirect_uri': original_url})
        self.redirect(uri)

    def fb_callback(self, original_url):
        if 'code' not in self.request.args:
            return self.redirect('/?msg=2')

        conf_ = conf['fb']
        code = self.request.args['code']
        callback_uri = oauth_base + conf_['callback_base'] + url_quote(original_url)
        callback = '/' + original_url

        q = requests.get('https://graph.facebook.com/oauth/access_token?' + \
                         url_encode({'client_id': conf_['consumer_key'],
                                     'redirect_uri': url_quote(callback_uri),
                                     'client_secret': conf_['consumer_secret'],
                                     'code': code}))

        if q.status_code != 200:
            return self.redirect('/?msg=2')

        content = url_decode(q.content)
        access_token = content['access_token']

        q = requests.get("https://graph.facebook.com/me?access_token=" + access_token)

        if q.status_code != 200:
            return self.redirect('/?msg=2')

        userdata = q.content
        userdata = loads(userdata)

        profile_id = userdata['id']

        # save userinfo by id
        User.save_fb_data(self.session, profile_id, userdata['name'], '')

        # set redirect with cookie
        self.redirect(callback)
        cookie_val = prepare_cookie('fb', str(profile_id))
        self._response.set_cookie('logged', cookie_val)
