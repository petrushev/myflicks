from os import environ
from sys import stderr
import json

from werkzeug.urls import url_encode
import requests

from myflick.controllers import BaseController, prepare_cookie
from myflick.db.models import User

conf = {
  'g': {
    'client_id': environ['MYFLICK_G_CLIENTID'],
    'client_secret': environ['MYFLICK_G_SECRET'],
    'token_url': 'https://accounts.google.com/o/oauth2/auth',
    'access_url': 'https://accounts.google.com/o/oauth2/token'
  }
}

oauth_base = environ['OAUTH_BASE']

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

        content = json.loads(q.content)
        access_token = content['access_token']
        del content

        # get userinfo
        q = requests.get('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token)
        content = json.loads(q.content)

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
