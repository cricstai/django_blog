import os

from flask import Flask, render_template
from flask.json import JSONEncoder
from flask_cors import CORS
from src.db import get_article, inc_views, home, recent, most_read
from bson import json_util, ObjectId
from datetime import datetime, timedelta

class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def create_app():

    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(APP_DIR, 'static')
    TEMPLATE_FOLDER = os.path.join(APP_DIR, 'templates')

    app = Flask(__name__, static_folder=STATIC_FOLDER,
                template_folder=TEMPLATE_FOLDER,
                )
    CORS(app)
    app.json_encoder = MongoJsonEncoder

    @app.route('/')
    def serve():
        context = home()
        return render_template("index.html", row1=context["row1"], row2=context["row2"])
        
    
    @app.route('/article/<id>')
    def article(id):
        obj = get_article(ObjectId(id))
        inc_views(id)
        return render_template('blog-post.html',object=obj, recent=recent(), top_read=most_read())
        

    return app
