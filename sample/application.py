from __future__ import absolute_import
import crazyhorse.application.wsgi
from myapp.application import MyApp
application = crazyhorse.application.wsgi.Application(MyApp());