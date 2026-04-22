import aiosqlite
from werkzeug.security import generate_password_hash
from datetime import datetime

DATABASE_URI = 'ads.db'

async def init_db():
    async with aiosqlite.connect(DATABASE_URI) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')
        await db.commit()

async def get_user_by_email(email):
    async with aiosqlite.connect(DATABASE_URI) as db:
        async with db.execute('SELECT id, email, password_hash FROM users WHERE email = ?', (email,)) as cur:
            row = await cur.fetchone()
            if row:
                return {'id': row[0], 'email': row[1], 'password_hash': row[2]}
    return None

async def create_user(email, password):
    password_hash = generate_password_hash(password)
    try:
        async with aiosqlite.connect(DATABASE_URI) as db:
            await db.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False

async def create_ad(title, description, owner_id):
    created_at = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE_URI) as db:
        cur = await db.execute(
            'INSERT INTO ads (title, description, created_at, owner_id) VALUES (?, ?, ?, ?)',
            (title, description, created_at, owner_id)
        )
        await db.commit()
        return cur.lastrowid

async def get_ad(ad_id):
    async with aiosqlite.connect(DATABASE_URI) as db:
        async with db.execute(
            'SELECT a.id, a.title, a.description, a.created_at, a.owner_id, u.email '
            'FROM ads a JOIN users u ON a.owner_id = u.id WHERE a.id = ?',
            (ad_id,)
        ) as cur:
            row = await cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'created_at': row[3],
                    'owner_id': row[4],
                    'owner_email': row[5]
                }
    return None

async def update_ad(ad_id, title=None, description=None):
    updates = []
    params = []
    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if not updates:
        return
    params.append(ad_id)
    async with aiosqlite.connect(DATABASE_URI) as db:
        await db.execute(f'UPDATE ads SET {", ".join(updates)} WHERE id = ?', params)
        await db.commit()

async def delete_ad(ad_id):
    async with aiosqlite.connect(DATABASE_URI) as db:
        await db.execute('DELETE FROM ads WHERE id = ?', (ad_id,))
        await db.commit()

async def is_ad_owner(ad_id, user_id):
    async with aiosqlite.connect(DATABASE_URI) as db:
        async with db.execute('SELECT owner_id FROM ads WHERE id = ?', (ad_id,)) as cur:
            row = await cur.fetchone()
            return row is not None and row[0] == user_id