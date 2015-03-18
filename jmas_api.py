"""
Temporary functions that mimic the api required from JMAS
"""
__author__ = 'cesar'

import datetime
import calendar
import random


def get_conversion_factor():
    """
    Returns a fake and temp conversion factor
        :return: conversion factor as int
    """
    return 10


def generate_history(months, mid_value, variance):
    """
    Generates a fake and temp history for the measurements and bills
        :param
            months: number of months of history to generate
            mid_value: central value to use for random numbers
            variance: how far from mid_value
        :return: random history as dict
    """
    history = dict()
    for month in range(1, months):
        v = random.randint(mid_value-variance, mid_value+variance)
        history[month] = v
    return history


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


def get_bills(account_number):
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
    h = generate_history(6, 300, 50)
    for i, m in enumerate(h):
        date = today - datetime.timedelta(days=i*30)
        date = datetime.datetime.combine(date, datetime.datetime.min.time())
        bills[date] = h[m]
    return bills
