import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

old_sg = """    async function startGame(code) {
      if (!code || code === '?') { toast('C?digo de partida inv?lido', 'error'); return; }
      confirmAction('Iniciar partida', `?Iniciar la partida <b style="color:var(--gold)">${code}</b>?`, async () => {
        const { ok } = await api('POST', `/api/games/${code}/start`);
        if (ok) { toast('Partida iniciada: ' + code); refreshCurrentSection(); }
        else { toast('Error al iniciar ? verifica que la partida exista', 'error'); }
      });
    }"""

idx = text.find("async function startGame(")
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+500])
print(repr(safe[:400]))

# Try to replace by finding exact block
end = text.find("\n\n    async function endGame(", idx)
old_block = text[idx:end]
print("OLD BLOCK:", repr(old_block))

new_block = """    async function startGame(code) {
      if (!code || code === '?') { showToast('Codigo invalido', 'error'); return; }
      const inp = document.getElementById('live-code');
      if (inp) inp.value = code;
      await liveLaunch();
    }"""

new_text = text[:idx] + new_block + text[end:]
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(new_text)
print("startGame replaced OK")
