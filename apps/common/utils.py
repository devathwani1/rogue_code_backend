import random
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from django.conf import settings
from apps.common.constants import Constants
from typing import Union


class Utils:
    def __init__(self):
        super().__init__()
        self.validation_error = Constants.validation_error



    @staticmethod
    def success_response_data(message, data: list | dict = None, image=False):
        if image:
            return message
        if data is None and message is None:
            return {'status': True}
        if message is None:
            return {'status': True, 'data': data}
        if data is None:
            return {'status': True, 'message': message}
        return {'status': True, 'message': message, 'data': data}

    @staticmethod
    def error_response_data(message: str, error: list[str]):
        return {'status': False, 'message': message, 'error': error}

    @staticmethod
    def env_exception_handler(message: str):
        if settings.DEBUG:
            return message
        return Constants.server_error

  