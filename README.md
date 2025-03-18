# MiraclGS Quiz App

Bu uygulama, öğretmenlerin soru ekleyebildiği ve öğrencilerin quiz çözebildiği bir web uygulamasıdır.

## Özellikler

- Koyu tema tasarım (Bootstrap)
- Kullanıcı yönetimi (Öğrenci, Öğretmen, Yönetici)
- Ders bazlı soru kategorizasyonu
- Konuya göre filtreleme
- Görsel destekli sorular
- Quiz sonunda skor çıktısı
- Admin ve öğretmen panelleri

## Hızlı Başlangıç

1. Bağımlılıkları yükleyin:
```
pip install -r requirements.txt
```

2. Veritabanını oluşturun:
```
python init_db.py
```

3. Admin kullanıcısı oluşturun:
```
python setup_admin.py admin şifre123
```

4. Uygulamayı çalıştırın:
```
python app.py
```

5. Tarayıcınızda şu adresi açın: http://127.0.0.1:5000

## Geliştirme Ortamı

Uygulama geliştirme modunda çalıştığında SQLite veritabanı kullanır. Bu mod hızlı geliştirme ve test için uygundur.

## Canlı Ortama Dağıtım

Ayrıntılı dağıtım talimatları için `deploy.md` dosyasına bakın.

### PythonAnywhere ile Dağıtım (Özet)
1. PythonAnywhere'de bir hesap oluşturun
2. Projeyi yükleyin ve sanal ortam oluşturun
3. Veritabanını oluşturun ve admin kullanıcısı ekleyin
4. WSGI dosyasını yapılandırın
5. Web uygulamasını başlatın

### Heroku ile Dağıtım (Özet)
1. Heroku CLI ile oturum açın
2. Uygulama ve PostgreSQL veritabanı oluşturun
3. Ortam değişkenlerini ayarlayın
4. Uygulamayı dağıtın
5. Veritabanını ve admin kullanıcısını oluşturun

## Kullanım

1. Admin kullanıcısıyla giriş yapın (yukarıda oluşturulan)
2. Yönetici panelinden dersler ekleyin
3. Öğretmen olarak soru ekleyin
4. Öğrenci hesabıyla quizleri çözün ve sonuçlarınızı görün

## Kullanıcı Tipleri

- **Öğrenci**: Quizleri çözebilir, sonuçlarını görebilir
- **Öğretmen**: Soru ekleyebilir, kendi sorularını görebilir
- **Yönetici**: Ders ekleyebilir, tüm soruları ve kullanıcıları görebilir

## Proje Yapısı

- app.py: Ana uygulama dosyası
- app_production.py: Canlı ortam için çalıştırma dosyası
- config.py: Uygulama yapılandırması
- wsgi.py: WSGI giriş noktası
- init_db.py: Veritabanı şeması oluşturma betiği
- setup_admin.py: Admin kullanıcısı oluşturma betiği
- deploy.md: Dağıtım talimatları
- templates/: HTML şablonları
- static/: Statik dosyalar (CSS, JS, resimler)
- instance/: SQLite veritabanı dosyası (geliştirme ortamı için)
- .env: Ortam değişkenleri 