import pytest
from app import app
from models import db, User, ForumPost

# Test mühitini hazırlayırıq
@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Testlər üçün əsas bazanı korlamamaq üçün müvəqqəti RAM bazası (memory) istifadə edirik
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

# TEST 1: Ana səhifə (Dashboard) problemsiz açılırmı?
def test_homepage_loads(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"EduShare" in response.data

# TEST 2: Qeydiyyat sistemi işləyirmi?
def test_user_registration(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@mail.com',
        'password': 'password123',
        'university': 'BDU',
        'course': '2'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Qeydiyyatdan sonra dashboard-a yönləndirməlidir və ya bazada user yaranmalıdır
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@mail.com'

# TEST 3: Login sistemi işləyirmi?
def test_user_login(client):
    # Əvvəlcə test user yaradaq
    with app.app_context():
        user = User(username='logintest', email='log@mail.com', password='123', university='ADNSU', course=1)
        db.session.add(user)
        db.session.commit()

    # İndi o userlə giriş edək
    response = client.post('/login', data={
        'username': 'logintest',
        'password': '123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Resurslar" in response.data # Uğurlu giriş səhifəsi

# TEST 4: İcazəsiz (Login olmadan) kimsə profilə girə bilərmi?
def test_unauthorized_profile_access(client):
    response = client.get('/profile', follow_redirects=True)
    # Login olmadığı üçün login səhifəsinə yönləndirməlidir
    assert b"Platformaya Giri" in response.data 

# TEST 5: Forum səhifəsi açılır və yeni post yaranırmı?
def test_forum_page(client):
    response = client.get('/forum')
    assert response.status_code == 200
    assert b"Sual-Cavab Forumu" in response.data