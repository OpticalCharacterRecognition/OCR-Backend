"""
Defines the datastore and all interfaces needed for a Bill in the OCR platform
"""
__author__ = 'Cesar'

import logging
from google.appengine.ext import ndb
from meter import Meter, GetMeterError
import jmas_api
from datetime import datetime


class Bill(ndb.Model):
    """
    Represents a Bill for a Meter in the platform.

        - meter: The meter associated with this reading
        - balance: Balance of the meter at the time of the bill (m3)
        - amount: Total in currency based on the meter balance and the conversion factor (from JMAS)
        - status: Paid or unpaid
    """

    date = ndb.DateTimeProperty()
    meter = ndb.KeyProperty(kind=Meter)
    balance = ndb.IntegerProperty()
    amount = ndb.FloatProperty()
    status = ndb.StringProperty(choices=['Paid', 'Unpaid'])

    @classmethod
    def get_all_from_datastore(cls, account_number, status):
        """
        Gets all bills from datastore based on:
        Args:
            account_number: (String)
            status: (String) 'Paid' or 'Unpaid'
        Returns:
            A List with all the bills that match the criteria
        """
        try:
            meter = Meter.get_from_datastore(account_number)
            query_response = Bill.query(ndb.AND(Bill.meter == meter.key,
                                                Bill.status == status)).fetch()
            if query_response:
                resp = []
                for b in query_response:
                    resp.append(b)
            else:
                raise GetBillError('No Bills found under specified criteria: Account Number: {0}, Status:{1}'
                                   .format(account_number, status))
        except Exception as e:
                raise GetBillError('Error getting Bill: '+e.__str__())
        else:
            for r in resp:
                logging.debug("[Bill] = {0}".format(r))
            return resp

    @classmethod
    def save_to_datastore(cls, meter):
        """
        Saves a Bill as a new entity on the datastore. Takes the current balance of the given meter
        to generate the amount based on the conversion factor (from JMAS) and updates the balance
        of the associated Meter. Once a bill is created the m3 billed are removed from the meter balance
        and stored in the bill with a status of 'Paid' or 'Unpaid'
        :param
            meter: (String) account_number from request

        :return
            True if creation successful, exception otherwise

        """
        try:
            m = Meter.get_from_datastore(meter)
            if m.balance > 0:
                factor = jmas_api.get_postpay_conversion_factor()
                calculated_amount = m.balance*factor
                b = Bill(date=datetime.now(),
                         meter=m.key,
                         balance=m.balance,
                         amount=calculated_amount,
                         status='Unpaid')
                key = b.put()
            else:
                raise BillCreationError('Nothing to Bill! Current Balance: {0} <= 0 '.format(m.balance))
        except Exception as e:
            logging.exception("[Bill] - "+e.message)
            raise BillCreationError('Error creating the bill in datastore: '+e.__str__())
        else:
            logging.debug('[Bill] - Bill with Key = {0} - Amount: {1} = (Balance = {2}) + (Factor = {3})'
                          .format(key, calculated_amount, m.balance, factor))
            # Update balance in datastore
            current_balance = Meter.get_balance(m.account_number)
            new_balance = current_balance - b.balance
            # FIXME handle exception from Meter class
            Meter.set_balance(m.account_number, new_balance)
            logging.debug('[Bill] - New Balance: {0} = (Old Balance = {1}) - (Billed Balance = {2})'
                          .format(new_balance, current_balance, b.balance))
            return True

    @classmethod
    def save_history_to_datastore(cls, meter_key, bills):
        """
        Saves historic Bills as a new entities on the datastore.
        :param
            account_number: (String) account_number
            bills: (Dictionary) from jmas_api

        :return
            True if creation successful, exception otherwise

        """
        try:
            for bill in bills:
                b = Bill(date=bill,
                         meter=meter_key,
                         balance=int(bills[bill]/jmas_api.get_postpay_conversion_factor()),
                         amount=bills[bill],
                         status='Paid')
                key = b.put()
        except Exception as e:
            logging.exception("[Bill] - "+e.message)
            raise BillCreationError('Error creating bill in datastore: '+e.__str__())
        else:
            logging.debug('[Bill] - Historical Bills successfully stored')
            return True

    @classmethod
    def pay(cls, bill_key):
        """
        Marks a Bill as payed.
        Args:
            bill_key: (ndb key) identifier of the Bill to mark as payed

        Returns:
            True if mark successful, exception otherwise

        """
        try:
            bill = bill_key.get()
            m = bill.meter.get()
            if m:
                if bill:
                    if bill.status == 'Unpaid':
                        bill.status = 'Paid'
                        bill.put()
                    else:
                        raise BillPaymentError('Error paying Bill, Bill already payed')
                else:
                    raise GetBillError('Error getting Bill from datastore, Bill not found')
            else:
                raise GetMeterError('Error getting Meter from datastore, Meter not found')
        except Exception as e:
            raise GetBillError('Error marking the bill as payed in datastore: '+e.__str__())
        else:
            return True


class BillCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Bill] - Creation Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class GetBillError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Bill] - Get Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class BillPaymentError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Bill] - Payment Error: '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)
