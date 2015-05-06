"""
Parse backend interface
"""

__author__ = 'cesar'

import logging
import requests
import json

REST_API_URL = "https://api.parse.com"
REST_API_Port = '443'
Application_Id = 'vewdKbKAPt6y9ufviEEYHlq62dXhlEAPldiwNi5P'
REST_API_Key = 'XBs6U4aoAgNCZtXnupadG7b74UvglZGCPvOu2x8C'


class Push():
    """
    Defines a Push notification using Parse backend
    """

    Push_URI = '/1/push'
    Installation_Id = None

    def __init__(self, installation_id):
        """
        Push object constructor. Gets the installation_id to identify the recipient of the Push notification.
            :param: installation_ind: Parse identification of a particular User app installation
            :return: True if successful Exception otherwise
        """
        self.Installation_Id = installation_id

    def send(self, title, message):
        """
        Push object constructor. Gets the installation_id to identify the recipient of the Push notification.
            :param: installation_ind: Parse identification of a particular User app installation
            :return: A push object.
        """
        try:
            headers = {'X-Parse-Application-Id': Application_Id,
                       'X-Parse-REST-API-Key': REST_API_Key,
                       'Content-Type': 'application/json'}

            payload = json.dumps({"where": {"installationId": self.Installation_Id},
                                  "data": {"alert": "{0}".format(message),
                                           "title": "{0}".format(title)}})

            r = requests.post("{0}:{1}{2}".format(REST_API_URL, REST_API_Port, self.Push_URI),
                              data=payload,
                              headers=headers)
        except Exception as e:
            logging.error('Error sending Push notification to Parse: {0}'.format(e.__str__()))
            raise Exception
        else:
            if r.status_code == 200:
                return True
            else:
                logging.error('Error response to Push notification request: {0}'.format(r.status_code))
                raise Exception