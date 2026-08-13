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


Demo hesap örnekleri:

- `serdar.muldur@ostimteknik.edu.tr` / `serdar.muldur123`
- `meltem.eryilmaz@ostimteknik.edu.tr` / `meltem.eryilmaz123`
- `murat.yulek@ostimteknik.edu.tr` / `murat.yulek123`

Şifreler veritabanına plaintext olarak yazılmaz; seed sırasında Argon2 hash’i saklanır. Seed politika değerleri demo/configuration amaçlıdır, gerçek üniversite İK politikası değildir. Production’da `.env` içinde güçlü bir `JWT_SECRET_KEY` kullanılmalı, HTTPS arkasında cookie `secure=True` yapılmalıdır.

## Uygulama kapsamı

- Rol ve akademik unvan birbirinden ayrıdır.
- `HierarchyService` approver ve görünür kullanıcı kapsamını merkezi olarak hesaplar.
- İzin günleri backend’de hafta sonu ve tatilleri dikkate alarak tekrar hesaplanır.
- PENDING izinler rezerve edilir; APPROVED kullanılmış bakiyeye aktarılır; REJECTED/CANCELLED rezervasyonu kaldırır.
- Çakışma, yetersiz bakiye ve self-approval kontrolleri backend’dedir.
- `/api/auth`, `/api/users`, `/api/leaves`, `/api/dashboard`, `/api/calendar`, `/api/faculties` ve `/api/departments` endpointleri hazırdır.
