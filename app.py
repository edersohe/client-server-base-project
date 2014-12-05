#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
import logging

from pymongo import MongoClient
from flask import Flask, json, Response
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES


class LoggingFilter(object):
    def __init__(self, *args):
        self.__args = args

    def filter(self, record):
        return record.levelno in self.__args


class APIResponse(Response):
    default_mimetype = 'application/json'

    def __init__(self, response=None, status=None, headers=None):
        status = status if status else 200
        super(APIResponse, self).__init__(
            response=json.dumps(dict(response=response, code=status, message=HTTP_STATUS_CODES[status])),
            status=status, headers=headers)


class APIApp(Flask):
    def __init__(self, *args, **kwargs):
        super(APIApp, self).__init__(*args, **kwargs)
        self.config.from_object('config')
        self.__db = MongoClient(self.config['MONGODB_URI']).suggestic_base
        self.default_log_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

        if self.config['ENVIRONMENT'] == 'development':
            handler = StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(Formatter(self.debug_log_format))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

        elif self.config['ENVIRONMENT'] == 'testing':
            handler = StreamHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(Formatter(self.default_log_format))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        else:
            handler = RotatingFileHandler('log/error.log', maxBytes=10000, backupCount=1)
            handler.setLevel(logging.ERROR)
            handler.setFormatter(Formatter(self.default_log_format))
            self.logger.addHandler(handler)

            handler = RotatingFileHandler('log/access.log', maxBytes=10000, backupCount=1)
            handler.setLevel(logging.INFO)
            handler.setFormatter(Formatter(self.default_log_format))
            handler.addFilter(LoggingFilter(logging.INFO, logging.WARNING))
            self.logger.addHandler(handler)

            self.logger.setLevel(logging.INFO)

        for code in default_exceptions.iterkeys():
            self.error_handler_spec[None][code] = self.make_json_error

    def route(self, rule, **options):
        def decorator(f):
            def wrap(*args, **kwargs):
                response = f(*args, **kwargs)
                if isinstance(response, (Response, APIResponse)):
                    return response
                elif isinstance(response, tuple):
                    return APIResponse(response=response[0], status=response[1] if len(response) > 1 else None,
                                       headers=response[2] if len(response) > 2 else None)
                elif hasattr(response, '__call__'):
                    return response
                else:
                    return APIResponse(response)

            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, wrap, **options)
            return wrap

        return decorator

    @staticmethod
    def make_json_error(ex):
        code = ex.code if isinstance(ex, HTTPException) else 500
        return APIResponse(status=code)

    def db(self, collection):
        return self.__db[collection]


app = APIApp(__name__)


@app.route('/', methods=['GET'])
def index():
    app.logger.debug('Esto es una prueba')
    # 1 / 0
    #return 'eder'
    #return ['google', 1, 2]
    #return ('Hello world', 500)
    return (None, 404)
    return app.send_static_file('templates/index.html')


if __name__ == "__main__":
    app.run(use_reloader=True)
