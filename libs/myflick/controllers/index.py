from myflick.controllers import BaseController

class Controller(BaseController):

    def index(self):
        self.template = 'index.phtml'

    def notfound(self):
        return BaseController.not_found(self, template = 'error/404.phtml')
