import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Fix loadGames
old_lg = """      tbody.innerHTML = games.map(g => {
        // La API devuelve 'code', normalizamos igual que en dashboard
        const gc = g.code || g.game_code || '?';
        const fecha = g.created_at && !g.created_at.startsWith('1970') ? formatDate(g.created_at) : '?';
        return `
        <tr>
          <td class="font-mono font-weight-600" style="color:var(--gold)">${gc}</td>
          <td>${getBadgeStatus(g.status)}</td>
          <td>${g.players_count || 0}</td>
          <td>${fecha}</td>
          <td>${g.finished_at ? formatDate(g.finished_at) : '?'}</td>
          <td>
            <div class="flex gap-2">
              <button class="btn btn-sm" onclick="viewGameDetail('${gc}')">Ver</button>
              <button class="btn btn-ghost btn-sm" onclick="showCodeModal('${gc}')">C?digo</button>
            </div>
          </td>
        </tr>
      `}).join('');"""

new_lg = """      tbody.innerHTML = games.map(g => {
        const gc = g.code || g.game_code || '?';
        const fecha = formatDate(g.created_at);
        const fin = g.ended_at ? formatDate(g.ended_at) : (g.finished_at ? formatDate(g.finished_at) : '-');
        return `
        <tr>
          <td class="font-mono font-weight-600" style="color:var(--gold)">${gc}</td>
          <td>${getBadgeStatus(g.status)}</td>
          <td>${g.players_count || 0}</td>
          <td>${fecha}</td>
          <td>${fin}</td>
          <td>
            <div class="flex gap-2">
              <button class="btn btn-sm" onclick="viewGameDetail('${gc}')">Ver</button>
              <button class="btn btn-ghost btn-sm" onclick="showCodeModal('${gc}')">C\u00f3digo</button>
            </div>
          </td>
        </tr>
      `}).join('');"""

# Fix loadDashboard recent games
old_ld = """      tbody.innerHTML = recent.map(g => {
        const fecha = g.created_at && !g.created_at.startsWith('1970') ? formatDate(g.created_at) : '?';
        return `
        <tr>
          <td>${getBadgeStatus(g.status)}</td>
          <td>${g.players_count || 0}</td>
          <td>${fecha}</td>
          <td>
            <div class="flex gap-2">
              <button class="btn btn-sm" onclick="viewGameDetail('${g.code}')">Ver</button>
              <button class="btn btn-ghost btn-sm" onclick="showCodeModal('${g.code}')">C?digo</button>
            </div>
          </td>
        </tr>
      `}).join('');"""

new_ld = """      tbody.innerHTML = recent.map(g => {
        const gc = g.code || g.game_code || '?';
        const fecha = formatDate(g.created_at);
        return `
        <tr>
          <td class="font-mono font-weight-600" style="color:var(--gold)">${gc}</td>
          <td>${getBadgeStatus(g.status)}</td>
          <td>${g.players_count || 0}</td>
          <td>${fecha}</td>
          <td>
            <div class="flex gap-2">
              <button class="btn btn-sm" onclick="viewGameDetail('${gc}')">Ver</button>
              <button class="btn btn-ghost btn-sm" onclick="showCodeModal('${gc}')">C\u00f3digo</button>
            </div>
          </td>
        </tr>
      `}).join('');"""

# Only replace if found (with flexible matching for odd characters)
import re
text = re.sub(r"      tbody\.innerHTML = games\.map\(g => \{\s*//.*?\s*const gc =.*?\s*const fecha =.*?\s*return `\s*<tr>.*?</tr>\s*`\}\)\.join\(''\);", new_lg, text, flags=re.DOTALL)
text = re.sub(r"      tbody\.innerHTML = recent\.map\(g => \{\s*const fecha =.*?\s*return `\s*<tr>.*?</tr>\s*`\}\)\.join\(''\);", new_ld, text, flags=re.DOTALL)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated admin.html tables")
