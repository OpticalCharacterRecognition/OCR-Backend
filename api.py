"""
Defines all methods needed for the API. Implemented using Google Cloud Endpoints.
"""
__author__ = 'Cesar'

import endpoints
from protorpc import remote
import logging
import messages
from user import User, UserCreationError, GetUserError
from meter import Meter, MeterCreationError, GetMeterError
from reading import Reading, ReadingCreationError

package = 'OCR'


@endpoints.api(name='backend', version='v1')
class OCRBackendApi(remote.Service):
    """
    OCR Backend Services
    """

    """
    USER
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

    """
    METER
    """
    @endpoints.method(messages.CreateMeter,
                      messages.CreateMeterResponse,
                      http_method='POST',
                      name='meter.create',
                      path='meter/create')
    def new_meter(self, request):
        """
        Generates a new meter in the platform, if the account number is already in use returns an error
        """
        logging.debug("[FrontEnd - new_meter()] - Account Number = {0}".format(request.account_number))
        logging.debug("[FrontEnd - new_meter()] - Balance = {0}".format(request.balance))
        logging.debug("[FrontEnd - new_meter()] - Model = {0}".format(request.model))
        resp = messages.CreateMeterResponse()
        try:
            Meter.create_in_datastore(account_number=request.account_number,
                                      balance=request.balance,
                                      model=request.model)
        except MeterCreationError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.GetMeter,
                      messages.GetMeterResponse,
                      http_method='POST',
                      name='meter.get',
                      path='meter/get')
    def get_meter(self, request):
        """
        Gets a meter information based on it's account_number
        """
        logging.debug("[FrontEnd - get_meter()] - account_number = {0}".format(request.account_number))
        resp = messages.GetMeterResponse()
        try:
            retrieved_meter = Meter.get_from_datastore(account_number=request.account_number)
            resp.account_number = retrieved_meter.account_number
            resp.balance = retrieved_meter.balance
            resp.model = retrieved_meter.model
        except GetMeterError as e:
            resp.ok = False
            resp.error = e.value
        except Exception as e:
            resp.ok = False
            resp.error = e.message

        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.AssignMeterToUser,
                      messages.AssignMeterToUserResponse,
                      http_method='POST',
                      name='meter.assign_to_user',
                      path='meter/assign_to_user')
    def assign_meter_to_user(self, request):
        """
        Assigns a meter to a user (email)
        """
        logging.debug("[FrontEnd - assign_meter_to_user()] - account_number = {0}".format(request.account_number))
        logging.debug("[FrontEnd - assign_meter_to_user()] - email = {0}".format(request.email))
        resp = messages.AssignMeterToUserResponse()
        try:
            if Meter.assign_to_user(email=request.email, account_number=request.account_number):
                resp.ok = True
            else:
                resp.ok = False
                resp.error = 'Meter could not be assigned to user!'
        except GetUserError as e:
            resp.ok = False
            resp.error = e.value
        except GetMeterError as e:
            resp.ok = False
            resp.error = e.value
        except Exception as e:
            resp.ok = False
            resp.error = e.message
        return resp

    """
    READING
    """
    @endpoints.method(messages.NewReading,
                      messages.NewReadingResponse,
                      http_method='POST',
                      name='reading.new',
                      path='reading/new')
    def new_reading(self, request):
        """
        Generates a new reading in the platform
        """
        logging.debug("[FrontEnd - new_reading()] - Account Number = {0}".format(request.account_number))
        logging.debug("[FrontEnd - new_reading()] - Reading = {0}".format(request.measure))
        resp = messages.NewReadingResponse()
        try:
            Reading.save_to_datastore(request.account_number, request.measure)
        except ReadingCreationError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp


app = endpoints.api_server([OCRBackendApi])