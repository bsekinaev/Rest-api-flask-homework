from flask import Flask, request, jsonify, g
from models import db, Ads, User
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
auth = HTTPBasicAuth()

with app.app_context():
    db.create_all()

# Проверка пользователя Basic Auth
@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        g.current_user = user
        return True
    return False

# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ('email','password')):
        return jsonify({'Ошибка': 'Email или пароль отсутствует'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'Ошибка': 'Пользователь уже существует'}), 409
    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# Создание
@app.route('/ads', methods=['POST'])
@auth.login_required
def create_ad():
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'description')):
        return jsonify({'Ошибка': "Неверные данные"}), 400
    ad = Ads(
        title=data["title"],
        description=data["description"],
        owner_id=g.current_user.id
    )
    db.session.add(ad)
    db.session.commit()
    return jsonify(ad.to_dict()), 201


# Получение
@app.route("/ads/<int:ad_id>", methods=["GET"])
def get_ad(ad_id):
    ad = Ads.query.get(ad_id)
    if not ad:
        return jsonify({"Ошибка": "Объявление не найдено!"}), 404
    return jsonify(ad.to_dict())


# Редактирование
@app.route('/ads/<int:ad_id>', methods=['PUT'])
@auth.login_required
def update_ad(ad_id):
    ad = Ads.query.get(ad_id)
    if not ad:
        return jsonify({"Ошибка": "Объявление не найдено!"}), 404
    if ad.owner_id != g.current_user.id:
        return jsonify({'Ошибка':'Вы можете редактировать только свои объявления'}), 403
    data = request.get_json()
    if not data:
        return jsonify({"Ошибка": "Неверные данные"}), 400
    if 'title' in data:
        ad.title = data["title"]
    if 'description' in data:
        ad.description = data["description"]
    db.session.commit()
    return jsonify(ad.to_dict())


# Удаление
@app.route('/ads/<int:ad_id>', methods=['DELETE'])
@auth.login_required
def delete_ad(ad_id):
    ad = Ads.query.get(ad_id)
    if not ad:
        return jsonify({"Ошибка": "Объявление не найдено"}), 404
    if ad.owner_id != g.current_user.id:
        return jsonify({'Ошибка':"Нет прав на удаление"}), 403
    db.session.delete(ad)
    db.session.commit()
    return jsonify({"Сообщения": "Успешно удалено"}), 200


if __name__ == '__main__':
    app.run(debug=True)