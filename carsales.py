import os
from flask import Flask, request, jsonify, abort
# import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
# updated
from dotenv import load_dotenv
load_dotenv()
# create .env file and setup secretes
user = os.getenv('u_name')
passwd = os.getenv('password')
carsales = Flask(__name__)

CORS(carsales)

carsales.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{user}:{passwd}@localhost/vehicles'
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
    car_plate_number = db.Column(db.String(100), unique=True, nullable=False)

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
    car_plate = car_data['car_plate']
    # updated
    check_plate = RedCars.query.filter(
        RedCars.car_plate_number == car_plate
    ).one_or_none()

    if check_plate is None:
        car = RedCars(
            car_name=car_name,
            car_type=car_type,
            car_year=car_year,
            car_price=car_price,
            car_description=car_description,
            car_plate_number=car_plate
        )
        db.session.add(car)
        db.session.commit()
        return jsonify({"success": True, "response": "Car successfully added"})
    else:
        abort(422)


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

    return jsonify(
        {
            "success": True,
            "cars": all_cars,
            "total_cars": len(cars)
        }
    )


# updated
@carsales.route('/getcar/<int:id>', methods=['GET'])
def get_car_by_id(id):
    try:
        get_car = RedCars.query.filter(RedCars.id == id).one_or_none()
        if get_car is None:
            abort(404)
        else:
            results = {
                "car_id": get_car.id,
                "car_name": get_car.car_name,
                "car_type": get_car.car_type,
                "car_price": get_car.car_price,
                "car_year": get_car.car_year,
                "car_plate": get_car.car_plate_number,
                "car_description": get_car.car_description
            }
            return jsonify({
                'success': True,
                'results': results,
            })
    except:
        abort(404)


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

        return jsonify({"success": True, "response": "Car successfully updated"})


# TODO: Implement Delete method
@carsales.route('/getcars/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    car = RedCars.query.get_or_404(car_id)

    db.session.delete(car)
    db.session.commit()


@carsales.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
        }), 400


@carsales.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
        }), 404


@carsales.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
        }), 405


@carsales.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'server error'
        }), 500

# def connection():
#     s = 'localhost' #my server name
#     d = 'vehicles' #my database
#     u = 'postgres' #my username
#     p = 'password' #my password

#     conn = psycopg2.connect(host=s, user=u, password=p, database=d)
#     return conn

# @carsales.route('/')
# def main():
#     cars = []
#     conn = connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM RedDevilCars")
#     for row in cursor.fetchall():
#         cars.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
#     conn.close()
#     return render_template("carslist.html", cars = cars)

# @carsales.route('/addcar', methods=['GET', 'POST'])
# def addcar():
#     if request.method == 'GET':
#         return render_template("addcar.html")
#     if request.method == 'POST':
#         id = int(request.form["id"])
#         name = request.form["name"]
#         year = int(request.form["year"])
#         price = float(request.form["price"])

#         conn = connection()
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO RedDevilCars (id, name, year, price) VALUES (%s, %s, %s, %s)", (id, name, year, price))
#         conn.commit()
#         conn.close()
#         return redirect('/')

# @carsales.route('/updatecar/<int:id>', methods=['GET', 'POST'])
# def updatecar(id):
#     cr = []
#     conn = connection()
#     cursor = conn.cursor()
#     if request.method == 'GET':
#         cursor.execute("SELECT * FROM RedDevilCars where id = %s", (str(id)))
#         for row in cursor.fetchall():
#             cr.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
#         conn.close()
#         return render_template("addcar.html", car = cr[0])

#     if request.method == 'POST':
#         name = str(request.form["name"])
#         year = int(request.form["year"])
#         price = float(request.form["price"])

#         cursor.execute("UPDATE RedDevilCars SET name = %s, year = %s, price = %s where id = %s", (name, year, price, id))
#         conn.commit()
#         conn.close()
#         return redirect('/')

# @carsales.route('/deletecar/<int:id>')
# def deletecar(id):
    # conn = connection()
    # cursor = conn.cursor()
    # cursor.execute("DELETE FROM RedDevilCars WHERE id = %s", (str(id)))
    # conn.commit()
    # conn.close()
    # return redirect('/')


if __name__ == '__main__':
    carsales.run(debug=True)
