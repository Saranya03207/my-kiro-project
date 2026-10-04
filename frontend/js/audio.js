/**
 * Audio Notification Manager for Smart Canteen Booking System
 * Handles order ready chime playback, browser autoplay policies,
 * Web Audio API fallback synthesis, and user sound preferences.
 */

const STORAGE_KEY = 'canteen_sound_notifications';
const AUDIO_ASSET_PATH = 'assets/sounds/order-ready.wav';

export class AudioManager {
  constructor() {
    this.audioContext = null;
    this.isUnlocked = false;
    this.audioElement = null;
    this.initAudioUnlock();
  }

  /**
   * Check whether sound notifications are enabled in settings
   * Defaults to true if not explicitly set to 'false'
   */
  isSoundEnabled() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored !== 'false';
    } catch {
      return true;
    }
  }

  /**
   * Set user sound notification preference
   * @param {boolean} enabled 
   */
  setSoundEnabled(enabled) {
    try {
      localStorage.setItem(STORAGE_KEY, enabled ? 'true' : 'false');
    } catch (e) {
      console.warn('Could not persist sound preference:', e);
    }
    this.notifyToggleButtons();
  }

  /**
   * Toggle sound notification setting
   * @returns {boolean} New sound enabled state
   */
  toggleSound() {
    const newState = !this.isSoundEnabled();
    this.setSoundEnabled(newState);
    return newState;
  }

  /**
   * Attach early user interaction listeners to unlock audio
   * according to modern browser autoplay security policies.
   */
  initAudioUnlock() {
    if (typeof window === 'undefined') return;
    const unlock = () => {
      this.isUnlocked = true;
      if (this.audioContext && this.audioContext.state === 'suspended') {
        this.audioContext.resume().catch(() => {});
      }
      // Clean up event listeners after first user interaction
      ['pointerdown', 'keydown', 'click'].forEach(evt => {
        window.removeEventListener(evt, unlock, true);
      });
    };

    ['pointerdown', 'keydown', 'click'].forEach(evt => {
      window.addEventListener(evt, unlock, { once: true, capture: true });
    });
  }

  /**
   * Synthesize a two-tone chime via Web Audio API
   * Used as a resilient fallback if HTML5 Audio fails or file is blocked
   */
  synthesizeChime() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;

      if (!this.audioContext) {
        this.audioContext = new AudioCtx();
      }

      if (this.audioContext.state === 'suspended') {
        this.audioContext.resume().catch(() => {});
      }

      const ctx = this.audioContext;
      const now = ctx.currentTime;

      // Tone 1: D5 (587.33 Hz)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(587.33, now);
      gain1.gain.setValueAtTime(0.001, now);
      gain1.gain.exponentialRampToValueAtTime(0.35, now + 0.02);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.36);

      // Tone 2: A5 (880.00 Hz) starting slightly later
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(880.00, now + 0.18);
      gain2.gain.setValueAtTime(0.001, now + 0.18);
      gain2.gain.exponentialRampToValueAtTime(0.40, now + 0.20);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.18);
      osc2.stop(now + 0.66);

    } catch (err) {
      console.warn('Web Audio synthesis fallback error:', err);
    }
  }

  /**
   * Play the ready-for-pickup sound notification
   * Safe, non-blocking, and gracefully handles autoplay restrictions
   */
  async playOrderReadySound() {
    if (!this.isSoundEnabled()) {
      return;
    }

    try {
      if (!this.audioElement) {
        this.audioElement = new Audio(AUDIO_ASSET_PATH);
        this.audioElement.volume = 0.6;
        this.audioElement.preload = 'auto';
      }

      // Rewind to beginning in case it was played before
      this.audioElement.currentTime = 0;
      const playPromise = this.audioElement.play();

      if (playPromise !== undefined) {
        await playPromise.catch((err) => {
          // If browser blocked HTML5 Audio (NotAllowedError), try Web Audio API fallback
          if (err && err.name === 'NotAllowedError') {
            this.synthesizeChime();
          } else {
            // File error or decoding issue: fallback to Web Audio synthesis
            this.synthesizeChime();
          }
        });
      }
    } catch {
      // Safe fallback if Audio element construction fails
      this.synthesizeChime();
    }
  }

  /**
   * Update all registered sound toggle buttons on the page
   */
  notifyToggleButtons() {
    if (typeof document === 'undefined') return;
    document.querySelectorAll('.sound-toggle-btn').forEach(btn => {
      this.updateButtonUI(btn);
    });
  }

  /**
   * Render SVG icons and accessible state for a sound toggle button
   * Strictly uses SVG icons (no emoji characters)
   * @param {HTMLElement} btn 
   */
  updateButtonUI(btn) {
    if (!btn) return;
    const enabled = this.isSoundEnabled();

    // Clean SVG icons (Sound On vs Sound Off)
    const iconSvg = enabled
      ? `<svg class="sound-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
           <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
           <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
           <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
         </svg>`
      : `<svg class="sound-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
           <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
           <line x1="23" y1="9" x2="17" y2="15"></line>
           <line x1="17" y1="9" x2="23" y2="15"></line>
         </svg>`;

    btn.innerHTML = `${iconSvg} <span>${enabled ? 'Sound On' : 'Sound Off'}</span>`;
    btn.setAttribute('aria-label', enabled ? 'Mute order ready sound notifications' : 'Enable order ready sound notifications');
    btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    btn.classList.toggle('sound-muted', !enabled);
  }
}

export const audioManager = new AudioManager();

export function playOrderReadySound() {
  return audioManager.playOrderReadySound();
}

export function isSoundEnabled() {
  return audioManager.isSoundEnabled();
}

export function toggleSound() {
  return audioManager.toggleSound();
}

export function updateSoundToggleUI(btn) {
  return audioManager.updateButtonUI(btn);
}

export default audioManager;
