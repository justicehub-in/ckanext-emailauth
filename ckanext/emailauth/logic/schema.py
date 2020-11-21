from ckan.logic.schema import validator_args


@validator_args
def register_user_schema(not_empty, user_name_validator, user_email_validator, user_password_validator,
                         user_password_not_empty, ignore_missing):

    schema = {
        'name': [not_empty, user_name_validator, unicode],
        'email': [not_empty, user_email_validator, unicode],
        'password': [user_password_validator, user_password_not_empty, ignore_missing, unicode],
    }
    return schema
