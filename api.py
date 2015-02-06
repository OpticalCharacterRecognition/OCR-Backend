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
        logging.debug("[FrontEnd - new_user()] - email = {0}".format(request.email))
        logging.debug("[FrontEnd - new_user()] - name = {0}".format(request.name))
        logging.debug("[FrontEnd - new_user()] - age = {0}".format(request.age))
        logging.debug("[FrontEnd - new_user()] - account_type = {0}".format(request.account_type))
        resp = messages.CreateUserResponse()
        try:
            User.create_in_datastore(email=request.email,
                                     name=request.name,
                                     age=request.age,
                                     account_type=request.account_type)
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
        logging.debug("[FrontEnd - get_user()] - email = {0}".format(request.email))
        resp = messages.GetUserResponse()
        try:
            retrieved_user = User.get_from_datastore(email=request.email)
            resp.email = retrieved_user.email
            resp.name = retrieved_user.name
            resp.age = retrieved_user.age
            resp.account_type = retrieved_user.account_type
        except GetUserError as e:
            resp.ok = False
            resp.error = e.value
        except Exception as e:
            resp.ok = False
            resp.error = e.message

        else:
            resp.ok = True
        return resp


app = endpoints.api_server([OCRBackendApi])