"""
Defines all methods needed for the API. Implemented using Google Cloud Endpoints.
"""

__author__ = 'Cesar'

import endpoints
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from protorpc import remote
import logging
import messages
from user import User, UserCreationError, GetUserError
from meter import Meter, MeterCreationError, GetMeterError
from reading import Reading, ReadingCreationError, GetReadingError
from reading import TaskCreationError, NotificationCreationError
from bill import Bill, BillCreationError, GetBillError, BillPaymentError
from prepay import Prepay, PrepayCreationError, GetPrepayError, PrepayPaymentError
import jmas_api
from parse_api import Push
package = 'OCR'


@endpoints.api(name='backend', version='v1', hostname='ocr-backend.appspot.com')
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
        logging.debug("[FrontEnd - new_user()] - installation_id = {0}".format(request.installation_id))
        resp = messages.CreateUserResponse()
        try:
            User.create_in_datastore(email=request.email,
                                     name=request.name,
                                     age=request.age,
                                     account_type=request.account_type,
                                     installation_id=request.installation_id)
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
            resp.installation_id = retrieved_user.installation_id
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
        resp = messages.CreateMeterResponse()
        try:
            Meter.create_in_datastore(account_number=request.account_number)
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

    @endpoints.method(messages.GetMeters,
                      messages.GetMetersResponse,
                      http_method='POST',
                      name='meter.get_all_assigned_to_user',
                      path='meter/get_all_assigned_to_user')
    def get_meters(self, request):
        """
        Gets all meters assigned to a user
        """
        logging.debug("[FrontEnd - get_meters()] - User = {0}".format(request.user))
        resp = messages.GetMetersResponse()
        try:
            meters = Meter.get_all_from_datastore(request.user)
        except GetMeterError as e:
            resp.ok = False
            resp.error = e.value
        else:
            for m in meters:
                r = messages.Meter()
                r.urlsafe_key = m.key.urlsafe()
                r.account_number = m.account_number
                r.balance = m.balance
                r.model = m.model
                resp.meters.append(r)
            resp.ok = True
        return resp

    """
    READING
    """
    @endpoints.method(messages.NewImageForProcessing,
                      messages.NewImageForProcessingResponse,
                      http_method='POST',
                      name='reading.new_image_for_processing',
                      path='reading/new_image_for_processing')
    def new_image_for_processing(self, request):
        """
        Generates a new task to process the new image received in the platform
        """
        logging.debug("[FrontEnd - new_image_for_processing()] - Account Number = {0}".format(request.account_number))
        logging.debug("[FrontEnd - new_image_for_processing()] - Image Name = {0}".format(request.image_name))
        resp = messages.NewImageForProcessingResponse()
        try:
            Reading.set_image_processing_task(queue='image-processing-queue',
                                              meter=request.account_number,
                                              image_name=request.image_name)
        except TaskCreationError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.ImageProcessingResult,
                      messages.ImageProcessingResultResponse,
                      http_method='POST',
                      name='reading.set_image_processing_result',
                      path='reading/set_image_processing_result')
    def set_image_processing_result(self, request):
        """
        Set the result of an image processing task
            request.task_name: Process--[image]
            request.task_payload: [meter]--[image]
            request.human: True, False
        """
        logging.debug("[FrontEnd - set_image_processing_result()] - Task Name = {0}".format(request.task_name))
        logging.debug("[FrontEnd - set_image_processing_result()] - Task Payload = {0}".format(request.task_payload))
        logging.debug("[FrontEnd - set_image_processing_result()] - Result = {0}".format(request.result))
        logging.debug("[FrontEnd - set_image_processing_result()] - Error = {0}".format(request.error))
        logging.debug("[FrontEnd - set_image_processing_result()] - Human = {0}".format(request.human))
        account_number, image = request.task_payload.split('--')
        resp = messages.ImageProcessingResultResponse()
        try:
            if request.human:
                # OCR performed by human hand (http://human-helper.ddns.net)
                if '' == request.error:
                    if Reading.save_to_datastore(meter=account_number, measure=request.result):
                        # Prepare Push notification
                        meter = Meter.get_from_datastore(account_number)
                        user = User.get_by_meter_key(meter.key)
                        logging.debug("[FrontEnd - set_image_processing_result()] - "
                                      "Installation_Id for notification = {0}"
                                      .format(user.installation_id))
                        # Send Push notification
                        p = Push(user.installation_id)
                        push_title = "Nueva Lectura!"
                        push_text = "Lectura Procesada. Valor: {0}".format(request.result)
                        logging.debug("[FrontEnd - set_image_processing_result()] - Text of notification = {0}"
                                      .format(push_text))

                        p.send(title=push_title, message=push_text)
                    else:
                        logging.warning('[FrontEnd - set_image_processing_result()] - Consumo Negativo')
                        # Create task to investigate negative consumption (OCR engineering)
                        Reading.set_image_processing_task(queue='negative-consumption-queue',
                                                          meter=account_number,
                                                          image_name=image)
                        # Prepare Push notification
                        meter = Meter.get_from_datastore(account_number)
                        user = User.get_by_meter_key(meter.key)
                        logging.debug("[FrontEnd - set_image_processing_result()] "
                                      "- Installation_Id for notification = {0}"
                                      .format(user.installation_id))
                        # Push notification for user to inform that the reading is wrong
                        p = Push(user.installation_id)
                        push_title = "Error en Lectura =("
                        push_text = "Lo sentimos, algo salio mal con tu lectura .." \
                                    " lo estamos revisando (consumo negativo)"
                        logging.debug("[FrontEnd - set_image_processing_result()]"
                                      " - Text of notification = {0}"
                                      .format(push_text))
                        p.send(title=push_title, message=push_text)

                else:
                    logging.warning('[FrontEnd - set_image_processing_result()] - Error in human OCR')
                    # Prepare Push notification
                    meter = Meter.get_from_datastore(account_number)
                    user = User.get_by_meter_key(meter.key)
                    logging.debug("[FrontEnd - set_image_processing_result()] -"
                                  " Installation_Id for notification = {0}"
                                  .format(user.installation_id))
                    # Push notification for user to inform that the reading is wrong
                    p = Push(user.installation_id)
                    push_title = "Resultado de Revision de Lectura"
                    push_text = request.error
                    logging.debug("[FrontEnd - set_image_processing_result()]"
                                  " - Text of notification = {0}"
                                  .format(push_text))
                    p.send(title=push_title, message=push_text)

            else:
                # OCR performed by VMX engine
                if '' == request.error:
                    if Reading.save_to_datastore(meter=account_number, measure=request.result):
                        # OCR-Worker done with task with successful result and result saved. Delete task from queue
                        q = taskqueue.Queue('image-processing-queue')
                        q.delete_tasks_by_name(str(request.task_name))
                        # Prepare Push notification
                        meter = Meter.get_from_datastore(account_number)
                        user = User.get_by_meter_key(meter.key)
                        logging.debug("[FrontEnd - set_image_processing_result()] "
                                      "- Installation_Id for notification = {0}"
                                      .format(user.installation_id))
                        # Send Push notification
                        p = Push(user.installation_id)
                        push_title = "Nueva Lectura!"
                        push_text = "Lectura Procesada. Valor: {0}".format(request.result)
                        logging.debug("[FrontEnd - set_image_processing_result()] - Text of notification = {0}"
                                      .format(push_text))

                        p.send(title=push_title, message=push_text)
                    else:
                        logging.warning('[FrontEnd - set_image_processing_result()] - Consumo Negativo')
                        # OCR-Worker done with task with successful result but we have negative consumption.
                        q = taskqueue.Queue('image-processing-queue')
                        q.delete_tasks_by_name(str(request.task_name))
                        # Create task to investigate negative consumption (OCR engineering)
                        Reading.set_image_processing_task(queue='negative-consumption-queue',
                                                          meter=account_number,
                                                          image_name=image)
                        # Prepare Push notification
                        meter = Meter.get_from_datastore(account_number)
                        user = User.get_by_meter_key(meter.key)
                        logging.debug("[FrontEnd - set_image_processing_result()] "
                                      "- Installation_Id for notification = {0}"
                                      .format(user.installation_id))
                        # Push notification for user to inform that the reading is wrong
                        p = Push(user.installation_id)
                        push_title = "Error en Lectura =("
                        push_text = "Lo sentimos, algo salio mal con tu lectura .." \
                                    " lo estamos revisando (consumo negativo)"
                        logging.debug("[FrontEnd - set_image_processing_result()]"
                                      " - Text of notification = {0}"
                                      .format(push_text))
                        p.send(title=push_title, message=push_text)
                else:
                    logging.warning('[FrontEnd - set_image_processing_result()] - Error en OCR')
                    # OCR-Worker done with task with invalid result. Delete OCR image processing task
                    q = taskqueue.Queue('image-processing-queue')
                    q.delete_tasks_by_name(str(request.task_name))
                    # Create task to help automatic OCR in recognizing numbers (OCR engineering)
                    Reading.set_image_processing_task(queue='need-help-queue',
                                                      meter=account_number,
                                                      image_name=image)
                    # Prepare Push notification
                    meter = Meter.get_from_datastore(account_number)
                    user = User.get_by_meter_key(meter.key)
                    logging.debug("[FrontEnd - set_image_processing_result()] -"
                                  " Installation_Id for notification = {0}"
                                  .format(user.installation_id))
                    # Push notification for user to inform that the reading is wrong
                    p = Push(user.installation_id)
                    push_title = "Error en Lectura =("
                    push_text = "Lo sentimos, algo salio mal con tu lectura .." \
                                " lo estamos revisando (error en OCR)"
                    logging.debug("[FrontEnd - set_image_processing_result()]"
                                  " - Text of notification = {0}"
                                  .format(push_text))
                    p.send(title=push_title, message=push_text)

        except (NotificationCreationError, ReadingCreationError) as e:
            resp.ok = False
            resp.error = e.value

        except Exception as e:
            resp.ok = False
            resp.error = 'Error deleting OCR-Worker task from queue: {0}'.format(e.__str__())
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.GetReadings,
                      messages.GetReadingsResponse,
                      http_method='POST',
                      name='reading.get',
                      path='reading/get')
    def get_readings(self, request):
        """
        Gets all readings that match the criteria.
        """
        logging.debug("[FrontEnd - get_readings()] - Account Number = {0}".format(request.account_number))
        resp = messages.GetReadingsResponse()
        try:
            readings = Reading.get_all_from_datastore(request.account_number)
        except GetReadingError as e:
            resp.ok = False
            resp.error = e.value
        else:
            for read in readings:
                r = messages.Reading()
                r.urlsafe_key = read.key.urlsafe()
                r.creation_date = read.date
                r.account_number = read.meter.get().account_number
                r.measure = read.measure
                resp.readings.append(r)
            resp.ok = True
        return resp

    """
    BILL
    """
    @endpoints.method(messages.NewBill,
                      messages.NewBillResponse,
                      http_method='POST',
                      name='bill.new',
                      path='bill/new')
    def new_bill(self, request):
        """
        Generates a new bill in the platform
        """
        logging.debug("[FrontEnd - new_bill()] - Account Number = {0}".format(request.account_number))
        resp = messages.NewBillResponse()
        try:
            Bill.save_to_datastore(request.account_number)
        except BillCreationError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.GetBills,
                      messages.GetBillsResponse,
                      http_method='POST',
                      name='bill.get',
                      path='bill/get')
    def get_bills(self, request):
        """
        Gets all bills that match the criteria.
        """
        logging.debug("[FrontEnd - get_bills()] - Account Number = {0}".format(request.account_number))
        logging.debug("[FrontEnd - get_bills()] - Status = {0}".format(request.status))
        resp = messages.GetBillsResponse()
        try:
            bills = Bill.get_all_from_datastore(request.account_number, request.status)
        except GetBillError as e:
            resp.ok = False
            resp.error = e.value
        else:
            for b in bills:
                r = messages.Bill()
                r.urlsafe_key = b.key.urlsafe()
                r.creation_date = b.date
                r.account_number = b.meter.get().account_number
                r.balance = b.balance
                r.amount = b.amount
                r.status = b.status
                resp.bills.append(r)
            resp.ok = True
        return resp

    @endpoints.method(messages.PayBill,
                      messages.PayBillResponse,
                      http_method='POST',
                      name='bill.pay',
                      path='bill/pay')
    def pay_bill(self, request):
        """
        Marks a bill as payed in the platform
        """
        logging.debug("[FrontEnd - pay_bill()] - Bill Key = {0}".format(request.bill_key))
        resp = messages.PayBillResponse()
        try:
            bill_key = ndb.Key(urlsafe=request.bill_key)
            Bill.pay(bill_key)
        except GetBillError as e:
            resp.ok = False
            resp.error = e.value
        except GetMeterError as e:
            resp.ok = False
            resp.error = e.value
        except BillPaymentError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp

    """
    PREPAY
    """
    @endpoints.method(messages.NewPrepay,
                      messages.NewPrepayResponse,
                      http_method='POST',
                      name='prepay.new',
                      path='prepay/new')
    def new_prepay(self, request):
        """
        Generates a new prepay event in the platform
        """
        logging.debug("[FrontEnd - new_prepay()] - Account Number = {0}".format(request.account_number))
        resp = messages.NewPrepayResponse()
        try:
            Prepay.save_to_datastore(request.account_number, request.m3_to_prepay)
        except PrepayCreationError as e:
            resp.ok = False
            resp.error = e.value
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.GetPrepayFactor,
                      messages.GetPrepayFactorResponse,
                      http_method='POST',
                      name='prepay.factor',
                      path='prepay/factor')
    def get_prepay_factor(self, request):
        """
        Gets the factor of a prepay taking into account the amount of m3 to prepay
        """
        logging.debug("[FrontEnd - get_prepay_factor()] - m3_to_prepay = {0}".format(request.m3_to_prepay))
        resp = messages.GetPrepayFactorResponse()
        try:
            resp.factor = jmas_api.get_prepay_conversion_factor()
            logging.debug("[FrontEnd - get_prepay_factor()] - factor = {0}".format(resp.factor))
        except Exception as e:
            resp.ok = False
            resp.error = e.__str__()
        else:
            resp.ok = True
        return resp

    @endpoints.method(messages.GetPrepays,
                      messages.GetPrepaysResponse,
                      http_method='POST',
                      name='prepay.get',
                      path='prepay/get')
    def get_prepays(self, request):
        """
        Gets all prepays events
        """
        logging.debug("[FrontEnd - get_prepays()] - Account Number = {0}".format(request.account_number))
        resp = messages.GetPrepaysResponse()
        try:
            prepays = Prepay.get_all_from_datastore(request.account_number)
        except GetPrepayError as e:
            resp.ok = False
            resp.error = e.value
        else:
            for p in prepays:
                r = messages.Prepay()
                r.urlsafe_key = p.key.urlsafe()
                r.creation_date = p.created
                r.account_number = p.meter.get().account_number
                r.balance = p.balance
                r.prepay = p.prepay
                r.amount = p.amount
                resp.prepays.append(r)
            resp.ok = True
        return resp

app = endpoints.api_server([OCRBackendApi])