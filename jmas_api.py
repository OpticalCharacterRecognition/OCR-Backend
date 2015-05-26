"""
Temporary functions that mimic the api required from JMAS
"""
__author__ = 'cesar'

import datetime
import calendar
import random


def get_postpay_conversion_factor():
    """
    Returns a fake and temp conversion factor
        :return: conversion factor as float
    """
    return 10.0


def get_prepay_conversion_factor():
    """
    Returns a fake and temp conversion factor
        :return: conversion factor as float
    """
    return 5.0


def get_balance(account_number):
    """
    Returns a fake and temp balance
        :param account_number:
        :return: random balance as int
    """
    return random.randint(0, 30)


def get_model(account_number):
    """
    Returns a fake and temp meter model
        :param account_number:
        :return: random model as string
    """
    models = ['AV3-STAR', 'Dorot', 'Cicasa', 'IUSA']
    return models[random.randint(0, 3)]


class FakeHistory:

    bills = dict()
    readings = []
    starting_value = 0
    months = 0

    def __init__(self, account_number, months, value_to_approximate):
        self.months = months
        history = self._generate_reading_history(value_to_approximate, 10)
        self.readings = self._get_readings(account_number, history)
        self.bills = self._get_bills(account_number, history)

    def _generate_reading_history(self, value_to_approximate, variance):
        """
        Generates a fake and temp history of meter readings (m3).
            :param
                months: number of months of history to generate
                value_to_approximate: meter value to approximate (useful for demo meters)
                variance: how far from 30m3 per month
            :return: random history as dict
        """
        history = []
        self.starting_value = value_to_approximate - self.months*(30+variance)
        previous_month = 0
        for month in xrange(0, self.months):
            if month == 0:
                v = self.starting_value
            else:
                v = previous_month + random.randint(30-variance, 30+variance)
            history.append(v)
            previous_month = v
        return history

    def _get_readings(self, account_number, readings):
        """
        Returns a dictionary of the form:
                {datetime: m3_reading}
                ex: {datetime.datetime(2015, 2, 15, 0, 0): 9000}
        with the readings of the last 6 months.
            :param account_number:
            :return: last 6 readings as dict (1 reading per month)
        """
        measurements = dict()
        today = datetime.date.today()
        h = readings
        for i, m in enumerate(h):
            date = today - datetime.timedelta(days=30*(self.months-i))
            date = datetime.datetime.combine(date, datetime.datetime.min.time())
            if i == 0:
                measurements[date] = self.starting_value
            else:
                measurements[date] = h[i]
        return measurements

    def _get_bills(self, account_number, readings):
        """
        Returns a dictionary of the form:
                {datetime: $_amount}
                ex: {datetime.datetime(2015, 2, 15, 0, 0): 346}
        with the bills of the last 6 months.
            :param account_number:
            :return: last 6 bills as dict (1 bill per month)
        """
        bills = dict()
        today = datetime.date.today()
        h = readings
        for i, m in enumerate(h):
            date = today - datetime.timedelta(days=30*(self.months-i))
            date = datetime.datetime.combine(date, datetime.datetime.min.time())
            if i == 0:
                bills[date] = 30*get_postpay_conversion_factor()
            else:
                bills[date] = (h[i] - h[i-1])*get_postpay_conversion_factor()
        return bills

