import os
import uuid
import sqlite3
from functools import wraps

from flask import (Flask, request, redirect, render_template_string,
                   session, send_from_directory, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Maxfiy kalit muhit o'zgaruvchisidan olinadi (GitHub'ga yozilmaydi!)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DATA_DIR = os.environ.get("DATA_DIR", ".")
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
DB = os.path.join(DATA_DIR, "ecoxabar.db")
ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "")  # shu raqam bilan ro'yxatdan o'tgan odam admin bo'ladi
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
STATUSES = ["Yangi", "Tekshirilmoqda", "Mas'ulga yuborildi", "Tozalandi", "Rad etildi"]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ========================= DATABASE =========================
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            region TEXT,
            district TEXT,
            role TEXT DEFAULT 'citizen'
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            region TEXT,
            district TEXT,
            address TEXT,
            category TEXT,
            description TEXT,
            photo TEXT,
            status TEXT DEFAULT 'Yangi',
            reward INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    conn.commit()
    conn.close()


init_db()


# ========================= DESIGN =========================
LAYOUT = """
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}} — EcoXabar</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
body{background:#f3f7f4;color:#183b25}
nav{background:#087f3d;color:white;padding:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap}
.logo{font-size:24px;font-weight:bold}
nav a{color:white;text-decoration:none;margin:6px 10px;font-weight:bold}
.container{max-width:1100px;margin:auto;padding:25px}
.hero{background:linear-gradient(135deg,#087f3d,#18a957);color:white;padding:55px 25px;text-align:center;border-radius:0 0 30px 30px}
.hero h1{font-size:42px;margin-bottom:15px}
.hero p{font-size:18px;margin-bottom:25px}
.btn{display:inline-block;background:#ffca28;color:#183b25;padding:13px 22px;border-radius:12px;text-decoration:none;font-weight:bold;border:none;cursor:pointer}
.btn-green{background:#087f3d;color:white}
.card{background:white;padding:22px;border-radius:18px;margin:18px 0;box-shadow:0 5px 20px rgba(0,0,0,.08)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}
.stat{text-align:center;padding:25px;background:white;border-radius:18px;box-shadow:0 4px 15px rgba(0,0,0,.07)}
.stat h2{color:#087f3d;font-size:32px}
input,select,textarea{width:100%;padding:13px;margin:7px 0 15px;border:1px solid #ccc;border-radius:10px;font-size:15px}
textarea{min-height:120px}
label{font-weight:bold}
.alert{padding:14px;background:#e8f5e9;border-left:5px solid #087f3d;margin-bottom:15px;border-radius:8px}
.danger{background:#ffebee;border-left-color:#d32f2f}
table{width:100%;border-collapse:collapse;background:white}
th,td{padding:12px;border-bottom:1px solid #ddd;text-align:left}
th{background:#087f3d;color:white}
td select{margin:0 0 8px}
.report-img{width:180px;max-width:100%;border-radius:12px}
footer{margin-top:50px;background:#123c25;color:white;text-align:center;padding:25px}
@media(max-width:600px){.hero h1{font-size:32px}.container{padding:15px}nav{gap:10px}}
</style>
</head>
<body>
<nav>
  <div class="logo">🌱 EcoXabar</div>
  <div>
    <a href="/">Bosh sahifa</a>
    <a href="/report">Xabar berish</a>
    <a href="/reports">Xabarlar</a>
    <a href="/about">Loyiha</a>
    {% if session.get('role') == 'admin' %}<a href="/admin">Admin</a>{% endif %}
    {% if session.get('user_id') %}
      <a href="/logout">Chiqish ({{session.get('fullname')}})</a>
    {% else %}
      <a href="/login">Kirish</a>
    {% endif %}
  </div>
</nav>
{{content|safe}}
<footer>EcoXabar © 2026<br>Tabiatni asrash — barchamizning vazifamiz.</footer>
</body>
</html>
"""


def page(title, body, **ctx):
    content = render_template_string(body, **ctx)
    return render_template_string(LAYOUT, title=title, content=content)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper


# ========================= HOME =========================
@app.route("/")
def home():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    cleaned = conn.execute("SELECT COUNT(*) FROM reports WHERE status='Tozalandi'").fetchone()[0]
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    return page("Bosh sahifa", """
<section class="hero">
  <h1>🌱 EcoXabar</h1>
  <p>Atrof-muhitdagi chiqindilar haqida xabar bering. Birgalikda shahrimiz va qishloqlarimizni toza qilamiz!</p>
  <a class="btn" href="/report">♻️ Chiqindi haqida xabar berish</a>
</section>
<div class="container">
  <h2 style="text-align:center;margin:20px">EcoXabar statistikasi</h2>
  <div class="grid">
    <div class="stat"><h2>{{total}}</h2><p>Jami xabarlar</p></div>
    <div class="stat"><h2>{{cleaned}}</h2><p>Tozalangan joylar</p></div>
    <div class="stat"><h2>{{users}}</h2><p>Foydalanuvchilar</p></div>
  </div>
  <div class="card">
    <h2>EcoXabar qanday ishlaydi?</h2><br>
    <div class="grid">
      <div><h3>📸 1. Surat yuboring</h3><p>Chiqindi joylashgan hududni suratga oling.</p></div>
      <div><h3>📍 2. Joylashuvni kiriting</h3><p>Viloyat, tuman va manzilni yozing.</p></div>
      <div><h3>🚛 3. Mas'ullar ko‘radi</h3><p>Xabar ekologiya va tozalash xizmatlariga yetkaziladi.</p></div>
      <div><h3>🏆 4. Natijani kuzating</h3><p>Xabaringiz holatini ko‘rib boring.</p></div>
    </div>
  </div>
</div>
""", total=total, cleaned=cleaned, users=users)


# ========================= ABOUT =========================
@app.route("/about")
def about():
    return page("Loyiha", """
<div class="container"><div class="card">
  <h2>🌍 EcoXabar loyihasi haqida</h2><br>
  <p>EcoXabar — fuqarolar atrof-muhitdagi chiqindilar haqida surat va manzil bilan xabar beradigan platforma.
  Xabarlar mas'ul xizmatlarga yetkaziladi va ularning holatini kuzatib borish mumkin.</p>
</div></div>
""")


# ========================= REGISTER =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        fullname = (request.form.get("fullname") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        password = request.form.get("password") or ""
        region = request.form.get("region")
        district = request.form.get("district")

        if not fullname or not phone or not password:
            message = "Barcha majburiy maydonlarni to‘ldiring."
        elif len(password) < 6:
            message = "Parol kamida 6 ta belgidan iborat bo‘lsin."
        else:
            role = "admin" if ADMIN_PHONE and phone == ADMIN_PHONE else "citizen"
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO users (fullname,phone,password,region,district,role) VALUES (?,?,?,?,?,?)",
                    (fullname, phone, generate_password_hash(password), region, district, role))
                conn.commit()
                return redirect("/login")
            except sqlite3.IntegrityError:
                message = "Bu telefon raqami bilan foydalanuvchi mavjud."
            finally:
                conn.close()

    return page("Ro‘yxatdan o‘tish", """
<div class="container"><div class="card">
  <h2>👤 Ro‘yxatdan o‘tish</h2>
  {% if message %}<div class="alert danger">{{message}}</div>{% endif %}
  <form method="POST">
    <label>F.I.Sh.</label><input name="fullname" required>
    <label>Telefon raqami</label><input name="phone" placeholder="+998..." required>
    <label>Parol (kamida 6 belgi)</label><input type="password" name="password" required>
    <label>Viloyat</label><input name="region">
    <label>Tuman / shahar</label><input name="district">
    <button class="btn btn-green">Ro‘yxatdan o‘tish</button>
  </form><br>
  <a href="/login">Hisobingiz bormi? Kirish</a>
</div></div>
""", message=message)


# ========================= LOGIN =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        phone = (request.form.get("phone") or "").strip()
        password = request.form.get("password") or ""

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["fullname"] = user["fullname"]
            session["role"] = user["role"]
            return redirect("/")
        message = "Telefon raqami yoki parol noto‘g‘ri."

    return page("Kirish", """
<div class="container"><div class="card">
  <h2>🔐 Tizimga kirish</h2>
  {% if message %}<div class="alert danger">{{message}}</div>{% endif %}
  <form method="POST">
    <label>Telefon</label><input name="phone" required>
    <label>Parol</label><input type="password" name="password" required>
    <button class="btn btn-green">Kirish</button>
  </form><br>
  <a href="/register">Yangi foydalanuvchi? Ro‘yxatdan o‘tish</a>
</div></div>
""", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ========================= REPORT =========================
@app.route("/report", methods=["GET", "POST"])
def report():
    if "user_id" not in session:
        return redirect("/login")

    message = ""
    if request.method == "POST":
        region = request.form.get("region")
        district = request.form.get("district")
        address = request.form.get("address")
        category = request.form.get("category")
        description = request.form.get("description")
        photo = request.files.get("photo")
        filename = ""

        if photo and photo.filename:
            ext = photo.filename.rsplit(".", 1)[-1].lower() if "." in photo.filename else ""
            if ext not in ALLOWED_EXT:
                message = "❌ Faqat rasm fayllari (png, jpg, jpeg, gif, webp) mumkin."
            else:
                filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
                photo.save(os.path.join(UPLOAD_FOLDER, filename))

        if not message:
            conn = get_db()
            conn.execute(
                "INSERT INTO reports (user_id,region,district,address,category,description,photo) VALUES (?,?,?,?,?,?,?)",
                (session["user_id"], region, district, address, category, description, filename))
            conn.commit()
            conn.close()
            message = "✅ Xabaringiz muvaffaqiyatli yuborildi!"

    return page("Xabar berish", """
<div class="container"><div class="card">
  <h2>♻️ Chiqindi haqida xabar berish</h2>
  {% if message %}<div class="alert">{{message}}</div>{% endif %}
  <form method="POST" enctype="multipart/form-data">
    <label>Viloyat</label><input name="region" required>
    <label>Tuman / shahar</label><input name="district" required>
    <label>Manzil</label><input name="address" placeholder="Ko‘cha, mahalla..." required>
    <label>Chiqindi turi</label>
    <select name="category" required>
      <option value="">Tanlang</option>
      <option>Maishiy chiqindi</option>
      <option>Qurilish chiqindisi</option>
      <option>Plastik chiqindi</option>
      <option>Daraxt / yashil hudud</option>
      <option>Noqonuniy chiqindi tashlash</option>
      <option>Boshqa</option>
    </select>
    <label>Muammo haqida</label>
    <textarea name="description" placeholder="Muammoni yozing..." required></textarea>
    <label>📸 Surat</label>
    <input type="file" name="photo" accept="image/*">
    <button class="btn btn-green">📤 Xabarni yuborish</button>
  </form>
</div></div>
""", message=message)


# ========================= REPORTS =========================
@app.route("/reports")
def reports():
    conn = get_db()
    rows = conn.execute("""
        SELECT reports.*, users.fullname FROM reports
        LEFT JOIN users ON reports.user_id = users.id
        ORDER BY reports.id DESC""").fetchall()
    conn.close()

    return page("Xabarlar", """
<div class="container">
  <h2>📋 EcoXabarlar</h2>
  {% for r in reports %}
  <div class="card">
    <h3>#{{r.id}} — {{r.category}}</h3>
    <p><b>📍 Joy:</b> {{r.region}}, {{r.district}}, {{r.address}}</p>
    <p><b>👤 Xabar beruvchi:</b> {{r.fullname}}</p>
    <p><b>📝 Izoh:</b> {{r.description}}</p>
    <p><b>Holati:</b> {{r.status}}</p>
    {% if r.photo %}<br><img class="report-img" src="/uploads/{{r.photo}}" alt="surat">{% endif %}
  </div>
  {% else %}
  <div class="card">Hozircha xabarlar mavjud emas.</div>
  {% endfor %}
</div>
""", reports=rows)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ========================= ADMIN =========================
@app.route("/admin")
@admin_required
def admin():
    conn = get_db()
    rows = conn.execute("""
        SELECT reports.*, users.fullname FROM reports
        LEFT JOIN users ON reports.user_id = users.id
        ORDER BY reports.id DESC""").fetchall()
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    return page("Admin", """
<div class="container">
  <div class="card">
    <h2>⚙️ Admin panel</h2>
    <p>Jami foydalanuvchilar: <b>{{users}}</b></p>
    <p>Jami xabarlar: <b>{{reports|length}}</b></p>
  </div>
  <div class="card">
    <h2>📋 Xabarlarni boshqarish</h2>
    <div style="overflow-x:auto">
    <table>
      <tr><th>ID</th><th>Foydalanuvchi</th><th>Hudud</th><th>Kategoriya</th><th>Holat</th><th>Amal</th></tr>
      {% for r in reports %}
      <tr>
        <td>{{r.id}}</td>
        <td>{{r.fullname}}</td>
        <td>{{r.region}}, {{r.district}}</td>
        <td>{{r.category}}</td>
        <td>{{r.status}}</td>
        <td>
          <form method="POST" action="/admin/status/{{r.id}}">
            <select name="status">
              {% for s in statuses %}<option {% if s == r.status %}selected{% endif %}>{{s}}</option>{% endfor %}
            </select>
            <button class="btn btn-green">Saqlash</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </table>
    </div>
  </div>
</div>
""", reports=rows, users=users, statuses=STATUSES)


@app.route("/admin/status/<int:report_id>", methods=["POST"])
@admin_required
def admin_status(report_id):
    status = request.form.get("status")
    if status in STATUSES:
        conn = get_db()
        conn.execute("UPDATE reports SET status=? WHERE id=?", (status, report_id))
        conn.commit()
        conn.close()
    return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
