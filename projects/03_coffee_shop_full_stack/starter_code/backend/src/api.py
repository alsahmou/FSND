import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database.models import db_drop_and_create_all, setup_db, Drink, db_init
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following lines to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

# db_drop_and_create_all()
# db_init()

## ROUTES

def validate_recipe(recipe):
    drink_recipe = []
    if not isinstance(recipe, list) and not isinstance(recipe, dict):
        return None
    if isinstance(recipe, dict):
        try:
            color = recipe['color']
            name = recipe['name']
            parts = recipe['parts']
            if not isinstance(color, str):
                return None
            if not isinstance(name, str):
                return None
            if not isinstance(parts, (str, float, int)):
                return None 
            drink_recipe = [{"color": color, "name": name, "parts": int(parts)}]
        except:
            return None
    else:
        for r in recipe:
            color = r['color']
            name = r['name']
            parts = r['parts']
            if not isinstance(color, str):
                return None
            if not isinstance(name, str):
                return None
            if not isinstance(parts, (str, float, int)):
                return None 
            drink_recipe = [{"color": color, "name": name, "parts": int(parts)}]
    return drink_recipe

@app.route('/drinks', methods=['GET'])
def get_drinks():
    '''
        public endpoint, returns list of drinks in the drink.short() data representation
    '''
    drinks = Drink.query.order_by(Drink.id).all()
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    '''
        requiers get:drinks-detail permission
        returns list of drinks in the drink.long() data representation
    '''
    drinks = Drink.query.order_by(Drink.id).all()
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        'sucess': True,
        'drinks': [drink.long() for drink in drinks]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    '''
        requires post:drinks permission
        posts a new drink to the database 
    '''
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if recipe is None or title is None:
            abort(422)
        
        if not validate_recipe(recipe):
            abort(422)
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({
            'success': True,    
            'drinks': [drink.long()]
        })

    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    '''
        requires patch:drinks permission
        updates a drink in the database 
    ''' 
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        if recipe is None or title is None:
            abort(422)
        if not validate_recipe(recipe):
            abort(422)
        drink.title = title
        drink.recipe = json.dumps(recipe)

        drink.update()
        return jsonify({
            'success': True,    
            'drinks': [drink.long()]
        })

    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    '''
        requiers delete:drinks permission
        deletes id where id is the id of the deleted record 
    '''
    try:
      drink = Drink.query.filter(Drink.id == id).one_or_none()
      if drink is None:
        abort(404)
      else:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(422)


## Error Handling

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
      "success": False,
      "error": e.code,
      "message": e.name
    }), e.code


@app.errorhandler(AuthError)
def handle_AuthException(e):
    return jsonify({
      "success": False, 
      "error": e.status_code,
      "message": e.error
      }), e.status_code