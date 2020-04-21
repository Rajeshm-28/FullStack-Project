import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES

# Get the list of drinks


@app.route('/drinks', methods=['GET'])
def get_drinks_public(*args, **kwargs):
    try:
        drink = Drink.query.order_by(Drink.id).all()

        drinks = [d.short() for d in drink]

        if len(drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks
        })

    except AttributeError:
        abort(422)

# Get the drinks details


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(*args, **kwargs):
    try:
        drink = Drink.query.order_by(Drink.id).all()
        drinks = [d.long() for d in drink]

        if len(drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks
        })

    except AttributeError:
        abort(422)

# Create a new drink


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(*args, **kwargs):
    try:
        body = request.get_json()
        new_title = body.get('title')
        new_recipe = body.get('recipe')

        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        })

    except AttributeError:
        abort(422)

# Update a drink


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(*args, **kwargs):

    drnk_id = kwargs['drink_id']

    try:
        drink = Drink.query.filter(Drink.id == drnk_id).one_or_none()

        if drink is None:
            abort(404)

        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        drink = Drink(id=drnk_id, title=new_title,
                      recipe=json.dumps(new_recipe))

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })

    except AttributeError:
        abort(422)

# delete a particular drink


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(*args, **kwargs):

    drnk_id = kwargs['drink_id']

    try:
        drink = Drink.query.filter(Drink.id == drnk_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drnk_id
        })

    except AttributeError:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "unprocessable"
                    }), 404


@app.errorhandler(AuthError)
def error_auth(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
