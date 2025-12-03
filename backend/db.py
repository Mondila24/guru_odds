# Import flask and datetime module for showing date and time
from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from routes.responses import bad_db_connection

load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
mongo_db_name = os.getenv('MONGO_DB_NAME', 'PredictionDB')
_client = None
_db = None

def _get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(mongo_uri)
        _db = _client[mongo_db_name]
    return _db

def connect(collection):
    
    if collection == 'users':
        return connectUsers()
    elif collection == 'games':
        return connectGames()
    elif collection == 'bets':
        return connectBets()


def connectUsers():
    try:
        db = _get_db()
        return db['users']

    except Exception as e:
        return bad_db_connection(e)

def connectGames():
    try:
        db = _get_db()
        return db['games']

    except Exception as e:
        return bad_db_connection(e)

def connectBets():
    try:
        db = _get_db()
        return db['bets']

    except Exception as e:
        return bad_db_connection(e)
