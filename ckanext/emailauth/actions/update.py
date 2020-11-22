from __future__ import print_function

import sys
from ckanext.emailauth.settings import PASSWORD_RESET_EXPIRY, BASE_URL

import ckan.logic as logic
import ckanext.emailauth.model as umodel
import ckanext.emailauth.user_extra_model as user_extra_model
from ckanext.emailauth.controllers.mail import Mail

import ckanext.emailauth.helpers.reset_password as reset_password


NotFound = logic.NotFound
_check_access = logic.check_access


def token_update(context, data_dict):
    token = data_dict.get('token')
    token_obj = umodel.ValidationToken.get_by_token(token=token)
    if token_obj is None:
        raise NotFound
    # Logged in user should have edit access to account token belongs to
    _check_access('user_update', context, {'id': token_obj.user_id})
    session = context["session"]
    token_obj.valid = True
    session.add(token_obj)
    session.commit()
    return token_obj.as_dict()


def send_reset_link(context, data_dict):
    from urlparse import urljoin
    import ckan.lib.helpers as h

    model = context['model']

    user = None
    reset_link = None
    user_fullname = None
    recipient_mail = None

    id = data_dict.get('id', None)
    if id:
        user = model.User.get(id)
        context['user_obj'] = user
        if user is None:
            raise NotFound

    expiration_in_hours = PASSWORD_RESET_EXPIRY
    if user:
        reset_password.create_reset_key(user, expiration_in_hours)

        recipient_mail = user.email if user.email else None
        user_fullname = user.fullname or ''
        reset_link = urljoin(BASE_URL,
                             h.url_for(controller='user', action='perform_reset', id=user.id, key=user.reset_key))

    email_data = {
        'user_fullname': user_fullname,
        'user_reset_link': reset_link,
        'expiration_in_hours': expiration_in_hours,
    }
    if recipient_mail:
        mail = Mail.new()
        mail.send(recipient_mail, 'Password Request for JusticeHub Platform',
                  email_data, snippet='email/forgot_password.html')


def user_extra_update(context, data_dict):
    """
    Update value in user_extra table
    :param context:
    :param data_dict: list of dictionary with key value as 'new_value'
    :return: new extras list
    """
    session = context['session']
    result = []
    _check_access('user_extra_update', context, data_dict)
    for ue in data_dict['extras']:
        try:
            user_extra = user_extra_model.UserExtra.get(user_id=data_dict['user_id'], key=ue['key'])
            if user_extra is None:
                raise NotFound
            user_extra.value = ue['new_value']
            session.add(user_extra)
            session.commit()
            result.append(user_extra.as_dict())
        except:
            print(sys.exc_info()[0])
    return result
