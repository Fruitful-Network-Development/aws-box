// data_injection.js
// Loads JSON data and injects it into components using data-slot attributes

async function loadUserData() {
  const USER_DATA_FILENAME = 'msn_32357767435.json';

  // Check for ?external=client-slug in the URL
  const params = new URLSearchParams(window.location.search);
  let dataUrl = `/${USER_DATA_FILENAME}`;  // default local path

  const externalSlug = params.get('external');
  if (externalSlug) {
    // If present, point to our proxy route; the slug may include dots
    dataUrl = `/proxy/${externalSlug}/${USER_DATA_FILENAME}`;
  }

  // Fetch the chosen JSON URL
  const response = await fetch(dataUrl);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

function setText(selector, value) {
  const el = document.querySelector(selector);
  if (el && value != null) {
    el.textContent = value;
  }
}

function setImgSrc(selector, value) {
  const el = document.querySelector(selector);
  if (el && value) {
    el.src = value;
  }
}

async function injectData() {
  try {
    const data = await loadUserData();
    // Support both legacy `mycite` root and canonical `MSS` root structures.
    const mss = data.MSS || data.mycite || {};

    const compendium = mss.compendium || {};
    const profile = compendium.profile || {};

    const dossier = mss.dossier || {};
    const oeuvre = dossier.oeuvre || {};
    const anthology = dossier.anthology || {};

    /* ---------------- PROFILE / COMPENDIUM ---------------- */

    // name in meta-bar and profile card
    setText("[data-slot='compendium.profile.name']", profile.name);

    // avatar + micro icon
    setImgSrc("[data-slot='compendium.profile.avatar']", profile.avatar);
    setImgSrc("[data-slot='compendium.profile.micro_icon']", profile.micro_icon);

    // handle line (e.g. "dylcmonty • he/him")
    setText("[data-slot='compendium.profile.handleLine']", profile.handleLine);

    // handle @link, location, linkedin
    setText("[data-slot='compendium.profile.displayHandle']", profile.displayHandle);
    setText("[data-slot='compendium.profile.location']", profile.location);
    setText("[data-slot='compendium.profile.linkedin']", profile.linkedin);

    // compendium title (top of box)
    setText("[data-slot='compendium.title']", compendium.title);

    // organizations list
    const orgList = document.querySelector("[data-slot='compendium.organizations']");
    if (orgList && Array.isArray(compendium.organizations)) {
      orgList.innerHTML = "";
      compendium.organizations.forEach(org => {
        const li = document.createElement('li');
        li.textContent = org;
        orgList.appendChild(li);
      });
    }

    /* ---------------- DOSSIER / OEUVRE ---------------- */

    setText("[data-slot='dossier.oeuvre.title']", oeuvre.title);

    const oeuvreBody = document.querySelector("[data-slot='dossier.oeuvre.paragraphs']");
    if (oeuvreBody && Array.isArray(oeuvre.paragraphs)) {
      oeuvreBody.innerHTML = "";
      oeuvre.paragraphs.forEach(p => {
        const para = document.createElement('p');
        para.textContent = p;
        para.style.marginBottom = '1rem';
        oeuvreBody.appendChild(para);
      });
    }

    /* ---------------- DOSSIER / ANTHOLOGY ---------------- */

    setText("[data-slot='dossier.anthology.title']", anthology.title);

    const anthGrid = document.querySelector("[data-slot='dossier.anthology.blocks']");
    if (anthGrid && Array.isArray(anthology.blocks)) {
      anthGrid.innerHTML = "";
      
      // Store blocks for overlay functionality
      const blocks = [];
      
      anthology.blocks.forEach((block) => {
        if (typeof block !== 'object' || block === null) {
          return; // skip any non-object placeholders
        }

        const index = blocks.length;
        blocks.push(block);

        const box = document.createElement('div');
        box.className = 'anthology-box';
        box.style.cssText = 'background-color: #ffffff; width: 90.9%; padding-top: 90.9%; border-radius: 2px; position: relative; overflow: hidden; cursor: pointer;';

        // default clickable element is the box itself
        let clickableEl = box;

        // if there is a target, keep href semantics but intercept to open overlay
        if (block.target) {
          const link = document.createElement('a');
          link.href = block.target;
          link.className = 'anthology-link';

          link.addEventListener('click', (evt) => {
            evt.preventDefault(); // do not navigate away
            if (window.anthologyOverlay && window.anthologyOverlay.open) {
              window.anthologyOverlay.open(index);
            }
          });

          box.appendChild(link);
          clickableEl = link;
        } else {
          // no target: click on box itself opens overlay
          box.addEventListener('click', () => {
            if (window.anthologyOverlay && window.anthologyOverlay.open) {
              window.anthologyOverlay.open(index);
            }
          });
        }

        // Thumbnail (if exists) or text placeholder
        if (block.thumbnail) {
          const img = document.createElement('img');
          img.src = block.thumbnail;
          img.alt = block.title || block.id || '';
          img.style.cssText = 'position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;';
          clickableEl.appendChild(img);
        } else {
          const label = document.createElement('div');
          label.className = 'anthology-placeholder';
          label.style.cssText = 'position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 0.5rem; text-align: center; font-size: 0.8rem; color: #202122;';
          label.textContent = block.title || block.id || '';
          clickableEl.appendChild(label);
        }

        anthGrid.appendChild(box);
      });
      
      // Set blocks in overlay module
      if (window.anthologyOverlay && window.anthologyOverlay.setBlocks) {
        window.anthologyOverlay.setBlocks(blocks);
      }
    }

  } catch (err) {
    console.error('Error loading user data:', err);
  }
}

// Wait for components to be loaded before injecting data
document.addEventListener('componentsLoaded', async () => {
  // Small delay to ensure DOM is fully ready
  setTimeout(() => {
    injectData();
  }, 100);
});
