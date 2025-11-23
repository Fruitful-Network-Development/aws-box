// root/app.js

const IMG_BASE = "assets/imgs/";
const DOC_BASE = "assets/docs/";

// Bootstraps the Mycite view into #mysite-root
async function bootstrapMycite() {
  const root = document.getElementById("mysite-root");
  if (!root) return;

  try {
    const data = await loadUserData();
    buildMyciteView(root, data);
  } catch (err) {
    console.error(err);
    root.textContent = "Error loading profile data.";
  }
}

async function loadUserData() {
  const res = await fetch("user_data.json");
  if (!res.ok) throw new Error("Could not load user_data.json");
  return res.json();
}

/* ---------- DOM builders ---------- */

function buildMyciteView(container, data) {
  const { Compendium, Oeuvre, Anthology } = data;

  container.innerHTML = "";

  const shell = el("div", "page-shell");
  container.appendChild(shell);

  /* Static chrome header (red in overlay) */
  shell.appendChild(buildGlobalHeader());

  /* Body grid: timeline rail + main + sidebar */
  const body = el("div", "page-body");
  shell.appendChild(body);

  // Left rail (static)
  body.appendChild(buildTimelineRail());

  // Main column (mixed: static frame + JSON-filled content)
  const mainColumn = el("div", "main-column");
  body.appendChild(mainColumn);

  // Sidebar (JSON compendium + static series box)
  const sidebar = el("aside", "sidebar");
  body.appendChild(sidebar);

  /* Main header: name (JSON), tabs (static) */
  if (Compendium) {
    mainColumn.appendChild(buildPageHeader(Compendium));
  }

  /* Oeuvre text (JSON) */
  if (Oeuvre) {
    mainColumn.appendChild(buildOeuvreSection(Oeuvre));
  }

  /* Anthology grid (JSON) */
  if (Array.isArray(Anthology) && Anthology.length) {
    mainColumn.appendChild(buildAnthologySection(Anthology));
  }

  /* Compendium (JSON) */
  if (Compendium) {
    sidebar.appendChild(buildCompendium(Compendium));
  }

  /* Series box (static chrome) */
  sidebar.appendChild(buildSeriesBox());
}

/* --- Static header chrome --- */
function buildGlobalHeader() {
  const header = el("header", "global-header");

  // row 1
  const top = el("div", "header-top");

  const brand = el("div", "brand-block");
  const logo = el("div", "brand-logo");
  const textWrap = el("div");
  const title = el("div", "brand-title");
  title.textContent = "Mycite Network";
  const sub = el("div", "brand-sub");
  sub.textContent = "Fruit Network Development";
  textWrap.appendChild(title);
  textWrap.appendChild(sub);
  brand.appendChild(logo);
  brand.appendChild(textWrap);

  const searchWrap = el("div", "header-search");
  const searchInput = document.createElement("input");
  searchInput.type = "search";
  searchInput.placeholder = "Search";
  searchWrap.appendChild(searchInput);

  const actions = el("div", "header-actions");
  ["Donate", "Create account", "Log in"].forEach(label => {
    const a = document.createElement("a");
    a.href = "javascript:void(0)";
    a.textContent = label;
    actions.appendChild(a);
  });

  top.appendChild(brand);
  top.appendChild(searchWrap);
  top.appendChild(actions);
  header.appendChild(top);

  // row 2
  const bottom = el("div", "header-bottom");

  const nav = el("nav", "section-nav");
  ["Read", "Library", "Bloom", "News"].forEach(label => {
    const a = document.createElement("a");
    a.href = "javascript:void(0)";
    a.textContent = label;
    nav.appendChild(a);
  });

  const lang = el("div", "header-lang");
  lang.textContent = "102 languages";

  bottom.appendChild(nav);
  bottom.appendChild(lang);
  header.appendChild(bottom);

  return header;
}

/* --- Static timeline rail --- */
function buildTimelineRail() {
  const rail = el("aside", "timeline-rail");

  const month = el("div", "timeline-month");
  const span1 = document.createElement("span");
  span1.textContent = "November";
  const span2 = document.createElement("span");
  span2.textContent = "2025";
  month.appendChild(span1);
  month.appendChild(span2);

  const line = el("div", "timeline-line");
  const dot = el("div", "timeline-dot");
  line.appendChild(dot);

  rail.appendChild(month);
  rail.appendChild(line);
  return rail;
}

/* --- Header in main column (name/title JSON, tabs static) --- */
function buildPageHeader(compendium) {
  const section = el("section", "page-header");

  const topRow = el("div", "page-header-top");

  const title = el("h1", "page-title");
  title.textContent = compendium.name || "";

  topRow.appendChild(title);
  section.appendChild(topRow);

  const tabs = el("div", "page-tabs");
  const tabOeuvre = el("button", "page-tab active");
  tabOeuvre.textContent = "Oeuvre";
  const tabContact = el("button", "page-tab");
  tabContact.textContent = "Contact";
  tabs.appendChild(tabOeuvre);
  tabs.appendChild(tabContact);

  section.appendChild(tabs);
  return section;
}

/* --- Oeuvre (JSON-driven) --- */
function buildOeuvreSection(oeuvre) {
  const section = el("section", "oeuvre");

  const body = el("div", "oeuvre-body");
  let paragraphs = [];

  if (Array.isArray(oeuvre.paragraphs)) {
    paragraphs = oeuvre.paragraphs;
  } else if (typeof oeuvre.text === "string") {
    paragraphs = oeuvre.text.split(/\n\s*\n/);
  }

  paragraphs.forEach(text => {
    const p = document.createElement("p");
    p.textContent = text;
    body.appendChild(p);
  });

  section.appendChild(body);
  return section;
}

/* --- Anthology (JSON-driven) --- */
function buildAnthologySection(entries) {
  const wrapper = document.createElement("div");

  const title = el("h2", "anthology-section-title");
  title.textContent = "Anthology";
  wrapper.appendChild(title);

  const grid = el("div", "anthology-grid");

  entries.forEach(entry => {
    const card = buildAnthologyCard(entry);
    grid.appendChild(card);
  });

  wrapper.appendChild(grid);
  return wrapper;
}

function buildAnthologyCard(entry) {
  const card = el("article", "anthology-card");

  const link = el("a", "anthology-link");
  const href = resolveAnthologyHref(entry);
  link.href = href || "javascript:void(0)";

  const thumbWrap = el("div", "anthology-thumb-wrapper");
  const img = el("img", "anthology-thumb");
  if (entry.image) {
    img.src = IMG_BASE + entry.image;
  }
  img.alt = entry.title || "";
  thumbWrap.appendChild(img);

  const body = el("div", "anthology-card-body");
  const title = el("h3", "anthology-title");
  title.textContent = entry.title || "Untitled entry";
  const summary = el("p", "anthology-summary");
  summary.textContent = entry.summary || "";

  body.appendChild(title);
  body.appendChild(summary);

  link.appendChild(thumbWrap);
  link.appendChild(body);
  card.appendChild(link);

  return card;
}

/* Where an anthology card should link;
   still neutral enough that webpage/ can choose differently later. */
function resolveAnthologyHref(entry) {
  if (entry.link) return entry.link;
  if (entry.target) return entry.target;
  if (Array.isArray(entry.docs) && entry.docs.length > 0) {
    const first = entry.docs[0];
    if (first.file) return `${DOC_BASE}${first.file}`;
  }
  return "";
}

/* --- Compendium (JSON-driven) --- */

function buildCompendium(compendium) {
  const section = el("section", "compendium");

  const title = el("h2", "compendium-title");
  title.textContent = "Compendium";
  section.appendChild(title);

  // maps
  if (Array.isArray(compendium.maps) && compendium.maps.length) {
    const mapsWrap = el("div", "compendium-maps");
    compendium.maps.forEach(m => {
      const img = el("img", "compendium-map-img");
      if (m.image) img.src = IMG_BASE + m.image;
      img.alt = m.label || "";
      mapsWrap.appendChild(img);
    });
    section.appendChild(mapsWrap);
  }

  // profile
  const profile = el("div", "compendium-profile");
  const pic = el("img", "profile-pic");
  if (compendium.profileImage) {
    pic.src = IMG_BASE + compendium.profileImage;
  }
  pic.alt = compendium.name || "Profile picture";

  const meta = el("div", "profile-meta");
  const name = el("div", "profile-meta-name");
  name.textContent = compendium.name || "";
  const role = el("div", "profile-meta-title");
  role.textContent = compendium.title || "";
  const loc = el("div", "profile-meta-location");
  loc.textContent = compendium.location || "";

  meta.appendChild(name);
  if (role.textContent) meta.appendChild(role);
  if (loc.textContent) meta.appendChild(loc);
  profile.appendChild(pic);
  profile.appendChild(meta);
  section.appendChild(profile);

  // meta dl
  if (Array.isArray(compendium.meta) && compendium.meta.length) {
    const dl = el("dl", "compendium-meta");
    compendium.meta.forEach(item => {
      const dt = document.createElement("dt");
      dt.textContent = item.label;

      const dd = document.createElement("dd");
      if (item.url) {
        const a = document.createElement("a");
        a.href = item.url;
        a.target = "_blank";
        a.rel = "noreferrer";
        a.textContent = item.value;
        dd.appendChild(a);
      } else {
        dd.textContent = item.value;
      }

      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    section.appendChild(dl);
  }

  return section;
}

/* --- Series box (static chrome) --- */

function buildSeriesBox() {
  const box = el("section", "series-box");
  const title = el("div", "series-box-title");
  title.textContent = "Part of a series on";
  const pills = el("div", "series-pill-row");

  ["Aspects", "Groups"].forEach(label => {
    const pill = el("div", "series-pill");
    pill.textContent = label;
    pills.appendChild(pill);
  });

  box.appendChild(title);
  box.appendChild(pills);
  return box;
}

/* Utility */

function el(tag, className) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  return node;
}

bootstrapMycite();

