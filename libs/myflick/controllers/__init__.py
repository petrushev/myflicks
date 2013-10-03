import json
from os import environ
from hashlib import md5
from base64 import b64encode, b64decode

from werkzeug.utils import redirect as http_redirect
from werkzeug.wrappers import Response

from sqlalchemy.orm.exc import NoResultFound

from myflick.db.models import User, Rating

COOKIE_SALT = 'flickcook'

def prepare_cookie(service, service_user_id):
    hash_ = service + service_user_id + COOKIE_SALT
    hash_ = md5(hash_).hexdigest()
    data = json.dumps({'service': service,
                       'service_user_id': service_user_id,
                       'hash': hash_})
    data = b64encode(data)
    return data

def parse_cookie(cookie):
    data = b64decode(cookie)
    try:
        data = json.loads(data)
    except ValueError:
        return None

    if 'service' not in data or 'service_user_id' not in data or 'hash' not in data:
        return None

    hash_in_data = data['hash']
    hash_ = data['service'] + data['service_user_id'] + COOKIE_SALT
    hash_ = md5(hash_).hexdigest()

    if hash_ != hash_in_data:
        return None

    return data['service'], data['service_user_id']

class BaseController(object):
    """Extendable base controller"""

    def __init__(self, request, tpl_env, appspace, action_name, **kwargs):

        self._request = request
        self.appspace = appspace
        self.action_name = action_name
        self.tpl_env = tpl_env

        # set blank template and empty view obj
        self.template = None
        self.view = {'path': request.path,
                     'get': request.args,
                     'cdn': environ['CDN_PREFIX']}

        # set the controller log
        self._log = ""

        # init response obj
        self._response = Response('', content_type = "text/html; charset=UTF-8")
        self._response.status_code = 200

        # rest of the initializers (db, session, etc)
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        self.view['last_rated'] = Rating.last_rated(self.session, limit=5)

        # check user data
        self.user = None
        if 'logged' in self.request.cookies:
            parsed_cookie = parse_cookie(self.request.cookies['logged'])
            if parsed_cookie is None:
                self.response.delete_cookie('logged')
            else:
                service, service_user_id = parsed_cookie
                self.user = User.load(self.session, service = service, nickname = service_user_id)

        self.view['user'] = self.user

    @property
    def request(self):
        return self._request

    @property
    def log(self):
        return self._log

    def init(self):
        """Executes before the action"""
        pass

    def exit(self):
        """Executes after the action"""
        pass

    @property
    def response(self):
        """Returns the response, if given a template,
        renders a view and puts it as data of the response"""
        if self.template is not None:
            self._response.data = self.tpl_env.get_template(self.template).render(**self.view)
            self._response.content_length = len(self._response.data)
        return self._response

    def add_log(self, text):
        self._log = self._log + text + "\n"

    def redirect(self, uri, permanent = False):
        code = 301 if permanent else 302
        self.template = None
        self._response = http_redirect(uri, code)

    def not_found(self, template = None):
        self.template = template
        self._response.status_code = 404

    def method_not_allowed(self, template = None):
        self.template = template
        self._response.status_code = 405

    def not_authorized(self, template = None):
        self.template = template
        self._response.status_code = 401

    def bad_request(self, template = None):
        self.template = template
        self._response.status_code = 400

    def return_json(self, data):
        self.template = None
        self._response.data = json.dumps(data)
        self._response.content_length = len(self._response.data)
        self._response.content_type = "application/json"

class UserController(BaseController):

    def init(self):
        if self.user is None:
            self.action_name = ''
            self.not_authorized('error/401.phtml')
