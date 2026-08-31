"use strict";

/**
 * Leaderboard — manages the live ranking display.
 * Renders into the dark game.html panel (lb-body, lb-mini).
 * Normalizes backend field names: player_id / avatar_initials / avatar_color.
 */
const Leaderboard = {
  entries:    [],
  myPlayerId: '',

  update(rawEntries) {
    if (!rawEntries || !Array.isArray(rawEntries)) return;
    this.entries = rawEntries.map((e, idx) => ({
      player_id:       e.player_id || e.id || `p${idx}`,
      name:            e.name || 'Jugador',
      avatar_initials: e.avatar_initials || e.initials || (e.name ? e.name.slice(0,2).toUpperCase() : '??'),
      avatar_color:    e.avatar_color    || e.color    || '#C41230',
      points:          e.points || e.total_points || 0,
      streak:          e.streak || 0,
      rank:            e.rank   || idx + 1,
      status:          e.status || 'connected',
    }));
    this.entries.sort((a, b) => b.points - a.points);
    this.entries.forEach((e, i) => e.rank = i + 1);
  },

  // Render full list into the side panel <tbody id="lb-body">
  renderFull() {
    const tbody = document.getElementById('lb-body');
    if (!tbody) return;
    if (!this.entries.length) {
      tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:rgba(255,255,255,0.25);padding:24px;">Sin jugadores aún</td></tr>`;
      return;
    }
    tbody.innerHTML = this.entries.map(e => {
      const isMe  = e.player_id === this.myPlayerId;
      const medal = e.rank === 1 ? '🥇' : e.rank === 2 ? '🥈' : e.rank === 3 ? '🥉' : e.rank;
      const posClass = e.rank === 1 ? 'gold' : e.rank === 2 ? 'silver' : e.rank === 3 ? 'bronze' : '';
      const streak = e.streak >= 2 ? `<div class="lb-entry-streak">🔥×${e.streak}</div>` : '';
      return `
        <tr>
          <td style="padding:0;">
            <div class="lb-entry${isMe ? ' me-entry' : ''}">
              <div class="lb-pos ${posClass}">${medal}</div>
              <div class="lb-avatar" style="background:${e.avatar_color};width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;color:white;flex-shrink:0;">${e.avatar_initials}</div>
              <div style="flex:1;min-width:0;">
                <div class="lb-entry-name" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                  ${e.name}${isMe ? ' <span style="color:#ff8899;font-size:0.7rem;">(Tú)</span>' : ''}
                </div>
                ${streak}
              </div>
              <div class="lb-entry-pts">${App.formatPoints(e.points)}</div>
            </div>
          </td>
        </tr>`;
    }).join('');
  },

  // Update the mini bar at the bottom of game.html
  renderMini() {
    const me = this.entries.find(e => e.player_id === this.myPlayerId);
    if (!me) return;

    const nameEl   = document.getElementById('my-name-mini');
    const rankEl   = document.getElementById('my-rank-mini');
    const ptsEl    = document.getElementById('my-points-mini');
    const avatarEl = document.getElementById('my-avatar-mini');

    if (nameEl)   nameEl.textContent       = me.name;
    if (rankEl)   rankEl.textContent       = me.rank;
    if (ptsEl)    ptsEl.textContent        = App.formatPoints(me.points) + ' PTS';
    if (avatarEl) {
      avatarEl.textContent       = me.avatar_initials;
      avatarEl.style.background  = me.avatar_color;
      avatarEl.style.boxShadow   = `0 0 10px ${me.avatar_color}88`;
    }
  },

  // Fetch from API and refresh both displays
  async fetch(gameCode) {
    if (!gameCode || !window.App) return;
    const { data } = await App.Api.get(`/api/scoring/leaderboard/${gameCode}`);
    if (data) {
      this.update(data);
      this.renderFull();
      this.renderMini();
    }
  },
};

window.Leaderboard = Leaderboard;
