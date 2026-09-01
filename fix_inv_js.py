with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

old_start = "    // ════════════════════════════════════════════════\n    // INVENTARIO v2"
old_end   = "\n    // Hook into navTo to load data when sections open"

si = text.find(old_start)
ei = text.find(old_end, si)

if si == -1 or ei == -1:
    print(f"JS inv markers not found: si={si} ei={ei}")
    exit(1)

new_js = """    // ════════════════════════════════════════════════
    // INVENTARIO (único, completo)
    // ════════════════════════════════════════════════
    async function loadInventory2() {
      const { data, ok } = await api("GET", "/api/admin/inventory");
      if (!ok || !data) { showToast("Error al cargar inventario", "error"); return; }
      const tbody = document.getElementById("inv2-body");
      if (!data.length) {
        tbody.innerHTML = "<tr><td colspan='6' class='text-center text-muted'>Sin premios registrados</td></tr>";
        return;
      }
      tbody.innerHTML = data.map(r => {
        const canjeados  = (r.stock_initial || 0) - (r.stock_remaining || 0);
        const isDisabled = r.disabled === 1 || r.disabled === true;
        const rowOpacity = isDisabled ? "opacity:.5" : "";
        return `<tr style="${rowOpacity}">
          <td>
            <strong>${r.emoji || ""} ${r.name}</strong>
            ${r.description ? `<br><small class="text-muted">${r.description}</small>` : ""}
          </td>
          <td style="text-align:center">
            <input type="number" id="inv2-initial-${r.id}" value="${r.stock_initial || 0}" min="0"
              style="width:75px;text-align:center;padding:5px 6px;border-radius:6px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.15);color:inherit">
          </td>
          <td style="text-align:center">
            <input type="number" id="inv2-curr-${r.id}" value="${r.stock_remaining || 0}" min="0"
              style="width:75px;text-align:center;padding:5px 6px;border-radius:6px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.15);color:inherit">
          </td>
          <td style="text-align:center;font-weight:700;color:${canjeados > 0 ? "#E62429" : "inherit"}">
            ${canjeados}
          </td>
          <td style="text-align:center">
            <label style="display:inline-flex;align-items:center;gap:6px;cursor:pointer">
              <input type="checkbox" id="inv2-active-${r.id}" ${isDisabled ? "" : "checked"}
                style="width:18px;height:18px;cursor:pointer;accent-color:#00E676">
              <span style="font-size:.8rem;color:var(--text-secondary)" id="inv2-active-label-${r.id}">
                ${isDisabled ? "Desactivado" : "Activo"}
              </span>
            </label>
          </td>
          <td style="text-align:center">
            <button class="btn btn-sm btn-primary" onclick="saveInv2('${r.id}')">Guardar</button>
          </td>
        </tr>`;
      }).join("");

      // Update label dynamically when checkbox changes
      data.forEach(r => {
        const cb = document.getElementById("inv2-active-" + r.id);
        if (cb) cb.addEventListener("change", () => {
          document.getElementById("inv2-active-label-" + r.id).textContent = cb.checked ? "Activo" : "Desactivado";
        });
      });
    }

    async function saveInv2(id) {
      const initialEl = document.getElementById("inv2-initial-" + id);
      const currEl    = document.getElementById("inv2-curr-" + id);
      const activeEl  = document.getElementById("inv2-active-" + id);
      if (!initialEl || !currEl || !activeEl) return;

      const stockInitial   = parseInt(initialEl.value) || 0;
      const stockRemaining = parseInt(currEl.value) || 0;
      const disabled       = !activeEl.checked;

      // Clamp: current can't exceed initial
      const safeRemaining = Math.min(stockRemaining, stockInitial);
      currEl.value = safeRemaining;

      const { ok } = await api("POST", "/api/admin/inventory/update", {
        reward_id:       id,
        stock_initial:   stockInitial,
        stock_remaining: safeRemaining,
        disabled:        disabled,
      });

      if (ok) showToast("Inventario guardado ✓", "success");
      else    showToast("Error al guardar", "error");
      loadInventory2();
    }
"""

text = text[:si] + new_js + text[ei:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Inventory JS replaced OK")
