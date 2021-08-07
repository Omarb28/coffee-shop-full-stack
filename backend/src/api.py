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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()


# Route for Testing
@app.route('/login-results')
def login_esults():
    logout_url = 'https://omar-fsnd.us.auth0.com/v2/logout?client_id=z4tYXHIDAtht6BCDzGoAa5Ut0wyFZzYs&returnTo=http://localhost:5000/logout'
    script = '<script>token = window.location.href.split("access_token=")[1].split("&")[0]; document.getElementById("demo").innerHTML = "Access Token is: " + token;</script>'
    return f'<p id="demo">{script}</p><a href="{logout_url}">Logout</a>'


# Route for Testing
@app.route('/logout')
def logout():
    login_url = 'https://omar-fsnd.us.auth0.com/authorize?audience=coffeeshop&response_type=token&client_id=z4tYXHIDAtht6BCDzGoAa5Ut0wyFZzYs&redirect_uri=http://localhost:5000/login-results'
    return f'<a href="{login_url}">Go to Login</a>'


# ROUTES

@app.route('/drinks')
@requires_auth('get:drinks')
def retrieve_drinks(jwt):
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    return 'Get me a drink'


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }), 404


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error_handler(error):
    status_code = error.status_code
    error_code = error.error['code']
    error_description = error.error['description']

    messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden"
    }

    status_code_message = messages.get(status_code, "Status code message could not be found")

    return jsonify({
        "success": False,
        "error": status_code,
        "message": status_code_message,
        "code": error_code,
        "description": error_description
    }), status_code
