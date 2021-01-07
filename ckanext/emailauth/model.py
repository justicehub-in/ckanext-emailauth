import logging

import sqlalchemy.orm as orm
from sqlalchemy.schema import Table, Column, ForeignKey
import sqlalchemy.types as types

import ckan.model as model
from ckan.model.domain_object import DomainObject

from ckan.model import meta, extension
import ckan.model.types as _types

mapper = orm.mapper
log = logging.getLogger(__name__)

USER_REGISTERED_STATUS = 'user_registered'
USER_VALIDATED_STATUS = 'user_validated'
USER_DETAILS_STATUS = 'details'
USER_FIRST_LOGIN_STATUS = 'first_login'
USER_FOLLOWS_STATUS = 'follows'
USER_ORG_STATUS = 'org'
USER_FRIENDS_STATUS = 'friends'
PLATFORM_LOGIN = 'platform_login'
PLATFORM_REGISTER = 'platform_register'
PLATFORM_RESET = 'platform_reset'
PLATFORM_LOGOUT = 'platform_logout'
PLATFORM_FIRST_NAME = "platform_first_name"
PLATFORM_LAST_NAME = "platform_last_name"
MESSAGE_DATASET_SUCCESS = "message_dataset_success"


USER_DETAILS = [
    PLATFORM_FIRST_NAME,
    PLATFORM_LAST_NAME
]

USER_STATUSES = [
    USER_REGISTERED_STATUS,
    USER_VALIDATED_STATUS,
    USER_DETAILS_STATUS,
    USER_FIRST_LOGIN_STATUS,
    USER_FOLLOWS_STATUS,
    USER_ORG_STATUS,
    USER_FRIENDS_STATUS
]

validation_token_table = None


class ValidationToken(DomainObject):
    """
    Tokens for validating email addresses upon user creation
    """

    def __init__(self, user_id, token, valid):
        self.user_id = user_id
        self.token = token
        self.valid = valid

    @classmethod
    def get(self, user_id):
        query = meta.Session.query(ValidationToken)
        return query.filter_by(user_id=user_id).first()

    @classmethod
    def get_by_token(self, token):
        query = meta.Session.query(ValidationToken)
        return query.filter_by(token=token).first()

    @classmethod
    def check_existence(self):
        return validation_token_table.exists()


def define_validation_token_table():
    global validation_token_table
    validation_token_table = Table('validation_tokens', meta.metadata,
                               Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
                               Column('user_id', types.UnicodeText, ForeignKey('user.id'), unique=True),
                               Column('token', types.UnicodeText),
                               Column('valid', types.Boolean)
                               )

    mapper(ValidationToken, validation_token_table, extension=[extension.PluginMapperExtension(), ])


def setup():
    """
    Create our tables!
    """
    if validation_token_table is None:
        define_validation_token_table()
        log.debug('Validation tokens table defined in memory')

    if model.user_table.exists() and not validation_token_table.exists():
        validation_token_table.create()
        log.debug('Validation tokens table created')


def delete_tables():
    """
    Delete data from some extra tables to prevent IntegrityError between tests.
    """

    if validation_token_table.exists():
        validation_token_table.delete()
        log.debug('Validation Token table deleted')
