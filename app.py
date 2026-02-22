import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flasgger import Swagger

app = Flask(__name__)
app.secret_key = 'edushare_gizli_acar'


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edushare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


SWAGGER_PATH = os.path.join(BASE_DIR, 'static', 'swagger.json')
swagger = Swagger(app, template_file=SWAGGER_PATH)


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, default=5)
    students = db.Column(db.Integer, default=0)

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    replies = db.Column(db.Integer, default=0)


with app.app_context():
    db.create_all()
    
    if not Mentor.query.first():
        mentor1 = Mentor(name="Aysel Məmmədova", subject="Riyaziyyat", rating=5, students=12)
        mentor2 = Mentor(name="Kamran Əliyev", subject="IT/Proqramlaşdırma", rating=4, students=8)
        mentor3 = Mentor(name="Leyla Quliyeva", subject="Xarici Dil", rating=5, students=15)
        db.session.add_all([mentor1, mentor2, mentor3])
        db.session.commit()

    if not ForumPost.query.first():
        post1 = ForumPost(author="Orxan V.", title="Python-da dövrləri necə optimallaşdırmaq olar?", replies=5)
        post2 = ForumPost(author="Nigar K.", title="Tarix imtahanı üçün hansı mənbələr yaxşıdır?", replies=2)
        db.session.add_all([post1, post2])
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        session['istifadeci_adi'] = user
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))

    subject_filter = request.args.get('subject')
    search_query = request.args.get('search') 

    query = Resource.query
    if search_query:
        query = query.filter(Resource.title.contains(search_query))
    if subject_filter and subject_filter != 'Hamısı':
        query = query.filter_by(subject=subject_filter)

    resources = query.all()
    return render_template('index.html', resources=resources)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        author = request.form['author'] 
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_resource = Resource(title=title, subject=subject, author=author, filename=filename)
            db.session.add(new_resource)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/profile')
def profile():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))
    
    ad = session['istifadeci_adi']
    my_resources = Resource.query.filter_by(author=ad).all() 
    return render_template('profile.html', user=ad, username=ad, resources=my_resources)

@app.route('/logout')
def logout():
    session.pop('istifadeci_adi', None)
    return redirect(url_for('login'))

@app.route('/mentors')
def mentors():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))
    real_mentors = Mentor.query.all()
    return render_template('mentors.html', mentors=real_mentors)

@app.route('/forum')
def forum():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))
    real_posts = ForumPost.query.all()
    return render_template('forum.html', posts=real_posts)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_resource(id):
    resource_to_delete = Resource.query.get_or_404(id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], resource_to_delete.filename))
    except:
        pass 
    db.session.delete(resource_to_delete)
    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)