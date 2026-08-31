const Rewards = {
  rewards: [],
  myPoints: 0,
  myRank: 0,
  hasClaimed: false,
  
  async fetchRewards(gameCode) {
    this.myPoints = parseInt(App.Session.get('uaa_final_points') || '0', 10);
    this.myRank = parseInt(App.Session.get('uaa_final_rank') || '999', 10);
    
    const { data } = await App.Api.get(`/api/rewards?game_code=${gameCode}`);
    if (data) {
      this.rewards = data;
      this.render();
    }
  },
  
  render() {
    const container = document.getElementById('rewards-grid');
    if (!container) return;
    
    if (this.rewards.length === 0) {
      container.innerHTML = '<p style="text-align:center; color:#666; width:100%;">No hay premios configurados para esta partida.</p>';
      return;
    }
    
    container.innerHTML = this.rewards.map(reward => {
      const eligible = this.myPoints >= reward.min_points && 
                       (reward.min_rank === null || this.myRank <= reward.min_rank);
      const available = reward.stock_remaining > 0;
      
      let btnText, btnClass, btnDisabled;
      if (!available) { 
        btnText = 'AGOTADO'; btnClass = 'btn-ghost'; btnDisabled = true; 
      } else if (!eligible) { 
        btnText = `Requiere ${reward.min_points} pts`; btnClass = 'btn-ghost'; btnDisabled = true; 
      } else if (this.hasClaimed) { 
        btnText = 'Ya canjeaste'; btnClass = 'btn-ghost'; btnDisabled = true; 
      } else { 
        btnText = 'CANJEAR PREMIO'; btnClass = 'btn-gold'; btnDisabled = false; 
      }
      
      return `
        <div class="reward-card" style="background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 2px solid ${eligible && available ? '#C87A00' : '#eee'}; opacity: ${available ? 1 : 0.6}; display: flex; flex-direction: column;">
          <div style="font-size: 48px; margin-bottom: 8px;">${reward.emoji}</div>
          <h3 style="margin: 0 0 8px 0; font-size: 18px;">${reward.name}</h3>
          <div style="color: #666; font-size: 14px; margin-bottom: 4px;">Disponibles: <strong>${reward.stock_remaining}</strong></div>
          <div style="color: #666; font-size: 14px; margin-bottom: 16px;">Mínimo: ${reward.min_points} pts ${reward.min_rank ? ` | Rank ≤ ${reward.min_rank}` : ''}</div>
          <button style="margin-top: auto; padding: 12px; border-radius: 8px; font-weight: bold; border: none; cursor: ${btnDisabled ? 'not-allowed' : 'pointer'}; background: ${btnDisabled ? '#eee' : '#C87A00'}; color: ${btnDisabled ? '#999' : 'white'};" ${btnDisabled ? 'disabled' : ''} onclick="Rewards.claim('${reward.id}')">
            ${btnText}
          </button>
        </div>`;
    }).join('');
  },
  
  async claim(rewardId) {
    if (this.hasClaimed) {
      UI.toast('Ya has canjeado un premio en esta partida.', 'warning');
      return;
    }
    
    UI.showModal({
      emoji: '🎁',
      title: '¿Confirmar canje?',
      message: 'Solo puedes canjear 1 premio por partida. ¡Asegúrate de que este sea el que quieres!',
      primaryBtn: { 
        text: 'CONFIRMAR', 
        action: async () => {
          UI.closeModal();
          UI.showLoader('Procesando canje...');
          const { data, error } = await App.Api.post('/api/rewards/claim', {
            player_id: App.Session.get('uaa_player_id'),
            game_code: App.Session.get('uaa_game_code'),
            reward_id: rewardId
          });
          UI.hideLoader();
          
          if (error || !data.success) {
            UI.toast(data?.message || 'Error al canjear', 'error');
            return;
          }
          
          this.hasClaimed = true;
          this.showClaimSuccess(data.claim_code, rewardId);
          UI.fireConfetti();
          UI.sounds.play('victory');
          this.fetchRewards(App.Session.get('uaa_game_code')); 
        }
      },
      secondaryBtn: { text: 'Cancelar', action: () => { UI.closeModal(); } },
      closable: true
    });
  },
  
  showClaimSuccess(claimCode, rewardId) {
    const reward = this.rewards.find(r => r.id === rewardId);
    const section = document.getElementById('claim-success');
    if (!section) return;
    
    section.hidden = false;
    document.getElementById('claim-code-display').textContent = claimCode;
    document.getElementById('claimed-reward-name').textContent = reward?.name || 'Tu premio';
    
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(claimCode)}`;
    const qrImg = document.getElementById('claim-qr');
    if (qrImg) {
      qrImg.src = qrUrl;
      qrImg.hidden = false;
    }
    
    section.scrollIntoView({behavior:'smooth'});
  }
};

window.Rewards = Rewards;
