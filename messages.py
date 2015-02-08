"""
Defined here are the ProtoRPC message class definitions for the API.
"""
__author__ = 'Cesar'


from protorpc import messages, message_types

"""
USER
"""


class CreateUser(messages.Message):
    """
    Message containing the information of a User
        email: (String)
        name: (String)
        age: (Integer)
        account_type: (String)
    """
    email = messages.StringField(1, required=True)
    name = messages.StringField(2, required=True)
    age = messages.IntegerField(3)
    account_type = messages.StringField(4, required=True)


class CreateUserResponse(messages.Message):
    """
    Response to user creation request
        ok: (Boolean) User creation successful or failed
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)


class GetUser(messages.Message):
    """
    Message containing the information of a user
        email: (String)
    """
    email = messages.StringField(1, required=True)


class GetUserResponse(messages.Message):
    """
    Response to user information request
        ok: (Boolean) User search successful or failed
        error: (String) If search failed, contains the reason, otherwise empty.

        email = (String)
        name = (String)
        age = (Integer)
        account_type = (String)
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)

    email = messages.StringField(3)
    name = messages.StringField(4)
    age = messages.IntegerField(5)
    account_type = messages.StringField(6)


"""
METER
"""


class Meter(messages.Message):
    """
    Message containing the details of a Meter
        urlsafe_key: (String) urlsafe key
        account_number: (String)
        balance: (Integer)
        model: (String)
    """
    urlsafe_key = messages.StringField(1)
    account_number = messages.StringField(2)
    balance = messages.IntegerField(3)
    model = messages.StringField(4)


class CreateMeter(messages.Message):
    """
    Message containing the information of a Meter
        account_number: (String)
        balance: (Integer)
        model: (String)
    """
    account_number = messages.StringField(1, required=True)
    balance = messages.IntegerField(2, required=True)
    model = messages.StringField(3, required=True)


class CreateMeterResponse(messages.Message):
    """
    Response to user creation request
        ok: (Boolean) Meter creation successful or failed
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)


class GetMeter(messages.Message):
    """
    Message containing the information of a meter
        account_number: (String)
    """
    account_number = messages.StringField(1, required=True)


class GetMeterResponse(messages.Message):
    """
    Response to user information request
        ok: (Boolean) Meter search successful or failed
        error: (String) If search failed, contains the reason, otherwise empty.

        account_number: (String)
        balance: (Integer)
        model: (String)
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)

    account_number = messages.StringField(3)
    balance = messages.IntegerField(4)
    model = messages.StringField(5)


class AssignMeterToUser(messages.Message):
    """
    Message containing information to assign a meter to a user
        account_number: (String)
        email: (String)
    """
    account_number = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class AssignMeterToUserResponse(messages.Message):
    """
    Response to user creation request
        ok: (Boolean) Meter creation successful or failed
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)


class GetMeters(messages.Message):
    """
    Message to get a Meter
        user: email of user
    """
    user = messages.StringField(1, required=True)


class GetMetersResponse(messages.Message):
    """
    Response to user creation request
        ok: (Boolean) Meter creation successful or failed
        meters: (Meter) Detailed info of each meter
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    meters = messages.MessageField(Meter, 2, repeated=True)
    error = messages.StringField(3)


"""
READING
"""


class NewReading(messages.Message):
    """
    Message containing the information of a Reading
        account_number: (String)
        measure: (Integer)
    """
    account_number = messages.StringField(1, required=True)
    measure = messages.IntegerField(2, required=True)


class NewReadingResponse(messages.Message):
    """
    Response to reading creation request
        ok: (Boolean) Reading creation successful or failed
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)


"""
BILL
"""


class Bill(messages.Message):
    """
    Message containing the details of Bill
        urlsafe_key: (String) unique id
        creation_date: (String)
        account_number: (String)
        balance: (Integer) m3 at the creation of the bill
        amount: (Integer) payment due based on the factor from JMAS
        status: (String) 'Paid' or 'Unpaid'

    """
    urlsafe_key = messages.StringField(1)
    creation_date = message_types.DateTimeField(2)
    account_number = messages.StringField(3)
    balance = messages.IntegerField(4)
    amount = messages.IntegerField(5)
    status = messages.StringField(6)


class NewBill(messages.Message):
    """
    Message containing the information to create a Bill
        account_number: (String)
    """
    account_number = messages.StringField(1, required=True)


class NewBillResponse(messages.Message):
    """
    Response to Bill creation request
        ok: (Boolean) Reading creation successful or failed
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)


class GetBills(messages.Message):
    """
    Message asking for Bills that meet certain criteria
        account_number: (String)
        status: status of the bill ('Paid', 'Unpaid')
    """
    account_number = messages.StringField(1, required=True)
    status = messages.StringField(2, required=True)


class GetBillsResponse(messages.Message):
    """
    Response to a location search
        ok: (Boolean) Bill search successful or failed
        bills: (String) If search successful contains a list of bills (see class Bill on messages.py)
        error: (String) If search failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    bills = messages.MessageField(Bill, 2, repeated=True)
    error = messages.StringField(3)


class PayBill(messages.Message):
    """
    Message requesting to mark a Bill as payed
        bill_key: (String)
    """
    bill_key = messages.StringField(1, required=True)


class PayBillResponse(messages.Message):
    """
    Response to Bill creation request
        ok: (Boolean) Reading creation successful or failed
        error: (String) If creation failed, contains the reason, otherwise empty.
    """
    ok = messages.BooleanField(1)
    error = messages.StringField(2)
