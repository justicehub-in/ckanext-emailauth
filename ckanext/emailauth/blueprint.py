from flask import Blueprint
from ckanext.emailauth.settings import BLUEPRINT, IS_FLASK_REQUEST

emailauth = Blueprint(u'emailauth', __name__)

if IS_FLASK_REQUEST:
    from ckanext.emailauth.controllers.mail_validation_controller import ValidationController
    emailauth_logic = ValidationController()

    for action in BLUEPRINT['actions']:
        emailauth.add_url_rule(
            action['url'], view_func=getattr(emailauth_logic, action['name']), methods=action['type']
        )
