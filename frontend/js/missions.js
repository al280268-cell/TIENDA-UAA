"use strict";

const Missions = {
  currentMission: null,
  currentMissionId: null,
  missionStartTime: null,
  answered: false,

  // ─── Public entry point ───────────────────────────────────────────────────
  /**
   * Render a mission received from /api/missions/generate
   * @param {Object} serverResponse - {mission_id, mission_type, mission_data}
   */
  render(serverResponse) {
    this.currentMission  = serverResponse;
    this.currentMissionId = serverResponse.mission_id;
    this.missionStartTime = Date.now();
    this.answered = false;

    const container = document.getElementById('mission-content');
    if (!container) return;
    container.innerHTML = '';

    // Update the type badge
    const badge = document.getElementById('mission-type-badge');
    if (badge) badge.textContent = this._typeLabel(serverResponse.mission_type);

    const d = serverResponse.mission_data;
    switch (serverResponse.mission_type) {
      case 'detective':  this._renderDetective(d, container);  break;
      case 'find_error': this._renderFindError(d, container);  break;
      case 'best_cart':  this._renderBestCart(d, container);   break;
      case 'decision':   this._renderDecision(d, container);   break;
      case 'speed':      this._renderSpeed(d, container);      break;
      case 'memory':     this._renderMemory(d, container);     break;
      case 'order':      this._renderOrder(d, container);      break;
      case 'code':       this._renderCode(d, container);       break;
      case 'social':     this._renderSocial(d, container);     break;
      case 'special':    this._renderSpecial(d, container);    break;
      default:
        container.innerHTML = `<p style="color:#C41230;">Misión desconocida: ${serverResponse.mission_type}</p>`;
    }
  },

  _typeLabel(type) {
    const labels = {
      detective:  '🔎 Detective',
      find_error: '🧮 Encuentra el Error',
      best_cart:  '🛒 Carrito Perfecto',
      decision:   '🤔 Decisión de Compra',
      speed:      '⚡ Velocidad',
      memory:     '🧠 Memoria',
      order:      '📋 Ordenar',
      code:       '🔑 Código Secreto',
      social:     '📱 Misión Social',
      special:    '⭐ Misión Especial',
    };
    return labels[type] || type;
  },

  // ─── DETECTIVE ─────────────────────────────────────────────────────────────
  // Backend sends: {products: [...], correct_id: str, explanation: str}
  // One product has price ~10% of real = suspicious
  _renderDetective(data, container) {
    const products = data.products || [];
    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">Detecta al vendedor sospechoso</h2>
          <p class="mission-description">Analiza estas 3 ofertas. Una tiene señales claras de fraude. ¿Cuál es?</p>
        </div>
        <div class="mission-body">
          <div class="options-list" id="detective-opts">
            ${products.map((p, i) => `
              <button class="option-btn" id="opt-${p.id}"
                onclick="Missions._selectOption('${p.id}', this, 'detective-opts')">
                <div style="display:flex;align-items:center;gap:12px;">
                  <span style="font-size:2rem">${p.emoji || '🛍️'}</span>
                  <div style="text-align:left">
                    <strong>${p.name}</strong><br>
                    <span style="font-size:1.1rem;font-weight:700;color:var(--uaa-red)">$${p.price} MXN</span><br>
                    <small>⭐ ${p.rating} · ${p.category}</small>
                  </div>
                </div>
              </button>
            `).join('')}
          </div>
        </div>
        <div class="mission-footer">
          <button class="btn btn-primary w-full" id="submit-detective" disabled
            onclick="Missions.submit(Missions._selectedAnswer)">
            CONFIRMAR SOSPECHOSO
          </button>
        </div>
      </div>`;
    this._selectedAnswer = null;
  },

  // ─── FIND ERROR ────────────────────────────────────────────────────────────
  // Backend sends: {order_data: {items, subtotal, shipping, total_shown}, correct_total, error_description}
  _renderFindError(data, container) {
    const od = data.order_data || {};
    const items = od.items || [];
    const totalShown = od.total_shown || 0;
    const correctTotal = data.correct_total || 0;

    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">Detecta el error en este pedido</h2>
          <p class="mission-description">Observa el desglose. ¿Hay algún problema con los números?</p>
        </div>
        <div class="mission-body">
          <div class="card" style="margin-bottom:16px;padding:16px;">
            ${items.map(it => `
              <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee;">
                <span>${it.emoji || ''} ${it.name}</span>
                <strong>$${it.price} MXN</strong>
              </div>
            `).join('')}
            <div style="display:flex;justify-content:space-between;padding:10px 0;font-size:1.1rem;">
              <span>Envío estándar</span>
              <strong>$${od.shipping || 0} MXN</strong>
            </div>
            <div style="display:flex;justify-content:space-between;padding:10px 0;font-weight:800;font-size:1.2rem;border-top:2px solid #1A1A1A;">
              <span>TOTAL MOSTRADO:</span>
              <span style="color:var(--uaa-red)">$${totalShown} MXN</span>
            </div>
          </div>
          <div class="options-list" id="error-opts">
            <button class="option-btn" onclick="Missions.submit('${correctTotal}')">
              <span class="option-key">A</span>
              El total es incorrecto. La suma correcta es <strong>$${correctTotal} MXN</strong>.
            </button>
            <button class="option-btn" onclick="Missions.submit('no_error')">
              <span class="option-key">B</span>
              No hay ningún error. Todo está bien calculado.
            </button>
            <button class="option-btn" onclick="Missions.submit('shipping_wrong')">
              <span class="option-key">C</span>
              El costo de envío es el error, es demasiado alto.
            </button>
          </div>
        </div>
      </div>`;
  },

  // ─── BEST CART ─────────────────────────────────────────────────────────────
  // Backend sends: {budget, target_range: [min,max], required_categories, max_items, bonus_condition}
  _renderBestCart(data, container) {
    // Use the global PRODUCTS catalog visible to frontend (embedded inline here)
    const catalog = [
      {id:'p1',name:'Audífonos Bluetooth Pro',category:'Electrónica',price:899,emoji:'🎧'},
      {id:'p2',name:'Mochila Tech UAA',category:'Accesorios',price:599,emoji:'🎒'},
      {id:'p3',name:'Termo Inoxidable 750ml',category:'Hogar',price:349,emoji:'🥤'},
      {id:'p4',name:'Webcam Full HD 1080p',category:'Electrónica',price:1299,emoji:'📷'},
      {id:'p5',name:'Teclado Mecánico RGB',category:'Electrónica',price:2499,emoji:'⌨️'},
      {id:'p6',name:'Ratón Inalámbrico',category:'Electrónica',price:449,emoji:'🖱️'},
      {id:'p7',name:'Lámpara LED Escritorio',category:'Hogar',price:289,emoji:'💡'},
      {id:'p8',name:'Mug Cerámica UAA',category:'Accesorios',price:129,emoji:'☕'},
      {id:'p9',name:'Hub USB-C 7 en 1',category:'Electrónica',price:799,emoji:'🔌'},
      {id:'p10',name:'Libreta Ejecutiva',category:'Accesorios',price:189,emoji:'📒'},
      {id:'p11',name:'Soporte Laptop Aluminio',category:'Accesorios',price:549,emoji:'💻'},
      {id:'p12',name:'Altavoz Bluetooth Mini',category:'Electrónica',price:699,emoji:'🔊'},
    ];

    let cartItems = [];
    const [minBudget, maxBudget] = data.target_range || [data.budget - 200, data.budget];

    const updateCart = () => {
      const total = cartItems.reduce((s, i) => s + i.price, 0);
      document.getElementById('cart-total').textContent = `$${total} MXN`;
      const pct = Math.min(100, (total / maxBudget) * 100);
      document.getElementById('cart-progress-fill').style.width = `${pct}%`;
      const inRange = total >= minBudget && total <= maxBudget;
      const hasEnoughCats = new Set(cartItems.map(i => i.category)).size >= (data.required_categories || 1);
      const notTooMany = cartItems.length <= (data.max_items || 4);
      document.getElementById('submit-cart').disabled = !(inRange && hasEnoughCats && notTooMany);

      const cartList = document.getElementById('cart-list');
      cartList.innerHTML = cartItems.length === 0
        ? '<p style="color:#999;font-style:italic">Carrito vacío</p>'
        : cartItems.map(ci => `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid #eee;">
              <span>${ci.emoji} ${ci.name}</span>
              <div style="display:flex;gap:8px;align-items:center;">
                <strong>$${ci.price}</strong>
                <button style="background:#C41230;color:white;border:none;border-radius:4px;width:24px;height:24px;cursor:pointer;font-weight:bold;"
                  onclick="Missions._removeFromCart('${ci.id}')">×</button>
              </div>
            </div>`).join('');
    };

    this._cartItems = cartItems;
    this._addToCart = (product) => {
      if (cartItems.length >= (data.max_items || 4)) {
        UI.toast(`Máximo ${data.max_items} productos`, 'warning');
        return;
      }
      if (!cartItems.find(i => i.id === product.id)) {
        cartItems.push(product);
        updateCart();
      } else {
        UI.toast('Este producto ya está en el carrito', 'info');
      }
    };
    this._removeFromCart = (productId) => {
      this._cartItems = cartItems = cartItems.filter(i => i.id !== productId);
      updateCart();
    };

    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">Construye el carrito perfecto</h2>
          <p class="mission-description">
            Objetivo: <strong>$${minBudget}–$${maxBudget} MXN</strong> · 
            Mín. <strong>${data.required_categories} categorías</strong> · 
            Máx. <strong>${data.max_items} productos</strong>
          </p>
        </div>
        <div class="mission-body" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
          <div>
            <h4 style="margin:0 0 8px;">Catálogo</h4>
            <div style="display:flex;flex-direction:column;gap:6px;max-height:380px;overflow-y:auto;">
              ${catalog.map(p => `
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px;background:#f9f9f9;border-radius:8px;">
                  <span>${p.emoji} ${p.name}<br><small style="color:#888">${p.category} · $${p.price}</small></span>
                  <button class="btn btn-sm btn-secondary" onclick="Missions._addToCart(${JSON.stringify(p).replace(/"/g, '&quot;')})">+</button>
                </div>`).join('')}
            </div>
          </div>
          <div>
            <h4 style="margin:0 0 8px;">Mi Carrito</h4>
            <div id="cart-list" style="min-height:100px;margin-bottom:12px;"></div>
            <div style="display:flex;justify-content:space-between;font-weight:700;margin-bottom:8px;">
              <span>Total:</span><span id="cart-total">$0 MXN</span>
            </div>
            <div class="progress-bar" style="margin-bottom:16px;">
              <div id="cart-progress-fill" class="progress-fill" style="width:0%;"></div>
            </div>
            <button class="btn btn-primary w-full" id="submit-cart" disabled
              onclick="Missions.submit(Missions._cartItems)">
              ENVIAR CARRITO
            </button>
          </div>
        </div>
      </div>`;
    updateCart();
  },

  _addToCart(p) { if (this._addToCart) this._addToCart(p); },
  _removeFromCart(id) { if (this._removeFromCart) this._removeFromCart(id); },

  // ─── DECISION ──────────────────────────────────────────────────────────────
  // Backend sends: {scenario, budget, options: [...products], correct_option_id}
  _renderDecision(data, container) {
    const options = data.options || [];
    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">Decisión de Compra</h2>
          <p class="mission-description">${data.scenario} — Presupuesto: <strong>$${data.budget} MXN</strong></p>
        </div>
        <div class="mission-body">
          <div class="options-list" id="decision-opts">
            ${options.map((opt, i) => `
              <button class="option-btn" id="opt-${opt.id}"
                onclick="Missions._selectOption('${opt.id}', this, 'decision-opts')">
                <span class="option-key">${String.fromCharCode(65 + i)}</span>
                <div style="text-align:left">
                  <strong>${opt.emoji || ''} ${opt.name}</strong><br>
                  <span style="color:var(--uaa-red);font-weight:700">$${opt.price} MXN</span>
                  <span> · ⭐${opt.rating} · ${opt.category}</span>
                </div>
              </button>
            `).join('')}
          </div>
        </div>
        <div class="mission-footer">
          <button class="btn btn-primary w-full" id="submit-decision" disabled
            onclick="Missions.submit(Missions._selectedAnswer)">
            CONFIRMAR ELECCIÓN
          </button>
        </div>
      </div>`;
    this._selectedAnswer = null;
  },

  // ─── SPEED ─────────────────────────────────────────────────────────────────
  // Backend sends: {target_description, target_product_id, time_limit_seconds, products}
  _renderSpeed(data, container) {
    const products = data.products || [];
    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title" style="color:var(--uaa-red);">⚡ MISIÓN DE VELOCIDAD</h2>
          <p class="mission-description">${data.target_description}</p>
          <div class="speed-timer" id="speed-timer" style="font-size:3rem;font-weight:900;color:var(--uaa-red);text-align:center;margin:12px 0;">
            ${data.time_limit_seconds}s
          </div>
        </div>
        <div class="mission-body">
          <div class="product-grid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
            ${products.map(p => `
              <button class="option-btn" onclick="Missions.submit('${p.id}'); Timer.stopMission();">
                <div style="text-align:center">
                  <div style="font-size:2.5rem">${p.emoji || '🛍️'}</div>
                  <strong>${p.name}</strong><br>
                  <span style="color:var(--uaa-red)">$${p.price} MXN</span>
                </div>
              </button>
            `).join('')}
          </div>
        </div>
      </div>`;

    // Start mission-specific timer
    Timer.startMission(data.time_limit_seconds,
      (remaining) => {
        const el = document.getElementById('speed-timer');
        if (el) {
          el.textContent = `${remaining}s`;
          if (remaining <= 5) el.style.animation = 'pulse 0.5s infinite';
        }
      },
      () => {
        if (!this.answered) {
          UI.toast('¡Tiempo agotado! -40 puntos', 'error');
          UI.sounds.play('wrong');
          this.answered = true;
          this.submit('__timeout__');
        }
      }
    );
  },

  // ─── MEMORY ────────────────────────────────────────────────────────────────
  // Backend sends: {show_data: {items}, questions: [...], show_duration_seconds}
  _renderMemory(data, container) {
    const items = (data.show_data || {}).items || [];
    const questions = data.questions || ['¿Cuántos productos viste?'];
    const duration = data.show_duration_seconds || 5;

    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">🧠 ¡Memoriza!</h2>
          <p class="mission-description" id="memory-instruction">Tienes <strong id="mem-countdown">${duration}</strong> segundos para memorizar.</p>
        </div>
        <div class="mission-body" id="memory-body">
          <div class="memory-display" style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
            ${items.map(p => `
              <div style="background:#f0f0f0;border-radius:10px;padding:12px;text-align:center;">
                <div style="font-size:2rem">${p.emoji || '📦'}</div>
                <strong>${p.name}</strong><br>
                <span style="color:var(--uaa-red);font-weight:700">$${p.price} MXN</span><br>
                <small>⭐${p.rating} · ${p.category}</small>
              </div>`).join('')}
          </div>
        </div>
      </div>`;

    // Countdown then hide and show question
    let secs = duration;
    const tick = setInterval(() => {
      secs--;
      const el = document.getElementById('mem-countdown');
      if (el) el.textContent = secs;
      if (secs <= 0) {
        clearInterval(tick);
        this._showMemoryQuestion(container, items, questions[0]);
      }
    }, 1000);
  },

  _showMemoryQuestion(container, items, question) {
    // Generate 4 answer options including one correct
    const correctItem = items[Math.floor(Math.random() * items.length)];
    const otherItems = items.filter(i => i.id !== correctItem.id);
    const wrongItem = otherItems[0] || {price: correctItem.price + 100};
    const wrongItem2 = otherItems[1] || {price: correctItem.price + 200};

    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">¿Qué recuerdas?</h2>
          <p class="mission-description">¿Cuál era el precio del <strong>${correctItem.name}</strong>?</p>
        </div>
        <div class="mission-body">
          <div class="options-list">
            ${[correctItem.price, wrongItem.price, wrongItem2.price, correctItem.price + 150]
              .sort(() => Math.random() - 0.5)
              .map((price, i) => `
                <button class="option-btn" onclick="Missions.submit('${price}')">
                  <span class="option-key">${String.fromCharCode(65+i)}</span>
                  $${price} MXN
                </button>`).join('')}
          </div>
        </div>
      </div>`;
  },

  // ─── ORDER ─────────────────────────────────────────────────────────────────
  // Backend sends: {items: [...], correct_order: [...ids sorted by price]}
  _renderOrder(data, container) {
    const items = data.items || [];
    let orderedItems = [];

    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">📋 Ordena de menor a mayor precio</h2>
          <p class="mission-description">Toca los productos en orden ascendente de precio.</p>
        </div>
        <div class="mission-body">
          <div id="order-source" style="display:flex;flex-direction:column;gap:8px;">
            ${items.map(p => `
              <button class="option-btn" id="order-item-${p.id}"
                onclick="Missions._tapOrderItem('${p.id}', '${p.name}', this)">
                ${p.emoji || '📦'} ${p.name} — <strong>$??? MXN</strong>
              </button>`).join('')}
          </div>
          <div id="order-result" style="margin-top:16px;min-height:40px;padding:10px;background:#f9f9f9;border-radius:8px;font-size:0.9rem;">
            Orden elegido: <span id="order-sequence">—</span>
          </div>
        </div>
        <div class="mission-footer">
          <button class="btn btn-danger btn-sm" onclick="Missions._resetOrder()" style="margin-right:8px;">Reiniciar</button>
          <button class="btn btn-primary" id="submit-order" disabled
            onclick="Missions.submit(Missions._orderResult)">
            CONFIRMAR ORDEN
          </button>
        </div>
      </div>`;

    this._orderResult = [];
    this._tapOrderItem = (id, name, btn) => {
      if (this._orderResult.includes(id)) return;
      this._orderResult.push(id);
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const seq = document.getElementById('order-sequence');
      if (seq) seq.textContent = this._orderResult.map((rid, i) => `${i+1}. ${items.find(it=>it.id===rid)?.name||rid}`).join(' → ');
      if (this._orderResult.length === items.length) {
        const submitBtn = document.getElementById('submit-order');
        if (submitBtn) submitBtn.disabled = false;
      }
    };
    this._resetOrder = () => {
      this._orderResult = [];
      items.forEach(p => {
        const btn = document.getElementById(`order-item-${p.id}`);
        if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
      });
      const seq = document.getElementById('order-sequence');
      if (seq) seq.textContent = '—';
      const submitBtn = document.getElementById('submit-order');
      if (submitBtn) submitBtn.disabled = true;
    };
  },

  // ─── CODE ──────────────────────────────────────────────────────────────────
  // Backend sends: {instructions, hint}
  _renderCode(data, container) {
    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">🔑 Código Secreto</h2>
          <p class="mission-description">${data.instructions || 'Encuentra el código secreto en el stand.'}</p>
        </div>
        <div class="mission-body" style="text-align:center;">
          <input type="text" id="code-input"
            class="input"
            placeholder="Introduce el código aquí"
            maxlength="20"
            style="text-align:center;font-size:1.4rem;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;"
            oninput="this.value=this.value.toUpperCase()"
            onkeydown="if(event.key==='Enter') Missions._submitCode()">
          <details style="margin-bottom:16px;text-align:left;">
            <summary style="cursor:pointer;color:#888;font-size:0.85rem;">Ver pista</summary>
            <p style="margin-top:8px;color:#555;">${data.hint || 'Busca en el stand.'}</p>
          </details>
        </div>
        <div class="mission-footer">
          <button class="btn btn-primary w-full" onclick="Missions._submitCode()">
            VALIDAR CÓDIGO
          </button>
        </div>
      </div>`;
  },

  _submitCode() {
    const val = document.getElementById('code-input')?.value?.trim();
    if (!val) { UI.toast('Ingresa un código', 'warning'); return; }
    this.submit(val);
  },

  // ─── SOCIAL ────────────────────────────────────────────────────────────────
  // Backend sends: {platform, handle, instructions, code_hint}
  _renderSocial(data, container) {
    container.innerHTML = `
      <div class="mission-card">
        <div class="mission-header">
          <h2 class="mission-title">📱 Misión Social</h2>
          <p class="mission-description">${data.instructions}</p>
        </div>
        <div class="mission-body" style="text-align:center;">
          <div style="font-size:1.5rem;font-weight:700;color:var(--uaa-red);margin:12px 0;">
            ${data.handle || '@UAA'}
          </div>
          <a href="https://www.instagram.com/${(data.handle||'').replace('@','')}"
            target="_blank" rel="noopener"
            class="btn btn-secondary" style="display:inline-block;margin-bottom:16px;">
            📸 Abrir Instagram
          </a>
          <p style="color:#888;font-size:0.85rem;">${data.code_hint || 'Busca el código en la historia.'}</p>
          <input type="text" id="social-code-input"
            class="input"
            placeholder="Introduce el código que encontraste"
            maxlength="20"
            style="text-align:center;font-size:1.2rem;letter-spacing:3px;text-transform:uppercase;margin-top:12px;"
            oninput="this.value=this.value.toUpperCase()">
        </div>
        <div class="mission-footer">
          <button class="btn btn-primary w-full" onclick="Missions._submitSocialCode()">
            VALIDAR CÓDIGO
          </button>
        </div>
      </div>`;
  },

  _submitSocialCode() {
    const val = document.getElementById('social-code-input')?.value?.trim();
    if (!val) { UI.toast('Ingresa el código encontrado', 'warning'); return; }
    this.submit(val);
  },

  // ─── SPECIAL ───────────────────────────────────────────────────────────────
  // Backend sends: {secret_title, task, reward_multiplier}
  _renderSpecial(data, container) {
    container.innerHTML = `
      <div class="mission-card" style="border:2px solid #D4A017;background:linear-gradient(135deg,#fffbf0,#fff8e0);">
        <div class="mission-header" style="text-align:center;">
          <div style="font-size:3rem;margin-bottom:8px;animation:pop 0.5s ease-out">⭐</div>
          <h2 class="mission-title" style="color:#D4A017;">MISIÓN SECRETA DESBLOQUEADA</h2>
          <p class="mission-description">${data.secret_title || 'Has encontrado algo especial'}</p>
          <div style="background:#D4A017;color:white;padding:6px 16px;border-radius:20px;display:inline-block;font-weight:700;margin-top:8px;">
            ×${data.reward_multiplier || 2.0} MULTIPLICADOR
          </div>
        </div>
        <div class="mission-body" style="text-align:center;padding:20px;">
          <p style="font-size:1.1rem;">${data.task || 'Completa la tarea especial del stand.'}</p>
          <p style="color:#888;font-size:0.85rem;margin-top:8px;">Habla con el staff para obtener el código de validación.</p>
          <input type="text" id="special-code-input"
            class="input"
            placeholder="Código de validación del staff"
            maxlength="20"
            style="text-align:center;font-size:1.2rem;letter-spacing:3px;text-transform:uppercase;margin-top:16px;"
            oninput="this.value=this.value.toUpperCase()">
        </div>
        <div class="mission-footer">
          <button class="btn btn-gold w-full" onclick="Missions._submitSpecial()">
            COMPLETAR MISIÓN ESPECIAL
          </button>
        </div>
      </div>`;
  },

  _submitSpecial() {
    const val = document.getElementById('special-code-input')?.value?.trim();
    if (!val) { UI.toast('Ingresa el código del staff', 'warning'); return; }
    this.submit(val);
  },

  // ─── Helpers ───────────────────────────────────────────────────────────────
  _selectedAnswer: null,
  _cartItems: [],
  _orderResult: [],

  _selectOption(value, btn, containerid) {
    this._selectedAnswer = value;
    document.querySelectorAll(`#${containerid} .option-btn`).forEach(b => {
      b.classList.remove('selected');
      b.style.borderColor = '';
    });
    btn.classList.add('selected');
    btn.style.borderColor = 'var(--uaa-red)';
    // Enable submit button
    const submitBtn = document.querySelector(`#submit-${containerid.replace('-opts', '')}`);
    if (submitBtn) submitBtn.disabled = false;
  },

  // ─── Submit answer to backend ─────────────────────────────────────────────
  async submit(answer) {
    if (this.answered) return;
    this.answered = true;

    const timeTaken = Date.now() - (this.missionStartTime || Date.now());

    // Disable all option buttons to prevent double-submit
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);

    const { data, error } = await App.Api.post('/api/missions/validate', {
      player_id:    App.Session.get('uaa_player_id'),
      game_code:    App.Session.get('uaa_game_code'),
      mission_id:   this.currentMissionId,
      mission_type: this.currentMission?.mission_type || '',
      answer:       answer,
      time_taken_ms: timeTaken,
    });

    if (error) {
      UI.toast('Error al enviar respuesta: ' + error, 'error');
      this.answered = false; // allow retry
      document.querySelectorAll('.option-btn').forEach(b => b.disabled = false);
      return;
    }

    // Let Scoring module handle the visual feedback
    if (window.Scoring) {
      Scoring.handleMissionResult(data);
    }

    // Show feedback on buttons if detective/decision/find_error
    if (data.correct) {
      UI.sounds && UI.sounds.play('correct');
      UI.toast(`+${data.points} puntos`, 'success', 2000);
    } else {
      UI.sounds && UI.sounds.play('wrong');
      UI.toast(`Incorrecto. ${data.explanation || ''}`, 'error', 3000);
    }

    // Load next mission after delay
    setTimeout(() => this.loadNext(), 2500);
  },

  // ─── Load next mission ────────────────────────────────────────────────────
  async loadNext() {
    const round = window.currentRound || 1;
    const { data, error } = await App.Api.post('/api/missions/generate', {
      player_id:    App.Session.get('uaa_player_id'),
      game_code:    App.Session.get('uaa_game_code'),
      round_number: round,
    });

    if (error || !data) {
      UI.toast('Error cargando siguiente misión', 'error');
      return;
    }

    this.render(data);
  },
};

window.Missions = Missions;
