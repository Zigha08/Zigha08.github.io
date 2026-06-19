# portfolio-source (private)

Source code untuk personal portfolio site di [zigha08.github.io](https://zigha08.github.io/).

**Repo ini private by design.** Code yang sedang dalam pengerjaan (security tools, writeup drafts, eksperimen) tidak di-expose ke publik. Site yang di-serve dari sini tetap publik — visitor tidak melihat source code, hanya output HTML/CSS/JS yang sudah di-build.

---

## Arsitektur

```
┌─────────────────────────────────────────┐
│ Zigha08/portfolio-source  (PRIVATE)     │
│   - Source code (HTML/CSS/JS/Python)    │
│   - .github/workflows/deploy.yml        │
└──────────────────┬──────────────────────┘
                   │ push to main → Action
                   ▼
┌─────────────────────────────────────────┐
│ Zigha08/Zigha08.github.io (PUBLIC)      │
│   - main branch: metadata only          │
│   - gh-pages branch: deployed site      │
└──────────────────┬──────────────────────┘
                   │ GitHub Pages
                   ▼
        https://zigha08.github.io/
```

**Kenapa split?** Repo `Zigha08.github.io` secara historis berisi source code site. Karena GitHub Pages (free plan) **mewajibkan repo source publik**, semua source code harus visible. Solusi: pindahkan source ke repo private ini, deploy output ke repo Pages yang publik.

---

## One-time setup

Repo ini punya GitHub Action (`.github/workflows/deploy.yml`) yang auto-deploy ke `Zigha08/Zigha08.github.io` `gh-pages` branch setiap push ke `main`. Action butuh Personal Access Token (PAT) untuk push ke repo lain.

### Bikin PAT (Personal Access Token)

1. Buka https://github.com/settings/tokens
2. Klik **"Generate new token"** → **"Generate new token (classic)"**
3. Isi:
   - **Note:** `portfolio-source deploy`
   - **Expiration:** `No expiration` (atau 1 tahun, sesuaikan security policy Anda)
   - **Scopes:** centang hanya **`repo`** (Full control of private repositories)
4. Klik **"Generate token"**
5. **Copy token value** — hanya ditampilkan SEKALI. Simpan di password manager.

### Tambah PAT sebagai secret

1. Buka https://github.com/Zigha08/portfolio-source/settings/secrets/actions
2. Klik **"New repository secret"**
3. Isi:
   - **Name:** `GH_DEPLOY_TOKEN`
   - **Secret:** paste token value dari step sebelumnya
4. Klik **"Add secret"**

Setelah ini, setiap push ke `main` di repo ini otomatis deploy ke `https://zigha08.github.io/`.

---

## Local development

### Prerequisites

- Python 3.x (untuk HTML validator + http server)
- Node.js (untuk `node -c` syntax check JS)
- Git

### Setup

```bash
git clone https://github.com/Zigha08/portfolio-source.git
cd portfolio-source
```

### Edit + preview locally

```bash
# Start dev server di port 9200 (aman, di luar range Sentinel)
python -m http.server 9200 --bind 127.0.0.1

# Browser: http://127.0.0.1:9200/
```

### Verify sebelum commit

```bash
# JS syntax check
node -c assets/app.js && echo JS_OK

# Python syntax check (build scripts)
python -m py_compile scripts/render_projects.py && echo PY_OK

# HTML validator
python tests/audit_html.py index.html 404.html writing/*.html

# Typo scan (English)
grep -rn -E 'Portofolio|teh |recieve|seperate|definately|occured' \
  --include='*.html' --include='*.js' --include='*.md' .

# Final: visit semua page lokal, click setiap link
```

### Deploy

```bash
git add .
git commit -m "Your descriptive message"
git push origin main
# → GitHub Action auto-deploy ke zigha08.github.io dalam ~30 detik
```

---

## File structure

```
portfolio-source/
├── index.html                    # Main portfolio page
├── 404.html                      # Custom 404 page
├── writing/                      # Articles + writeups
│   └── sqli-union-login.html
├── assets/
│   ├── style.css                 # All styles
│   ├── app.js                    # All interactive JS (no deps)
│   ├── ghazi-abid-al-azzam-cv.pdf  # Downloadable CV
│   └── og-image.svg              # Open Graph preview image
├── scripts/
│   └── render_projects.py        # Optional: dynamic project card renderer
│                                # (currently unused, kept for future re-use)
├── tests/
│   ├── audit_html.py             # HTML structure validator (stdlib)
│   ├── convert-to-pdf.js         # Utility: HTML → PDF via puppeteer
│   ├── lab_server.py             # Local vulnerable Flask lab (intentionally)
│   └── run_pipeline.py           # Historical build pipeline (snapshot)
├── reports/                      # Audit reports, screenshots
├── .github/workflows/
│   └── deploy.yml                # Auto-deploy to gh-pages
├── manifest.json                 # PWA manifest
├── robots.txt
├── sitemap.xml
├── LICENSE                       # MIT
└── README.md                     # This file
```

---

## Design principles

- **No frameworks, no build step** — vanilla HTML/CSS/JS, browser-native features only
- **No SaaS, no tracking** — no Google Analytics, no fonts CDN, no third-party scripts
- **Static-first** — every page renders without JS (JS adds progressive enhancement only)
- **Accessibility** — semantic HTML, ARIA labels, `prefers-reduced-motion` respected
- **SEO** — Open Graph, Twitter Card, JSON-LD Person schema, sitemap.xml
- **Performance** — small payload (~20KB HTML), inline critical assets, lazy where possible

---

## License

MIT — see [LICENSE](LICENSE).

Visitor-facing site content © Ghazi Abid Al Azzam.
