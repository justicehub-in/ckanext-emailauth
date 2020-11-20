import logging

import ckan.logic as logic
import ckan.logic.action.get as user_get
import ckanext.emailauth.user_extra_model as user_extra_model
from ckan.model.user import User

log = logging.getLogger(__name__)
NotFound = logic.NotFound


@logic.side_effect_free
def user_show(context, data_dict):
    user_dict = user_get.user_show(context, data_dict)
    # TODO: Ability to add custom user_dict values here for user show
    return user_dict


@logic.side_effect_free
def user_email_show(context, data_dict):
    user_dict = User.by_email(data_dict['id'])
    if len(user_dict) >= 1:
        return user_dict[0].name
    else:
        raise NotFound


@logic.side_effect_free
def user_extra_show(context, data_dict):
    """
    Retrieves user extra list based on 'user_id'
    :param context:
    :param data_dict: contains the user_id
    :return: list of user extra filtered by user_id
    """
    user_id = data_dict.get('user_id')
    user_extra_list = user_extra_model.UserExtra.get_by_user(user_id=user_id)
    if user_extra_list is None:
        raise NotFound
    user_extra_dict_list = [ue.as_dict() for ue in user_extra_list]

    return user_extra_dict_list
