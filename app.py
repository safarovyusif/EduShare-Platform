import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Yaddaşın işləməsi üçün gizli açar
app.secret_key = 'edushare_gizli_acar'

# --- Konfiqurasiya ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edushare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Verilənlər Bazası Modeli ---
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

# Bazanı yaratmaq
with app.app_context():
    db.create_all()

# --- ROUTES (Səhifələr) ---

# 1. Giriş Səhifəsi (Sayt açılanda birinci bura gələcək)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Formdan yazılan istifadəçi adını alırıq
        user = request.form.get('username')
        # Onu sistemin yaddaşına (session) yazırıq
        session['istifadeci_adi'] = user
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# 2. Ana Səhifə (Dashboard)
@app.route('/dashboard')
def dashboard():
    # Əgər yaddaşda istifadəçi adı yoxdursa (giriş etməyibsə), Loginə atırıq
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))

    # Filterləmə məntiqi
    subject_filter = request.args.get('subject')
    search_query = request.args.get('search') 

    query = Resource.query

    if search_query:
        query = query.filter(Resource.title.contains(search_query))

    if subject_filter and subject_filter != 'Hamısı':
        query = query.filter_by(subject=subject_filter)

    resources = query.all()
    return render_template('index.html', resources=resources)

# 3. Resurs Yüklə
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Təhlükəsizlik: Giriş etməyibsə Loginə atır
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        # Müəllif adını avtomatik session-dan (yaddaşdan) da götürə bilərik, amma hələlik formadan qalır
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

# 4. Şəxsi Kabinet
@app.route('/profile')
def profile():
    # Təhlükəsizlik: Giriş etməyibsə Loginə atır
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))
    
    # Yaddaşdakı adı alıb HTML-ə göndəririk
    ad = session['istifadeci_adi']
    my_resources = Resource.query.all() 
    
    # HTML-ə həm user, həm username olaraq ötürürük ki, köhnə kodlar xarab olmasın
    return render_template('profile.html', user=ad, username=ad, resources=my_resources)

# 5. Çıxış (Logout)
@app.route('/logout')
def logout():
    # Yaddaşı təmizləyib Loginə qaytarırıq
    session.pop('istifadeci_adi', None)
    return redirect(url_for('login'))

# 6. Mentorluq Sistemi (Statik Data)
@app.route('/mentors')
def mentors():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))
        
    dummy_mentors = [
        {"name": "Aysel Məmmədova", "subject": "Riyaziyyat", "rating": 5, "students": 12},
        {"name": "Kamran Əliyev", "subject": "IT/Proqramlaşdırma", "rating": 4, "students": 8},
        {"name": "Leyla Quliyeva", "subject": "Xarici Dil", "rating": 5, "students": 15},
    ]
    return render_template('mentors.html', mentors=dummy_mentors)

# 7. Sual-Cavab Forumu (Statik Data)
@app.route('/forum')
def forum():
    if 'istifadeci_adi' not in session:
        return redirect(url_for('login'))

    dummy_posts = [
        {"author": "Orxan V.", "title": "Python-da dövrləri necə optimallaşdırmaq olar?", "replies": 5},
        {"author": "Nigar K.", "title": "Tarix imtahanı üçün hansı mənbələr yaxşıdır?", "replies": 2},
    ]
    return render_template('forum.html', posts=dummy_posts)

# 8. SİLMƏK FUNKSİYASI
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

# 9. FAYL ENDİRMƏ FUNKSİYASI
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)