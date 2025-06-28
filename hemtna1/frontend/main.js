// ========== إعداد المتغيرات العامة ==========
const api = "http://127.0.0.1:5000/api";
let token = localStorage.getItem("token");
let userId = null;
let username = null;
let role = null;
let socket = null;

// ========== عناصر التبويب ==========
const navLogin = document.getElementById("nav-login");
const navProfile = document.getElementById("nav-profile");
const navUsers = document.getElementById("nav-users");
const navPosts = document.getElementById("nav-posts");
const navActivities = document.getElementById("nav-activities");
const navChat = document.getElementById("nav-chat");
const navLogout = document.getElementById("nav-logout");

const sectionLogin = document.getElementById("section-login");
const sectionProfile = document.getElementById("section-profile");
const sectionUsers = document.getElementById("section-users");
const sectionPosts = document.getElementById("section-posts");
const sectionActivities = document.getElementById("section-activities");
const sectionChat = document.getElementById("section-chat");

// ========== دوال مساعدة ==========
function showSection(section) {
  [sectionLogin, sectionProfile, sectionUsers, sectionPosts, sectionActivities, sectionChat].forEach(s => s.style.display = "none");
  section.style.display = "block";
}
function setNav(loggedIn) {
  navLogin.style.display = loggedIn ? "none" : "inline-block";
  navProfile.style.display = loggedIn ? "inline-block" : "none";
  navUsers.style.display = loggedIn ? "inline-block" : "none";
  navPosts.style.display = loggedIn ? "inline-block" : "none";
  navActivities.style.display = loggedIn ? "inline-block" : "none";
  navChat.style.display = loggedIn ? "inline-block" : "none";
  navLogout.style.display = loggedIn ? "inline-block" : "none";
}
function apiHeaders(isJson = true) {
  const h = token ? { Authorization: `Bearer ${token}` } : {};
  if (isJson) h["Content-Type"] = "application/json";
  return h;
}
function showMsg(el, msg, type = "success") {
  el.innerHTML = `<div class="${type}-message">${msg}</div>`;
}
function clearMsg(el) { el.innerHTML = ""; }

// ========== واجهة تسجيل/دخول ==========
function renderLogin() {
  showSection(sectionLogin);
  sectionLogin.innerHTML = `
    <div class="tab-title">تسجيل الدخول / إنشاء حساب</div>
    <form id="loginForm">
      <label>الإيميل</label>
      <input type="email" id="loginEmail" required>
      <label>كلمة المرور</label>
      <input type="password" id="loginPassword" required>
      <button type="submit">دخول</button>
      <div id="loginMsg"></div>
    </form>
    <hr>
    <form id="registerForm">
      <label>الاسم الأول</label>
      <input type="text" id="regFirstName" required>
      <label>الاسم الأخير</label>
      <input type="text" id="regLastName" required>
      <label>الإيميل</label>
      <input type="email" id="regEmail" required>
      <label>كلمة المرور</label>
      <input type="password" id="regPassword" required>
      <label>نوع المستخدم</label>
      <select id="regUserType" required><option value="">اختر</option><option value="parent">ولي أمر</option><option value="doctor">دكتور</option></select>
      <label>التصنيف (category)</label>
      <input type="text" id="regCategory">
      <label>رقم الهاتف</label>
      <input type="text" id="regPhone">
      <label>كود الدولة</label>
      <input type="text" id="regCountryCode">
      <label>تاريخ ميلاد الطفل</label>
      <input type="date" id="regChildBirthdate">
      <label>مستوى تعليم الطفل</label>
      <input type="text" id="regChildEducationLevel">
      <label>مشكلة الطفل</label>
      <input type="text" id="regChildProblem">
      <label>تخصص الدكتور</label>
      <input type="text" id="regDoctorSpecialty">
      <button type="submit">تسجيل</button>
      <div id="registerMsg"></div>
    </form>
  `;
  document.getElementById("loginForm").onsubmit = async e => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    const msg = document.getElementById("loginMsg");
    clearMsg(msg);
    try {
      const res = await fetch(`${api}/auth/login`, {
        method: "POST",
        headers: apiHeaders(),
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        token = data.token;
        username = data.username;
        role = data.role;
        localStorage.setItem("token", token);
        localStorage.setItem("username", username);
        localStorage.setItem("role", role);
        await fetchProfile();
        setNav(true);
        renderProfile();
      } else {
        showMsg(msg, data.error || "فشل الدخول", "error");
      }
    } catch (err) { showMsg(msg, "خطأ في الاتصال", "error"); }
  };
  document.getElementById("registerForm").onsubmit = async e => {
    e.preventDefault();
    const body = {
      first_name: document.getElementById("regFirstName").value,
      last_name: document.getElementById("regLastName").value,
      email: document.getElementById("regEmail").value,
      password: document.getElementById("regPassword").value,
      user_type: document.getElementById("regUserType").value,
      category: document.getElementById("regCategory").value,
      phone: document.getElementById("regPhone").value,
      country_code: document.getElementById("regCountryCode").value,
      child_birthdate: document.getElementById("regChildBirthdate").value,
      child_education_level: document.getElementById("regChildEducationLevel").value,
      child_problem: document.getElementById("regChildProblem").value
    };
    // أضف doctor_specialty فقط إذا كان نوع المستخدم دكتور
    if (body.user_type === "doctor") {
      body.doctor_specialty = document.getElementById("regDoctorSpecialty").value;
    }
    const msg = document.getElementById("registerMsg");
    clearMsg(msg);
    try {
      const res = await fetch(`${api}/auth/register`, {
        method: "POST",
        headers: apiHeaders(),
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (res.ok) {
        showMsg(msg, "تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.");
        document.getElementById("registerForm").reset();
      } else {
        showMsg(msg, data.error || "فشل التسجيل", "error");
      }
    } catch (err) { showMsg(msg, "خطأ في الاتصال", "error"); }
  };
}

// ========== تحميل البروفايل ==========
async function fetchProfile() {
  const res = await fetch(`${api}/auth/me`, { headers: apiHeaders() });
  if (res.ok) {
    const data = await res.json();
    userId = data.id;
    username = data.username;
    role = data.user_type;
    localStorage.setItem("username", username);
    localStorage.setItem("role", role);
  }
}

// ========== واجهة البروفايل ==========
function renderProfile() {
  showSection(sectionProfile);
  sectionProfile.innerHTML = `<div class="tab-title">البروفايل</div><div id="profileData"></div>`;
  fetch(`${api}/auth/me`, { headers: apiHeaders() })
    .then(res => res.json())
    .then(data => {
      let html = "<table>";
      for (const k in data) {
        html += `<tr><th>${k}</th><td>${data[k] || "-"}</td></tr>`;
      }
      html += "</table>";
      document.getElementById("profileData").innerHTML = html;
    });
}

// ========== واجهة المستخدمين ==========
function renderUsers() {
  showSection(sectionUsers);
  sectionUsers.innerHTML = `<div class="tab-title">كل المستخدمين</div><div id="usersTable"></div>`;
  fetch(`${api}/users/`, { headers: apiHeaders() })
    .then(res => res.json())
    .then(data => {
      let html = `<table><tr><th>الاسم</th><th>الإيميل</th><th>النوع</th><th>التصنيف</th></tr>`;
      data.data.forEach(u => {
        html += `<tr><td>${u.first_name || ""} ${u.last_name || ""}</td><td>${u.email}</td><td>${u.user_type}</td><td>${u.category}</td></tr>`;
      });
      html += `</table>`;
      document.getElementById("usersTable").innerHTML = html;
    });
}

// ========== واجهة البوستات ==========
function renderPosts() {
  showSection(sectionPosts);
  sectionPosts.innerHTML = `<div class="tab-title">البوستات</div><div id="postsTable"></div><div id="addPost"></div>`;
  // عرض البوستات
  fetch(`${api}/posts/`, { headers: apiHeaders() })
    .then(res => res.json())
    .then(data => {
      let html = `<table><tr><th>العنوان</th><th>المحتوى</th><th>الدكتور</th><th>تصنيف</th><th>صورة</th><th>مشاهدات</th><th>لايك</th><th>تعليقات</th></tr>`;
      data.data.forEach(p => {
        html += `<tr><td>${p.title}</td><td>${p.content}</td><td>${p.doctor_name || "-"}</td><td>${p.category || "-"}</td><td>${p.image ? `<img src='${p.image}' style='max-width:60px;'>` : "-"}</td><td>${p.views}</td><td>${p.likes}</td><td>${p.comments}</td></tr>`;
      });
      html += `</table>`;
      document.getElementById("postsTable").innerHTML = html;
    });
  // إضافة بوست
  document.getElementById("addPost").innerHTML = `
    <form id="addPostForm" enctype="multipart/form-data">
      <label>العنوان</label><input type="text" name="title" required>
      <label>المحتوى</label><input type="text" name="content" required>
      <label>تصنيف</label><input type="text" name="category">
      <label>رقم الدكتور</label><input type="number" name="doctor_id">
      <label>صورة</label><input type="file" name="image" accept="image/*">
      <button type="submit">إضافة بوست</button>
      <div id="addPostMsg"></div>
    </form>`;
  document.getElementById("addPostForm").onsubmit = async e => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    try {
      const res = await fetch(`${api}/posts/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        showMsg(document.getElementById("addPostMsg"), "تمت الإضافة!");
        renderPosts();
      } else {
        showMsg(document.getElementById("addPostMsg"), data.error || "فشل الإضافة", "error");
      }
    } catch (err) { showMsg(document.getElementById("addPostMsg"), "خطأ في الاتصال", "error"); }
  };
}

// ========== واجهة الأنشطة ==========
function renderActivities() {
  showSection(sectionActivities);
  sectionActivities.innerHTML = `<div class="tab-title">الأنشطة</div><div id="activitiesTable"></div><div id="addActivity"></div>`;
  fetch(`${api}/activities/`, { headers: apiHeaders() })
    .then(res => res.json())
    .then(data => {
      let html = `<table><tr><th>النشاط</th><th>المدة</th><th>التفاصيل</th><th>الطفل</th><th>الدكتور</th><th>ولي الأمر</th><th>صورة</th><th>منجز؟</th><th>تقييم</th></tr>`;
      data.data.forEach(a => {
        html += `<tr><td>${a.activity_name}</td><td>${a.duration || "-"}</td><td>${a.details}</td><td>${a.child_name}</td><td>${a.doctor_id}</td><td>${a.parent_id}</td><td>${a.activity_image ? `<img src='${a.activity_image}' style='max-width:60px;'>` : "-"}</td><td>${a.is_done ? "✔" : "✗"}</td><td>${a.score}%</td></tr>`;
      });
      html += `</table>`;
      document.getElementById("activitiesTable").innerHTML = html;
    });
  document.getElementById("addActivity").innerHTML = `
    <form id="addActivityForm" enctype="multipart/form-data">
      <label>اسم النشاط</label><input type="text" name="activity_name" required>
      <label>المدة</label><input type="text" name="duration">
      <label>التفاصيل</label><input type="text" name="details" required>
      <label>اسم الطفل</label><input type="text" name="child_name" required>
      <label>رقم الدكتور</label><input type="number" name="doctor_id" required>
      <label>رقم ولي الأمر</label><input type="number" name="parent_id" required>
      <label>منجز؟</label><select name="is_done"><option value="0">لا</option><option value="1">نعم</option></select>
      <label>صورة النشاط</label><input type="file" name="activity_image" accept="image/*">
      <button type="submit">إضافة نشاط</button>
      <div id="addActivityMsg"></div>
    </form>`;
  document.getElementById("addActivityForm").onsubmit = async e => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    try {
      const res = await fetch(`${api}/activities/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        showMsg(document.getElementById("addActivityMsg"), "تمت الإضافة!");
        renderActivities();
      } else {
        showMsg(document.getElementById("addActivityMsg"), data.error || "فشل الإضافة", "error");
      }
    } catch (err) { showMsg(document.getElementById("addActivityMsg"), "خطأ في الاتصال", "error"); }
  };
}

// ========== واجهة الشات ==========
function renderChat() {
  showSection(sectionChat);
  sectionChat.innerHTML = `<div class="tab-title">الشات اللحظي</div><div id="chatRooms"></div><div id="chatBox"></div>`;
  // الاتصال بـ SocketIO
  if (!socket) {
    socket = io("http://127.0.0.1:5000");
    socket.on("receive_message", msg => {
      appendMessage(msg);
    });
    socket.on("messages_list", msgs => {
      document.getElementById("chatBox").innerHTML = `<div class='chat-box' id='chatMessages'></div>`;
      msgs.forEach(m => appendMessage(m));
    });
  }
  // جلب الغرف
  socket.emit("get_rooms", { user_id: userId });
  socket.on("rooms_list", rooms => {
    let html = `<div>غرف الشات:</div><ul>`;
    rooms.forEach(r => {
      html += `<li><button onclick="joinRoom(${r.id})">${r.name}</button></li>`;
    });
    html += `</ul>`;
    document.getElementById("chatRooms").innerHTML = html;
  });
}
function joinRoom(roomId) {
  socket.emit("join_room", { room_id: roomId });
  socket.emit("get_messages", { room: roomId });
  document.getElementById("chatBox").innerHTML = `
    <div class='chat-box' id='chatMessages'></div>
    <form id='chatForm' class='chat-input'>
      <input type='text' id='chatInput' placeholder='اكتب رسالة...'>
      <button type='submit'>إرسال</button>
    </form>
  `;
  document.getElementById("chatForm").onsubmit = e => {
    e.preventDefault();
    const msg = document.getElementById("chatInput").value;
    if (msg) {
      socket.emit("send_message", { message: msg, user_id: userId, room: roomId });
      document.getElementById("chatInput").value = "";
    }
  };
}
function appendMessage(msg) {
  const box = document.getElementById("chatMessages");
  if (!box) return;
  const html = `<div class='chat-message${msg.user_id === userId ? " me" : ""}'>
    <span class='sender'>${msg.username || "مستخدم"}</span>:
    <span>${msg.message}</span>
    <span class='time'>[${msg.timestamp ? msg.timestamp.split("T")[1].slice(0,5) : ""}]</span>
  </div>`;
  box.innerHTML += html;
  box.scrollTop = box.scrollHeight;
}

// ========== التنقل بين التبويبات ==========
navLogin.onclick = () => { renderLogin(); };
navProfile.onclick = () => { renderProfile(); };
navUsers.onclick = () => { renderUsers(); };
navPosts.onclick = () => { renderPosts(); };
navActivities.onclick = () => { renderActivities(); };
navChat.onclick = () => { renderChat(); };
navLogout.onclick = () => {
  token = null; userId = null; username = null; role = null;
  localStorage.clear();
  setNav(false);
  renderLogin();
};

// ========== بدء التشغيل ==========
if (token) {
  setNav(true);
  renderProfile();
} else {
  setNav(false);
  renderLogin();
} 