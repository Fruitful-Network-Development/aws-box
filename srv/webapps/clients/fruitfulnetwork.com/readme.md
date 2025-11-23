# Mycite Profile Framework

## Overview

The Mycite Profile Framework provides a unified data schema (user_data.json) and a standardized rendering layer defined at the repository root (index.html, style.css, app.js), which together establish a neutral, interoperable profile format.

This format is deliberately designed so that:
1. Any website can embed or access a standardized version of a user’s profile.
2. Creative, free-form websites (stored in /webpage/) can reinterpret the same data without layout constraints.
3. The root-level index.html acts as the default profile view and canonical structural definition, but not the definitive layout for alternative pages.
4. Third-party aggregators (markets, co-ops, directories, etc.) can load the same JSON file and render a consistent view.
This project provides both:
- A standardized profile interface (Mycite View)
- A free-form creative layer that consumes the same schema
The result is an extensible personal or organizational site with built-in interoperability and layout independence.

---

## Conceptual Purpose

The Mycite framework addresses a common problem:
    Websites often contain rich personal or organizational content, but there is no universal, neutral way to exchange or display profiles across platforms.
The Mycite approach solves this by:
- Defining a data-first profile schema (Compendium, Oeuvre, Anthology)
- Building a standardized UI that can be used anywhere
- Allowing creative reinterpretation through a separate free-form site

This allows:
1. A single canonical profile source
    - All information is stored structurally in user_data.json, independent of HTML layout.
2. Multiple render layers
    - Mycite Standard View → neutral, predictable, portable
    - Free-form Webpage View → expressive, themeable, personal
3. Interoperability
    - Any third-party environment can pull the JSON and display a stable profile.
4. Future-proof extension
    - New sections (videos, certifications, links, project groups) can be added to the JSON without breaking existing pages.
This achieves a philosophical and technical goal:
separation of content and representation, enabling multi-context identity display.

---

## Technical Architecture
/root
  ├── index.html
  ├── style.css
  ├── app.js
  ├── user_data.json
  ├── /assets
  │  ├── imgs/
  │  │   ├── profile.png
  │  │   ├── map_1.png
  │  │   ├── map_2.png
  │  │   ├── map_3.png
  │  │   ├── mycite_logo.png
  │  │   └── gallery_img-1.jpeg
  │  └── docs/
  │      ├── essay-1.pdf
  │      ├── essay-2.pdf
  │      └── essay-3.pdf
  └── /webpage
     ├── style.css
     ├── app.js
     └── pages/
         ├── home-splash.html
         ├── about.html
         └── project.html

---

## Schema Overview (user_data.json)

The JSON file defines the entire content model.
Its structure determines what both Mycite and free-form views can display.

### Compendium
Metadata and visual identifiers.
        {
          "name": "",
          "title": "",
          "location": "",
          "profileImage": "",
          "maps": [...],
          "meta": [...]
        }

### Oeuvre
Long-form, narrative text.
        {
          "headline": "",
          "paragraphs": [...]
        }

### Anthology
Neutral list of items representing:
    - pages
    - collections
    - external links
    - projects
    - documents
    - media
Each entry contains no layout semantics, only meaning.
        [
          {
            "id": "",
            "title": "",
            "summary": "",
            "kind": "page | collection | external | ...",
            "target": "webpage/pages/home-splash.html",
            "image": "",
            "docs": [...]
          }
        ]

---

## Rendering Model

### Standardized View (root/index.html)
The root index.html contains:
        <div id="mysite-root"></div>
All Mycite UI is constructed inside this container.

This ensures:
- The standard view is clean, isolated, and portable
- No UI assumptions bleed into the schema
- Other renderers (such as /webpage/) can remain independent
The root-level app.js:
- Fetches user_data.json
- Builds the Mycite-standard UI dynamically
- Never embeds fixed layout structure in HTML
This is Option B, the containerized rendering model.

### Free-form Webpage View (/webpage/)

The free-form site contains:
- Its own style.css
- Its own app.js
- Arbitrary HTML pages in /pages/
But it still uses the same user_data.json.

This allows:
- Personal homepage designs
- Rich navigation flows
- Arbitrary layouts for Anthology items
- Media carousels, galleries, mosaics, etc.
Nothing forces /webpage/ to resemble the standardized Mycite layout.

The schema is a shared foundation, not a constraint.

---

## Objectives and Design Principles

- Separation of Content and Layout
    - All content is stored structurally in JSON.
    - The Mycite view and free-form site are merely renderers.
- Interoperability and Portability
    - Any host that understands the schema can generate a valid profile.
    - This creates a “portable identity page” across contexts.
- Extendability
    - Add new sections to the JSON without breaking the Mycite viewer.
- Neutral Standardization
    The Mycite layout is intentionally simple and standardized:
    - predictable typography
    - consistent left/right column structure
    - accessible and portable design
- Creative Freedom
    - The free-form website allows unrestricted design while still pulling accurate profile information.

---

## Execution Summary

Author your profile data in user_data.json.
1. Root renderer loads and builds the Mycite-standard profile at index.html.
2. Free-form renderer (webpage/app.js) can interpret the same data for custom layouts.
3. Third-party systems may also fetch the JSON to construct curated profiles.
4. Add/remove Anthology objects to define navigation structures for alternate UIs.
This dual-layer architecture allows:
- A consistent canonical identity
- A creative personalized site
- Reusable identity pages for co-ops, markets, vendors, etc.
- Multiple, context-adapted representations from one dataset

---

## Future Extensions

Potential next steps include:
- Shared JS module (schema.js) to define interfaces for both views
- i18n layer (support for multiple languages)
- A “profile card” embed mode generator for external sites
- Programmatic loading of remote user_data.json URLs (federated identity)
- Server-side versioning system for multiple profiles

---

## License

---

## Acknowledgments

Built and authored by Dylan Montgomery

MODIFIED:	####-##-##
VERSION:	##.##.##
STATUS:     Active prototyping and architectural refinement

