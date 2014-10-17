from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs
from genesis.plugins.users.backend import UsersBackend

import nginx
import os


class Gollum(Plugin):
    implements(apis.webapps.IWebapp)

    addtoblock = [
        nginx.Location('/',
            nginx.Key('proxy_pass', 'http://127.0.0.1:4567'),
            nginx.Key('proxy_set_header', 'X-Real-IP $remote_addr'),
            nginx.Key('proxy_set_header', 'Host $host'),
            nginx.Key('proxy_buffering', 'off')
            )
        ]
    
    def pre_install(self, name, vars):
		rubyctl = apis.langassist(self.app).get_interface('Ruby')
		rubyctl.install_gem('gollum', 'redcarpet', 'wikicloth')

    def post_install(self, name, path, vars, dbinfo={}):
        users = UsersBackend(self.app)
        users.add_user('gollum')

        s = self.app.get_backend(apis.services.IServiceManager)
        s.edit('gollum',
            {
                'stype': 'program',
                'directory': path,
                'user': 'gollum',
                'command': 'gollum',
                'autostart': 'true',
                'autorestart': 'true',
                'stdout_logfile': '/var/log/gollum.log',
                'stderr_logfile': '/var/log/gollum.log'
            }
        )
        s.enable('gollum', 'supervisor')

        shell("chown gollum %s" % path)
        shell("GIT_DIR=%s git init" % os.path.join(path, ".git"))

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        users = UsersBackend(self.app)
        users.del_user('gollum')
        s = self.app.get_backend(apis.services.IServiceManager)
        s.delete('gollum', 'supervisor')

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass
