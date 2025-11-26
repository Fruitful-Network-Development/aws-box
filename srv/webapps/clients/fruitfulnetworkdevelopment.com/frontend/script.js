async function loadUserData() {
  const response = await fetch('user_data.json');
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

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const data = await loadUserData();
    const mss = data.MSS;
    const compendium = mss.compendium;
    const dossier = mss.dossier;

    const profile = compendium.profile;
    const oeuvre = dossier.oeuvre;
    const anthology = dossier.anthology;

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

    /* ---------------- OEUVRE ---------------- */

    // title
    setText("[data-slot='dossier.oeuvre.title']", oeuvre.title);

    // paragraphs
    const oeuvreBox = document.querySelector("[data-slot='dossier.oeuvre.paragraphs']");
    if (oeuvreBox && Array.isArray(oeuvre.paragraphs)) {
      oeuvreBox.innerHTML = "";
      oeuvre.paragraphs.forEach(pText => {
        const p = document.createElement('p');
        p.textContent = pText;
        oeuvreBox.appendChild(p);
      });
    }

    /* ---------------- ANTHOLOGY ---------------- */

    // title
    setText("[data-slot='dossier.anthology.title']", anthology.title);

    // blocks -> boxes in grid
    const anthGrid = document.querySelector("[data-slot='dossier.anthology.blocks']");
    if (anthGrid && Array.isArray(anthology.blocks)) {
      anthGrid.innerHTML = "";
      anthology.blocks.forEach(block => {
        const box = document.createElement('div');
        box.className = 'anthology-box';
        // For now, just put the block text inside; later this could be an image or icon.
        box.textContent = block;
        anthGrid.appendChild(box);
      });
    }

  } catch (err) {
    console.error('Error loading user data:', err);
  }
});
