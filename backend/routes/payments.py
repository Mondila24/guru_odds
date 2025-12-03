from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import requests
import hmac
import hashlib
import json
from db import connect
from routes.responses import good_response, bad_response

payments_blueprint = Blueprint('payments_blueprint', __name__)

@payments_blueprint.route('/initiate', methods=['POST'])
@jwt_required()
def initiate():
    try:
        username = get_jwt_identity()
        amount = request.json.get('amount')
        connection = connect('users')
        user = list(connection.find({'username': username}))
        if len(user) == 0:
            return bad_response('User not found')
        email = user[0].get('email')
        secret = os.getenv('PAYSTACK_SECRET_KEY')
        headers = {"Authorization": f"Bearer {secret}", "Content-Type": "application/json"}
        payload = {"email": email, "amount": int(float(amount) * 100), "metadata": {"username": username}}
        r = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=payload)
        if r.status_code == 200:
            data = r.json().get('data')
            return good_response({"authorization_url": data.get('authorization_url'), "reference": data.get('reference')})
        return bad_response(r.text)
    except Exception as e:
        return bad_response(e)

@payments_blueprint.route('/verify', methods=['POST'])
@jwt_required()
def verify():
    try:
        username = get_jwt_identity()
        reference = request.json.get('reference')
        secret = os.getenv('PAYSTACK_SECRET_KEY')
        headers = {"Authorization": f"Bearer {secret}"}
        r = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
        if r.status_code == 200:
            res = r.json()
            status = res.get('data', {}).get('status')
            amount = res.get('data', {}).get('amount')
            if status == 'success':
                connection = connect('users')
                account = list(connection.find({'username': username}))
                if len(account) == 0:
                    return bad_response('User not found')
                new_balance = float(account[0].get('current_balance', 0)) + float(amount) / 100.0
                connection.update_one({'username': username}, {'$set': {"current_balance": new_balance}, '$currentDate': { 'lastUpdated': True }})
                return good_response({"status": "success", "new_balance": new_balance})
            return bad_response('Verification failed')
        return bad_response(r.text)
    except Exception as e:
        return bad_response(e)

@payments_blueprint.route('/webhook', methods=['POST'])
def webhook():
    try:
        raw = request.get_data()
        secret = os.getenv('PAYSTACK_SECRET_KEY')
        signature = request.headers.get('x-paystack-signature')
        expected = hmac.new(secret.encode('utf-8'), raw, hashlib.sha512).hexdigest()
        if signature != expected:
            return jsonify({}), 401
        body = json.loads(raw.decode('utf-8'))
        event = body.get('event')
        if event == 'charge.success':
            data = body.get('data', {})
            amount = data.get('amount')
            meta = data.get('metadata', {})
            username = meta.get('username')
            if username:
                connection = connect('users')
                account = list(connection.find({'username': username}))
                if len(account) > 0:
                    new_balance = float(account[0].get('current_balance', 0)) + float(amount) / 100.0
                    connection.update_one({'username': username}, {'$set': {"current_balance": new_balance}, '$currentDate': { 'lastUpdated': True }})
        return jsonify({}), 200
    except Exception:
        return jsonify({}), 200
