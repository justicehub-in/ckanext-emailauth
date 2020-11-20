from __future__ import print_function

import ckan.plugins as p
import ckanext.emailauth.model as umodel
import ckanext.emailauth.user_extra_model as user_extra


class ValidationCommand(p.toolkit.CkanCommand):
    """
    Usage:
        paster users [initdb]
        - Creates the necessary tables in the database
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(ValidationCommand, self).__init__(name)

    def command(self):
        if not self.args or self.args[0] in ['-h', '--help', 'help'] or not len(self.args) in [1, 2]:
            print(self.usage)
            return

        cmd = self.args[0]
        self._load_config(load_site_user=False)
        if cmd == 'initdb':
            print ('Initializing Database...')
            self.initdb()
            print ('DONE Initializing Database...')
        elif cmd == 'cleandb':
            print ('Cleandb Database...')
            self.cleandb()
        else:
            print ('Error: command "{0}" not recognized'.format(cmd))
            print (self.usage)

    def initdb(self):
        """
        Create the tables defined by model
        """
        umodel.setup()

    def cleandb(self):
        """
        Delete tables defined by model
        """
        umodel.delete_tables()


class UserExtraCommand(p.toolkit.CkanCommand):
    """
    Usage:
        paster user_extra [initdb]
        Creates the table in db
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(UserExtraCommand, self).__init__(name)

    def command(self):
        if not self.args or self.args[0] in ['-h', '--help', 'help'] or not len(self.args) in [1, 2]:
            print (self.usage)
            return

        cmd = self.args[0]
        self._load_config(load_site_user=False)
        if cmd == 'initdb':
            print ('Initializing Database...')
            self.initdb()
            print ('DONE Initializing Database...')
        elif cmd == 'cleandb':
            print ('Cleandb Database...')
            self.cleandb()
        else:
            print ('Error: command "{0}" not recognized'.format(cmd))
            print (self.usage)

    def initdb(self):
        """
        Create the table defined by model
        """
        user_extra.create_table()

    def cleandb(self):
        """
        Delete information from table defined by model
        """
        user_extra.delete_table()

    def dropdb(self):
        """
        Drop table defined by model
        """
        user_extra.drop_table()
