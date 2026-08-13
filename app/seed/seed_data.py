"""Demo seed. Names/e-mails/photos are based on ostim_akademik_personel_veri_seti.pdf.
The PDF reports 126 unique records; this curated starter set keeps the demo compact and
can be extended by adding rows to PEOPLE (or importing the PDF rows in a deployment job)."""

from datetime import date
from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models import *
from app.services.auth_service import hash_password
from pathlib import Path
from pypdf import PdfReader

PEOPLE = [
    (
        "Mühendislik",
        "Bilgisayar Mühendisliği",
        "Prof. Dr.",
        "Serdar Müldür",
        "DEAN",
        "serdar.muldur@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Bilgisayar Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Ahmet Özdil",
        "DEPARTMENT_HEAD",
        "ahmet.ozdil@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Bilgisayar Mühendisliği",
        "Prof. Dr.",
        "Çağatay Büyükköç",
        "ACADEMIC",
        "cagatay.buyukkoc@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Elektrik-Elektronik Mühendisliği",
        "Prof. Dr.",
        "İsmail Hakkı Altaş",
        "DEPARTMENT_HEAD",
        "ismailhakki.altas@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Elektrik-Elektronik Mühendisliği",
        "Prof. Dr.",
        "İsmail Avcıbaş",
        "ACADEMIC",
        "ismail.avcibas@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Endüstri Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Emre Yazıcı",
        "DEPARTMENT_HEAD",
        "emre.yazici@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Endüstri Mühendisliği",
        "Prof. Dr.",
        "Neşe Çelebi",
        "ACADEMIC",
        "nese.celebi@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Prof. Dr.",
        "Meltem Eryılmaz",
        "DEPARTMENT_HEAD",
        "meltem.eryilmaz@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Prof. Dr.",
        "Hasan Erbay",
        "ACADEMIC",
        "hasan.erbay@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Can Güldüren",
        "ACADEMIC",
        "can.gulduren@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Dr. Öğr. Üyesi",
        "İlker Yoncacı",
        "ACADEMIC",
        "ilker.yoncaci@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Ufuk Asıl",
        "ACADEMIC",
        "ufuk.asil@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Yücel Tekin",
        "ACADEMIC",
        "yucel.tekin@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yazılım Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Maksat Atagoziev",
        "ACADEMIC",
        "maksat.atagoziev@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yapay Zeka Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Murat Şimşek",
        "ACADEMIC",
        "murat.simsek@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Yapay Zeka Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Gülsüm Kayabaşı Koru",
        "ACADEMIC",
        "gulsum.kayabasikoru@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Nanoteknoloji Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Pelin Tören Özgün",
        "DEPARTMENT_HEAD",
        "pelin.ozgun@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Havacılık ve Uzay Mühendisliği",
        "Dr. Öğr. Üyesi",
        "Hikmet Bal",
        "ACADEMIC",
        "hikmet.bal@ostimteknik.edu.tr",
    ),
    (
        "Mühendislik",
        "Makine Mühendisliği",
        "Prof. Dr.",
        "Kadir Aydın",
        "DEPARTMENT_HEAD",
        "kadir.aydin@ostimteknik.edu.tr",
    ),
    (
        "Mimarlık ve Tasarım",
        "İç Mimarlık",
        "Prof. Dr.",
        "Sare Sahil",
        "DEAN",
        "sare.sahil@ostimteknik.edu.tr",
    ),
    (
        "Mimarlık ve Tasarım",
        "İç Mimarlık",
        "Doç. Dr.",
        "Tuğçe Çelik",
        "ACADEMIC",
        "tugce.celik@ostimteknik.edu.tr",
    ),
    (
        "İktisadi ve İdari Bilimler Fakültesi",
        "İşletme",
        "Doç. Dr.",
        "Hamide Özyürek",
        "DEPARTMENT_HEAD",
        "hamide.ozyurek@ostimteknik.edu.tr",
    ),
    (
        "İktisadi ve İdari Bilimler Fakültesi",
        "İşletme",
        "Doç. Dr.",
        "Göksel Korkmaz",
        "ACADEMIC",
        "goksel.korkmaz@ostimteknik.edu.tr",
    ),
    (
        "İktisadi ve İdari Bilimler Fakültesi",
        "Yönetim Bilişim Sistemleri",
        "Prof. Dr.",
        "Filiz Ersöz",
        "ACADEMIC",
        "filiz.ersoz@ostimteknik.edu.tr",
    ),
    (
        "İktisadi ve İdari Bilimler Fakültesi",
        "Ekonomi",
        "Prof. Dr.",
        "Murat Yülek",
        "RECTOR",
        "murat.yulek@ostimteknik.edu.tr",
    ),
    (
        "İktisadi ve İdari Bilimler Fakültesi",
        "Uluslararası Ticaret ve Finansman",
        "Prof. Dr.",
        "Ünsal Sığrı",
        "VICE_RECTOR",
        "unsal.sigri@ostimteknik.edu.tr",
    ),
    (
        "Bilişim Teknolojileri MYO",
        "Bilişim Teknolojileri MYO",
        "Öğr. Gör.",
        "Halit Ayanlı",
        "ACADEMIC",
        "halit.ayanli@ostimteknik.edu.tr",
    ),
    (
        "Bilişim Teknolojileri MYO",
        "Üretimde Kalite Kontrol",
        "Dr. Öğr. Üyesi",
        "Büşra Yedekci",
        "ACADEMIC",
        "busra.yedekci@ostimteknik.edu.tr",
    ),
    (
        "Yabancı Diller Yüksekokulu",
        "Yabancı Diller",
        "Öğr. Gör.",
        "İrem Onat",
        "ACADEMIC",
        "irem.onat@ostimteknik.edu.tr",
    ),
    (
        "Ortak Dersler Koordinatörlüğü",
        "Ortak Dersler",
        "Doç. Dr.",
        "Hakan Eren",
        "ACADEMIC",
        "hakan.eren@ostimteknik.edu.tr",
    ),
]
TITLE = {
    "Prof. Dr.": AcademicTitle.PROFESSOR,
    "Doç. Dr.": AcademicTitle.ASSOCIATE_PROFESSOR,
    "Dr. Öğr. Üyesi": AcademicTitle.ASSISTANT_PROFESSOR,
    "Öğr. Gör.": AcademicTitle.LECTURER,
    "Arş. Gör.": AcademicTitle.RESEARCH_ASSISTANT,
}
ROLE_MAP = {
    "RECTOR": "RECTOR",
    "VICE_RECTOR": "VICE_RECTOR",
    "DEAN": "DEAN",
    "VICE_DEAN": "VICE_DEAN",
    "VICE_DEPARTMENT_HEAD": "VICE_DEAN",
    "DEPARTMENT_HEAD": "DEPARTMENT_HEAD",
    "ADMIN": "ADMIN",
    "ACADEMIC": "ACADEMIC",
}
TITLE_LINES = set(TITLE) | {"Assist. Prof. Dr.", "Assist. Prof.", "Dr.", "Adjunct Instructor"}


def load_people_from_pdf():
    """Parse the numbered staff blocks from the supplied PDF (126 records)."""
    pdf = Path(__file__).resolve().parents[2] / "ostim_akademik_personel_veri_seti.pdf"
    if not pdf.exists():
        return PEOPLE
    lines = []
    for page in PdfReader(str(pdf)).pages:
        lines.extend((page.extract_text() or "").splitlines())
    starts = [i for i, x in enumerate(lines) if x.strip().isdigit() and 1 <= int(x.strip()) <= 126]
    records = []
    for pos, start in enumerate(starts):
        block = [
            x.strip()
            for x in lines[start + 1 : (starts[pos + 1] if pos + 1 < len(starts) else len(lines))]
            if x.strip()
        ]
        role_i = next(
            (
                i
                for i, x in enumerate(block)
                if x
                in {
                    "RECTOR",
                    "VICE_RECTOR",
                    "DEAN",
                    "VICE_DEAN",
                    "VICE_DEPARTMENT_HEAD",
                    "DEPARTMENT_HEAD",
                    "ACADEMIC",
                    "ADMIN",
                    "PART_TIME",
                    "COURSE_STAFF",
                    "PROGRAM_HEAD",
                }
            ),
            None,
        )
        if role_i is None or len(block) < role_i + 2:
            continue
        role = ROLE_MAP.get(block[role_i], "ACADEMIC")
        before = block[:role_i]
        title_i = next(
            (i for i in range(len(before) - 1, -1, -1) if before[i] in TITLE_LINES), None
        )
        if title_i is None or title_i + 1 >= len(before):
            continue
        title = before[title_i]
        name = before[title_i + 1]
        unit = " ".join(before[:title_i])
        email_i = role_i + 1
        email = ""
        while (
            email_i < len(block) and not block[email_i].startswith("http") and block[email_i] != "-"
        ):
            email += block[email_i]
            email_i += 1
        email = email.replace(" ", "").lower()
        urls = [x for x in block[email_i:] if x.startswith("http")]
        source = urls[-1] if urls else ""
        photo = urls[0] if len(urls) > 1 else None
        if " / " in unit:
            faculty, department = unit.split(" / ", 1)
        else:
            faculty, department = unit, unit
        if " / " not in unit and faculty == "İİBF":
            faculty = "İktisadi ve İdari Bilimler Fakültesi"
        records.append((faculty, department, title, name, role, email, photo))
    if len(records) < 100:
        return PEOPLE
    print(f"PDF seed kaynağı okundu: {len(records)} kayıt")
    return records


def slug(s):
    import unicodedata

    return (
        "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
        .replace("ı", "i")
        .replace("İ", "I")
    )


def main():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.scalar(select(User).limit(1)):
            print("Seed zaten uygulanmış.")
            return
        people = load_people_from_pdf()
        uni = University(name="OSTİM Teknik Üniversitesi")
        db.add(uni)
        db.flush()
        faculties = {}
        for row in people:
            fac = row[0]
            if fac not in faculties:
                faculties[fac] = Faculty(name=fac)
                db.add(faculties[fac])
                db.flush()
        depts = {}
        for row in people:
            fac, dep = row[0], row[1]
            key = (fac, dep)
            if key not in depts:
                depts[key] = Department(name=dep, faculty_id=faculties[fac].id)
                db.add(depts[key])
                db.flush()
        users = []
        used_emails = set()
        for row in people:
            fac, dep, title, name, role, email = row[:6]
            first, *last = name.split()
            last = " ".join(last) or first
            normalized = slug(first).lower() + "." + slug(last.split()[-1]).lower() + "123"
            if not email or email == "-":
                email = f"{slug(first).lower()}.{slug(last.split()[-1]).lower()}@ostimteknik.edu.tr"
            if email in used_emails:
                local, domain = email.split("@", 1)
                email = f"{local}.{len(used_emails)}@{domain}"
            used_emails.add(email)
            u = User(
                first_name=first,
                last_name=last,
                email=email,
                password_hash=hash_password(normalized),
                academic_title=TITLE.get(title, AcademicTitle.OTHER),
                system_role=role,
                faculty_id=faculties[fac].id,
                department_id=depts[(fac, dep)].id,
                profile_photo_url=row[6] if len(row) > 6 else None,
                must_change_password=False,
            )
            db.add(u)
            users.append((u, normalized))
            db.flush()
        for u, _ in users:
            if u.system_role == SystemRole.DEAN:
                faculties[
                    next(k for k, v in faculties.items() if v.id == u.faculty_id)
                ].dean_user_id = u.id
            if u.system_role == SystemRole.DEPARTMENT_HEAD:
                depts[
                    (
                        next(k for k, v in faculties.items() if v.id == u.faculty_id),
                        next(k for k, v in depts.items() if v.id == u.department_id)[1],
                    )
                ].department_head_user_id = u.id
        for t, n in [
            (AcademicTitle.PROFESSOR, 30),
            (AcademicTitle.ASSOCIATE_PROFESSOR, 25),
            (AcademicTitle.ASSISTANT_PROFESSOR, 25),
            (AcademicTitle.LECTURER, 20),
            (AcademicTitle.RESEARCH_ASSISTANT, 20),
            (AcademicTitle.OTHER, 20),
        ]:
            db.add(LeavePolicy(academic_title=t, annual_days=n))
        db.add_all(
            [
                Holiday(date=date(2026, 1, 1), name="Yılbaşı"),
                Holiday(date=date(2026, 4, 23), name="23 Nisan"),
                Holiday(date=date(2026, 5, 1), name="Emek ve Dayanışma Günü"),
                Holiday(date=date(2026, 8, 30), name="30 Ağustos"),
            ]
        )
        for u, _ in users:
            db.add(
                LeaveBalance(
                    user_id=u.id,
                    year=2026,
                    total_days={
                        AcademicTitle.PROFESSOR: 30,
                        AcademicTitle.ASSOCIATE_PROFESSOR: 25,
                        AcademicTitle.ASSISTANT_PROFESSOR: 25,
                    }.get(u.academic_title, 20),
                )
            )
        db.flush()
        by_email = {u.email: u for u, _ in users}
        for email, start, end, status in [
            ("yucel.tekin@ostimteknik.edu.tr", date(2026, 9, 7), date(2026, 9, 11), "APPROVED"),
            ("hasan.erbay@ostimteknik.edu.tr", date(2026, 8, 17), date(2026, 8, 21), "PENDING"),
            ("ilker.yoncaci@ostimteknik.edu.tr", date(2026, 8, 3), date(2026, 8, 7), "APPROVED"),
        ]:
            owner = by_email.get(email)
            if owner:
                days = sum(
                    (start.replace(day=start.day + i).weekday() < 5)
                    for i in range((end - start).days + 1)
                )
                approver = (
                    __import__("app.services.hierarchy_service", fromlist=["HierarchyService"])
                    .HierarchyService()
                    .approver(db, owner)
                )
                db.add(
                    LeaveRequest(
                        user_id=owner.id,
                        leave_type=LeaveType.ANNUAL,
                        start_date=start,
                        end_date=end,
                        working_days=days,
                        status=status,
                        approver_id=approver.id if approver else None,
                    )
                )
                bal = db.scalar(
                    select(LeaveBalance).where(
                        LeaveBalance.user_id == owner.id, LeaveBalance.year == 2026
                    )
                )
                if status == "APPROVED":
                    bal.used_days += days
                else:
                    bal.reserved_days += days
        db.commit()
        print("Seed tamamlandı. Demo şifre: FirstName.lastName123 (ASCII normalize).")
        for u, p in users:
            print(f"{u.email} / {p}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
