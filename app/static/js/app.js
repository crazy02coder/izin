const $ = (s) => document.querySelector(s);
const api = async (url, opt = {}) => {
  let r = await fetch("/api" + url, {
    headers: { "Content-Type": "application/json" },
    ...opt,
  });
  if (r.status === 401) {
    renderLogin();
    throw Error("Oturum gerekli");
  }
  let d = await r.json();
  if (!r.ok) throw Error(d.detail || "İşlem başarısız");
  return d;
};
const titleMap = {
  PROFESSOR: "Prof. Dr.",
  ASSOCIATE_PROFESSOR: "Doç. Dr.",
  ASSISTANT_PROFESSOR: "Dr. Öğr. Üyesi",
  LECTURER: "Öğr. Gör.",
  RESEARCH_ASSISTANT: "Arş. Gör.",
  OTHER: "Diğer",
};
const statusMap = {
  PENDING: "Bekliyor",
  APPROVED: "Onaylandı",
  REJECTED: "Reddedildi",
  CANCELLED: "İptal",
  AUTO_APPROVED: "Kayıtlandı",
};
let me;
function initials(u) {
  return (u.first_name[0] + u.last_name[0]).toUpperCase();
}
function avatar(u) {
  return `<span class="avatar">${u.profile_photo_url ? `<img src="${u.profile_photo_url}" alt="">` : initials(u)}</span>`;
}
function fmt(d) {
  return new Date(d + "T00:00:00").toLocaleDateString("tr-TR");
}
function toast(t) {
  let x = document.createElement("div");
  x.className = "toast";
  x.textContent = t;
  document.body.append(x);
  setTimeout(() => x.remove(), 3200);
}
function renderLogin() {
  document.body.innerHTML = `<main class="login"><form class="login-card" id="login"><div class="brand-mark">OTÜ</div><h1>İzin Yönetim Portalı</h1><p>OSTİM Teknik Üniversitesi akademik personel sistemi</p><label>E-posta</label><input name="email" type="email" required placeholder="ad.soyad@ostimteknik.edu.tr"><label>Şifre</label><div class="password-field"><input id="login-password" name="password" type="password" required placeholder="FirstName.lastName123"><button type="button" class="password-toggle" id="toggle-password" aria-label="Şifreyi göster">Görünür</button></div><button class="btn primary" style="width:100%;margin-top:24px">Giriş yap</button><p style="font-size:12px;margin-top:20px">Demo ortamı: Serdar Müldür / Serdar.muldur123</p></form></main>`;
  const passwordInput = $("#login-password");
  $("#toggle-password").onclick = () => {
    const visible = passwordInput.type === "text";
    passwordInput.type = visible ? "password" : "text";
    $("#toggle-password").textContent = visible ? "Görünür" : "Gizle";
    $("#toggle-password").setAttribute("aria-label", visible ? "Şifreyi göster" : "Şifreyi gizle");
  };
  $("#login").onsubmit = async (e) => {
    e.preventDefault();
    try {
      let d = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(e.target))),
      });
      me = d.user;
      if (location.hash === "#logout") {
        history.replaceState(null, "", "#dashboard");
      }
      renderApp();
    } catch (x) {
      toast(x.message);
    }
  };
}
async function renderApp() {
  document.body.innerHTML = `<div class="layout"><aside class="sidebar" id="side"><div class="logo">OTÜ İZİN<small>Akademik Personel Portalı</small></div><nav class="nav"><a href="#dashboard" class="active">▦ &nbsp; Dashboard</a><a href="#new">＋ &nbsp; İzin Talebi</a><a href="#leaves">▤ &nbsp; İzinlerim</a><a href="#calendar">◫ &nbsp; Takvim</a>${["DEPARTMENT_HEAD", "DEAN", "VICE_DEAN", "RECTOR", "VICE_RECTOR", "ADMIN"].includes(me.system_role) ? '<a href="#people">♙ &nbsp; Personel</a>' : ""}${["DEPARTMENT_HEAD", "DEAN", "VICE_DEAN", "RECTOR", "VICE_RECTOR"].includes(me.system_role) ? '<a href="#approvals">✓ &nbsp; Onay Bekleyenler</a>' : ""}<a href="#profile">◎ &nbsp; Profil</a><a href="#logout">↪ &nbsp; Çıkış</a></nav></aside><main class="main"><header class="topbar"><button class="mobile-menu ghost" onclick="$('#side').classList.toggle('open')">☰</button><strong>OSTİM Teknik Üniversitesi <span style="color:#9aa9bb">/ İzin Yönetim Sistemi</span></strong><div class="user-chip">${me.first_name} ${me.last_name} ${avatar(me)}</div></header><section class="content" id="view"></section></main></div>`;
  window.onhashchange = route;
  route();
}
async function route() {
  let h = location.hash.slice(1) || "dashboard";
  document
    .querySelectorAll(".nav a")
    .forEach((a) => a.classList.toggle("active", a.hash.slice(1) == h));
  try {
    if (h === "dashboard") await dashboard();
    else if (h === "new") newLeave();
    else if (h === "leaves") await leaves();
    else if (h === "calendar") await calendar();
    else if (h === "people") await people();
    else if (h === "approvals") await approvals();
    else if (h === "profile") profile();
    else if (h === "logout") {
      await api("/auth/logout", { method: "POST" });
      renderLogin();
    }
  } catch (e) {
    toast(e.message);
  }
}
async function dashboard() {
  let d = await api("/dashboard");
  $("#view").innerHTML =
    `<div class="eyebrow">Genel Bakış</div><h1 class="title">Hoş geldiniz, ${titleMap[me.academic_title]} ${me.first_name} ${me.last_name}</h1><div class="grid"><div class="card"><div class="stat-label">Yıllık İzin</div><div class="stat-value">${d.balance.total} <small style="font-size:14px">gün</small></div></div><div class="card"><div class="stat-label">Kullanılan</div><div class="stat-value">${d.balance.used}</div></div><div class="card"><div class="stat-label">Bekleyen</div><div class="stat-value">${d.balance.reserved}</div></div><div class="card"><div class="stat-label">Kalan</div><div class="stat-value" style="color:var(--green)">${d.balance.remaining}</div></div></div><div class="grid section"><div class="card"><div class="stat-label">Görüntülenebilir personel</div><div class="stat-value">${d.stats.total_people}</div><div class="stat-foot">Rol: ${me.system_role}</div></div><div class="card"><div class="stat-label">Şu anda izinli</div><div class="stat-value">${d.stats.active_leave}</div><div class="stat-foot">Bugün aktif izinler</div></div><div class="card"><div class="stat-label">Bekleyen talep</div><div class="stat-value">${d.stats.pending}</div><div class="stat-foot">Yetki alanınızdaki toplam</div></div><div class="card"><div class="stat-label">Hızlı işlem</div><button class="btn primary" onclick="location.hash='new'" style="margin-top:12px">Yeni izin talebi</button></div></div>`;
}
function newLeave() {
  $("#view").innerHTML =
    `<div class="eyebrow">İzin Yönetimi</div><h1 class="title">Yeni izin talebi</h1><div class="card form-card"><form id="leaveForm"><label>İzin türü</label><select name="leave_type"><option value="ANNUAL">Yıllık İzin</option><option value="EXCUSE">Mazeret İzni</option><option value="SICK">Hastalık İzni</option></select><div class="row"><div><label>Başlangıç tarihi</label><input type="date" name="start_date" required></div><div><label>Bitiş tarihi</label><input type="date" name="end_date" required></div></div><label>Açıklama</label><textarea name="reason" rows="4" placeholder="Talebiniz hakkında kısa açıklama"></textarea><div class="notice" id="preview">Tarihleri seçtiğinizde iş günü ve tahmini bakiye gösterilir.</div><button class="btn primary" style="margin-top:18px">Talebi gönder</button></form></div>`;
  let f = $("#leaveForm");
  f.oninput = () => {
    let a = f.start_date.value,
      b = f.end_date.value;
    if (a && b) {
      let n = 0,
        d = new Date(a),
        e = new Date(b);
      while (d <= e) {
        if (d.getDay() > 0 && d.getDay() < 6) n++;
        d.setDate(d.getDate() + 1);
      }
      $("#preview").textContent =
        `Tahmini izin süresi: ${n} iş günü · Mevcut bakiye: yükleniyor...`;
    }
  };
  f.onsubmit = async (e) => {
    e.preventDefault();
    try {
      let d = await api("/leaves", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(f))),
      });
      toast("İzin talebi oluşturuldu");
      location.hash = "leaves";
    } catch (x) {
      toast(x.message);
    }
  };
}
async function leaves() {
  let rows = await api("/leaves/my");
  $("#view").innerHTML =
    `<div class="eyebrow">Kayıtlar</div><h1 class="title">İzinlerim</h1><div class="card table-wrap"><table class="table"><thead><tr><th>Tarih</th><th>Tür</th><th>Süre</th><th>Durum</th><th></th></tr></thead><tbody>${rows.map((x) => `<tr><td>${fmt(x.start_date)} → ${fmt(x.end_date)}</td><td>Yıllık İzin</td><td>${x.working_days} gün</td><td><span class="badge ${x.status.toLowerCase()}">${statusMap[x.status]}</span></td><td>${x.status === "PENDING" ? `<button class="btn danger" onclick="cancelLeave(${x.id})">İptal</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="5" class="empty">Henüz izin başvurunuz yok.</td></tr>'}</tbody></table></div>`;
}
async function cancelLeave(id) {
  try {
    await api("/leaves/" + id + "/cancel", { method: "POST" });
    route();
  } catch (e) {
    toast(e.message);
  }
}
async function approvals() {
  let [rows, staff] = await Promise.all([
    api("/leaves/pending-approvals"),
    api("/users"),
  ]);
  let byId = Object.fromEntries(staff.map((u) => [u.id, u]));
  $("#view").innerHTML =
    `<div class="eyebrow">İş Akışı</div><h1 class="title">Bekleyen izin talepleri</h1><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">${
      rows
        .map((x) => {
          let u = byId[x.user_id];
          return `<div class="card"><div style="display:flex;gap:12px;align-items:center;margin-bottom:14px">${u ? avatar(u) : ""}<div><strong>${u ? `${titleMap[u.academic_title]} ${u.first_name} ${u.last_name}` : `Talep sahibi #${x.user_id}`}</strong><div class="stat-foot">${u?.email || ""}</div></div></div><span class="badge pending">Bekliyor</span><h3>${fmt(x.start_date)} → ${fmt(x.end_date)}</h3><p class="stat-foot">${x.working_days} iş günü · Yıllık İzin</p><button class="btn primary" onclick="approveLeave(${x.id})">Onayla</button> <button class="btn danger" onclick="rejectLeave(${x.id})">Reddet</button></div>`;
        })
        .join("") || '<div class="card empty">Bekleyen talep yok.</div>'
    }</div>`;
}
async function approveLeave(id) {
  try {
    await api("/leaves/" + id + "/approve", { method: "POST" });
    route();
  } catch (e) {
    toast(e.message);
  }
}
async function rejectLeave(id) {
  let r = prompt("Ret nedeni");
  if (!r) return;
  try {
    await api("/leaves/" + id + "/reject", {
      method: "POST",
      body: JSON.stringify({ rejection_reason: r }),
    });
    route();
  } catch (e) {
    toast(e.message);
  }
}
async function people() {
  let rows = await api("/users");
  $("#view").innerHTML =
    `<div class="eyebrow">Organizasyon</div><h1 class="title">Personel</h1><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">${rows.map((u) => `<div class="card" style="display:flex;gap:14px;align-items:center">${avatar(u)}<div><strong>${titleMap[u.academic_title]} ${u.first_name} ${u.last_name}</strong><div class="stat-foot">${u.email}</div><span class="badge">${u.system_role}</span></div></div>`).join("")}</div>`;
}
async function calendar() {
  let rows = await api("/calendar");
  $("#view").innerHTML =
    `<div class="eyebrow">Planlama</div><h1 class="title">İzin takvimi</h1><div class="card"><div class="notice">Yetki alanınızdaki izin kayıtları gösteriliyor. Toplam ${rows.length} kayıt.</div><div class="table-wrap"><table class="table"><thead><tr><th>Başlangıç</th><th>Bitiş</th><th>İş günü</th><th>Durum</th></tr></thead><tbody>${rows.map((x) => `<tr><td>${fmt(x.start_date)}</td><td>${fmt(x.end_date)}</td><td>${x.working_days}</td><td><span class="badge ${x.status.toLowerCase()}">${statusMap[x.status]}</span></td></tr>`).join("") || '<tr><td colspan="4" class="empty">Takvim boş.</td></tr>'}</tbody></table></div></div>`;
}
function profile() {
  $("#view").innerHTML =
    `<div class="eyebrow">Hesap</div><h1 class="title">Profilim</h1><div class="card" style="max-width:620px;display:flex;gap:18px;align-items:center">${avatar(me)}<div><h2 style="margin:0">${titleMap[me.academic_title]} ${me.first_name} ${me.last_name}</h2><p class="stat-foot">${me.email}</p><span class="badge">${me.system_role}</span></div></div>`;
}
api("/auth/me")
  .then((u) => {
    me = u;
    renderApp();
  })
  .catch(() => renderLogin());

async function calendar() {
  let [rows, staff] = await Promise.all([api("/calendar"), api("/users")]);
  let byId = Object.fromEntries(staff.map((u) => [u.id, u]));
  $("#view").innerHTML =
    `<div class="eyebrow">Planlama</div><h1 class="title">İzin takvimi</h1><div class="card"><div class="notice">Yetki alanınızdaki izin kayıtları gösteriliyor. Toplam ${rows.length} kayıt. Detay için satıra tıklayın.</div><div class="table-wrap"><table class="table"><thead><tr><th>Personel</th><th>Başlangıç</th><th>Bitiş</th><th>İş günü</th><th>Durum</th></tr></thead><tbody>${
      rows
        .map((x) => {
          let u = byId[x.user_id];
          return `<tr class="calendar-row" onclick="toggleCalendarDetail(${x.id})"><td>${u ? `${titleMap[u.academic_title]} ${u.first_name} ${u.last_name}` : `Personel #${x.user_id}`}</td><td>${fmt(x.start_date)}</td><td>${fmt(x.end_date)}</td><td>${x.working_days}</td><td><span class="badge ${x.status.toLowerCase()}">${statusMap[x.status]}</span></td></tr><tr id="calendar-detail-${x.id}" class="detail-row"><td colspan="5">${u ? `<strong>${titleMap[u.academic_title]} ${u.first_name} ${u.last_name}</strong> · ${u.email}<br>` : ""}İzin aralığı: ${fmt(x.start_date)} → ${fmt(x.end_date)} · ${x.working_days} iş günü · Durum: ${statusMap[x.status]}</td></tr>`;
        })
        .join("") || '<tr><td colspan="5" class="empty">Takvim boş.</td></tr>'
    }</tbody></table></div></div>`;
}
function toggleCalendarDetail(id) {
  let detail = document.getElementById("calendar-detail-" + id);
  if (!detail) return;
  detail.classList.toggle("open");
  detail.previousElementSibling.classList.toggle("open");
}
