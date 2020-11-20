import hashlib
import json
import ckan.logic as logic
import ckanext.emailauth.model as user_model
import ckanext.emailauth.user_extra_model as user_extra_model

_check_access = logic.check_access


def token_create(context, user):
    _check_access('user_create', context, None)
    model = context['model']
    token = hashlib.md5()
    token.update(user['email'] + user['name'])
    token_obj = user_model.ValidationToken(user_id=user['id'], token=token.hexdigest(), valid=False)
    model.Session.add(token_obj)
    model.Session.commit()
    return token_obj.as_dict()


def error_message(error_summary):
    return json.dumps({'success': False, 'error': {'message': error_summary}})


def user_extra_create(context, data_dict):
    """
    Creates an  user extra in database
    :param context:
    :param data_dict: contains 'user_id' and a list 'extras' with pairs (key,value) to be added in db
    :return: list of user_extra objects added in db
    """
    result = []
    model = context['model']
    _check_access('user_extra_create', context, data_dict)
    for extra in data_dict['extras']:
        user_extra = user_extra_model.UserExtra(user_id=data_dict['user_id'], key=extra['key'], value=extra['value'])
        model.Session.add(user_extra)
        model.Session.commit()
        result.append(user_extra.as_dict())
    return result
