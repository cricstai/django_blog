"""
This module contains all database interfacing methods for the MFlix
application. You will be working on this file for the majority of M220P.

Each method has a short description, and the methods you must implement have
docstrings with a short explanation of the task.

Look out for TODO markers for additional help. Good luck!
"""


from flask import current_app, g
from werkzeug.local import LocalProxy

from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.write_concern import WriteConcern
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.read_concern import ReadConcern


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)
    MFLIX_DB_URI = current_app.config["MFLIX_DB_URI"]
    print(MFLIX_DB_URI)
    
    MFLIX_DB_NAME = current_app.config["MFLIX_NS"]
    if db is None:

        """
        Ticket: Connection Pooling

        Please change the configuration of the MongoClient object by setting the
        maximum connection pool size to 50 active connections.
        """

        """
        Ticket: Timeouts

        Please prevent the program from waiting indefinitely by setting the
        write concern timeout limit to 2500 milliseconds.
        """

        db = g._database = MongoClient(
        MFLIX_DB_URI,maxPoolSize=50,wTimeoutMS=2500
        )[MFLIX_DB_NAME]
    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def get_article(id):
    return db.articles.find_one({"_id":ObjectId(id)})

def inc_views(id):
    db.analytics.update({"article_id":id}, { "$inc": { "views": 1 }})

def home():
    pipeline = [{"$project":{"_id":0, "title":1, "category":1, "id":{"$toString": "$_id"}, "date":1, "poster":1, "author":1}}]
    ans = list(db.articles.aggregate(pipeline))
    context = {}
    context["row1"] = ans[0:4]
    context["row2"] = ans[4:8]
    return context

def recent():
    recent = list(db.articles.find().sort([("date",DESCENDING)]).limit(4))
    return recent

def most_read():
    pipeline = [{
                        '$lookup': {
                            'from': 'analytics', 
                            'localField': '_id', 
                            'foreignField': 'article_id', 
                            'as': 'views'
                        }
                    }, {
                        '$project': {
                            'title': 1, 
                            'views': {
                                '$arrayElemAt': [
                                    '$views', 0
                                ]
                            }, 
                            '_id': 0, 
                            'poster': 1,
                            "id":{"$toString": "$_id"},
                            "category":1,
                            "author":1
                        }
                    }
                ]
    ans = list(db.articles.aggregate(pipeline))
    return ans
    