with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Remove the duplicate "Setup row" card inside active-game-panel
# (it has its own live-code, live-duration, btn-launch which now duplicates the one we just added)
old_setup_card = """            <!-- Setup row -->
            <div class="card mb-4" style="border:1px solid rgba(230,36,41,.3)">
              <div class="card-header" style="color:#FF3B40">🚀 Lanzar Partida Kahoot</div>
              <div style="padding:12px 0">
                <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:12px">
                  <div>
                    <label style="font-size:.72rem;color:var(--text-secondary);display:block;margin-bottom:3px">Código</label>
                    <input type="text" id="live-code" placeholder="Auto" style="width:120px;text-transform:uppercase"
                      oninput="this.value=this.value.toUpperCase()">
                  </div>
                  <div>
                    <label style="font-size:.72rem;color:var(--text-secondary);display:block;margin-bottom:3px">Seg/Misión</label>
                    <input type="number" id="live-duration" value="30" min="10" max="300" style="width:75px">
                  </div>
                  <div>
                    <label style="font-size:.72rem;color:var(--text-secondary);display:block;margin-bottom:3px">Seg resultados</label>
                    <input type="number" id="live-results-sec" value="5" min="3" max="15" style="width:65px">
                  </div>
                  <button class="btn btn-danger" style="font-weight:800;padding:10px 20px" onclick="liveLaunch()" id="btn-launch">
                    🚀 CREAR E INICIAR JUEGO
                  </button>
                  <button class="btn btn-sm" onclick="liveConnect()" id="btn-connect">🔍 Solo ver</button>
                  <button class="btn btn-danger btn-sm" onclick="liveEndGame()" id="btn-end-game" style="display:none">🏁 Terminar</button>
                </div>
                <div id="live-status-msg" style="font-size:.82rem;color:var(--text-secondary)">
                  💡 Deja el código vacío para crear nueva partida automáticamente.
                </div>
              </div>
            </div>

"""

new_setup_simple = """            <!-- Botones de control inline -->
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.06)">
              <input type="hidden" id="live-code" value="">
              <button class="btn btn-sm" onclick="liveConnect()" id="btn-connect">🔍 Solo ver partida</button>
              <button class="btn btn-danger btn-sm" onclick="liveEndGame()" id="btn-end-game" style="display:none">🏁 Terminar partida</button>
            </div>
"""

if old_setup_card in text:
    text = text.replace(old_setup_card, new_setup_simple)
    print("Duplicate setup card removed OK")
else:
    print("Setup card not found exactly")
    import re
    idx = text.find("Seg/Misi")
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-200):idx+400])
    print(safe)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")
