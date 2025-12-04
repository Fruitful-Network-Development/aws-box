// overlay/overlay.js
// Overlay state management, navigation, keyboard controls

let anthologyBlocks = [];
let currentAnthologyIndex = -1;

let overlayEls = {
  overlay: null,
  title: null,
  description: null,
  urlText: null,
  kind: null,
  targetLabel: null,
  canvas: null,
  closeBtn: null,
  prevBtn: null,
  nextBtn: null
};

function initOverlayElements() {
  overlayEls.overlay = document.getElementById('anthology-overlay');
  if (!overlayEls.overlay) return;

  overlayEls.title = document.getElementById('anthology-overlay-title');
  overlayEls.description = document.getElementById('anthology-overlay-description');
  overlayEls.urlText = document.getElementById('anthology-overlay-url');
  overlayEls.kind = document.getElementById('anthology-overlay-kind');
  overlayEls.targetLabel = document.getElementById('anthology-overlay-target-label');
  overlayEls.canvas = document.getElementById('anthology-overlay-canvas');
  overlayEls.closeBtn = document.getElementById('anthology-overlay-close');
  overlayEls.prevBtn = document.getElementById('anthology-overlay-prev');
  overlayEls.nextBtn = document.getElementById('anthology-overlay-next');

  // Close button
  if (overlayEls.closeBtn) {
    overlayEls.closeBtn.addEventListener('click', closeAnthologyOverlay);
  }

  // Clicking the dark background closes overlay
  overlayEls.overlay.addEventListener('click', (evt) => {
    if (evt.target === overlayEls.overlay) {
      closeAnthologyOverlay();
    }
  });

  // Keyboard controls
  document.addEventListener('keydown', (evt) => {
    if (!overlayEls.overlay || overlayEls.overlay.classList.contains('is-hidden')) {
      return;
    }
    if (evt.key === 'Escape') {
      closeAnthologyOverlay();
    } else if (evt.key === 'ArrowRight') {
      changeAnthologyOverlay(1);
    } else if (evt.key === 'ArrowLeft') {
      changeAnthologyOverlay(-1);
    }
  });

  // Prev/next buttons
  if (overlayEls.prevBtn) {
    overlayEls.prevBtn.addEventListener('click', () => changeAnthologyOverlay(-1));
  }
  if (overlayEls.nextBtn) {
    overlayEls.nextBtn.addEventListener('click', () => changeAnthologyOverlay(1));
  }
}

function openAnthologyOverlay(index) {
  if (!overlayEls.overlay || !anthologyBlocks.length) return;

  currentAnthologyIndex = index;
  updateAnthologyOverlay();

  overlayEls.overlay.classList.remove('is-hidden');
  document.body.classList.add('overlay-open');
}

function closeAnthologyOverlay() {
  if (!overlayEls.overlay) return;
  overlayEls.overlay.classList.add('is-hidden');
  document.body.classList.remove('overlay-open');
}

function changeAnthologyOverlay(delta) {
  if (!anthologyBlocks.length) return;
  currentAnthologyIndex =
    (currentAnthologyIndex + delta + anthologyBlocks.length) % anthologyBlocks.length;
  updateAnthologyOverlay();
}

function updateAnthologyOverlay() {
  const block = anthologyBlocks[currentAnthologyIndex];
  if (!block || !overlayEls.overlay) return;

  if (overlayEls.title) {
    overlayEls.title.textContent = block.title || block.id || 'Anthology item';
  }

  if (overlayEls.description) {
    // placeholder for future "description" field in JSON
    if (block.description) {
      overlayEls.description.textContent = block.description;
    } else {
      overlayEls.description.textContent =
        'More information about this entry will go here as the data model evolves.';
    }
  }

  const targetText = block.target || 'No link configured yet';

  if (overlayEls.urlText) {
    overlayEls.urlText.textContent = targetText;
  }
  if (overlayEls.kind) {
    overlayEls.kind.textContent = block.kind || '—';
  }
  if (overlayEls.targetLabel) {
    overlayEls.targetLabel.textContent = targetText;
  }

  if (overlayEls.canvas) {
    if (block.thumbnail) {
      overlayEls.canvas.style.backgroundImage = `url(${block.thumbnail})`;
    } else {
      overlayEls.canvas.style.backgroundImage = 'none';
    }
  }
}

// Export functions for use by data_injection.js
window.anthologyOverlay = {
  init: initOverlayElements,
  open: openAnthologyOverlay,
  setBlocks: (blocks) => { anthologyBlocks = blocks; }
};

// Initialize when components are loaded
document.addEventListener('componentsLoaded', () => {
  initOverlayElements();
});
