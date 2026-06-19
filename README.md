# Portfolio — Ghazi Abid Al Azzam

Personal portfolio website. Static, framework-free, dark editorial aesthetic.

## Stack

- HTML5 (semantic, accessible)
- CSS3 (custom properties, fluid type, responsive)
- Vanilla JavaScript (no dependencies, IntersectionObserver for reveal)
- No build step, no bundler, no framework

## Structure

```
portfolio/
├── index.html              # Main page
├── assets/
│   ├── style.css           # Design system (tokens, layout, components)
│   └── app.js              # Smooth scroll, reveal-on-scroll, header shadow
├── tests/
│   ├── run_pipeline.py     # Skill-team-coding pipeline (orchestrator→coder→reviewer)
│   └── lab_server.py       # Local dev server (Flask)
├── reports/
│   └── security_audit.json # Security pass output
└── README.md
```

## Design system

All visual decisions are driven by CSS custom properties at `:root`. To re-theme:

| Token | Default | Purpose |
|---|---|---|
| `--c-bg` | `#0a0a0c` | Page background |
| `--c-fg` | `#e8e6e1` | Primary text |
| `--c-accent` | `#d63384` | Brand accent (magenta-rose) |
| `--font-display` | Cormorant Garamond stack | Editorial serif for headings |
| `--font-body` | system-ui stack | Body text |
| `--fs-display` | `clamp(2.5rem, 6vw + 1rem, 5.5rem)` | Hero title size |
| `--sp-3` | `1.5rem` | Base spacing unit |

## Local preview

```bash
python tests/lab_server.py
# Open http://127.0.0.1:8765
```

Or with any static server:
```bash
python -m http.server 8765 --directory .
```

## Accessibility

- Skip-to-content link
- Semantic HTML (`<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`)
- Focus-visible rings (2px solid yellow, 3px offset)
- `prefers-reduced-motion` respected
- `prefers-color-scheme: light` fallback included
- All links have accessible names

## Pipeline provenance

Built using three combined skills:

1. **`skill-team-coding`** — Orchestrator decomposed into 3 steps (HTML, CSS, JS); each step passed through Coder → Reviewer loop (max 3 iterations); security pass at the end.
2. **`autonomous-project-delivery`** — Project structure under `C:/Users/admin/project-hermes/web-development/portfolio/`, sample artifacts in `reports/`, lab server in `tests/`.
3. **`open-design` (after-hours-editorial principles)** — Dark canvas, large serif display type, magenta accent, subtle paper grain, fluid typography, asymmetric two-column layout for About.

## 👤 Author

**Developed by Ghazi Abid Al Azzam (@Zigha08)**
*Aspiring Penetration Tester | Cybersecurity Enthusiast*

- **GitHub:** [github.com/Zigha08](https://github.com/Zigha08)
- **Email:** ghaziabidalazzam3@gmail.com
- **LinkedIn:** [linkedin.com/in/ghazi-abid-al-azzam-a78363296](https://www.linkedin.com/in/ghazi-abid-al-azzam-a78363296)
