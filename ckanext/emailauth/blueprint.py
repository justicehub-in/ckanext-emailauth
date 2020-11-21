from flask import Blueprint
import ckan.plugins as plugins
from ckanext.emailauth.constants import BLUEPRINT

_version_status = plugins.toolkit.check_ckan_version(min_version='2.9.0')
emailauth = Blueprint(u'emailauth', __name__)

if _version_status:
    print("CKAN Version 2.9+")
    from ckanext.emailauth.controllers.mail_validation_controller import ValidationLogic
    emailauth_logic = ValidationLogic()

    for action in BLUEPRINT['actions']:
        emailauth.add_url_rule(
            action['url'], view_func=getattr(emailauth_logic, action['name']), methods=action['type']
        )
else:
    print("Not using Blueprint, CKAN version is not 2.9 or higher")
