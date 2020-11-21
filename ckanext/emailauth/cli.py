import logging
import ckanext.emailauth.model as umodel
import ckanext.emailauth.user_extra_model as uxmodel
import click


log = logging.getLogger(__name__)


@click.group()
def user_validation():
    """
    Perform commands to set up user_validation table
    """


@user_validation.command(
    u'initdb',
    short_help=u'Initialize user_validation table'
)
def initdb():
    umodel.setup()
    print("Successfully Created")


@user_validation.command(
    u'cleandb',
    short_help=u'Delete user_validation table'
)
def cleandb():
    umodel.delete_tables()
    print("Successfully Deleted")


@click.group()
def user_extra():
    """
    Perform commands to set up user_extra table
    """


@user_extra.command(
    u'initdb',
    short_help=u'Initialize user_validation table'
)
def initdb():
    uxmodel.create_table()
    print("Successfully Created")


@user_extra.command(
    u'cleandb',
    short_help=u'Delete user_extra table'
)
def cleandb():
    uxmodel.delete_table()
    print("Successfully Deleted")


@user_extra.command(
    u'dropdb',
    short_help=u'Drop user_extra table'
)
def dropdb():
    uxmodel.drop_table()
    print("Successfully Dropped")
