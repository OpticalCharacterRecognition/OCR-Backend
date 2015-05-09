"""
Defines the datastore and all interfaces needed for a Meter in the OCR platform
"""
__author__ = 'Cesar'

import logging
from google.appengine.ext import ndb
from user import User, GetUserError
import jmas_api


class Meter(ndb.Model):
    """
    Represents a meter in the platform. A user may be several meters assigned.

        - user: The user that has this meter assigned.
        - account_number: Key that ties to JMAS system.
        - balance: + - m3. Positive balance means debt, negative balance means prepay.
        - model: Model of the physical meter, for OCR purposes.
    """
    # TODO: add geolocation property
    user = ndb.KeyProperty(kind=User)
    account_number = ndb.StringProperty()
    balance = ndb.IntegerProperty()
    model = ndb.StringProperty(choices=['AV3-STAR', 'Dorot', 'Cicasa', 'IUSA'])

    @classmethod
    def exists(cls, account_number):
        """
        Checks the datastore to find if the meter (account_number) is already on it.

        Args:
            account_number: (String) account_number from request

        Returns:
            True if account exist False otherwise
        """
        return cls.query(cls.account_number == account_number).count(1) == 1

    @classmethod
    def create_in_datastore(cls, account_number):
        """
        Creates a new meter in datastore. Checks if the account number is already in the platform
        if not, calls the transactional create of the datastore objects.
        """
        try:
            if Meter.exists(account_number):
                raise MeterCreationError('Meter account number already in platform')
            else:
                Meter.transactional_create(account_number)
        except Exception as e:
            raise MeterCreationError('Error creating the meter in platform: '+e.__str__())
        else:
            return True

    @classmethod
    @ndb.transactional(xg=True)
    def transactional_create(cls, account_number):
        """
        Transactional to the datastore. A transaction is an operation
        or set of operations that either succeeds completely or fails completely.

            :param account_number: meter number to create
            :exception if transaction fails
        """
        # Import in the function to avoid circular import
        from reading import Reading
        from bill import Bill

        try:
            balance = jmas_api.get_balance(account_number)
            model = jmas_api.get_model(account_number)
            # Create Meter
            m = Meter(account_number=account_number, balance=balance, model=model)
            meter_key = m.put()
            # Get and save historic bills
            bills = jmas_api.get_bills(account_number)
            # from bill import Bill
            Bill.save_history_to_datastore(meter_key, bills)
            # Get and save historic readings
            # TODO: TEMP -> historic readings are based on historic bills
            measurements = dict()
            for date in bills.keys():
                measurements[date] = int(bills[date]/jmas_api.get_postpay_conversion_factor())
            Reading.save_history_to_datastore(meter_key, measurements)
        except Exception as e:
            raise MeterCreationError('Error in transactional create: '+e.__str__())
        else:
            logging.debug('[Meter] - New Meter Key = {0}'.format(meter_key))

    @classmethod
    def get_all_from_datastore(cls, user):
        """
        Gets all meters from datastore assigned to a user
        Args:
            user: (String) email
        Returns:
            A List with all the meters assigned to a user
        """
        try:
            u = User.get_from_datastore(user)
            query_response = Meter.query(Meter.user == u.key).fetch()
            if query_response:
                resp = []
                for b in query_response:
                    resp.append(b)
            else:
                raise GetMeterError('No Meters found under specified criteria: User: {0}'
                                    .format(user))
        except Exception as e:
                raise GetMeterError('Error getting Meter: '+e.__str__())
        else:
            for r in resp:
                logging.debug("[Meter] = {0}".format(r))
            return resp

    @classmethod
    def get_from_datastore(cls, account_number):
        """
        Gets meter from datastore based on account number
        """
        try:
            if Meter.exists(account_number):
                m = Meter.query(Meter.account_number == account_number).fetch(limit=1)
            else:
                raise GetMeterError('Meter does not exist')
        except Exception as e:
            raise GetMeterError('Error getting meter: '+e.__str__())
        else:
            logging.debug("[Meter] - Key = {0}".format(m[0].key))
            logging.debug("[Meter] - User Key = {0}".format(m[0].user))
            logging.debug("[Meter] - Account Number = {0}".format(m[0].account_number))
            logging.debug("[Meter] - Balance = {0}".format(m[0].balance))
            logging.debug("[Meter] - Model = {0}".format(m[0].model))
            return m[0]

    @classmethod
    def assign_to_user(cls, email, account_number):
        """
        Assigns a meter to a user (email) in the platform.

        Args:
            email: (String) email from user that will be assigned the meter
            account_number: (String) account number of the meter to assign

        Returns:
            True if assignment successful, False otherwise
        """
        try:
            u = User.get_from_datastore(email)
            m = Meter.get_from_datastore(account_number)

            meter = m.key.get()
            meter.user = u.key
            meter.put()
        except GetUserError:
            raise
        except GetMeterError:
            raise
        else:
            logging.debug("[Meter] - assign_to_user(): Assignment successful! meter = {0} assigned to user = {1}"
                          .format(meter.account_number, u.email))
            return True

    @classmethod
    def set_balance(cls, account_number, new_balance):
        """
        Sets a new balance

        Args:
            account_number: (String) account number of the meter
            new_balance: (Int) New balance to set

        Returns:
            True if assignment successful, False otherwise
        """
        try:
            m = Meter.get_from_datastore(account_number)

            meter = m.key.get()
            meter.balance = new_balance
            meter.put()
        except Exception:
            # FIXME rise exception for error handling
            return False
        else:
            return True

    @classmethod
    def get_balance(cls, account_number):
        """
        Gets a meter current balance

        Args:
            account_number: (String) account number of the meter

        Returns:
            (Int) balance
        """
        m = Meter.get_from_datastore(account_number)

        return m.balance

    @classmethod
    def set_model(cls, account_number, new_model):
        """
        Assigns a new value to the model of a meter

        Args:
            account_number: (String) account number of the meter
            new_model: (String) New model to set. Refer to the accepted values on ndb Properties

        Returns:
            True if assignment successful, False otherwise
        """
        m = Meter.get_from_datastore(account_number)

        try:
            meter = m.key.get()
            meter.model = new_model
            meter.put()
        except Exception:
            # FIXME rise exception for error handling
            return False
        else:
            return True

    @classmethod
    def get_model(cls, account_number):
        """
        Gets a meter current model

        Args:
            account_number: (String) account number of the meter

        Returns:
            (String) model
        """
        m = Meter.get_from_datastore(account_number)

        return m.model


class MeterCreationError(Exception):
    def __init__(self, value):
        self.value = value
        logging.exception('[Meter] - '+value, exc_info=True)

    def __str__(self):
        return repr(self.value)


class GetMeterError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
