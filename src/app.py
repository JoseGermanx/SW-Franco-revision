"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Vehicles, Favorite_Characters, Favorite_Planets, Favorite_Vehicles
import datetime
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():

    users = User.query.all()

    return jsonify([user.serialize() for user in users]), 200


@app.route('/characters', methods=['GET'])
def get_characters():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_single_character():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/planets', methods=['GET'])
def get_planets():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/vehicles', methods=['GET'])
def get_vehicles():

    response_body = {
        "msg": "Hello, this is your GET /vehicles response "
    }

    return jsonify(response_body), 200


@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_single_vehicle():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200



@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_single_favorite_character(character_id):
    
    user_id = 2
    user = User.query.get(user_id)
    if not user:
        return jsonify({"Message": "User not found."}), 404
    
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({"Message": "Character not found."}), 404
    if Favorite_Characters.query.filter_by(user_id = user_id, character_id = character_id).first():
        return jsonify({"Message": "Character is already on user's favorites"}), 400
    
    favorite_character = Favorite_Characters(user_id = user_id, character_id = character_id)
    db.session.add(favorite_character)
    db.session.commit()

    return jsonify({"Message": "The character was added to the user's favorites."}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_single_favorite_planet(planet_id):
    
    user_id = 2
    user = User.query.get(user_id)
    if not user:
        return jsonify({"Message": "User not found."}), 404
    
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"Message": "Planet not found."}), 404
    if Favorite_Planets.query.filter_by(user_id = user_id, planet_id = planet_id).first():
        return jsonify({"Message": "The planet is already on user's favorites"}), 400
    
    favorite_planet = Favorite_Planets(user_id = user_id, planet_id = planet_id)
    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({"Message": "The planet was added to the user's favorites."}), 201


@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['POST'])
def add_single_favorite_vehicle(vehicle_id):
    
    user_id = 2
    user = User.query.get(user_id)
    if not user:
        return jsonify({"Message": "User not found."}), 404
    
    vehicle = Vehicles.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"Message": "Vehicle not found."}), 404
    if Favorite_Vehicles.query.filter_by(user_id = user_id, vehicle_id = vehicle_id).first():
        return jsonify({"Message": "The vehicle is already on user's favorites"}), 400
    
    favorite_vehicle = Favorite_Vehicles(user_id = user_id, vehicle_id = vehicle_id)
    db.session.add(favorite_vehicle)
    db.session.commit()

    return jsonify({"Message": "The vehicle was added to the user's favorites."}), 201


@app.route('/user/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 2

    favorite_characters = db.session.query(Favorite_Characters, Characters)\
    .join(Characters, Favorite_Characters.character_id == Characters.id)\
    .filter(Favorite_Characters.user_id == user_id)\
    .all()

    favorite_planets = db.session.query(Favorite_Planets, Planets)\
    .join(Planets, Favorite_Planets.planet_id == Planets.id)\
    .filter(Favorite_Planets.user_id == user_id)\
    .all()

    favorite_vehicles = db.session.query(Favorite_Vehicles, Vehicles)\
    .join(Vehicles, Favorite_Vehicles.vehicle_id == Vehicles.id)\
    .filter(Favorite_Vehicles.user_id == user_id)\
    .all()

    response = {
        "favorite_characters": [
            {
            "id": fav_characters.id,
            "character_id": fav_characters.character_id,
            "character_name": characters.name,
            }
            for fav_characters, characters in favorite_characters
        ],
        
        "favorite_planets": [
            {
            "id": fav_planets.id,
            "planet_id": fav_planets.planet_id,
            "planet_name": planets.name,
            }
            for fav_planets, planets in favorite_planets
        ],

        "favorite_vehicles": [
            {
            "id": fav_vehicles.id,
            "vehicle_id": fav_vehicles.vehicle_id,
            "vehicle_name": vehicles.name,
            }
            for fav_vehicles, vehicles in favorite_vehicles
        ]
    }

    return jsonify(response), 200

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):

    user_id = 2 
    user = User.query.get(user_id)
    if not user:
        return jsonify({"Message": "User not found."}), 404
    favorite_character = Favorite_Characters.query.filter_by(user_id=user_id, character_id= character_id).first()
    if not favorite_character:
        return jsonify({"Message": "The character is not a favorite."}), 404
    db.session.delete(favorite_character)
    db.session.commit()
    return jsonify({"Message": "Character deleted from favorites."}), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    user_id = 2 
    user = User.query.get(user_id)
    if not user:
        return jsonify({"Message": "User not found."}), 404
    favorite_planet = Favorite_Planets.query.filter_by(user_id=user_id, planet_id= planet_id).first()
    if not favorite_planet:
        return jsonify({"Message": "The planet is not a favorite."}), 404
    db.session.delete(favorite_planet)
    db.session.commit()
    return jsonify({"Message": "Planet deleted from favorites."}), 200

@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_favorite_vehicle(vehicle_id):

    user_id = 2 
    user = User.query.get(user_id)
    if not user:
        return jsonify({"Message": "User not found."}), 404
    favorite_vehicle = Favorite_Vehicles.query.filter_by(user_id=user_id, vehicle_id = vehicle_id).first()
    if not favorite_vehicle:
        return jsonify({"Message": "The vehicle is not a favorite."}), 404
    db.session.delete(favorite_vehicle)
    db.session.commit()
    return jsonify({"Message": "Vehicle deleted from favorites."}), 200

with app.app_context():
    existing_user = User.query.filter_by(email = 'mail@test.com').first()
    if not existing_user:
        new_user = User(
            username = 'User1',
            name = 'User',
            lastname = 'One',
            email = 'mail@test.com',
            subscription_date = datetime.datetime(2020, 5, 17),
            password = '123456'
        )
        db.session.add(new_user)
        db.session.commit()

with app.app_context():
    luke_skywalker = Characters.query.filter_by(name = 'Luke Skywalker').first()
    if not luke_skywalker:
        luke_skywalker = Characters(
            name = 'Luke Skywalker',
            age = 22,
            eye_color = 'Blue',
            hair_color = 'Blonde'
        )
        db.session.add(luke_skywalker)

    c3po = Characters.query.filter_by(name = 'C3PO').first()
    if not c3po:
        c3po = Characters(
            name = 'C3PO',
            age = 99,
            eye_color = 'Yellow',
            hair_color = 'None'
        )
        db.session.add(c3po)
    
        db.session.commit()

with app.app_context():
    alderaan = Planets.query.filter_by(name = 'Alderaan').first()
    if not alderaan:
        alderaan = Planets(
            name = 'Alderaan',
            diameter = 12500,
            terrain = 'Desert',
            population = 2000000000
        )
        db.session.add(alderaan)

    tatooine = Planets.query.filter_by(name = 'Tatooine').first()
    if not tatooine:
        tatooine = Planets(
            name = 'Tatooine',
            diameter = 12500,
            terrain = 'Lake',
            population = 2000000000
        )
        db.session.add(tatooine)
    
        db.session.commit()

with app.app_context():
    sand_crawler = Vehicles.query.filter_by(name = 'Sand Crawler').first()
    if not sand_crawler:
        sand_crawler = Vehicles(
            name = 'Sand Crawler',
            model = 'Digger Crawler',
            crew = 46,
            passengers = 30
        )
        db.session.add(sand_crawler)

    t_16_skyhopper = Vehicles.query.filter_by(name = 'T-16 skyhopper').first()
    if not t_16_skyhopper:
        t_16_skyhopper = Vehicles(
            name = 'T-16 skyhopper',
            model = 'T-16 skyhopper',
            crew = 1,
            passengers = 1
        )
        db.session.add(t_16_skyhopper)
    
        db.session.commit()


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
