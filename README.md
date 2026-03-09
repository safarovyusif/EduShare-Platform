# 🎓 EduShare - Təhsil və Ünsiyyət Platforması

EduShare, tələbələrin dərs materiallarını paylaşdığı, təcrübəli mentorlarla əlaqə qurduğu və sual-cavab forumu vasitəsilə bilik mübadiləsi etdiyi vahid, interaktiv veb platformadır.

🚀 **Canlı Demo (Deploy olunmuş versiya):** [edushare.pythonanywhere.com](https://edushare.pythonanywhere.com/)

---

## ✨ Əsas Funksionallıqlar (Features)

### 🔐 Rol Əsaslı İdarəetmə və Təhlükəsizlik (RBAC)
* **3 Fərqli Rol:** Tələbə, Mentor və Admin rollarına uyğun xüsusi icazə sistemi.
* **Qeydiyyat & Giriş:** Tələbələrin universitet və kurs məlumatları ilə birlikdə sistemdə tam qeydiyyatı.
* **Fayl Təhlükəsizliyi:** Zərərli faylların qarşısını almaq üçün arxa planda uzantı yoxlanışı (yalnız `.pdf`, `.ppt`, `.doc`) və hər fayl üçün maksimum 10MB ölçü limiti.

### 📚 Material və Resurs İdarəetməsi
* **Ağıllı Axtarış & Filtr:** Fənlər üzrə kateqoriyalaşdırma və mövzu adına görə sürətli axtarış imkanı.
* **Səhifələmə (Pagination):** Sistem performansının düşməməsi üçün yüklənən resursların avtomatik səhifələrə bölünməsi.
* **Şəxsi Kabinet:** İstifadəçilərin yalnız öz yüklədiyi materialları silə bilməsi və profil (ad, e-poçt, şifrə) yeniləməsi.

### 💬 "Reddit" Tipli Sual-Cavab Forumu
* **Mövzu və Şərhlər:** Tələbələrin və mentorların suallar verib müzakirələr apara biləcəyi forum arxitekturası.
* **İnteraktiv Qiymətləndirmə:** Şərhlər üçün *Upvote* (Bəyən) və *Downvote* (Bəyənmə) mexanizmi.
* **Sürətli Naviqasiya:** Səhifələmə sistemi və mövzular daxilində sözə görə axtarış funksiyası.

### ✉️ Şəxsi Mesajlaşma (DM)
* **Mesaj Qutusu:** İstifadəçilərin bir-birinə və ya birbaşa mentorlara şəxsi mesaj göndərə bilməsi.
* **Canlı Bildiriş:** Oxunmamış yeni mesajlar gəldikdə Navbar üzərində qırmızı bildiriş (işığ) xəbərdarlığı.

### 🌟 Mentorluq Sistemi və İdarəetmə Paneli
* **Mentorluğa Müraciət:** Tələbələrin platformada rəsmi mentor olmaq üçün adminə müraciət formu göndərməsi.
* **Admin Panel:** Moderatorların mentor müraciətlərini təsdiq/rədd etməsi, şikayətləri oxuyub həll etməsi və zərərli postları tamamilə silmə səlahiyyəti.

---

## 🛠 Texnologiya Stack-i (Tech Stack)

* **Backend:** Python, Flask Framework
* **Verilənlər Bazası:** SQLite (Flask-SQLAlchemy ORM)
* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2 Template Engine
* **API Sənədləşdirməsi:** Flasgger (Swagger UI v2.0)
* **Test & QA:** PyTest (Avtomatlaşdırılmış Testlər)
* **Deployment:** PythonAnywhere

---

## 📁 Layihə Strukturu

```text
├── app.py                # Əsas tətbiq məntiqi və Flask marşrutları (Routes)
├── models.py             # SQLAlchemy verilənlər bazası modelləri (User, Post, Reply, Message və s.)
├── seed_db.py            # Baza strukturunun və test datalarının avtomatik yaradılması
├── test_app.py           # PyTest ilə avtomatlaşdırılmış test ssenariləri
├── instance/
│   └── edushare.db       # SQLite verilənlər bazası
├── static/
│   └── swagger.json      # OpenAPI/Swagger sənədləşdirmə faylı
├── templates/            # HTML Şablonları (Jinja2)
│   ├── base.html         # Əsas struktur və Navbar
│   ├── index.html        # Ana səhifə və resursların siyahısı
│   ├── forum.html        # Sual-Cavab forumu
│   ├── post_detail.html  # Forum mövzusu və şərhlər
│   ├── messages.html     # Daxil olan və göndərilən mesajlar qutusu
│   ├── admin_panel.html  # Admin moderasiya paneli
│   ├── profile.html      # Şəxsi kabinet və tənzimləmələr
│   └── ... 
└── uploads/              # Serverdə saxlanılan dərs materialları
