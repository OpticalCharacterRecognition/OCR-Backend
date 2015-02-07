"""
Defined here are the ProtoRPC message class definitions for the API.
"""
__author__ = 'Cesar'


from protorpc import messages

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
