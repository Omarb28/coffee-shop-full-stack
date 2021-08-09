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
@DONE uncomment the following line to initialize the datbase
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
def retrieve_drinks():
    '''
    @DONE implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404, description='No drinks found.')

    for i in range(len(drinks)):
        drink = drinks[i].short()
        drinks[i] = drink

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(jwt):
    '''
    @DONE implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404, description='No drinks found.')

    for i in range(len(drinks)):
        drink = drinks[i].long()
        drinks[i] = drink

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    '''
    @DONE implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
            where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    if (
        type(title) is not str
        or type(recipe) is not list
    ):
        abort(400, description='Title or recipe list is not correct type.')

    if (
        title == ''
        or len(recipe) == 0
    ):
        abort(422, description='Title or recipe list is empty.')

    # Check if title is unique
    search = Drink.query.filter(Drink.title == title).one_or_none()
    if search is not None:
        abort(409, description='Title is not unique.')

    # Check recipe elements
    for r in recipe:
        if type(r) is not dict:
            abort(400, description='Recipe is not dictionary type.')

        name = r.get('name')
        color = r.get('color')
        parts = r.get('parts')

        if (
            type(name) is not str
            or type(color) is not str
            or type(parts) is not int
        ):
            abort(400, description='Recipe elements are either '
                                   'missing or not correct type.')

        if (
            name == ''
            or color == ''
            or parts < 1
        ):
            abort(422, description='Recipe element is empty or incorrect.')

    try:
        recipe = json.dumps(recipe)

        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except exc.SQLAlchemyError:
        abort(400, description='Could not create drink.')


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    '''
    @DONE implement endpoint
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
    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404, description='Drink not found.')

    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    if title is not None:
        if type(title) is not str:
            abort(400, description='Title is not string type.')
        elif title == '':
            abort(422, description='Title is empty.')

        # Check if title is unique (excluding current drink)
        search = Drink.query.filter(Drink.title == title).one_or_none()
        if search is not None and drink.title != title:
            abort(409, description='Title is not unique.')

    if recipe is not None:
        if type(recipe) is not list:
            abort(400, description='Recipe list is not list type.')
        elif len(recipe) == 0:
            abort(422, description='Recipe list is empty.')

        # Check recipe elements
        for r in recipe:
            if type(r) is not dict:
                abort(400, description='Recipe is not dictionary type.')

            name = r.get('name')
            color = r.get('color')
            parts = r.get('parts')

            if (
                type(name) is not str
                or type(color) is not str
                or type(parts) is not int
            ):
                abort(400, description='Recipe element is either '
                                       'missing or not correct type.')

            if (
                name == ''
                or color == ''
                or parts < 1
            ):
                abort(422, description='Recipe element is empty or incorrect.')

    try:
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            'success': True,
            'status_code': 200,
            'drinks': [drink.long()]
        })
    except exc.SQLAlchemyError:
        abort(400, description='Could not update drink.')


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    '''
    @DONE implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
            where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404, description='Drink not found.')

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'status_code': 200,
            'delete': drink.id
        })
    except exc.SQLAlchemyError:
        abort(400, description='Could not delete drink.')


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


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request',
        'description': error.description
    }), 400


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        'success': False,
        'error': 409,
        'message': 'Conflict'
    }), 409


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
    status_code_message = messages.get(
        status_code,
        "Status code message could not be found"
    )

    return jsonify({
        "success": False,
        "error": status_code,
        "message": status_code_message,
        "code": error_code,
        "description": error_description
    }), status_code
