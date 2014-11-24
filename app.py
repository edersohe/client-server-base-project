#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import flask

app = flask.Flask(__name__)
app.config.from_object('config')

db = pymongo.MongoClient(app.config['MONGODB_URI']).suggestic_base


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('templates/index.html')


if __name__ == "__main__":
    app.run()
