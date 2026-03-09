from app import app
from models import db, User, Mentor, ForumPost, ForumReply, Message, MentorApplication, Report

def seed_data():
    with app.app_context():
        db.drop_all() 
        db.create_all()
        
        admin = User(username="Admin", email="admin@edushare.az", password="123", role="Admin", university="EduShare Team", course=0)
        telebe1 = User(username="Orxan V.", email="orxan@mail.com", password="123", role="Tələbə", university="Bakı Dövlət Universiteti", course=2)
        mentor_user = User(username="Aysel M.", email="aysel@mail.com", password="123", role="Mentor", university="Azərbaycan Dövlət İqtisad Universiteti", course=4)
        
        db.session.add_all([admin, telebe1, mentor_user])
        db.session.commit()

        mentor1 = Mentor(user_id=mentor_user.id, subject="Riyaziyyat", rating=5.0, students=12)
        db.session.add(mentor1)
        
        post1 = ForumPost(author_id=telebe1.id, title="Python-da dövrləri necə optimallaşdırmaq olar?")
        db.session.add(post1)
        db.session.commit()

        reply1 = ForumReply(post_id=post1.id, author_id=mentor_user.id, content="List comprehension istifadə etmək dövrləri xeyli sürətləndirir.", likes=3)
        db.session.add(reply1)
        db.session.commit()
        
        print("Məlumat bazası quruldu! Admin hesabı: Admin | Şifrə: 123")

if __name__ == '__main__':
    seed_data()