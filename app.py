import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from werkzeug.utils import secure_filename
from flasgger import Swagger

from models import db, Resource, Mentor, ForumPost, ForumReply, User, MentorApplication, Message, Report

app = Flask(__name__)
app.secret_key = 'edushare_gizli_acar_super_gizli'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edushare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# YENİ: Maksimum fayl həcmi (10 MB) və icazə verilən uzantılar
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 
ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx', 'doc', 'docx'}

db.init_app(app)

SWAGGER_PATH = os.path.join(BASE_DIR, 'static', 'swagger.json')
swagger = Swagger(app, template_file=SWAGGER_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# YENİ: Əgər kimsə 10MB-dan böyük fayl yükləsə xəta versin
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Faylın həcmi çox böyükdür! Maksimum 10MB yükləyə bilərsiniz.', 'danger')
    return redirect(request.url), 413

@app.context_processor
def inject_user():
    current_user = None
    unread_count = 0
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
        if current_user:
            unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    return dict(current_user=current_user, unread_count=unread_count)

UNIVERSITETLER = [
    "Bakı Dövlət Universiteti (BDU)", "Azərbaycan Dövlət İqtisad Universiteti (UNEC)",
    "Azərbaycan Texniki Universiteti (AzTU)", "ADA Universiteti",
    "Azərbaycan Dövlət Neft və Sənaye Universiteti (ADNSU)", "Bakı Ali Neft Məktəbi (BANM)",
    "Azərbaycan Tibb Universiteti (ATU)", "Azərbaycan Memarlıq və İnşaat Universiteti (AzMİU)",
    "Xəzər Universiteti", "Bakı Mühəndislik Universiteti (BMU)",
    "Milli Aviasiya Akademiyası (MAA)", "Azərbaycan Dövlət Pedaqoji Universiteti (ADPU)", "Digər"
]

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user:
            error = 'Belə bir istifadəçi tapılmadı. <a href="/register" class="alert-link">Qeydiyyatdan keçin</a>.'
        elif user.password != password:
            error = 'Daxil etdiyiniz şifrə yalnışdır!'
        else:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        university = request.form.get('university')
        course = request.form.get('course')
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return "Bu istifadəçi adı və ya e-poçt artıq mövcuddur!"
        new_user = User(username=username, email=email, password=password, university=university, course=course)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('dashboard'))
    return render_template('register.html', universities=UNIVERSITETLER)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('dashboard'))

# YENİLƏNDİ: Resurslarda Pagination (Səhifələmə)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    subject_filter = request.args.get('subject')
    search_query = request.args.get('search') 
    page = request.args.get('page', 1, type=int)
    
    query = Resource.query
    if search_query: query = query.filter(Resource.title.contains(search_query))
    if subject_filter and subject_filter != 'Hamısı': query = query.filter_by(subject=subject_filter)
    
    # Hər səhifədə 5 resurs göstəriləcək
    resources = query.order_by(Resource.id.desc()).paginate(page=page, per_page=5, error_out=False)
    
    return render_template('index.html', resources=resources, subject_filter=subject_filter, search_query=search_query)

# YENİLƏNDİ: Yükləmədə Fayl Təhlükəsizliyi
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        user = User.query.get(session['user_id'])
        
        if 'file' not in request.files:
            flash('Fayl seçilməyib!', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('Fayl seçilməyib!', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_resource = Resource(title=title, subject=subject, author=user.username, filename=filename)
            db.session.add(new_resource)
            db.session.commit()
            flash('Material uğurla yükləndi!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Təhlükəsizlik: Yalnız PDF, PPT, PPTX, DOC və DOCX faylları yükləyə bilərsiniz!', 'danger')
            return redirect(request.url)
            
    return render_template('upload.html')

@app.route('/mentors')
def mentors():
    real_mentors = Mentor.query.all()
    return render_template('mentors.html', mentors=real_mentors)

# YENİLƏNDİ: Forumda Pagination (Səhifələmə)
@app.route('/forum')
def forum():
    search_query = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    
    query = ForumPost.query
    if search_query:
        query = query.filter(ForumPost.title.contains(search_query))
        
    # Hər səhifədə 5 mövzu göstəriləcək
    posts = query.order_by(ForumPost.created_at.desc()).paginate(page=page, per_page=5, error_out=False)
    
    return render_template('forum.html', posts=posts, search_query=search_query)

@app.route('/forum/post/<int:post_id>')
def post_detail(post_id):
    post = ForumPost.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/user/<username>')
def public_profile(username):
    profile_user = User.query.filter_by(username=username).first_or_404()
    resources = Resource.query.filter_by(author=profile_user.username).all()
    replies = ForumReply.query.filter_by(author_id=profile_user.id).order_by(ForumReply.created_at.desc()).all()
    return render_template('public_profile.html', profile_user=profile_user, resources=resources, replies=replies)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    my_resources = Resource.query.filter_by(author=user.username).all() 
    my_replies = ForumReply.query.filter_by(author_id=user.id).order_by(ForumReply.created_at.desc()).all()
    return render_template('profile.html', user=user, resources=my_resources, replies=my_replies)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')
        if new_username and new_username != user.username:
            if User.query.filter_by(username=new_username).first(): return "Bu ad artıq istifadə olunur."
            Resource.query.filter_by(author=user.username).update({'author': new_username})
            user.username = new_username
        if new_email and new_email != user.email:
            if User.query.filter_by(email=new_email).first(): return "Bu e-poçt artıq istifadə olunur."
            user.email = new_email
        if new_password: user.password = new_password
        db.session.commit()
        flash('Profil məlumatlarınız yeniləndi.', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

@app.route('/messages')
def inbox():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    received = Message.query.filter_by(receiver_id=user.id).order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=user.id).order_by(Message.created_at.desc()).all()
    for msg in received:
        if not msg.is_read: msg.is_read = True
    db.session.commit()
    return render_template('messages.html', received=received, sent=sent)

@app.route('/send_message/<int:receiver_id>', methods=['POST'])
def send_message(receiver_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    content = request.form.get('content')
    if content:
        msg = Message(sender_id=session['user_id'], receiver_id=receiver_id, content=content)
        db.session.add(msg)
        db.session.commit()
        flash('Mesajınız göndərildi!', 'success')
    return redirect(request.referrer)

@app.route('/support', methods=['GET', 'POST'])
def support():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        if subject and content:
            new_report = Report(sender_id=session['user_id'], subject=subject, content=content)
            db.session.add(new_report)
            db.session.commit()
            flash('Müraciətiniz adminə göndərildi. Təşəkkür edirik!', 'success')
            return redirect(url_for('support'))
    return render_template('support.html')

@app.route('/mentors/apply', methods=['GET', 'POST'])
def become_mentor():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    existing_app = MentorApplication.query.filter_by(user_id=user.id).order_by(MentorApplication.id.desc()).first()
    if request.method == 'POST':
        subject = request.form.get('subject')
        new_app = MentorApplication(user_id=user.id, subject=subject)
        db.session.add(new_app)
        db.session.commit()
        flash('Müraciətiniz qeydə alındı.', 'success')
        return redirect(url_for('become_mentor'))
    return render_template('become_mentor.html', existing_app=existing_app)

@app.route('/forum/new', methods=['GET', 'POST'])
def new_topic():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            new_post = ForumPost(author_id=session['user_id'], title=title)
            db.session.add(new_post)
            db.session.commit()
            flash('Yeni mövzu yaradıldı!', 'success')
            return redirect(url_for('forum'))
    prefill_title = request.args.get('title', '')
    return render_template('new_topic.html', prefill_title=prefill_title)

@app.route('/forum/post/<int:post_id>/reply', methods=['POST'])
def add_reply(post_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    content = request.form.get('content')
    if content:
        new_reply = ForumReply(post_id=post_id, author_id=session['user_id'], content=content)
        db.session.add(new_reply)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/forum/reply/<int:reply_id>/<action>', methods=['POST'])
def vote_reply(reply_id, action):
    if 'user_id' not in session: return redirect(url_for('login'))
    reply = ForumReply.query.get_or_404(reply_id)
    if action == 'like': reply.likes += 1
    elif action == 'dislike': reply.dislikes += 1
    db.session.commit()
    return redirect(url_for('post_detail', post_id=reply.post_id))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_resource(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    resource_to_delete = Resource.query.get_or_404(id)
    try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], resource_to_delete.filename))
    except: pass 
    db.session.delete(resource_to_delete)
    db.session.commit()
    flash('Fayl bazadan silindi.', 'success')
    return redirect(url_for('profile'))

@app.route('/forum/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    post = ForumPost.query.get_or_404(post_id)
    user = User.query.get(session['user_id'])
    if user.id == post.author_id or user.role == 'Admin':
        db.session.delete(post)
        db.session.commit()
        flash('Sual uğurla silindi.', 'success')
    return redirect(url_for('forum'))

@app.route('/forum/delete_reply/<int:reply_id>', methods=['POST'])
def delete_reply(reply_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    reply = ForumReply.query.get_or_404(reply_id)
    post_id = reply.post_id
    user = User.query.get(session['user_id'])
    if user.id == reply.author_id or user.role == 'Admin':
        db.session.delete(reply)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'Admin': return "İcazə yoxdur."
    pending_mentors = MentorApplication.query.filter_by(status='Gözləyir').all()
    active_mentors = Mentor.query.all()
    reports = Report.query.order_by(Report.created_at.desc()).all()
    all_users = User.query.all()
    return render_template('admin_panel.html', pending_mentors=pending_mentors, active_mentors=active_mentors, reports=reports, users=all_users)

@app.route('/admin/approve_mentor/<int:app_id>')
def approve_mentor(app_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    application = MentorApplication.query.get_or_404(app_id)
    application.status = 'Təsdiqləndi'
    user = application.user
    user.role = 'Mentor'
    if not Mentor.query.filter_by(user_id=user.id).first():
        new_mentor = Mentor(user_id=user.id, subject=application.subject)
        db.session.add(new_mentor)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/reject_mentor/<int:app_id>')
def reject_mentor(app_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    application = MentorApplication.query.get_or_404(app_id)
    application.status = 'Rədd edildi'
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/revoke_mentor/<int:mentor_id>')
def revoke_mentor(mentor_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    mentor_record = Mentor.query.get_or_404(mentor_id)
    user = mentor_record.user
    user.role = 'Tələbə'
    db.session.delete(mentor_record)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/resolve_report/<int:report_id>')
def resolve_report(report_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    report = Report.query.get_or_404(report_id)
    report.status = 'Həll edildi'
    db.session.commit()
    return redirect(url_for('admin_panel'))

if __name__ == "__main__":
    if not os.path.exists('uploads'): os.makedirs('uploads')
    app.run(debug=True)