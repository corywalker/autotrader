import site
site.addsitedir('/root/.virtualenvs/autotrader/lib/python2.6/site-packages')

import os, sys
import django.core.handlers.wsgi

sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = django.core.handlers.wsgi.WSGIHandler()
