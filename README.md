# OSTİM Teknik Üniversitesi İzin Portalı


## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed.seed_data
uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed.seed_data
uvicorn app.main:app --reload
```

Swagger arayüzü: `http://127.0.0.1:8000/docs`

## Railway deployment

Proje kök dizininde `Dockerfile` ve `railway.toml` hazırdır. Railway bu repository'yi Docker image üzerinden deploy eder. Container sırasıyla migration çalıştırır, veritabanı boşsa PDF kaynaklı seed verisini yükler ve Railway'in verdiği `PORT` üzerinde Uvicorn'u başlatır.

SQLite kullanıldığı için Railway servisinde kalıcı bir Volume oluşturulmalıdır. Volume mount path olarak `/data` kullanın; Docker veritabanını `/data/izin.db` içinde tutar. Volume kullanılmazsa yeniden deploy veya restart sonrasında SQLite verisi kaybolabilir. Production için Railway Variables bölümünde güçlü ve rastgele bir `JWT_SECRET_KEY` tanımlayın.

Railway CLI ile alternatif deploy:

```bash
railway login
railway link
railway up
```

Demo hesap örnekleri:

- `serdar.muldur@ostimteknik.edu.tr` / `Serdar.muldur123`
- `meltem.eryilmaz@ostimteknik.edu.tr` / `Meltem.eryilmaz123`
- `murat.yulek@ostimteknik.edu.tr` / `Murat.yulek123`

Şifreler veritabanına plaintext olarak yazılmaz; seed sırasında Argon2 hash’i saklanır. Seed politika değerleri demo/configuration amaçlıdır, gerçek üniversite İK politikası değildir. Production’da `.env` içinde güçlü bir `JWT_SECRET_KEY` kullanılmalı, HTTPS arkasında cookie `secure=True` yapılmalıdır.

## Uygulama kapsamı

- Rol ve akademik unvan birbirinden ayrıdır.
- `HierarchyService` approver ve görünür kullanıcı kapsamını merkezi olarak hesaplar.
- İzin günleri backend’de hafta sonu ve tatilleri dikkate alarak tekrar hesaplanır.
- PENDING izinler rezerve edilir; APPROVED kullanılmış bakiyeye aktarılır; REJECTED/CANCELLED rezervasyonu kaldırır.
- Çakışma, yetersiz bakiye ve self-approval kontrolleri backend’dedir.
- `/api/auth`, `/api/users`, `/api/leaves`, `/api/dashboard`, `/api/calendar`, `/api/faculties` ve `/api/departments` endpointleri hazırdır.
