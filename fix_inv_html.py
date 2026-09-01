with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

start_marker = "<!-- ════ SECTION: INVENTARIO v2 ════ -->"
end_marker   = "\n    </main>"

si = text.find(start_marker)
ei = text.find(end_marker, si)

if si == -1 or ei == -1:
    print(f"Markers not found: si={si} ei={ei}")
    exit(1)

new_inv = """<!-- ════ SECTION: INVENTARIO ════ -->
      <section id="sec-inv2" class="sec-content">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-display" style="font-size:22px;font-weight:800">📦 Inventario de Premios</h2>
          <button class="btn btn-primary btn-sm" onclick="loadInventory2()">↻ Actualizar</button>
        </div>

        <div class="table-responsive card" style="padding:0">
          <table id="inv2-table">
            <thead><tr>
              <th>Premio</th>
              <th style="text-align:center">Stock Inicial</th>
              <th style="text-align:center">Stock Actual</th>
              <th style="text-align:center">Canjeados</th>
              <th style="text-align:center">Activo</th>
              <th style="text-align:center">Guardar</th>
            </tr></thead>
            <tbody id="inv2-body">
              <tr><td colspan="6"><div class="skeleton"></div></td></tr>
            </tbody>
          </table>
        </div>

        <div style="margin-top:14px;font-size:.8rem;color:var(--text-secondary)">
          💡 Desactivar un premio lo oculta de la tienda de canjeables. Los canjeados = Stock Inicial − Stock Actual.
        </div>
      </section>"""

text = text[:si] + new_inv + text[ei:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Inventory section replaced OK")
