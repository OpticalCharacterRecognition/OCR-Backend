"""
Defines the datastore and all interfaces needed for a Prepay event in the OCR platform
"""
__author__ = 'Cesar'


import logging
from google.appengine.ext import ndb
from meter import Meter, GetMeterError


def get_conversion_factor():
    """
    Temp function until we get the API from JMAS
    """
    return .5


class Prepay(ndb.Model):
    """
    Represents a Prepay event for a Meter in the platform.

        - meter: The meter associated with this reading
        - balance: Balance of the meter at the time of the prepay event (m3) (must be 0 or less)
        - prepay: Amount of water to prepay (m3)
        - amount: Total in currency based on the water to prepay and the conversion factor (from JMAS)
        - status: 'Paid' or 'Unpaid'
    """

    created = ndb.DateTimeProperty(auto_now_add=True)
    meter = ndb.KeyProperty(kind=Meter)
    balance = ndb.IntegerProperty()
    prepay = ndb.IntegerProperty()
    amount = ndb.FloatProperty()
    status = ndb.StringProperty(choices=['Paid', 'Unpaid'])

    @classmethod
    def get_all_from_datastore(cls, account_number, status):
        """
        Gets all prepay events from datastore based on:
        Args:
            account_number: (String)
        Returns:
            A List with all the prepay events that match the criteria
        """
        try:
            meter = Meter.get_from_datastore(account_number)
            query_response = Prepay.query(Prepay.meter == meter.key and Prepay.status == status).fetch()
            if query_response:
                resp = []
                for p in query_response:
                    resp.append(p)
            else:
                raise GetPrepayError('No Prepay events found under specified criteria: Account Number: {0}'
                                     .format(account_number))
        except Exception as e:
                raise GetPrepayError('Error getting prepay: '+e.__str__())
        else:
            for r in resp:
                logging.debug("[Prepay] = {0}".format(r))
            return resp

    @classmethod
    def save_to_datastore(cls, meter, m3_to_prepay):
        """
        Saves a Prepay event as a new entity on the datastore. Takes the m3 prepay amount to generate
        the amount based on the conversion factor (from JMAS) and updates the balance
        of the associated Meter.
        Args:
            account_number: (String) account_number from request
            prepay: (Integer) amount in m3 to prepay

        Returns:
            True if creation successful, exception otherwise

        """
        try:
            m = Meter.get_from_datastore(meter)
            if m.balance <= 0:
                factor = get_conversion_factor()
                calculated_amount = m3_to_prepay*factor
                p = Prepay(
                    meter=m.key,
                    balance=m.balance,
                    prepay=m3_to_prepay,
                    amount=calculated_amount,
                    status='Unpaid')
                key = p.put()
            else:
                raise PrepayCreationError('Positive Balance, pay first! Current Balance: {0} <= 0 '.format(m.balance))
        except Exception as e:
            logging.exception("[Prepay] - "+e.message)
            raise PrepayCreationError('Error creating the prepay event in datastore: '+e.__str__())
        else:
            logging.debug('[Prepay] - Prepay with Key = {0} - Amount: ${1} = (m3 to Prepay = {2})*(Factor = {3})'
                          .format(key, calculated_amount, m3_to_prepay, factor))
            return True

    @classmethod
    def pay(cls, prepay_key):
        """
        Marks a Prepay event as payed.
        Args:
            prepay_key: (ndb key) identifier of the Prepay event to mark as payed

        Returns:
            True if mark successful, exception otherwise

        """
        try:
            prepay = prepay_key.get()
            m = prepay.meter.get()
            if m:
                if prepay:
                    if prepay.status == 'Unpaid':
                        prepay.status = 'Paid'
                        prepay.put()
                    else:
                        raise PrepayPaymentError('Error paying Prepay, Prepay already payed')
                else:
                    raise GetPrepayError('Error getting Prepay from datastore, Prepay not found')
            else:
                raise GetMeterError('Error getting Meter from datastore, Meter not found')
        except Exception as e:
            raise GetPrepayError('Error marking the Prepay event as payed in datastore: '+e.__str__())
        else:
            # Update balance in datastore
            current_balance = Meter.get_balance(m.account_number)
            new_balance = current_balance - prepay.prepay
            # FIXME handle exception from Meter class
            Meter.set_balance(m.account_number, new_balance)
            logging.debug('[Prepay] - New Balance: {0} = (Old Balance = {1}) - (Paid Balance = {2})'
                          .format(new_balance, current_balance, prepay.prepay))

            return True


class PrepayCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Prepay] - Creation Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class GetPrepayError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Prepay] - Get Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class PrepayPaymentError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Prepay] - Payment Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)
