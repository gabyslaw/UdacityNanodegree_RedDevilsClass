import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


carsales = Flask(__name__)

CORS(carsales)

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

carsales.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{DB_USER}:{DB_PASSWORD}@192.168.100.10/vehicles'
)
carsales.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(carsales)


class RedCars(db.Model):
    __tablename__ = "redcars"
    id = db.Column(db.Integer, primary_key=True)
    car_name = db.Column(db.String(100), nullable=False)
    car_type = db.Column(db.String(100), nullable=False)
    car_year = db.Column(db.Integer(), nullable=False)
    car_price = db.Column(db.Float(), nullable=False)
    car_description = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return "<RedCars %r>" % self.car_name


db.create_all()


@carsales.route('/')
def index():
    return jsonify({"message": "Welcome to redcars"})


@cross_origin()
@carsales.route('/addcar', methods=['POST'])
def addcar():
    car_data = request.json

    car_name = car_data['car_name']
    car_type = car_data['car_type']
    car_year = car_data['car_year']
    car_price = car_data['car_price']
    car_description = car_data['car_description']

    car = RedCars(
            car_name=car_name,
            car_type=car_type,
            car_year=car_year,
            car_price=car_price,
            car_description=car_description
        )
    db.session.add(car)
    db.session.commit()

    # TODO: add a new field car_plate_number and ensure the addcar
    # method doesn't save in the database if the plate number exists

    return jsonify({"success": True, "response": "Car successfully added"})


# retrieve all cars
@cross_origin()
@carsales.route('/getcars', methods=['GET'])
def getcars():
    all_cars = []
    cars = RedCars.query.all()
    for car in cars:
        results = {
            "car_id": car.id,
            "car_name": car.car_name,
            "car_type": car.car_type,
            "car_price": car.car_price,
            "car_year": car.car_year,
            "car_description": car.car_description
        }
        all_cars.append(results)

    # TODO: create a getcar by id route

    return jsonify(
        {
            "success": True,
            "cars": all_cars,
            "total_cars": len(cars)
        }
    )


@carsales.route('/updatecar/<int:car_id>', methods=['PATCH'])
def updatecar(car_id):
    car = RedCars.query.get(car_id)

    car_name = request.json['car_name']
    car_price = request.json['car_price']
    car_description = request.json['car_description']

    if car is None:
        abort(404)
    else:
        car.car_name = car_name
        car.car_price = car_price
        car.car_description = car_description

        db.session.add(car)
        db.session.commit()

        return jsonify({
            "success": True,
            "response": "Car successfully updated"
        })


# TODO: Implement Delete method
@carsales.route('/deletecar/<int:car_id>', methods=['DELETE'])
def deletecar(car_id):
    car = RedCars.query.get_or_404(car_id)

    db.session.delete(car)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Car: {car_id} has been deleted'
        })

@carsales.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not Found'
    }), 404

@carsales.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Methos not allowed'
    }), 405

@carsales.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'server error'
    }), 500


if __name__ == '__main__':
    carsales.run(debug=True)
