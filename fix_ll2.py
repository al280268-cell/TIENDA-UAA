with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace the fragile element lookups at the top of liveLaunch
old_top = """    async function liveLaunch() {
      _liveCode = (document.getElementById("live-code").value || "").trim().toUpperCase();
      const dur  = parseInt(document.getElementById("live-duration").value) || 30;
      const res  = parseInt(document.getElementById("live-results-sec").value) || 5;
      _liveDuration = dur;

      const btnLaunch = document.getElementById("btn-launch");
      btnLaunch.disabled = true;
      btnLaunch.textContent = "Iniciando\u2026";
      document.getElementById("live-status-msg").textContent = "";"""

new_top = """    async function liveLaunch() {
      // Robust element lookup — use fallback values if elements missing
      _liveCode = (document.getElementById("live-code")?.value || "").trim().toUpperCase();
      const dur  = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res  = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      _liveDuration = dur;

      const btnLaunch = document.getElementById("btn-launch");
      if (btnLaunch) { btnLaunch.disabled = true; btnLaunch.textContent = "Iniciando\u2026 (max 15s)"; }
      const statusEl = document.getElementById("live-status-msg");
      if (statusEl) statusEl.textContent = "Conectando con el servidor\u2026";"""

if old_top in text:
    text = text.replace(old_top, new_top)
    print("liveLaunch top replaced OK")
else:
    print("Top not matched exactly")
    import re
    idx = text.find("async function liveLaunch()")
    safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+300])
    print(repr(safe))

# Also fix the button re-enable lines that use textContent hardcoded
text = text.replace(
    'btnLaunch.textContent = "\U0001f680 INICIAR JUEGO AUTOM\u00c1TICO";',
    'if (btnLaunch) { btnLaunch.disabled = false; btnLaunch.textContent = "\U0001f680 CREAR E INICIAR JUEGO"; }'
)
text = text.replace(
    'btnLaunch.textContent = "\U0001f680 INICIAR JUEGO AUTOM?TICO";',
    'if (btnLaunch) { btnLaunch.disabled = false; btnLaunch.textContent = "\U0001f680 CREAR E INICIAR JUEGO"; }'
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")
