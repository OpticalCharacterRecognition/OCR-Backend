"""
Defines the datastore and all interfaces needed for a Bill in the OCR platform
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


class Error(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[User] - '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)
