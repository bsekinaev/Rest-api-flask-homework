from flask import Flask, request, jsonify
from models import db, Ads

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


# Создание
@app.route('/ads', methods=['POST'])
def create_ad():
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'description', 'owner')):
        return jsonify({'Ошибка': "Неверные данные"}), 400
    ad = Ads(
        title=data["title"],
        description=data["description"],
        owner=data["owner"]
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
def update_ad(ad_id):
    ad = Ads.query.get(ad_id)
    if not ad:
        return jsonify({"Ошибка": "Объявление не найдено!"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"Ошибка": "Неверные данные"}), 400
    if 'title' in data:
        ad.title = data["title"]
    if 'description' in data:
        ad.description = data["description"]
    if 'owner' in data:
        ad.owner = data["owner"]
    db.session.commit()
    return jsonify(ad.to_dict())


# Удаление
@app.route('/ads/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    ad = Ads.query.get(ad_id)
    if not ad:
        return jsonify({"Ошибка": "Объявление не найдено"}), 404
    db.session.delete(ad)
    db.session.commit()
    return jsonify({"Сообщения": "Успешно удалено"}), 200


if __name__ == '__main__':
    app.run(debug=True)