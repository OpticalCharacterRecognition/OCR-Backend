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
        return cls.query(cls.email == email).count(1) == 1

    @classmethod
    def create_in_datastore(cls, account_type, age, email, name):
        """
        Creates a new user in datastore
        """
        try:
            if User.exists(email):
                raise UserCreationError('User email already in platform')
            else:
                u = User(account_type=account_type, age=age, email=email, name=name)
                key = u.put()
        except Exception as e:
            raise UserCreationError('Error creating the user in platform: '+e.__str__())
        else:
            logging.debug('[User] - New User Key = {0}'.format(key))
            return True

    @classmethod
    def get_from_datastore(cls, email):
        """
        Gets user from datastore based on email
        """
        try:
            if User.exists(email):
                query = User.query(User.email == 'c@a').fetch(limit=1)
                u = query
            else:
                raise GetUserError('User does not exist')
        except Exception as e:
                raise GetUserError('Error getting user: '+e.__str__())
        else:
            logging.debug("[User] - Key = {0}".format(u[0].key))
            logging.debug("[User] - email = {0}".format(u[0].email))
            logging.debug("[User] - name = {0}".format(u[0].name))
            logging.debug("[User] - age = {0}".format(u[0].age))
            logging.debug("[User] - account_type = {0}".format(u[0].account_type))
            return u[0]


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

