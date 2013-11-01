import sys
from os.path import dirname
from os import environ
from os.path import join as pathjoin

from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException
from werkzeug import url_quote

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.bccache import FileSystemBytecodeCache

try:
    import psycopg2
except ImportError:
    from psycopg2ct import compat
    compat.register()
    import psycopg2

from myflick.routes import url_map
from myflick.db.mappers import Session

project_path = dirname(dirname(dirname(__file__)))

# set up template environment
templates = pathjoin(project_path, 'templates')
template_cache = environ['OPENSHIFT_DATA_DIR']+'template_cache'
tpl_env = Environment(loader = FileSystemLoader(templates),
                      bytecode_cache = FileSystemBytecodeCache(template_cache),
                      auto_reload = int(environ['TEMPLATES_AUTORELOAD']))
tpl_env.globals.update({'url_quote': url_quote})

appspace = {}
controllers_path = 'myflick.controllers.'
url_bind = url_map.bind_to_environ

def dispatch(urls):
    """Returns controller class, action name and args given match on the rules"""
    try:
        endpoint, args = urls.match()
    except HTTPException, exc:
        sys.stderr.write('Routing error:\n    %s\n' % str(exc))
        endpoint, args = 'index|notfound', {}

    controller_name, action_name = endpoint.split('|')

    __import__(controllers_path + controller_name)
    controller_module = sys.modules[controllers_path + controller_name]
    controller_class = controller_module.Controller

    return controller_class, action_name, args


def application(environ, start_response):
    urls = url_bind(environ)

    controller_class, action_name, args = dispatch(urls)

    session = Session()

    controller = controller_class(Request(environ), tpl_env, appspace, action_name,
                                  session = session)

    controller.init()

    action = getattr(controller, controller.action_name, None)
    if action is not None:
        action(**args)
    else:
        sys.stderr.write('Routing error: action `%s` not found in %s\n' % (controller.action_name, repr(controller)))

    controller.exit()

    response = controller.response

    session.commit()

    return response(environ, start_response)
