# EduShare - Test Sənədləşdirməsi (Testing Documentation)

Bu sənəd EduShare təhsil platformasının funksionallığını, təhlükəsizliyini və davamlılığını yoxlamaq üçün həyata keçirilən avtomatlaşdırılmış və manual test proseslərini əhatə edir.

## 1. Avtomatlaşdırılmış Testlər (Automated Testing)

Sistemin əsas arxitekturası və mühüm marşrutları (routes) Python-un `pytest` kitabxanası vasitəsilə avtomatlaşdırılmış şəkildə test edilmişdir. Testlər əsas məlumat bazasına zərər verməmək üçün müvəqqəti RAM (memory) bazası üzərində izolyasiya edilmiş mühitdə aparılır.

### Testlərin İşə Salınması

Test mühitini qurmaq və testləri icra etmək üçün terminalda aşağıdakı əmrlər daxil edilməlidir:

```bash
# PyTest kitabxanasının quraşdırılması
pip install pytest

# Testlərin ətraflı (verbose) rejimdə işə salınması
python -m pytest testapp.py -v