/**
 * Audio Notification Manager for Smart Canteen Booking System
 * Handles order ready chime playback, browser autoplay policies,
 * Web Audio API fallback synthesis, and user sound preferences.
 */

const STORAGE_KEY = 'canteen_sound_notifications';
const AUDIO_ASSET_PATH = 'assets/sounds/order-ready.wav';
const ORDER_CONFIRMED_ASSET_PATH = 'assets/sounds/order-confirmed.wav';
const NEW_ORDER_ASSET_PATH = 'assets/sounds/new-order.wav';

export class AudioManager {
  constructor() {
    this.audioContext = null;
    this.isUnlocked = false;
    this.audioElement = null;
    this.orderConfirmedAudioElement = null;
    this.newOrderAudioElement = null;
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
   * Synthesize a pleasant 3-tone confirmation chime via Web Audio API
   * Used as a resilient fallback if HTML5 Audio fails or file is blocked
   */
  synthesizeOrderConfirmedChime() {
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

      // Tone 1: E5 (659.25 Hz)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(659.25, now);
      gain1.gain.setValueAtTime(0.001, now);
      gain1.gain.exponentialRampToValueAtTime(0.30, now + 0.015);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.36);

      // Tone 2: G5 (783.99 Hz) starting at +0.12s
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(783.99, now + 0.12);
      gain2.gain.setValueAtTime(0.001, now + 0.12);
      gain2.gain.exponentialRampToValueAtTime(0.35, now + 0.135);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.12);
      osc2.stop(now + 0.46);

      // Tone 3: C6 (1046.50 Hz) starting at +0.24s with warm decay
      const osc3 = ctx.createOscillator();
      const gain3 = ctx.createGain();
      osc3.type = 'sine';
      osc3.frequency.setValueAtTime(1046.50, now + 0.24);
      gain3.gain.setValueAtTime(0.001, now + 0.24);
      gain3.gain.exponentialRampToValueAtTime(0.40, now + 0.255);
      gain3.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
      osc3.connect(gain3);
      gain3.connect(ctx.destination);
      osc3.start(now + 0.24);
      osc3.stop(now + 0.66);

    } catch (err) {
      console.warn('Web Audio synthesis fallback error for order confirmation:', err);
    }
  }

  /**
   * Play the order-confirmed sound notification
   * Safe, non-blocking, and gracefully handles autoplay restrictions
   */
  async playOrderConfirmedSound() {
    if (!this.isSoundEnabled()) {
      return;
    }

    try {
      if (!this.orderConfirmedAudioElement) {
        this.orderConfirmedAudioElement = new Audio(ORDER_CONFIRMED_ASSET_PATH);
        this.orderConfirmedAudioElement.volume = 0.6;
        this.orderConfirmedAudioElement.preload = 'auto';
      }

      this.orderConfirmedAudioElement.currentTime = 0;
      const playPromise = this.orderConfirmedAudioElement.play();

      if (playPromise !== undefined) {
        await playPromise.catch((err) => {
          // If browser blocked HTML5 Audio (NotAllowedError), try Web Audio API fallback
          if (err && err.name === 'NotAllowedError') {
            this.synthesizeOrderConfirmedChime();
          } else {
            this.synthesizeOrderConfirmedChime();
          }
        });
      }
    } catch {
      this.synthesizeOrderConfirmedChime();
    }
  }

  /**
   * Synthesize an alert chime via Web Audio API for incoming admin orders
   * Used as a resilient fallback if HTML5 Audio fails or file is blocked
   */
  synthesizeNewOrderChime() {
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

      // Strike 1: F5 (698.46 Hz) + C6 (1046.50 Hz)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'triangle';
      osc1.frequency.setValueAtTime(698.46, now);
      gain1.gain.setValueAtTime(0.001, now);
      gain1.gain.exponentialRampToValueAtTime(0.35, now + 0.01);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.23);

      // Strike 2: A5 (880.00 Hz) + E6 (1318.51 Hz) at +0.16s with longer ring
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(880.00, now + 0.16);
      gain2.gain.setValueAtTime(0.001, now + 0.16);
      gain2.gain.exponentialRampToValueAtTime(0.40, now + 0.17);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.start(now + 0.16);
      osc2.stop(now + 0.66);

    } catch (err) {
      console.warn('Web Audio synthesis fallback error for new order alert:', err);
    }
  }

  /**
   * Play the admin new-order sound notification
   * Safe, non-blocking, and gracefully handles autoplay restrictions
   */
  async playNewOrderSound() {
    if (!this.isSoundEnabled()) {
      return;
    }

    try {
      if (!this.newOrderAudioElement) {
        this.newOrderAudioElement = new Audio(NEW_ORDER_ASSET_PATH);
        this.newOrderAudioElement.volume = 0.6;
        this.newOrderAudioElement.preload = 'auto';
      }

      this.newOrderAudioElement.currentTime = 0;
      const playPromise = this.newOrderAudioElement.play();

      if (playPromise !== undefined) {
        await playPromise.catch((err) => {
          if (err && err.name === 'NotAllowedError') {
            this.synthesizeNewOrderChime();
          } else {
            this.synthesizeNewOrderChime();
          }
        });
      }
    } catch {
      this.synthesizeNewOrderChime();
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
    btn.setAttribute('aria-label', enabled ? 'Mute sound notifications' : 'Enable sound notifications');
    btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    btn.classList.toggle('sound-muted', !enabled);
  }
}

export const audioManager = new AudioManager();

export function playOrderReadySound() {
  return audioManager.playOrderReadySound();
}

export function playOrderConfirmedSound() {
  return audioManager.playOrderConfirmedSound();
}

export function playNewOrderSound() {
  return audioManager.playNewOrderSound();
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
