// API usa rutas relativas — funciona tanto en dev (puerto 8000) como en Vercel
const API_BASE = '';

const Session = {
  get(key)      { return sessionStorage.getItem(key); },
  set(key, val) { sessionStorage.setItem(key, val); },
  remove(key)   { sessionStorage.removeItem(key); }
};

const Api = {
  async request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = Session.get('uaa_admin_token') || Session.get('uaa_player_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = { method, headers };
    if (body !== null) options.body = JSON.stringify(body);

    try {
      const response = await fetch(API_BASE + path, options);
      const data = await response.json();
      if (!response.ok) {
        return { data: null, error: data.detail || data.message || 'Error en la petición' };
      }
      return { data, error: null };
    } catch (err) {
      console.error('[API Error]', path, err);
      return { data: null, error: 'Error de conexión al servidor' };
    }
  },
  get:  (path)       => Api.request('GET',  path, null),
  post: (path, body) => Api.request('POST', path, body),
  put:  (path, body) => Api.request('PUT',  path, body),
};

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
}

function formatPoints(n) {
  return new Intl.NumberFormat('es-MX').format(n || 0);
}

function getAvatarStyle(color) {
  return `background-color: ${color || '#C41230'}; color: white;`;
}

function createAvatar(initials, color, size = 'md') {
  const sizeMap = { sm: '32px', md: '44px', lg: '64px', xl: '88px' };
  const px = sizeMap[size] || sizeMap.md;
  const fs = parseInt(px) / 2.5 + 'px';
  return `<div class="avatar avatar-${size}" style="width:${px};height:${px};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:${fs};font-weight:800;${getAvatarStyle(color)}">${initials}</div>`;
}

function navigateTo(page) { window.location.href = page; }

function redirectIfNoSession() {
  if (!Session.get('uaa_player_token')) navigateTo('index.html');
}

window.App = { API_BASE, Session, Api, formatTime, formatPoints, getAvatarStyle, createAvatar, navigateTo, redirectIfNoSession };
