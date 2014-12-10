#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
import logging

from pymongo import MongoClient
from flask import Flask, json, Response, Blueprint
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES


class LoggingFilter(object):
    def __init__(self, *args):
        self.__args = args

    def filter(self, record):
        return record.levelno in self.__args


def logging_setup(environment, maxbytes=100000):
    kwargs_handler = {'maxBytes': maxbytes, 'backupCount': 1}
    default_log_format = '%(levelname)s: %(message)s'
    development_log_format = '%(levelname)s in %(filename)s:%(lineno)d\n'
    development_log_format = '%(message)s\n' + ('-' * 80)
    production_error_log_format = '%(asctime)s %(levelname)s: %(message)s'
    production_message_log_format = '%(asctime)s %(levelname)s: %(message)s '
    production_message_log_format += '[in %(filename)s:%(lineno)d]'

    if environment == 'development':
        handler = StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(Formatter(development_log_format))
        log = logging.getLogger()
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

    elif environment == 'testing':
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(Formatter(default_log_format))
        log = logging.getLogger()
        log.addHandler(handler)
        log.setLevel(logging.INFO)

    elif environment == 'production':
        handler = RotatingFileHandler('log/error.log', **kwargs_handler)
        handler.setLevel(logging.ERROR)
        handler.setFormatter(Formatter(production_error_log_format))
        log = logging.getLogger()
        log.addHandler(handler)
        log.setLevel(logging.ERROR)

        handler = RotatingFileHandler('log/access.log', **kwargs_handler)
        log = logging.getLogger('werkzeug')
        log.addHandler(handler)
        log.propagate = False

        handler = RotatingFileHandler('log/messages.log', **kwargs_handler)
        handler.setLevel(logging.INFO)
        handler.setFormatter(Formatter(production_message_log_format))
        handler.addFilter(LoggingFilter(logging.INFO, logging.WARNING))
        log = logging.getLogger()
        log.addHandler(handler)
        log.setLevel(logging.INFO)


class APIResponse(Response):
    default_mimetype = 'application/json'

    def __init__(self, response=None, status=None, headers=None):
        status = status if status else 200
        response = {
            'response': response,
            'code': status,
            'status': HTTP_STATUS_CODES[status]

        }
        super(APIResponse, self).__init__(
            response=json.dumps(response), status=status, headers=headers)


class APIApp(Flask):
    def __init__(self, *args, **kwargs):
        super(APIApp, self).__init__(*args, **kwargs)
        for code in default_exceptions.iterkeys():
            self.error_handler_spec[None][code] = self.make_json_error

    @staticmethod
    def make_json_error(ex):
        code = ex.code if isinstance(ex, HTTPException) else 500
        return APIResponse(status=code)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        def wrap(*args, **kwargs):
            response = view_func(*args, **kwargs)
            if isinstance(response, (Response, APIResponse)):
                return response
            elif isinstance(response, tuple):
                response = {
                    'response': response[0],
                    'status': response[1] if len(response) > 1 else None,
                    'headers': response[2] if len(response) > 2 else None
                }
                return APIResponse(**response)
            elif hasattr(response, '__call__'):
                return response
            else:
                return APIResponse(response)

        super(APIApp, self).add_url_rule(rule, endpoint, wrap, **options)

    def get(self, rule):
        return self.route(rule, methods=['GET'])

    def post(self, rule):
        return self.route(rule, methods=['POST'])

    def put(self, rule):
        return self.route(rule, methods=['PUT'])

    def delete(self, rule):
        return self.route(rule, methods=['DELETE'])


class APIBlueprint(Blueprint):
    def get(self, rule):
        return self.route(rule, methods=['GET'])

    def post(self, rule):
        return self.route(rule, methods=['POST'])

    def put(self, rule):
        return self.route(rule, methods=['PUT'])

    def delete(self, rule):
        return self.route(rule, methods=['DELETE'])


app = APIApp(__name__)
app.config.from_object('config')
logging_setup(app.config.get('ENVIRONMENT', 'production'))
logging.info('loading var from config object:\n%s', dict(app.config))
app.db = lambda: MongoClient(app.config['MONGODB_URI'])

from blueprints.user import bp as user

app.register_blueprint(user, url_prefix='/' + 'user')


@app.get('/')
def index():
    logging.info('Esto es una prueba')
    #1 / 0
    #return 'eder'
    return ['google', 1, 2]
    return ('Hello world', 500)
    return (None, 404)
    print app.db('menu_items_flattened_all_ingredients')
    return app.send_static_file('templates/index.html')


if __name__ == "__main__":
    app.run(use_reloader=True)
