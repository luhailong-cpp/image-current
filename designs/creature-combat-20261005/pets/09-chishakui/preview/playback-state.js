/* Exact elapsed-time state for one normal/0.25x preview pair. No interpolation. */
(function (root) {
  class CombatTimeline {
    constructor(count, durationMs) {
      if (!Number.isInteger(count) || count < 1 || !(durationMs > 0)) throw new Error('Invalid timeline');
      this.count = count;
      this.durationMs = durationMs;
      this.totalMs = count * durationMs;
      this.reset();
    }
    reset() {
      this.normalMs = 0;
      this.slowMs = 0;
      this.paused = false;
    }
    advance(deltaMs, globallyPaused = false) {
      if (this.paused || globallyPaused || !Number.isFinite(deltaMs) || deltaMs < 0) return;
      this.normalMs = (this.normalMs + deltaMs) % this.totalMs;
      this.slowMs = (this.slowMs + deltaMs * 0.25) % this.totalMs;
    }
    get frames() {
      return [Math.floor(this.normalMs / this.durationMs), Math.floor(this.slowMs / this.durationMs)];
    }
    seek(frame) {
      const index = ((Math.trunc(frame) % this.count) + this.count) % this.count;
      this.normalMs = index * this.durationMs;
      this.slowMs = index * this.durationMs;
      this.paused = true;
    }
    step(delta) { this.seek(this.frames[0] + delta); }
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = CombatTimeline;
  else root.CombatTimeline = CombatTimeline;
})(globalThis);
