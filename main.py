from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import hashlib
import sqlite3
import uvicorn

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_username(request: Request):
    return request.cookies.get('username')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    username = get_username(request)
    is_logged_in = username is not None

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute("""
        SELECT messages.message, messages.created_at, users.username, users.age
        FROM messages
        JOIN users ON messages.sender_id = users.id
        ORDER BY messages.created_at DESC
    """)
    messages = [
        {'message': row[0], 'created_at': row[1], 'username': row[2], 'age': row[3]}
        for row in cur.fetchall()
    ]
    con.close()

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': is_logged_in,
            'messages': messages,
        }
    )


@app.get('/login', response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={'is_logged_in': False, 'error': None}
    )


@app.post('/login', response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute(
        'SELECT id FROM users WHERE username = ? AND password = ?',
        (username, hash_password(password)),
    )
    user = cur.fetchone()
    con.close()

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={'is_logged_in': False, 'error': 'Invalid username or password.'}
        )

    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='username', value=username)
    return response


@app.get('/logout')
async def logout():
    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie('username')
    return response


@app.get('/create_message', response_class=HTMLResponse)
async def create_message_get(request: Request):
    username = get_username(request)
    if username is None:
        return RedirectResponse(url='/login', status_code=303)
    return templates.TemplateResponse(
        request=request,
        name='create_message.html',
        context={'is_logged_in': True}
    )


@app.post('/create_message', response_class=HTMLResponse)
async def create_message_post(
    request: Request,
    message: str = Form(),
):
    username = get_username(request)
    if username is None:
        return RedirectResponse(url='/login', status_code=303)

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    cur.execute(
        'INSERT INTO messages (sender_id, message) VALUES (?, ?)',
        (user[0], message),
    )
    con.commit()
    con.close()

    return RedirectResponse(url='/', status_code=303)


@app.get('/create_user', response_class=HTMLResponse)
async def create_user_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='create_user.html',
        context={'is_logged_in': False, 'error': None}
    )


@app.post('/create_user', response_class=HTMLResponse)
async def create_user_post(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    password_confirm: str = Form(),
    age: int = Form(),
):
    if password != password_confirm:
        return templates.TemplateResponse(
            request=request,
            name='create_user.html',
            context={'is_logged_in': False, 'error': 'Passwords do not match.'}
        )

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    try:
        cur.execute(
            'INSERT INTO users (username, password, age) VALUES (?, ?, ?)',
            (username, hash_password(password), age),
        )
        con.commit()
    except sqlite3.IntegrityError:
        con.close()
        return templates.TemplateResponse(
            request=request,
            name='create_user.html',
            context={'is_logged_in': False, 'error': f'Username "{username}" is already taken.'}
        )
    con.close()

    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='username', value=username)
    return response


@app.get('/messages.json')
async def messages_json():
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute("""
        SELECT messages.message, messages.created_at, users.username
        FROM messages
        JOIN users ON messages.sender_id = users.id
        ORDER BY messages.created_at DESC
    """)
    messages = [
        {'message': row[0], 'created_at': row[1], 'username': row[2]}
        for row in cur.fetchall()
    ]
    con.close()
    return JSONResponse(content=messages)


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8080, reload=True)
