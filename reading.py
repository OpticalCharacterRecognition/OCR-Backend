"""
Defines the datastore and all interfaces needed for a Reading in the OCR platform
"""
__author__ = 'Cesar'

import logging
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from meter import Meter
from datetime import datetime


class Reading(ndb.Model):
    """
    Represents a reading of a meter in the platform.

        - meter: The meter associated with this reading
        - measure: m3 read by OCR
    """

    date = ndb.DateTimeProperty()
    meter = ndb.KeyProperty(kind=Meter)
    measure = ndb.IntegerProperty()

    @classmethod
    def get_all_from_datastore(cls, account_number):
        """
        Gets all readings from datastore based on:
        Args:
            account_number: (String)
        Returns:
            A List with all the readings that match the criteria
        """
        try:
            meter = Meter.get_from_datastore(account_number)
            query_response = Reading.query(Reading.meter == meter.key).fetch()
            if query_response:
                resp = []
                for r in query_response:
                    resp.append(r)
            else:
                raise GetReadingError('No Readings found under specified criteria: Account Number: {0}'
                                      .format(account_number))
        except Exception as e:
            raise GetReadingError('Error getting Reading: '+e.__str__())
        else:
            for r in resp:
                logging.debug("[Reading] = {0}".format(r))
            return resp

    @classmethod
    def save_to_datastore(cls, meter, measure):
        """
        Saves a Reading as a new entity on the datastore.
        Args:
            account_number: (String) account_number from request

        Returns:
            True if creation successful, exception otherwise

        """
        try:
            m = Meter.get_from_datastore(meter)
            r = Reading(date=datetime.now(),
                        meter=m.key,
                        measure=measure)
            key = r.put()
        except Exception as e:
            logging.exception("[Reading] - "+e.message)
            raise ReadingCreationError('Error creating the reading in datastore: '+e.__str__())
        else:
            logging.debug('[Reading] - New Reading, Measure = {0} Key = {1}'.format(measure, key))
            # Update balance in datastore
            current_balance = Meter.get_balance(meter)
            new_balance = current_balance + measure
            # FIXME handle exception from Meter class
            Meter.set_balance(meter, new_balance)
            logging.debug('[Reading] - New Balance: {0} = (Old Balance = {1}) + (Reading = {2})'
                          .format(new_balance, current_balance, measure))
            return True

    @classmethod
    def save_history_to_datastore(cls, meter_key, measurements):
        """
        Saves historic Readings as a new entities on the datastore.
        :param
            account_number: (String) account_number
            measurements: (Dictionary) from jmas_api

        :return
            True if creation successful, exception otherwise

        """
        try:
            for measure in measurements:
                r = Reading(date=measure,
                            meter=meter_key,
                            measure=measurements[measure])
                key = r.put()
        except Exception as e:
            logging.exception("[Reading] - "+e.message)
            raise ReadingCreationError('Error creating the reading in datastore: '+e.__str__())
        else:
            logging.debug('[Reading] - Historical Measurements successfully stored')
            return True

    @classmethod
    def set_image_processing_task(cls, meter, image_name):
        """
        Creates a new pull task to await processing by a OCR-Worker. The task properties are as follows:
            name: Process--[image_name]
            payload: [account_number]--[image_name]
        Args:
            account_number: (String) account_number from request
            image_name: (String) name of the image in CloudStorage
        Returns:
            True if task creation successful, exception otherwise

        """
        try:
            q = taskqueue.Queue('image-processing-queue')
            tasks = [taskqueue.Task(name='Process--{0}'.format(image_name),
                                    payload='{0}--{1}'.format(meter, image_name),
                                    method='PULL')]
            q.add(tasks)
        except Exception as e:
            raise TaskCreationError('Error creating OCR-Worker task:'+e.__str__())
        else:
            logging.debug('[Reading] - OCR-Worker task successfully created')
            return True


class ReadingCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Reading] - Reading Error:'+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class NotificationCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Reading] - Notification Error:'+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class TaskCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Reading] - Task Error:'+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class GetReadingError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Reading] - Get Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)
