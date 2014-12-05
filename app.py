#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from flask import Flask, jsonify, request
from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

import logging


class LoggingFilter(object):

    def __init__(self, *args):
        self.__args = args

    def filter(self, record):
        return record.levelno in self.__args


class API(Flask):
    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)
        self.config.from_object('config')
        self.__db = MongoClient(self.config['MONGODB_URI']).suggestic_base

        if self.config['ENVIRONMENT'] == 'development':
            handler = StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

        elif self.config['ENVIRONMENT'] == 'testing':
            handler = StreamHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        else:
            handler = RotatingFileHandler('log/error.log', maxBytes=10000, backupCount=1)
            handler.setLevel(logging.ERROR)
            handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            self.logger.addHandler(handler)

            handler = RotatingFileHandler('log/access.log', maxBytes=10000, backupCount=1)
            handler.setLevel(logging.INFO)
            handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            handler.addFilter(LoggingFilter(logging.INFO, logging.WARNING))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        for code in default_exceptions.iterkeys():
            self.error_handler_spec[None][code] = self.make_json_error

    @staticmethod
    def make_json_error(ex):

        error = {
            'code': ex.code if isinstance(ex, HTTPException) else 500,
            'message': ex.message if isinstance(ex, HTTPException) else "Internal Server Error"
        }

        response = jsonify(error=error, response=None)
        response.status_code = error['code']
        return response

    def db(self, collection):
        return self.__db[collection]


app = API(__name__)


@app.route('/', methods=['GET'])
def index():
    app.logger.debug('Esto es una prueba')
    a = 1 / 0
    return jsonify()
    # return app.send_static_file('templates/index.html')


if __name__ == "__main__":
    app.run()
