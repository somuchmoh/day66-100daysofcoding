from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def get_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify({'cafe': {
        'id': random_cafe.id,
        'name': random_cafe.name,
        'location': random_cafe.location,
        'seats': random_cafe.seats,
        'has_toilet': random_cafe.has_toilet,
        'has_wifi': random_cafe.has_wifi,
        'has_sockets': random_cafe.has_sockets,
        'can_take_calls': random_cafe.can_take_calls,
        'coffee_price': random_cafe.coffee_price,
        'map_url': random_cafe.map_url,
        'img_url': random_cafe.img_url
    }})


@app.route("/all", methods=['GET'])
def get_all_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    cafe_dict = {}
    for cafe in all_cafes:
        cafe_a = cafe.to_dict()
        cafe_dict[cafe.id] = cafe_a
    return jsonify(cafe_dict)


@app.route('/search/<loc>', methods=['GET'])
def find_cafe(loc):
    result = db.session.execute(db.select(Cafe).where(Cafe.location == loc))
    all_cafes = result.scalars().all()
    cafe_dict = {}
    for cafe in all_cafes:
        cafe_a = cafe.to_dict()
        cafe_dict[cafe.id] = cafe_a
    if cafe_dict != {}:
        return jsonify(cafe_dict)
    else:
        return {"error": {
            "Not Found": "Sorry, we don't have a cafe in that location"
        }}


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['GET','POST'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})



# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
