"use strict";

/**
 * Scoring — handles mission results, HUD updates, rank changes, streaks.
 * Works with the IDs in game.html: score-val, streak-chip, streak-val.
 */
const Scoring = {
  currentPoints:  0,
  currentStreak:  0,
  currentRank:    0,
  myPlayerId:     '',

  // Called by Missions.submit() after /api/missions/validate response
  handleMissionResult(result) {
    const prevPoints = this.currentPoints;
    const prevRank   = this.currentRank;

    this.currentPoints = result.total_points != null ? result.total_points : this.currentPoints;
    this.currentStreak = result.streak != null ? result.streak : this.currentStreak;

    // Sounds
    if (window.UI && UI.sounds) {
      if (result.correct) {
        UI.sounds.play('correct');
      } else {
        UI.sounds.play('wrong');
      }
      if (result.streak >= 2 && result.streak > (prevRank || 0)) {
        UI.sounds.play('streak');
      }
    }

    // Floating points popup
    if (result.correct && result.points > 0 && window.UI && UI.showPointsPopup) {
      UI.showPointsPopup(result.points);
    }

    // Streak popup
    if (result.streak >= 2 && window.UI && UI.showStreakPopup) {
      UI.showStreakPopup(result.streak);
    }

    // Rank change
    if (result.new_rank && this.currentRank && result.new_rank !== this.currentRank) {
      const dir = result.new_rank < this.currentRank ? 'up' : 'down';
      if (window.UI && UI.showRankChange) UI.showRankChange(result.new_rank, dir);
    }
    if (result.new_rank) this.currentRank = result.new_rank;

    this.updateHUD();
  },

  // Update all HUD display elements (IDs match game.html)
  updateHUD() {
    // Points counter
    const scoreEl = document.getElementById('score-val');
    if (scoreEl) {
      this.animatePoints(parseInt(scoreEl.textContent.replace(/[^0-9]/g, '') || '0'), this.currentPoints, scoreEl);
    }

    // Mini leaderboard points
    const miniPts = document.getElementById('my-points-mini');
    if (miniPts) miniPts.textContent = App.formatPoints(this.currentPoints) + ' PTS';

    // Streak chip
    const streakChip = document.getElementById('streak-chip');
    const streakVal  = document.getElementById('streak-val');
    if (streakChip && streakVal) {
      if (this.currentStreak >= 2) {
        streakChip.classList.remove('hidden');
        streakVal.textContent = this.currentStreak;
      } else {
        streakChip.classList.add('hidden');
      }
    }

    // Mini rank
    const miniRank = document.getElementById('my-rank-mini');
    if (miniRank && this.currentRank) miniRank.textContent = this.currentRank;
  },

  // Smooth counter animation
  animatePoints(from, to, element) {
    if (from === to) {
      element.textContent = App.formatPoints(to);
      return;
    }
    const duration  = 800;
    const startTime = performance.now();
    const update = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      element.textContent = App.formatPoints(Math.floor(from + (to - from) * eased));
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  },
};

window.Scoring = Scoring;
