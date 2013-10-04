from .base import BaseRepo
import logging
import urlparse
from ..util import _run
import re
import os

logger = logging.getLogger(__name__)

class SubversionRepo(BaseRepo):
    vcs = 'svn'

    schemes = ('svn')

    def __init__(self, arguments, *args, **kwargs):
        BaseRepo.__init__(self, arguments, *args, **kwargs)

    def obtain(self):
        self.check_destination()

        url, rev = self.get_url_rev()
        rev_options = self.get_rev_options(url, rev)

        _run([
            'svn', 'checkout', '-q', url, self['path'],
        ])

    def get_revision(self, location=None):

        if location:
            cwd = location
        else:
            cwd = self['path']

        current_rev = _run(
            ['svn', 'info', cwd],
        )
        infos = current_rev['stdout']

        _INI_RE = re.compile(r"^([^:]+):\s+(\S.*)$", re.M)

        info_list = []
        for infosplit in infos.split('\n\n'):
            info_list.append(_INI_RE.findall(infosplit))

        return int([dict(tmp) for tmp in info_list][0]['Revision'])

    def get_rev_options(self, url, rev):
        ''' from pip pip.vcs.subversion '''
        if rev:
            rev_options = ['-r', rev]
        else:
            rev_options = []

        r = urlparse.urlsplit(url)
        if hasattr(r, 'username'):
            # >= Python-2.5
            username, password = r.username, r.password
        else:
            netloc = r[1]
            if '@' in netloc:
                auth = netloc.split('@')[0]
                if ':' in auth:
                    username, password = auth.split(':', 1)
                else:
                    username, password = auth, None
            else:
                username, password = None, None

        if username:
            rev_options += ['--username', username]
        if password:
            rev_options += ['--password', password]
        return rev_options

    def update_repo(self, dest=None):
        self.check_destination()
        if os.path.isdir(os.path.join(self['path'], '.svn')):
            dest = self['path'] if not dest else dest

            url, rev = self.get_url_rev()
            _run(
                ['svn', 'update'],
                cwd=self['path']
            )
        else:
            self.obtain()
            self.update_repo()
