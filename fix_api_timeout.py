import re

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add AbortController timeout to api()
old_api = """async function api(method, url, body) {
      const token = sessionStorage.getItem('uaa_admin_token') || '';
      try {
        const opts = { method, headers: { 'Content-Type': 'application/json' } };
        if (token) opts.headers['Authorization'] = 'Bearer ' + token;
        if (body) opts.body = JSON.stringify(body);
        const r = await fetch(url, opts);"""

new_api = """async function api(method, url, body, timeoutMs) {
      const token = sessionStorage.getItem('uaa_admin_token') || '';
      try {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs || 15000);
        const opts = { method, headers: { 'Content-Type': 'application/json' }, signal: controller.signal };
        if (token) opts.headers['Authorization'] = 'Bearer ' + token;
        if (body) opts.body = JSON.stringify(body);
        const r = await fetch(url, opts);
        clearTimeout(tid);"""

if old_api in text:
    text = text.replace(old_api, new_api)
    print("api() timeout added OK")
else:
    print("api() not matched")
    idx = text.find("async function api(")
    print(re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+300]))

# 2. Also fix the catch block to handle AbortError
old_catch = """      } catch (e) {
        return { data: null, ok: false };
      }
    }

    // ── TOAST"""

new_catch = """      } catch (e) {
        if (e && e.name === 'AbortError') {
          console.warn('[api] Request timed out:', url);
          return { data: { detail: 'El servidor tardo demasiado. Espera 30s y reintenta.' }, ok: false };
        }
        console.error('[api] Error:', e);
        return { data: null, ok: false };
      }
    }

    // ── TOAST"""

if old_catch in text:
    text = text.replace(old_catch, new_catch)
    print("catch block updated OK")
else:
    old_catch2 = """      } catch (e) {
        return { data: null, ok: false };
      }
    }"""
    if old_catch2 in text:
        text = text.replace(old_catch2, """      } catch (e) {
        if (e && e.name === 'AbortError') return { data: { detail: 'Tiempo de espera agotado. El servidor se esta iniciando, reintenta en 30 segundos.' }, ok: false };
        return { data: null, ok: false };
      }
    }""", 1)
        print("catch block updated (variant) OK")
    else:
        print("catch not matched")

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")
