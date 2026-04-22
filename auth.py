from aiohttp import web, hdrs
import base64
from models import get_user_by_email
from werkzeug.security import check_password_hash


async def check_basic_auth(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        raise web.HTTPUnauthorized(
            text='{"Ошибка": "Authorization header отсутствует или имеет неправильную форму"}',
            headers={'WWW-Authenticate': 'Basic realm="Access"'}
        )
    encoded = auth_header[6:]
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        email, password = decoded.split(':', 1)
    except Exception:
        raise web.HTTPUnauthorized(
            text='{"Ошибка": "Неверный формат учетных данных"}',
            headers={'WWW-Authenticate': 'Basic realm="Access"'}
        )
    user = await get_user_by_email(email)
    if not user:
        raise web.HTTPUnauthorized(
            text='{"Ошибка": "Неверный email или пароль"}',
            headers={'WWW-Authenticate': 'Basic realm="Access"'}
        )
    if not check_password_hash(user['password_hash'], password):
        raise web.HTTPUnauthorized(
            text='{"Ошибка": "Неверный email или пароль"}',
            headers={'WWW-Authenticate': 'Basic realm="Access"'}
        )
    return user


def login_required(handler):
    async def wrapper(request):
        request.user = await check_basic_auth(request)
        return await handler(request)
    return wrapper
