const UI = {
  toast(message, type = 'info', duration = 3000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      container.style.cssText = 'position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; display: flex; flex-direction: column; gap: 10px;';
      document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const bgColors = {
      'success': '#1A7A4A',
      'error': '#C41230',
      'warning': '#C87A00',
      'info': '#1565C0'
    };
    toast.style.cssText = `background-color: ${bgColors[type] || bgColors['info']}; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); opacity: 0; transition: opacity 0.3s ease-in-out; text-align: center;`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '1';
    }, 10);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },
  
  showModal(config) {
    let modalOverlay = document.getElementById('ui-modal');
    if (!modalOverlay) {
      modalOverlay = document.createElement('div');
      modalOverlay.id = 'ui-modal';
      modalOverlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000; padding: 20px;';
      document.body.appendChild(modalOverlay);
    }
    
    modalOverlay.innerHTML = `
      <div class="modal-content" style="background: white; padding: 24px; border-radius: 12px; max-width: 400px; width: 100%; text-align: center; position: relative; transform: scale(0.9); opacity: 0; transition: all 0.2s ease-out;">
        ${config.closable ? '<button class="close-btn" style="position: absolute; right: 10px; top: 10px; border: none; background: transparent; font-size: 24px; cursor: pointer;">&times;</button>' : ''}
        ${config.emoji ? `<div style="font-size: 48px; margin-bottom: 16px;">${config.emoji}</div>` : ''}
        ${config.title ? `<h2 style="margin: 0 0 12px 0; color: #333;">${config.title}</h2>` : ''}
        ${config.message ? `<p style="margin: 0 0 24px 0; color: #666; line-height: 1.5;">${config.message}</p>` : ''}
        <div style="display: flex; flex-direction: column; gap: 12px;">
          ${config.primaryBtn ? `<button id="primary-btn" style="background: #C41230; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;">${config.primaryBtn.text}</button>` : ''}
          ${config.secondaryBtn ? `<button id="secondary-btn" style="background: #f0f0f0; color: #333; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;">${config.secondaryBtn.text}</button>` : ''}
        </div>
      </div>
    `;
    
    modalOverlay.style.display = 'flex';
    
    setTimeout(() => {
      const content = modalOverlay.querySelector('.modal-content');
      content.style.transform = 'scale(1)';
      content.style.opacity = '1';
    }, 10);
    
    if (config.primaryBtn) {
      document.getElementById('primary-btn').addEventListener('click', () => {
        config.primaryBtn.action();
      });
    }
    
    if (config.secondaryBtn) {
      document.getElementById('secondary-btn').addEventListener('click', () => {
        config.secondaryBtn.action();
      });
    }
    
    if (config.closable) {
      modalOverlay.querySelector('.close-btn').addEventListener('click', () => this.closeModal());
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) this.closeModal();
      });
    }
  },
  
  closeModal() {
    const modal = document.getElementById('ui-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  },
  
  showPointsPopup(points, isBonus = false) {
    const popup = document.createElement('div');
    popup.textContent = `+${points}`;
    popup.style.cssText = `position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%); font-size: ${isBonus ? '48px' : '36px'}; font-weight: bold; color: ${isBonus ? '#C87A00' : '#1A7A4A'}; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); z-index: 9999; pointer-events: none; transition: all 1s ease-out;`;
    document.body.appendChild(popup);
    
    setTimeout(() => {
      popup.style.transform = 'translate(-50%, -150%) scale(1.5)';
      popup.style.opacity = '0';
    }, 50);
    
    setTimeout(() => popup.remove(), 1000);
  },
  
  showRankChange(newRank, direction) {
    this.toast(`${direction === 'up' ? '↑ SUBISTE' : '↓ BAJASTE'} AL ${newRank}.º LUGAR`, direction === 'up' ? 'success' : 'warning');
  },
  
  showStreakPopup(streak) {
    const popup = document.createElement('div');
    popup.textContent = `🔥 RACHA x${streak}!`;
    popup.style.cssText = `position: fixed; left: 50%; top: 30%; transform: translate(-50%, -50%) scale(0.5); font-size: 42px; font-weight: bold; color: #C41230; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); z-index: 9999; pointer-events: none; transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);`;
    document.body.appendChild(popup);
    
    setTimeout(() => {
      popup.style.transform = 'translate(-50%, -50%) scale(1)';
    }, 50);
    
    setTimeout(() => {
      popup.style.opacity = '0';
      popup.style.transform = 'translate(-50%, -100%) scale(1.2)';
    }, 1500);
    
    setTimeout(() => popup.remove(), 2000);
  },
  
  showEventBanner(eventData) {
    let banner = document.getElementById('event-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'event-banner';
      banner.style.cssText = 'position: fixed; top: -100px; left: 0; right: 0; background: linear-gradient(135deg, #7A3E9D, #C41230); color: white; text-align: center; padding: 16px; font-weight: bold; font-size: 18px; z-index: 10000; box-shadow: 0 4px 10px rgba(0,0,0,0.2); transition: top 0.5s ease;';
      document.body.appendChild(banner);
    }
    banner.textContent = `⭐ EVENTO GLOBAL: ${eventData.name || '¡Doble de Puntos!'} ⭐`;
    banner.style.top = '0';
    
    setTimeout(() => {
      banner.style.top = '-100px';
    }, 5000);
  },
  
  sounds: {
    enabled: true,
    ctx: null,
    init() {
      if (!this.ctx) {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    },
    playTone(freq, type, duration, vol) {
      if (!this.enabled) return;
      this.init();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(vol, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    },
    play(type) {
      if (!this.enabled) return;
      this.init();
      switch (type) {
        case 'correct':
          this.playTone(440, 'sine', 0.1, 0.5);
          setTimeout(() => this.playTone(659.25, 'sine', 0.2, 0.5), 100);
          break;
        case 'wrong':
          this.playTone(300, 'square', 0.15, 0.3);
          setTimeout(() => this.playTone(250, 'square', 0.2, 0.3), 150);
          break;
        case 'streak':
          this.playTone(523.25, 'triangle', 0.1, 0.5);
          setTimeout(() => this.playTone(659.25, 'triangle', 0.1, 0.5), 100);
          setTimeout(() => this.playTone(783.99, 'triangle', 0.2, 0.5), 200);
          break;
        case 'countdown':
          this.playTone(880, 'sine', 0.1, 0.2);
          break;
        case 'tick':
          this.playTone(1000, 'sine', 0.05, 0.1);
          break;
        case 'victory':
          this.playTone(523.25, 'triangle', 0.2, 0.5);
          setTimeout(() => this.playTone(659.25, 'triangle', 0.2, 0.5), 200);
          setTimeout(() => this.playTone(783.99, 'triangle', 0.4, 0.5), 400);
          break;
      }
    }
  },
  
  toggleSound() {
    this.sounds.enabled = !this.sounds.enabled;
    this.toast(this.sounds.enabled ? 'Sonido activado' : 'Sonido silenciado', 'info');
  },
  
  fireConfetti() {
    const colors = ['#C41230', '#ffffff', '#C87A00'];
    for (let i = 0; i < 80; i++) {
      const conf = document.createElement('div');
      conf.style.cssText = `position: fixed; top: -10px; width: 10px; height: 10px; background-color: ${colors[Math.floor(Math.random() * colors.length)]}; left: ${Math.random() * 100}vw; opacity: ${Math.random() + 0.5}; z-index: 9999; transform: rotate(${Math.random() * 360}deg); border-radius: ${Math.random() > 0.5 ? '50%' : '0'}; transition: top ${Math.random() * 2 + 1}s ease-in, transform ${Math.random() * 2 + 1}s linear;`;
      document.body.appendChild(conf);
      
      setTimeout(() => {
        conf.style.top = '110vh';
        conf.style.transform = `rotate(${Math.random() * 720 + 360}deg)`;
      }, 50);
      
      setTimeout(() => conf.remove(), 3500);
    }
  },
  
  showLoader(message = 'Cargando...') {
    let loader = document.getElementById('ui-loader');
    if (!loader) {
      loader = document.createElement('div');
      loader.id = 'ui-loader';
      loader.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.8); z-index: 10001; display: flex; flex-direction: column; align-items: center; justify-content: center;';
      document.body.appendChild(loader);
    }
    loader.innerHTML = `
      <div style="width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #C41230; border-radius: 50%; animation: spin 1s linear infinite;"></div>
      <p style="margin-top: 16px; font-weight: bold; color: #333;">${message}</p>
      <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
    `;
    loader.style.display = 'flex';
  },
  
  hideLoader() {
    const loader = document.getElementById('ui-loader');
    if (loader) loader.style.display = 'none';
  },
  
  showCountdown(onComplete) {
    const container = document.createElement('div');
    container.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center; font-size: 120px; font-weight: bold; color: white;';
    document.body.appendChild(container);
    
    let count = 3;
    container.textContent = count;
    this.sounds.play('countdown');
    
    const interval = setInterval(() => {
      count--;
      if (count > 0) {
        container.textContent = count;
        this.sounds.play('countdown');
      } else if (count === 0) {
        container.textContent = '¡GO!';
        container.style.color = '#1A7A4A';
        this.sounds.play('correct');
      } else {
        clearInterval(interval);
        container.remove();
        if (onComplete) onComplete();
      }
    }, 1000);
  },
  
  renderAvatar(initials, color, size = 'md') {
    return App.createAvatar(initials, color, size);
  }
};

window.UI = UI;
