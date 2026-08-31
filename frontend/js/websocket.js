"use strict";

/**
 * RealtimeClient — Ably WebSocket wrapper with polling fallback.
 *
 * Usage:
 *   RealtimeClient.connect(ablyClientKey, gameCode)  // try Ably first
 *   RealtimeClient.startPolling(gameCode)             // force polling
 *   RealtimeClient.on('event_name', callback)
 *   RealtimeClient.off('event_name', callback)
 *   RealtimeClient.emit('event_name', data)           // trigger local handlers
 */
const RealtimeClient = (() => {
  let ably = null;
  let channel = null;
  let pollingInterval = null;
  let reconnectAttempts = 0;
  const MAX_RECONNECT = 8;
  const handlers = {};
  let _gameCode = null;

  // ── Event Bus ─────────────────────────────────────────────────────────────
  function on(eventType, callback) {
    if (!handlers[eventType]) handlers[eventType] = [];
    handlers[eventType].push(callback);
  }

  function off(eventType, callback) {
    if (handlers[eventType]) {
      handlers[eventType] = handlers[eventType].filter(cb => cb !== callback);
    }
  }

  function emit(eventType, data) {
    (handlers[eventType] || []).forEach(cb => {
      try { cb(data); }
      catch (e) { console.error(`[WS] handler error for ${eventType}:`, e); }
    });
  }

  // ── Ably connection ────────────────────────────────────────────────────────
  function connect(ablyKey, gameCode) {
    _gameCode = gameCode;

    if (!ablyKey || !window.Ably) {
      console.info('[WS] No Ably key or SDK — using polling fallback.');
      startPolling(gameCode);
      return;
    }

    try {
      ably = new window.Ably.Realtime({ key: ablyKey, autoConnect: true });

      ably.connection.on('connected', () => {
        reconnectAttempts = 0;
        stopPolling(); // in case polling was already running
        if (window.UI) UI.toast('Conectado en tiempo real', 'success', 2000);
      });

      ably.connection.on('disconnected', () => _handleDisconnect(gameCode));
      ably.connection.on('suspended',    () => _handleDisconnect(gameCode));
      ably.connection.on('failed',       () => {
        console.warn('[WS] Ably failed, switching to polling');
        startPolling(gameCode);
      });

      channel = ably.channels.get(`game:${gameCode}`);
      channel.subscribe((message) => {
        emit(message.name, message.data);
      });

    } catch (err) {
      console.error('[WS] Ably init error, using polling:', err);
      startPolling(gameCode);
    }
  }

  function _handleDisconnect(gameCode) {
    if (reconnectAttempts < MAX_RECONNECT) {
      reconnectAttempts++;
      const delay = Math.min(Math.pow(2, reconnectAttempts) * 1000, 30000);
      console.warn(`[WS] Disconnected. Retry #${reconnectAttempts} in ${delay}ms`);
      if (window.UI) UI.toast('Reconectando...', 'warning', delay);
      setTimeout(() => {
        if (ably) ably.connection.connect();
      }, delay);
    } else {
      console.warn('[WS] Max reconnects reached. Switching to polling.');
      startPolling(gameCode);
    }
  }

  // ── Polling fallback ───────────────────────────────────────────────────────
  /**
   * Polls /api/games/{code}/state every 3 seconds and synthesizes
   * the same events that Ably would publish.
   */
  let _lastSnapshot = null;

  function startPolling(gameCode) {
    if (pollingInterval) return; // already polling
    _gameCode = gameCode;
    console.info('[WS] Polling /api/games/' + gameCode + '/state every 3s');

    pollingInterval = setInterval(async () => {
      if (!window.App) return;
      const { data } = await window.App.Api.get(`/api/games/${gameCode}/state`);
      if (!data) return;

      const prev = _lastSnapshot;

      // ── Synthesize events from state changes ──────────────────────────────

      // game_paused / game_resumed
      if (prev && prev.status !== data.status) {
        if (data.status === 'paused')   emit('game_paused',  data);
        if (data.status === 'active' && prev.status === 'paused') emit('game_resumed', data);
        if (data.status === 'finished') emit('game_ended',   { leaderboard: data.players });
      }

      // Timer sync (emit a time_sync event that game.js can pick up)
      if (data.time_remaining != null) {
        emit('time_sync', { time_remaining: data.time_remaining });
      }

      // player list changes → score_update with full leaderboard
      if (data.players) {
        // Always emit — game.js will update the leaderboard
        emit('score_update', { leaderboard: data.players });
      }

      // New players joined
      if (prev && data.players && prev.players) {
        const prevIds = new Set(prev.players.map(p => p.player_id));
        data.players.forEach(p => {
          if (!prevIds.has(p.player_id)) emit('player_joined', p);
        });
        // Removed players
        const curIds = new Set(data.players.map(p => p.player_id));
        prev.players.forEach(p => {
          if (!curIds.has(p.player_id)) emit('player_left', p);
        });
      }

      _lastSnapshot = data;

    }, 3000);
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
      console.info('[WS] Polling stopped.');
    }
  }

  function disconnect() {
    stopPolling();
    if (channel) { try { channel.detach(); } catch (_) {} channel = null; }
    if (ably)    { try { ably.close();    } catch (_) {} ably    = null; }
  }

  return { connect, on, off, emit, startPolling, stopPolling, disconnect };
})();

window.RealtimeClient = RealtimeClient;
