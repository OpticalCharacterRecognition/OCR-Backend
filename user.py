"""
Defines the datastore and all interfaces needed for a User in the OCR platform
"""
__author__ = 'Cesar'


import logging
from google.appengine.ext import ndb


class User(ndb.Model):
    """
    Represents a user of the platform.

        - account_type: Authentication used to validate the User.
    """

    created = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty()
    name = ndb.StringProperty()
    age = ndb.IntegerProperty()
    account_type = ndb.StringProperty(choices=['Facebook', 'G+'])

    @classmethod
    def exists(cls, email):
        """
        Checks the datastore to find if the user (email) is already on it.

        Args:
            email: (String) email from request

        Returns:
            True if email exist False otherwise
        """
        return User.query(User.email == email).count(1) == 1

    @classmethod
    def get_data(cls, email):
        """
        Gets user data form the datastore.

        Args:
            email: (String) email from request

        Returns:
            user data as dict
        """
        return User.query(User.email == email).fetch(1)

    def __init__(self, email, name='', age=0, account_type='', **kwds):
        """
        Creates new user
        """
        super(User, self).__init__(**kwds)

        self.email = email
        self.name = name
        self.age = age
        self.account_type = account_type

    def create_in_datastore(self):
        """
        Creates a new user in datastore
        """
        try:
            if self.exists(self.email):
                raise UserCreationError('User email already in platform')
            else:
                u = self.__init__(email=self.email,
                                  name=self.name,
                                  age=self.age,
                                  account_type=self.account_type)
                key = u.put()
        except Exception as e:
            raise UserCreationError('Error creating the user in platform: '+e.message)
        else:
            logging.debug('[User] - New User Key = {0}'.format(key))
            return True

    def get(self):
        """
        Gets user from datastore based on email
        """
        if self.exists(self.email):
            logging.debug("[User] - Key = {0}".format(u[0].key))
            u = self.get_data(self.email)
            logging.debug("[User] - email = {0}".format(u[0].email))
            self.name = u[0].name
            logging.debug("[User] - name = {0}".format(u[0].name))
            self.age = u[0].age
            logging.debug("[User] - age = {0}".format(u[0].age))
            self.account_type = u[0].account_type
            logging.debug("[User] - account_type = {0}".format(u[0].account_type))
        else:
            raise GetUserError('User does not exist')


class UserCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[User] - '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class GetUserError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

