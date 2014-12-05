#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from flask import Flask, jsonify, request
from logging import Formatter
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

import logging

def make_json_app(import_name, **kwargs):
    app = Flask(import_name, **kwargs)
    app.config.from_object('config')

    if not app.debug:
        handler = RotatingFileHandler('log/foo.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.__dict__[app.config['LOG_LEVEL'].upper()])
        handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(handler)

    def make_json_error(ex):

        error = {
            'code': ex.code if isinstance(ex, HTTPException) else 500,
            'message': ex.message if isinstance(ex, HTTPException) else "Internal Server Error"
        }

        app.logger.exception("%s %s at %s %s", error['code'], error['message'], request.method, request.url)

        response = jsonify(error=error, response=None)
        response.status_code = code
        return response

    for code in default_exceptions.iterkeys():
        print code
        app.error_handler_spec[None][code] = make_json_error

    return app


app = make_json_app(__name__)
db = MongoClient(app.config['MONGODB_URI']).suggestic_base


@app.route('/', methods=['GET'])
def index():
    a = 1 / 0
    return jsonify()
    # return app.send_static_file('templates/index.html')


if __name__ == "__main__":
    app.run()
