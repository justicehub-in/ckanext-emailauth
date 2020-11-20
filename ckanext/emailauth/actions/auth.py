import logging

import ckan.logic as logic
import ckan.logic.auth.update as core_auth_update
from ckan.common import _

from ckanext.emailauth.helpers.reset_password import ResetKeyHelper

log = logging.getLogger(__name__)


def user_extra_create(context, data_dict):
    """
    A user with access to its own metadata
    """
    success = False

    user_obj = context.get('auth_user_obj') or context.get('user_obj')
    if user_obj and user_obj.id == data_dict.get('user_id', ''):
        success = True

    if success:
        return {
            'success': True
        }
    else:
        return {
            'success': False,
            'msg': _('Not authorized to perform this request')
        }


def user_extra_update(context, data_dict):

    return user_extra_create(context, data_dict)


def user_extra_show(context, data_dict):

    return user_extra_create(context, data_dict)


@logic.auth_allow_anonymous_access
def user_update(context, data_dict):
    if data_dict.get('reset_key'):
        reset_key_helper = ResetKeyHelper(data_dict.get('reset_key'))
        if not reset_key_helper.contains_expiration_time():
            return {'success': False, 'msg': _("Reset key has wrong format")}
        elif reset_key_helper.is_expired():
            return {'success': False, 'msg': _("Reset key no longer valid")}

    return core_auth_update.user_update(context, data_dict)
