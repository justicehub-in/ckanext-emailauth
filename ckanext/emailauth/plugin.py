import ckanext.emailauth.actions.create as create
import ckanext.emailauth.actions.get as get
import ckanext.emailauth.actions.update as update
import ckanext.emailauth.actions.auth as auth
import ckanext.emailauth.logic.register_auth as authorize
import ckanext.emailauth.logic.validators as validators
import ckanext.emailauth.model as users_model
import ckanext.emailauth.user_extra_model as user_extra_model
from ckanext.emailauth import blueprint
from ckanext.emailauth.settings import BLUEPRINT

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class EmailAuthPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IValidators)
    if plugins.toolkit.check_ckan_version(min_version='2.9.0'):
        print("CKAN Version 2.9+")
        plugins.implements(plugins.IBlueprint)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')

    def get_helpers(self):
        return {}

    def is_fallback(self):
        return False

    def get_blueprint(self):
        return blueprint.emailauth

    def before_map(self, map):
        for action in BLUEPRINT['actions']:
            map.connect(action['url'],
                        controller=BLUEPRINT['controller'],
                        action=action['name'])
        return map

    def after_map(self, map):
        return map

    def get_actions(self):
        return {
            'token_create': create.token_create,
            'token_update': update.token_update,
            'send_reset_link': update.send_reset_link,
            'user_extra_create': create.user_extra_create,
            'user_extra_show': get.user_extra_show,
            'user_extra_update': update.user_extra_update,
            'user_email_show': get.user_email_show
        }

    def get_auth_functions(self):
        return {
            'user_can_register': authorize.user_can_register,
            'user_can_validate': authorize.user_can_validate,
            'user_update': auth.user_update,
            'user_extra_create': auth.user_extra_create,
            'user_extra_update': auth.user_extra_update,
            'user_extra_show': auth.user_extra_show
        }

    def configure(self, config):
        users_model.setup()
        user_extra_model.setup()

    def get_validators(self):
        return {
            u'user_email_validator': validators.user_email_validator,
            u'user_name_validator': validators.user_name_validator
        }
