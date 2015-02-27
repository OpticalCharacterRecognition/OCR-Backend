"""
Defines the datastore and all interfaces needed for a Reading in the OCR platform
"""
__author__ = 'Cesar'

import logging
from google.appengine.ext import ndb
from meter import Meter


class Reading(ndb.Model):
    """
    Represents a reading of a meter in the platform.

        - meter: The meter associated with this reading
        - measure: m3 read by OCR
    """

    created = ndb.DateTimeProperty(auto_now_add=True)
    meter = ndb.KeyProperty(kind=Meter)
    measure = ndb.IntegerProperty()

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
            r = Reading(meter=m.key, measure=measure)
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
    def set_image_processing_task(cls, meter, image_name):
        """
        Saves a Reading as a new entity on the datastore.
        Args:
            account_number: (String) account_number from request
            image_name: (String) name of the image in CloudStorage
        Returns:
            True if creation successful, exception otherwise

        """
        logging.debug('[Reading] - Set Image Processing Task: Image Name = {0}'.format(image_name))
        # TODO : Implement the new task in the pull queue
        return True


class ReadingCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Reading] - '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)
