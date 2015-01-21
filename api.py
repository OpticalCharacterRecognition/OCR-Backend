"""
Defines all methods needed for the API. Implemented using Google Cloud Endpoints.
"""
__author__ = 'Cesar'

import endpoints
from protorpc import remote
import logging
import messages
from user import User, UserCreationError, GetUserError

package = 'OCR'


@endpoints.api(name='backend', version='v1')
class OCRBackendApi(remote.Service):
    """
    OCR Backend Services
    """

    @endpoints.method(messages.CreateUser,
                      messages.CreateUserResponse,
                      http_method='POST',
                      name='user.create',
                      path='user/create')
    def new_user(self, request):
        """
        Generates a new user in the platform, if the email is already in use returns an error
        """
        logging.debug("[FrontEnd] - email = {0}".format(request.email))
        logging.debug("[FrontEnd] - name = {0}".format(request.name))
        logging.debug("[FrontEnd] - age = {0}".format(request.age))
        logging.debug("[FrontEnd] - account_type = {0}".format(request.account_type))
        resp = messages.CreateUserResponse()
        try:
            u = User(email=request.email,
                     name=request.name,
                     age=request.age,
                     account_type=request.account_type)
            u.create_in_datastore()
        except UserCreationError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.GetUser,
                      messages.GetUserResponse,
                      http_method='POST',
                      name='user.get',
                      path='user/get')
    def get_user(self, request):
        """
        Gets a user information based on it's email address
        """
        resp = messages.GetUserResponse()
        u = User(email=request.email)
        try:
            retrieved_user = u.get()
            resp.email = retrieved_user.email
            resp.imei = retrieved_user.imei
            resp.name = retrieved_user.name
            resp.age = retrieved_user.age
            resp.balance = retrieved_user.balance
            resp.rank = retrieved_user.rank
        except GetUserError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp
