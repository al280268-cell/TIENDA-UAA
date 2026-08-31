const Timer = {
  gameSeconds: 0,
  gameInterval: null,
  onTick: null,
  onExpire: null,
  
  startGame(seconds, onTick, onExpire) {
    this.stopGame();
    this.gameSeconds = seconds;
    this.onTick = onTick;
    this.onExpire = onExpire;
    
    if (this.onTick) this.onTick(this.gameSeconds);
    
    this.gameInterval = setInterval(() => {
      if (this.gameSeconds > 0) {
        this.gameSeconds--;
        if (this.onTick) this.onTick(this.gameSeconds);
      } else {
        this.stopGame();
        if (this.onExpire) this.onExpire();
      }
    }, 1000);
  },
  
  pauseGame() {
    if (this.gameInterval) {
      clearInterval(this.gameInterval);
      this.gameInterval = null;
    }
  },
  
  resumeGame() {
    if (!this.gameInterval && this.gameSeconds > 0) {
      this.startGame(this.gameSeconds, this.onTick, this.onExpire);
    }
  },
  
  stopGame() {
    if (this.gameInterval) {
      clearInterval(this.gameInterval);
      this.gameInterval = null;
    }
  },
  
  syncGame(serverSeconds) {
    this.gameSeconds = serverSeconds;
    if (this.onTick) this.onTick(this.gameSeconds);
  },
  
  addTime(seconds) {
    this.gameSeconds += seconds;
    if (this.onTick) this.onTick(this.gameSeconds);
  },
  
  missionSeconds: 0,
  missionInterval: null,
  missionOnTick: null,
  missionOnExpire: null,
  
  startMission(seconds, onTick, onExpire) {
    this.stopMission();
    this.missionSeconds = seconds;
    this.missionOnTick = onTick;
    this.missionOnExpire = onExpire;
    
    if (this.missionOnTick) this.missionOnTick(this.missionSeconds);
    
    this.missionInterval = setInterval(() => {
      if (this.missionSeconds > 0) {
        this.missionSeconds--;
        if (this.missionOnTick) this.missionOnTick(this.missionSeconds);
      } else {
        this.stopMission();
        if (this.missionOnExpire) this.missionOnExpire();
      }
    }, 1000);
  },
  
  stopMission() {
    if (this.missionInterval) {
      clearInterval(this.missionInterval);
      this.missionInterval = null;
    }
  },
  
  format(seconds) {
    if (seconds < 0) seconds = 0;
    return window.App ? window.App.formatTime(seconds) : '00:00';
  }
};

window.Timer = Timer;
