from aiohttp import web
from models import init_db, create_user, get_user_by_email, create_ad, get_ad, update_ad, delete_ad, is_ad_owner
from auth import login_required

app = web.Application()

async def on_startup(app):
    await init_db()
    print('База данных готова')

app.on_startup.append(on_startup)

async def register(request):
    try:
        data = await request.json()
    except:
        return web.json_response({'Ошибка': 'Некорректный JSON'}, status=400)

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return web.json_response({'Ошибка': 'Требуется адрес электронной почты и пароль'}, status=400)

    existing = await get_user_by_email(email)
    if existing:
        return web.json_response({"Ошибка": "Пользователь с таким Email уже существует"}, status=409)

    success = await create_user(email, password)
    if not success:
        return web.json_response({"Ошибка": "Не удалось создать пользователя"}, status=500)

    return web.json_response({"Уведомление": "Пользователь создан"}, status=200)

@login_required
async def create_ad_handler(request):
    try:
        data = await request.json()
    except:
        return web.json_response({"Ошибка": "Некорректный JSON"}, status=400)

    title = data.get('title')
    description = data.get('description')
    if not title or not description:
        return web.json_response({"Ошибка": "Требуется ввести название и описание объявления"}, status=400)

    user = request.user
    ad_id = await create_ad(title, description, user['id'])
    ad = await get_ad(ad_id)
    if ad is None:
        return web.json_response({"Ошибка": "Не удалось создать объявление"}, status=500)
    return web.json_response(ad, status=201)

async def get_ad_handler(request):
    ad_id = int(request.match_info['ad_id'])
    ad = await get_ad(ad_id)
    if not ad:
        return web.json_response({"Ошибка": "Объявление не найдено"}, status=404)
    return web.json_response(ad)

@login_required
async def update_ad_handler(request):
    ad_id = int(request.match_info['ad_id'])
    ad = await get_ad(ad_id)
    if not ad:
        return web.json_response({"Ошибка": "Объявление не найдено"}, status=404)

    if not await is_ad_owner(ad_id, request.user['id']):
        return web.json_response({"Ошибка": "Вы можете редактировать только свои объявления"}, status=403)

    try:
        data = await request.json()
    except:
        return web.json_response({"Ошибка": "Некорректный JSON"}, status=400)

    title = data.get('title')
    description = data.get('description')
    if title is None and description is None:
        return web.json_response({"Ошибка": "Ничего не изменилось"}, status=400)

    await update_ad(ad_id, title, description)
    updated_ad = await get_ad(ad_id)
    return web.json_response(updated_ad)

@login_required
async def delete_ad_handler(request):
    ad_id = int(request.match_info['ad_id'])
    ad = await get_ad(ad_id)
    if not ad:
        return web.json_response({"Ошибка": "Объявление не найдено"}, status=404)

    if not await is_ad_owner(ad_id, request.user['id']):
        return web.json_response({"Ошибка": "Вы можете удалять только свои объявления"}, status=403)

    await delete_ad(ad_id)
    return web.json_response({'Уведомление': 'Объявление удалено'}, status=200)

app.router.add_post('/register', register)
app.router.add_post('/ads', create_ad_handler)
app.router.add_get('/ads/{ad_id}', get_ad_handler)
app.router.add_put('/ads/{ad_id}', update_ad_handler)
app.router.add_delete('/ads/{ad_id}', delete_ad_handler)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)