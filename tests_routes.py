import pytest
from app import create_app, db
from app.models import User, Tutorial

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def new_user():
    user = User(username='testuser', email='test@example.com', password='testpassword')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def new_tutorial(new_user):
    tutorial = Tutorial(title='Test Tutorial', content='This is a test tutorial.', author_id=new_user.id)
    db.session.add(tutorial)
    db.session.commit()
    return tutorial

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Web Development Tutorials' in response.data

def test_tutorial_detail(client, new_tutorial):
    response = client.get(f'/tutorial/{new_tutorial.id}')
    assert response.status_code == 200
    assert b'Test Tutorial' in response.data

def test_login(client, new_user):
    response = client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
    assert response.status_code == 200
    assert b'Login successful' in response.data
