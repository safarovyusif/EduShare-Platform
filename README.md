# 🎓 EduShare - Təhsil və Resurs Paylaşım Platforması

**EduShare**, tələbələr üçün nəzərdə tutulmuş, tədris materiallarının mərkəzləşdirilmiş şəkildə paylaşılması, axtarılması və idarə edilməsi üçün yaradılmış dinamik veb platformadır.

## 🚀 Canlı Demo
Layihə hal-hazırda PythonAnywhere üzərindən canlı yayımdadır:
🔗 [edushare.pythonanywhere.com](https://edushare.pythonanywhere.com)

Login yerinə istədiyiniz username-i,şifrə yerinə 12345 yazıb dashboarda daxil ola bilərsiniz.

---

## ✨ Əsas Funksionallıqlar (MVP Mərhələsi)

### 🔑 İstifadəçi Girişi və Təhlükəsizlik
* **Sessiya İdarəetməsi:** İstifadəçilər öz adları ilə sistemə daxil olur və sessiya ərzində adları yaddaşda saxlanılır.
* **Təhlükəsiz Çıxış:** Sessiyanın sonlandırılması və sistemdən Logout funksiyası tam inteqrasiya olunub.

### 📊 Dashboard və Resurs İdarəetməsi
* **Ağıllı Axtarış və Filtr:** Fənlər üzrə (Riyaziyyat, IT, Tarix və s.) və mövzu adına görə sürətli axtarış imkanı.
* **Fayl Endirmə:** Yüklənmiş materialların (PDF formatında) real vaxtda serverdən endirilməsi.
* **Dinamik İdarəetmə:** Materialların təsdiqlənmə statusunun izlənilməsi və silinməsi.

### 👤 Şəxsi Kabinet
* **Dinamik Profil:** Giriş edən istifadəçinin adı və məlumatları kabinet bölməsində avtomatik əks olunur.
* **Materialların İdarəedilməsi:** İstifadəçinin öz yüklədiyi faylların siyahısı və bazadan silinməsi imkanı.

---

## 📂 Layihə Strukturu

Layihə mütəşəkkil qovluq iyerarxiyası əsasında qurulub:

```text
├── app.py              # Backend məntiqi, Flask marşrutları və session idarəetməsi
├── instance/
│   └── edushare.db     # SQLite verilənlər bazası (İstifadəçi və resurs dataları)
├── static/
│   └── swagger.json    # API sənədləşməsi (OpenAPI 2.0 standartı)
├── templates/          # HTML5 şablonları (Jinja2 mühərriki ilə)
│   ├── base.html       # Əsas HTML kodları
|   ├── forum.html      # Forum hissəsi
|   ├── index.html      # Ana səhifə (Dashboard)
|   ├── login.html      # Giriş (Authentication) səhifəsi      
│   ├── mentors.html    # Mentor bölməsi
│   ├── profile.html    # Şəxsi kabinet bölməsi
│   └── upload.html     # Fayl yükləmə bölməsi
└── uploads/            # Serverdə saxlanılan tələbə resursları (PDF/Docx)
