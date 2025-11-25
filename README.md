# infra-aws-linux

## Overview

---

## Project Layout

- /infra-aws-linux
- ├── /ect 
  - └── nginx/
    - ├── nginx.conf
    - ├── sites-available/
      - └── fruitfulnetwork.com.conf
    - └── sites-enabled/
      - └── fruitfulnetwork.com.conf
- ├── /srv
  - └── webapps/
    - ├── platform/                         # shared Flask backend
      - ├── app.py                          # main Flask app
      - ├── client_context.py               # figure out which client from Host etc.
      - ├── data_access.py                  # read/write JSON for backend_data.json
      - ├── modules/                        # reusable backend "tools"
        - ├── __init__.py
        - ├── donations.py                  # shared donation logic
        - ├── payments.py                   # shared PayPal logic
        - └── pos_integration.py            # shared POS logic
      - └── requirements.txt
    - └── clients/
          └── fruitfulnetwork.com/
              ├── frontend/
              │   ├── index.html
              │   ├── mycite.html
              │   ├── webpage.html
              │   ├── style.css
              │   ├── app.js
              │   ├── script.js
              │   ├── user_data.js
              │   ├── webpage/
              │   │   ├── home.html
              │   │   ├── csa_browser.html
              │   │   ├── happenings.html
              │   │   ├── about_us.html
              │   │   └── about_csa_program.html
              │   └── assets/
              │       └── imgs/
              │           ├── profile.png
              │           └── logo.jpeg
              ├── backend_data.json
              └── config/
                  └── settings.json
          - ├── cuyahogavalleycountryside.com/
          - ├── front9farm.com/
          - └── trappfamilyfarm.com/
- └── [README](README.md)                   # <-- this file

---

## How It Works

The lego-style, modular, snap-in component, website system has three major layers:
- PRESENTATION LAYER (Client Frontend)
- CONTENT LAYER (Client Data)
- CONFIG LAYER (Client Feature Definitions)

### How Pages Load Components
index.html chooses:
  - which header
  - which footer
  - which pages (links/navigation)
And each page HTML loads component-loader.js:
        <div data-component="header"></div>
        <div data-page></div>
        <div data-component="footer"></div>

        <script src="../components/component-loader.js"></script>

### Pages
Each HTML page uses:
1. Load config/settings.json
2. For each component placeholder:
   - fetch component HTML (e.g., 'components/header/header-001.html')
   - insert into DOM
   - find all data-text/data-img/data-button attributes
   - replace with mapped content defined in 'bindings'
3. If component is actually a widget, load widget-loader.js

### Widgets
product browser, CSA, donation box, etc. live in:
        components/widgets/
And:
  - Their HTML is imported like any other component
  - Their JS connects to backend APIs
  - They pull data dynamically from /api/products, /api/csa, /api/inventory, etc.

### Relationship Between Frontend + Backend
Your frontend consumes backend APIs like:
        /api/inventory
        /api/products
        /api/csa
        /api/customers
        /api/donations
        /api/paypal/create-order
        /api/pos/sync
The backend:
  - uses client_context.py to know client from request
  - uses data_access.py to open correct JSON files
  - uses each module (donations, payments, pos_integration) to handle logic
This is clean, scalable, multi-tenant.

---

## Background Concepts (for reference)

---

## Development Roadmap

---

## License

---

## Acknowledgments

Built and authored by Dylan Montgomery

MODIFIED:	####-##-##
VERSION:	##.##.##
STATUS:     Active prototyping and architectural refinement
