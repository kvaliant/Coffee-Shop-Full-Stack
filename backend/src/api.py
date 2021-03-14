import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@DONE TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drin k.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    short_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': short_drinks
    })
'''
@DONE TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': long_drinks
    })
'''
@DONE TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    data = request.get_json()
    new_title = data['title']
    new_recipe = data['recipe']
    if isinstance(new_recipe, dict):
        new_recipe = [new_recipe]
    try:
        drink = Drink()
        drink.title = new_title
        drink.recipe = json.dumps(new_recipe)
        drink.insert()
    except:
        abort(422)
    long_drinks = drink.long()
    return jsonify({
        'success': True,
        'drinks': long_drinks
    })
'''
@DONE TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if(drink == None):
        abort(404)
    try:
        data = request.get_json()
        new_title = data.get('title',None)
        if(new_title != None):
            drink.title = new_title
        new_recipe = data.get('recipe',None)
        if(new_recipe != None):
            drink.recipe = new_recipe
        drink.update()
        long_drink = [drink.long()]
        return jsonify({
            'success': True,
            'drinks': long_drink
        })
    except:
        abort(422)
'''
@DONE TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if(drink == None):
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

'''
@DONE TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404
'''
@DONE TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False, 
        "error": error.status_code,
        "message": error.error.get('description',None)
        }), error.status_code
