import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .app import get_root
from .model import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    required_keys = [
        'tahrir.salt',
        'tahrir.pngs.uri',
    ]
    # validate the config
    for key in required_keys:
        if key not in settings:
            raise ValueError("%s required in settings." % key)

    # Make data dir if it doesn't already exist.
    if not os.path.exists(settings['tahrir.pngs.uri']):
        os.makedirs(settings['tahrir.pngs.uri'])

    # start setting things up
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    authn_policy = AuthTktAuthenticationPolicy(
        secret='verysecret',
    )
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory=get_root)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view(
        'static', 'static', cache_max_age=3600)
    config.add_static_view(
        'pngs', settings['tahrir.pngs.uri'], cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.scan()

    return config.make_wsgi_app()

