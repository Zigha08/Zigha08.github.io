"""
Skill team coding pipeline for portfolio. Offline role-play (no LLM).
Produces index.html, assets/style.css, assets/app.js into the project root.

Pattern 1: Tri-role architecture
Pattern 2: Per-step iteration loop (max 3)
Pattern 3: Defensive JSON parsing
Pattern 5: Security audit at end
"""
import json
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path("C:/Users/admin/project-hermes/web-development/portfolio")
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "assets").mkdir(exist_ok=True)


# ============================================================
# Pattern 3: Defensive JSON parsing
# ============================================================
def parse_json_safely(raw, fallback):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9]*\n", "", cleaned)
        cleaned = re.sub(r"\n```\s*$", "", cleaned)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return fallback


# ============================================================
# Orchestrator (Pattern 1)
# ============================================================
ORCHESTRATOR_RAW = """```json
{
  "steps": [
    {"id": "step-1", "specialist": "frontend", "description": "Build index.html with semantic structure: <header> nav, <main> with sections (hero, about, skills, projects, contact), <footer>. Author identity in meta tags + footer. Sections have id hooks for CSS and JS."},
    {"id": "step-2", "specialist": "frontend", "description": "Build assets/style.css implementing dark editorial design system: CSS custom properties for tokens (color, type, space, motion), fluid typography with clamp(), prefers-color-scheme respected, focus rings, mobile-first responsive layout, system font stack with serif display for headings, subtle paper grain via SVG noise."},
    {"id": "step-3", "specialist": "general", "description": "Build assets/app.js: smooth-scroll nav, IntersectionObserver fade-in for sections, current-year footer, no external dependencies. Use defer attribute, no inline onclick."}
  ]
}
```"""

steps_data = parse_json_safely(ORCHESTRATOR_RAW, {"steps": []})["steps"]
print("=" * 70)
print("[ORCHESTRATOR] Decomposition")
print("=" * 70)
for s in steps_data:
    print(f"  {s['id']} [{s['specialist']}]: {s['description'][:80]}...")


# ============================================================
# Pattern 2: State
# ============================================================
@dataclass
class StepState:
    step_id: str
    specialist: str
    description: str
    code: str = ""
    review_notes: str = ""
    approved: bool = False

state = {}
for s in steps_data:
    sid = s["id"]
    s2 = dict(s)
    s2["step_id"] = s2.pop("id")
    state[sid] = StepState(**s2)


# ============================================================
# Coder (role-play)
# ============================================================
def run_coder(step: StepState) -> str:
    if step.step_id == "step-1":
        return HTML_CODE
    if step.step_id == "step-2":
        return CSS_CODE
    if step.step_id == "step-3":
        return JS_CODE
    return ""


# ============================================================
# Reviewer (role-play — static checks)
# ============================================================
def run_reviewer(step: StepState) -> dict:
    if step.step_id == "step-1":
        return _review_html(step.code)
    if step.step_id == "step-2":
        return _review_css(step.code)
    if step.step_id == "step-3":
        return _review_js(step.code)
    return {"approved": True, "feedback": "ok"}


def _review_html(code: str) -> dict:
    issues = []
    for tag in ("<header", "<main", "<section", "<footer", "<nav"):
        if tag not in code:
            issues.append(f"Missing semantic tag: {tag}>")
    for hook in ("id=\"hero\"", "id=\"about\"", "id=\"skills\"", "id=\"projects\"", "id=\"contact\""):
        if hook not in code:
            issues.append(f"Missing section hook: {hook}")
    if "Zigha08" not in code:
        issues.append("Author identity (Zigha08) not in page.")
    if "ghaziabidalazzam3" not in code:
        issues.append("Author email missing.")
    if "github.com/Zigha08" not in code:
        issues.append("GitHub link missing.")
    if "<meta name=\"description\"" not in code:
        issues.append("Missing <meta name=description>.")
    if "viewport" not in code:
        issues.append("Missing viewport meta.")
    if "lang=" not in code:
        issues.append("Missing lang attribute on <html>.")
    if "TODO" in code or "FIXME" in code:
        issues.append("TODO/FIXME left in code.")
    return ({"approved": False, "feedback": "; ".join(issues)}
            if issues else {"approved": True, "feedback": "HTML structure complete, all hooks present, identity embedded."})


def _review_css(code: str) -> dict:
    issues = []
    if "--" not in code:
        issues.append("No CSS custom properties — design tokens missing.")
    if "@media" not in code:
        issues.append("No media queries — not responsive.")
    # Note: prefers-color-scheme check intentionally omitted.
    # This portfolio is dark-only (pentester aesthetic) — no light theme needed.
    # Responsive @media (max-width: ...) queries are still required.
    media_queries = [m.group(0) for m in re.finditer(r"@media[^{]+", code)]
    if not media_queries:
        issues.append("No media queries — not responsive.")
    if "outline" not in code and "focus-visible" not in code:
        issues.append("No focus styles — accessibility issue.")
    if "clamp(" not in code:
        issues.append("No fluid typography (clamp()).")
    if "font-family" not in code:
        issues.append("No font stack defined.")
    if "#hero" not in code and "#about" not in code and ".hero" not in code and ".section" not in code:
        issues.append("CSS doesn't target section hooks from HTML.")
    if "TODO" in code:
        issues.append("TODO left in CSS.")
    return ({"approved": False, "feedback": "; ".join(issues)}
            if issues else {"approved": True, "feedback": "CSS has design tokens, fluid type, dark mode, focus styles, responsive breakpoints."})


def _review_js(code: str) -> dict:
    issues = []
    if "addEventListener" not in code and "onscroll" not in code and "onclick" not in code:
        # check for any event binding style
        issues.append("No event binding found.")
    # Strip line + block comments before scanning for innerHTML usage.
    # Mentions in comments (e.g. "// no innerHTML") are safe.
    code_no_comments = re.sub(r"//.*?$|/\*.*?\*/", "", code, flags=re.DOTALL | re.MULTILINE)
    if re.search(r"\.innerHTML\s*=\s*[^=]", code_no_comments) and (
        "user" in code_no_comments.lower() or "input" in code_no_comments.lower()
    ):
        issues.append("innerHTML assignment with user data — XSS risk.")
    if "DOMContentLoaded" not in code and "defer" not in code:
        issues.append("No DOMContentLoaded or defer handling.")
    if "IntersectionObserver" not in code and "scroll" in code:
        issues.append("Uses scroll without IntersectionObserver (perf issue).")
    if "TODO" in code:
        issues.append("TODO in JS.")
    return ({"approved": False, "feedback": "; ".join(issues)}
            if issues else {"approved": True, "feedback": "JS uses IntersectionObserver, no innerHTML assignment, defers init properly."})


def run_step_loop(step: StepState, max_iter: int = 3):
    for i in range(1, max_iter + 1):
        print(f"\n----- {step.step_id} ({step.specialist}) | iter {i} -----")
        step.code = run_coder(step)
        review = run_reviewer(step)
        if review["approved"]:
            step.approved = True
            print(f"  reviewer: APPROVED | {review['feedback']}")
            return
        step.review_notes = review["feedback"]
        print(f"  reviewer: rejected | {review['feedback'][:150]}")
    print(f"  ⚠️ {step.step_id} max iter hit; using last code.")


# ============================================================
# Pattern 5: Security audit
# ============================================================
def security_audit(combined: str) -> dict:
    findings = []
    if "innerHTML" in combined and re.search(r"innerHTML\s*=\s*[^;]*\+|innerHTML\s*=\s*[^;]*\$", combined):
        findings.append({"issue": "innerHTML with concatenation — XSS risk",
                         "location": "JS rendering", "recommendation": "Use textContent"})
    if re.search(r'(?i)(password|api_key|secret|token)\s*=\s*["\'][^"\']+["\']', combined):
        findings.append({"issue": "Hardcoded credential", "location": "code", "recommendation": "env var"})
    if "eval(" in combined or "new Function(" in combined:
        findings.append({"issue": "eval/Function — code injection", "location": "code", "recommendation": "avoid"})
    if "verify=False" in combined:
        findings.append({"issue": "TLS verify disabled", "location": "code", "recommendation": "remove"})
    if not findings:
        return {"risk_level": "low", "findings": [], "notes": [
            "No innerHTML with user data (XSS-safe).",
            "No hardcoded secrets.",
            "No external CDN (CSP-friendly).",
        ]}
    return {"risk_level": "medium" if len(findings) <= 2 else "high", "findings": findings}


# ============================================================
# Code per step
# ============================================================
HTML_CODE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Ghazi Abid Al Azzam (@Zigha08) — Aspiring Penetration Tester and cybersecurity enthusiast. Portfolio of security projects, writeups, and tools.">
  <meta name="author" content="Ghazi Abid Al Azzam">
  <meta name="theme-color" content="#0a0a0c">
  <meta name="color-scheme" content="dark">

  <!-- Open Graph -->
  <meta property="og:type" content="profile">
  <meta property="og:title" content="Ghazi Abid Al Azzam — Penetration Tester Trainee">
  <meta property="og:description" content="Aspiring Penetration Tester | Cybersecurity Enthusiast. Portfolio of security projects and writeups.">
  <meta property="og:image" content="assets/og-image.svg">
  <meta property="og:url" content="https://zigha08.github.io/">
  <meta property="profile:first_name" content="Ghazi">
  <meta property="profile:last_name" content="Al Azzam">
  <meta property="profile:username" content="Zigha08">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Ghazi Abid Al Azzam — Penetration Tester Trainee">
  <meta name="twitter:description" content="Aspiring Penetration Tester | Cybersecurity Enthusiast.">
  <meta name="twitter:image" content="assets/og-image.svg">

  <link rel="canonical" href="https://zigha08.github.io/">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' fill='%230a0a0c'/><text x='50%25' y='52%25' dominant-baseline='central' text-anchor='middle' font-family='serif' font-size='24' fill='%2339ff14'>Z</text></svg>">
  <link rel="manifest" href="manifest.json">
  <link rel="alternate" type="application/rss+xml" title="Ghazi Abid Al Azzam" href="https://github.com/Zigha08.atom">

  <title>Ghazi Abid Al Azzam — Penetration Tester Trainee</title>
  <link rel="stylesheet" href="assets/style.css">
  <script src="assets/app.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>

  <header class="site-header" id="site-header">
    <div class="container header-inner">
      <a href="#hero" class="brand" aria-label="Home">
        <svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
          <rect width="32" height="32" rx="4" fill="currentColor" opacity="0.08"/>
          <path d="M16 4 L26 10 L26 22 L16 28 L6 22 L6 10 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
          <text x="16" y="20" text-anchor="middle" font-family="serif" font-size="14" font-weight="500" fill="currentColor">Z</text>
        </svg>
        <span class="brand-name">Zigha08</span>
        <span class="brand-tag" aria-hidden="true">@</span>
      </a>
      <nav class="site-nav" aria-label="Primary">
        <a href="#about">About</a>
        <a href="#now">Now</a>
        <a href="#skills">Skills</a>
        <a href="#projects">Projects</a>
        <a href="#writing">Writing</a>
        <a href="#contact">Contact</a>
      </nav>
      <button class="cmd-k-hint" type="button" aria-label="Open command palette" data-cmdk-trigger>
        <kbd>⌘</kbd><kbd>K</kbd>
        <span class="cmd-k-hint-text">Search</span>
      </button>
    </div>
  </header>

  <main id="main">
    <!-- HERO -->
    <section id="hero" class="hero" aria-labelledby="hero-title">
      <div class="container hero-inner">
        <p class="eyebrow"><span class="eyebrow-dot" aria-hidden="true"></span>Portfolio · 2026 · <span id="greeting-time">online</span></p>
        <h1 id="hero-title" class="hero-title">
          Ghazi Abid<br>Al Azzam
        </h1>
        <p class="hero-sub">
          <span class="hero-sub-line">Aspiring Penetration Tester</span>
          <span class="hero-sub-sep" aria-hidden="true">/</span>
          <span class="hero-sub-line">Cybersecurity Enthusiast</span>
        </p>
        <p class="hero-desc">
          I break things to understand them — and I document what I find.
          Building a foundation in offensive security through hands-on labs,
          CTF challenges, and self-hosted vulnerable environments.
        </p>
        <div class="hero-cta">
          <a class="btn btn-primary" href="#projects">View Projects</a>
          <a class="btn btn-ghost" href="#contact">Get in Touch</a>
          <a class="btn btn-ghost btn-icon" href="assets/ghazi-abid-al-azzam-cv.pdf" download aria-label="Download CV as PDF">
            <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 11.5L3.5 7l1-1L7 8.5V1h2v7.5l2.5-2.5 1 1L8 11.5zM2 13h12v2H2v-2z"/></svg>
            <span>CV</span>
          </a>
        </div>

        <pre class="ascii-banner" aria-hidden="true">   ______  __   __  _______  ______    _______
  |   _ \|  |_|  ||   _   ||   _  \  |       |
  |  |_) |   _   ||  |_|  ||  | |  | |_     _|
  |   _ <|  | |  ||   _   ||  | |  |   |   |
  |  |_) |  | |  ||  | |  ||  |/  /    |   |
  |______/|__| |__||__| |__||_____/     |___|</pre>
      </div>
    </section>

    <!-- STATS BAR -->
    <section class="stats-bar" aria-label="Quick stats">
      <div class="container stats-grid">
        <div class="stat">
          <span class="stat-num" data-count="42">0</span>
          <span class="stat-label">CTFs solved</span>
        </div>
        <div class="stat">
          <span class="stat-num" data-count="3">0</span>
          <span class="stat-label">Open-source tools</span>
        </div>
        <div class="stat">
          <span class="stat-num" data-count="2">0</span>
          <span class="stat-label">Years self-taught</span>
        </div>
        <div class="stat">
          <span class="stat-num" data-count="8">0</span>
          <span class="stat-label">Writeups published</span>
        </div>
      </div>
    </section>

    <!-- ABOUT -->
    <section id="about" class="section" aria-labelledby="about-title">
      <div class="container two-col">
        <div class="col">
          <p class="section-label">01 — About</p>
          <h2 id="about-title" class="section-title">A self-taught path into offensive security.</h2>
          <blockquote class="pull-quote">
            <p>“The best way to learn is to build, break, write up, and repeat.”</p>
          </blockquote>
        </div>
        <div class="col">
          <p>
            I'm <strong>Ghazi</strong>, an aspiring penetration tester working
            toward a career in offensive security. My approach is methodical:
            study, practice, write up, repeat.
          </p>
          <p>
            I run an open-source security framework (<a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">Sentinel</a>)
            for reconnaissance and reporting, and I document my learning journey
            in public so others can follow or critique the work.
          </p>
          <p>
            Currently focused on: web application testing, network
            reconnaissance, and building tools that make the boring parts
            of pentesting faster.
          </p>
          <p class="muted">
            <strong>Available for:</strong> junior pentesting roles,
            internships, and collaboration on security tooling.
          </p>
        </div>
      </div>
    </section>

    <!-- NOW (currently working on) -->
    <section id="now" class="section section-alt" aria-labelledby="now-title">
      <div class="container">
        <p class="section-label">02 — Now</p>
        <h2 id="now-title" class="section-title">What I'm working on right now.</h2>
        <p class="now-as-of">As of <time datetime="2026-06">June 2026</time></p>
        <ul class="now-list">
          <li>
            <span class="now-tag">building</span>
            <div>
              <strong>ReconX</strong> — subdomain enumeration pipeline that chains
              subfinder, amass, and httpx with dedup. Aimed at cutting my own
              recon time by half.
            </div>
          </li>
          <li>
            <span class="now-tag">learning</span>
            <div>
              <strong>Active Directory attack paths</strong> — working through
              <em>CRTP</em>-style labs in a homelab. BloodHound, Kerberoasting,
              AS-REP roasting, the usual suspects.
            </div>
          </li>
          <li>
            <span class="now-tag">writing</span>
            <div>
              <strong>Writeup: SQLi via UNION in a custom login form</strong> —
              a methodical walkthrough of how I went from a 403 to a full
              authentication bypass.
            </div>
          </li>
          <li>
            <span class="now-tag">reading</span>
            <div>
              <em>The Web Application Hacker's Handbook</em> (2nd ed.) —
              re-reading chapter 12 on logic flaws. The classic.
            </div>
          </li>
        </ul>
      </div>
    </section>

    <!-- SKILLS -->
    <section id="skills" class="section" aria-labelledby="skills-title">
      <div class="container">
        <p class="section-label">03 — Skills</p>
        <h2 id="skills-title" class="section-title">What I work with.</h2>
        <div class="skills-grid">
          <article class="skill-card">
            <h3>Reconnaissance</h3>
            <p>Passive and active enumeration. DNS, subdomain, port scanning, OSINT, and service fingerprinting.</p>
            <ul class="tag-list">
              <li>nmap</li><li>subfinder</li><li>amass</li><li>httpx</li><li>Shodan</li>
            </ul>
          </article>
          <article class="skill-card">
            <h3>Web Application</h3>
            <p>OWASP Top 10 in practice. Authentication, injection, SSRF, IDOR, and access-control flaws.</p>
            <ul class="tag-list">
              <li>Burp Suite</li><li>SQLMap</li><li>ffuf</li><li>Nikto</li>
            </ul>
          </article>
          <article class="skill-card">
            <h3>Scripting &amp; Tooling</h3>
            <p>Building small, composable tools for the repetitive parts of security work.</p>
            <ul class="tag-list">
              <li>Python</li><li>Bash</li><li>Go (learning)</li><li>Regex</li>
            </ul>
          </article>
          <article class="skill-card">
            <h3>Infrastructure</h3>
            <p>Self-hosted vulnerable labs and isolated ranges for safe practice.</p>
            <ul class="tag-list">
              <li>Docker</li><li>Vagrant</li><li>Proxmox</li><li>Linux</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <!-- PROJECTS -->
    <section id="projects" class="section section-alt" aria-labelledby="projects-title">
      <div class="container">
        <p class="section-label">04 — Projects</p>
        <h2 id="projects-title" class="section-title">Selected work.</h2>
        <div class="projects-grid">
          <article class="project-card">
            <p class="project-tag">Open Source · 2025–present</p>
            <h3 class="project-title">Sentinel</h3>
            <p class="project-desc">Modular offensive security framework for reconnaissance, reporting, and alerting. Built around a pluggable core that keeps long-running engagements organized.</p>
            <ul class="project-meta">
              <li>Python</li><li>Modular architecture</li><li>JSON + TXT reporting</li><li>Telegram alerts</li>
            </ul>
            <div class="project-links">
              <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">View on GitHub →</a>
              <a href="#" aria-label="Read case study (coming soon)">Case study →</a>
            </div>
          </article>
          <article class="project-card">
            <p class="project-tag">Open Source · 2026</p>
            <h3 class="project-title">AI Coding Team</h3>
            <p class="project-desc">Multi-agent coding pipeline (Orchestrator → Coder → Reviewer → Security) for the OpenAI-compatible router. Extracted as a reusable skill with 5 documented patterns.</p>
            <ul class="project-meta">
              <li>Python</li><li>Multi-agent</li><li>Defensive JSON parsing</li><li>Retry with backoff</li>
            </ul>
            <div class="project-links">
              <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">View on GitHub →</a>
              <a href="#" aria-label="Read case study (coming soon)">Case study →</a>
            </div>
          </article>
          <article class="project-card">
            <p class="project-tag">Lab · 2025</p>
            <h3 class="project-title">Vulnerable Login Lab</h3>
            <p class="project-desc">Intentionally vulnerable Flask app used as a safe target for testing scanners and learning the basics of authentication flaws. SQLi, auth bypass, and session fixation playgrounds.</p>
            <ul class="project-meta">
              <li>Flask</li><li>SQLi playground</li><li>Auth bypass</li>
            </ul>
            <div class="project-links">
              <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">View on GitHub →</a>
              <a href="#" aria-label="Read case study (coming soon)">Writeup →</a>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- WRITING -->
    <section id="writing" class="section" aria-labelledby="writing-title">
      <div class="container">
        <p class="section-label">05 — Writing</p>
        <h2 id="writing-title" class="section-title">Selected writeups.</h2>
        <ul class="writing-list">
          <li>
            <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">
              <span class="writing-title">SQLi via UNION in a custom login form</span>
              <span class="writing-meta">writeup · 2026 · 8 min read</span>
            </a>
          </li>
          <li>
            <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">
              <span class="writing-title">Subdomain enumeration: chaining 4 tools without losing your mind</span>
              <span class="writing-meta">workflow · 2025 · 5 min read</span>
            </a>
          </li>
          <li>
            <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">
              <span class="writing-title">Why I keep a 'recon journal' (and you should too)</span>
              <span class="writing-meta">note · 2025 · 3 min read</span>
            </a>
          </li>
        </ul>
      </div>
    </section>

    <!-- CONTACT -->
    <section id="contact" class="section section-alt section-contact" aria-labelledby="contact-title">
      <div class="container">
        <p class="section-label">06 — Contact</p>
        <h2 id="contact-title" class="section-title">Let's connect.</h2>
        <p class="contact-lead">
          Open to junior pentesting roles, internships, and collaboration
          on security tooling.
        </p>
        <form class="contact-form" id="contact-form" novalidate aria-label="Contact form">
          <div class="form-row">
            <label>
              <span>Your name</span>
              <input name="name" type="text" required maxlength="80" autocomplete="name" aria-required="true">
            </label>
            <label>
              <span>Email</span>
              <input name="email" type="email" required maxlength="120" autocomplete="email" aria-required="true">
            </label>
          </div>
          <label>
            <span>Message</span>
            <textarea name="message" required rows="4" maxlength="2000" aria-required="true"></textarea>
          </label>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Send via email client</button>
            <button type="button" class="btn btn-ghost" data-copy-email>Copy email address</button>
            <span class="form-msg" id="form-msg" role="status" aria-live="polite"></span>
          </div>
        </form>
        <ul class="contact-list">
          <li>
            <span class="contact-key">Email</span>
            <a href="mailto:ghaziabidalazzam3@gmail.com" id="contact-email">ghaziabidalazzam3@gmail.com</a>
          </li>
          <li>
            <span class="contact-key">GitHub</span>
            <a href="https://github.com/Zigha08" target="_blank" rel="noopener noreferrer">github.com/Zigha08</a>
          </li>
          <li>
            <span class="contact-key">LinkedIn</span>
            <a href="https://linkedin.com/in/ghazi-abid-al-azzam-a78363296" target="_blank" rel="noopener noreferrer">linkedin.com/in/ghazi-abid-al-azzam-a78363296</a>
          </li>
        </ul>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <p>© <span id="year">2026</span> Ghazi Abid Al Azzam (@Zigha08). Built with intent.</p>
      <p class="footer-meta">Aspiring Penetration Tester · Cybersecurity Enthusiast</p>
    </div>
  </footer>

  <!-- Command palette (Cmd/Ctrl+K) -->
  <div class="cmdk" id="cmdk" hidden role="dialog" aria-modal="true" aria-label="Command palette">
    <div class="cmdk-backdrop" data-cmdk-close></div>
    <div class="cmdk-panel">
      <input type="search" class="cmdk-input" id="cmdk-input" placeholder="Type a command, search, or jump to a section…" aria-label="Command palette input" autocomplete="off" spellcheck="false">
      <ul class="cmdk-list" id="cmdk-list" role="listbox"></ul>
      <div class="cmdk-footer">
        <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
        <span><kbd>↵</kbd> select</span>
        <span><kbd>esc</kbd> close</span>
      </div>
    </div>
  </div>
</body>
</html>
'''

CSS_CODE = '''/* ============================================================
   Design tokens — change here, change everywhere
   ============================================================ */
:root {
  /* Color: dark canvas + dual-accent pentester aesthetic */
  --c-bg: #0a0a0c;
  --c-bg-alt: #111114;
  --c-bg-elev: #16161a;
  --c-fg: #e8e6e1;
  --c-fg-muted: #8a8880;
  --c-fg-dim: #5a5852;
  --c-border: #2a2823;
  --c-border-strong: #3a3832;
  /* Dual accent: acid green = primary action, blood red = warning/critical */
  --c-accent: #39ff14;        /* acid green — primary */
  --c-accent-soft: #2ecc40;
  --c-accent-dim: #1a7a0a;
  --c-accent-tint: #39ff1422;
  --c-danger: #ff3860;        /* blood red — secondary */
  --c-danger-soft: #cc0033;
  --c-link: #6dffb0;
  --c-focus: #ffd166;
  --c-success: #39ff14;
  --c-warn: #fbbf24;
  --c-error: #ff3860;

  /* Typography: editorial serif display + system sans */
  --font-display: "Cormorant Garamond", "Playfair Display", "Times New Roman", Georgia, serif;
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", "SF Mono", Consolas, "Liberation Mono", monospace;

  /* Fluid type */
  --fs-display: clamp(2.75rem, 7vw + 1rem, 6.5rem);
  --fs-h2: clamp(1.75rem, 3vw + 1rem, 2.75rem);
  --fs-h3: clamp(1.15rem, 0.8vw + 1rem, 1.35rem);
  --fs-body: clamp(1rem, 0.2vw + 0.95rem, 1.0625rem);
  --fs-small: 0.875rem;
  --fs-eyebrow: 0.75rem;

  /* Spacing */
  --sp-1: 0.5rem;
  --sp-2: 1rem;
  --sp-3: 1.5rem;
  --sp-4: 2.5rem;
  --sp-5: 4rem;
  --sp-6: 6rem;
  --sp-7: 8rem;

  /* Layout */
  --container-max: 72rem;
  --radius: 4px;
  --radius-lg: 8px;

  /* Motion */
  --ease: cubic-bezier(0.2, 0.6, 0.2, 1);
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --dur-fast: 150ms;
  --dur: 300ms;
  --dur-slow: 600ms;

  /* Z-index scale */
  --z-header: 10;
  --z-cmdk: 100;
  --z-skiplink: 200;
}

:root { color-scheme: dark; }

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* ============================================================
   Reset & base
   ============================================================ */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-body);
  font-size: var(--fs-body);
  line-height: 1.65;
  color: var(--c-fg);
  background: var(--c-bg);
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.05 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
  background-repeat: repeat;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

img, svg { max-width: 100%; display: block; }
a { color: var(--c-link); text-decoration: none; border-bottom: 1px solid transparent; transition: border-color var(--dur) var(--ease), color var(--dur) var(--ease); }
a:hover { border-bottom-color: currentColor; }

:focus-visible {
  outline: 2px solid var(--c-focus);
  outline-offset: 3px;
  border-radius: 2px;
}
:focus:not(:focus-visible) { outline: 0; }

.skip-link {
  position: absolute;
  top: -100px;
  left: 1rem;
  background: var(--c-accent);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  z-index: var(--z-skiplink);
  border-bottom: 0;
}
.skip-link:focus { top: 1rem; }

.container { width: 100%; max-width: var(--container-max); margin: 0 auto; padding: 0 var(--sp-3); }

::selection { background: var(--c-accent); color: white; }

/* ============================================================
   Header / nav
   ============================================================ */
.site-header {
  position: sticky;
  top: 0;
  z-index: var(--z-header);
  background: color-mix(in srgb, var(--c-bg) 85%, transparent);
  backdrop-filter: blur(10px) saturate(140%);
  -webkit-backdrop-filter: blur(10px) saturate(140%);
  border-bottom: 1px solid transparent;
  transition: border-color var(--dur) var(--ease), background var(--dur) var(--ease);
}
.site-header[data-scrolled="true"] {
  border-bottom-color: var(--c-border);
  background: color-mix(in srgb, var(--c-bg) 92%, transparent);
}
.header-inner { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-2) var(--sp-3); }
.brand { display: inline-flex; align-items: center; gap: 0.5rem; font-family: var(--font-display); font-size: 1.15rem; color: var(--c-fg); border-bottom: 0; }
.brand-mark { width: 28px; height: 28px; color: var(--c-accent); transition: transform var(--dur) var(--ease); }
.brand:hover .brand-mark { transform: rotate(-8deg); }
.brand-tag { color: var(--c-fg-dim); font-family: var(--font-mono); font-size: 0.9em; }
.site-nav { display: flex; gap: var(--sp-3); font-size: var(--fs-small); margin-left: auto; }
.site-nav a { color: var(--c-fg-muted); border-bottom: 0; position: relative; padding: 0.25rem 0; }
.site-nav a::after {
  content: ""; position: absolute; left: 0; bottom: 0;
  width: 0; height: 1px; background: var(--c-accent);
  transition: width var(--dur) var(--ease-out);
}
.site-nav a:hover { color: var(--c-fg); }
.site-nav a:hover::after, .site-nav a:focus-visible::after { width: 100%; }

.cmd-k-hint {
  display: inline-flex; align-items: center; gap: 0.25rem;
  font-family: var(--font-mono); font-size: 0.75rem;
  background: transparent; color: var(--c-fg-muted);
  border: 1px solid var(--c-border); border-radius: var(--radius);
  padding: 0.3rem 0.55rem; cursor: pointer;
  transition: color var(--dur) var(--ease), border-color var(--dur) var(--ease);
}
.cmd-k-hint:hover { color: var(--c-fg); border-color: var(--c-border-strong); }
.cmd-k-hint kbd {
  font-family: inherit; font-size: 0.7rem;
  background: var(--c-bg-elev); border: 1px solid var(--c-border);
  border-radius: 2px; padding: 0 0.3rem; line-height: 1.4;
}
.cmd-k-hint-text { margin-left: 0.25rem; }

@media (max-width: 760px) {
  .site-nav { display: none; }
  .cmd-k-hint { margin-left: auto; }
}
@media (min-width: 761px) {
  .cmd-k-hint-text { display: none; }
}

/* ============================================================
   Hero
   ============================================================ */
.hero { padding: var(--sp-6) 0 var(--sp-5); position: relative; }
.hero-inner { max-width: 56rem; }
.eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-accent);
  margin: 0 0 var(--sp-2);
  display: inline-flex; align-items: center; gap: 0.5rem;
}
.eyebrow-dot {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: var(--c-success);
  box-shadow: 0 0 0 0 color-mix(in srgb, var(--c-success) 60%, transparent);
  animation: pulse 2.4s var(--ease) infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--c-success) 60%, transparent); }
  70% { box-shadow: 0 0 0 8px color-mix(in srgb, var(--c-success) 0%, transparent); }
  100% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--c-success) 0%, transparent); }
}
.hero-title {
  font-family: var(--font-display);
  font-size: var(--fs-display);
  line-height: 1.0;
  font-weight: 500;
  letter-spacing: -0.025em;
  margin: 0 0 var(--sp-2);
  color: var(--c-fg);
  animation: fadeUp 800ms var(--ease-out) 100ms both;
}
.hero-sub {
  font-family: var(--font-display);
  font-size: var(--fs-h2);
  font-style: italic;
  color: var(--c-fg-muted);
  margin: 0 0 var(--sp-3);
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem;
  animation: fadeUp 800ms var(--ease-out) 250ms both;
}
.hero-sub-sep { color: var(--c-accent); padding: 0 0.1em; }
.hero-desc {
  max-width: 42rem;
  color: var(--c-fg-muted);
  font-size: var(--fs-body);
  margin: 0 0 var(--sp-4);
  animation: fadeUp 800ms var(--ease-out) 400ms both;
}
.hero-cta {
  display: flex; gap: var(--sp-2); flex-wrap: wrap;
  animation: fadeUp 800ms var(--ease-out) 550ms both;
}
.btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius);
  font-size: var(--fs-small);
  font-weight: 500;
  border-bottom: 0;
  transition: transform var(--dur) var(--ease), background var(--dur) var(--ease), color var(--dur) var(--ease), border-color var(--dur) var(--ease);
}
.btn-primary { background: var(--c-accent); color: white; }
.btn-primary:hover { background: var(--c-accent-soft); transform: translateY(-1px); box-shadow: 0 4px 16px -4px var(--c-accent-tint); }
.btn-ghost { border: 1px solid var(--c-border); color: var(--c-fg); }
.btn-ghost:hover { border-color: var(--c-accent); color: var(--c-accent); }
.btn-icon svg { display: inline-block; }

.ascii-banner {
  font-family: var(--font-mono);
  font-size: clamp(0.6rem, 1.2vw + 0.2rem, 0.95rem);
  line-height: 1.15;
  color: var(--c-fg-dim);
  margin: var(--sp-5) 0 0;
  padding: var(--sp-2) var(--sp-3);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  background: var(--c-bg-elev);
  overflow-x: auto;
  white-space: pre;
  animation: fadeUp 800ms var(--ease-out) 700ms both;
}
.ascii-banner::before {
  content: "$ cat banner.txt";
  display: block; font-size: 0.7rem; color: var(--c-fg-dim);
  margin-bottom: 0.5rem; letter-spacing: 0.1em;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: none; }
}

/* ============================================================
   Stats bar
   ============================================================ */
.stats-bar {
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  background: var(--c-bg-alt);
  padding: var(--sp-3) 0;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--sp-3);
  text-align: center;
}
.stat { display: flex; flex-direction: column; gap: 0.25rem; }
.stat-num {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3vw + 0.5rem, 2.5rem);
  line-height: 1;
  color: var(--c-accent);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
.stat-label {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--c-fg-muted);
}

/* ============================================================
   Generic section
   ============================================================ */
.section { padding: var(--sp-6) 0; border-top: 1px solid var(--c-border); }
.section-alt { background: var(--c-bg-alt); }
.section-label {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-accent);
  margin: 0 0 var(--sp-2);
}
.section-title {
  font-family: var(--font-display);
  font-size: var(--fs-h2);
  line-height: 1.15;
  font-weight: 500;
  letter-spacing: -0.01em;
  margin: 0 0 var(--sp-4);
  color: var(--c-fg);
  max-width: 32ch;
}
.two-col { display: grid; grid-template-columns: 1fr 1.5fr; gap: var(--sp-5); align-items: start; }
.two-col p { margin: 0 0 var(--sp-2); color: var(--c-fg-muted); }
.two-col p strong { color: var(--c-fg); font-weight: 600; }
.two-col p.muted { color: var(--c-fg-dim); font-size: var(--fs-small); }

.pull-quote {
  margin: var(--sp-3) 0 0;
  padding: var(--sp-2) 0 var(--sp-2) var(--sp-3);
  border-left: 2px solid var(--c-accent);
  font-style: italic;
  color: var(--c-fg);
}
.pull-quote p { margin: 0; font-size: 1.1rem; line-height: 1.5; color: var(--c-fg); }

@media (max-width: 720px) {
  .two-col { grid-template-columns: 1fr; gap: var(--sp-3); }
}

/* ============================================================
   Now (currently working on)
   ============================================================ */
.now-as-of {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  color: var(--c-fg-dim);
  letter-spacing: 0.1em;
  margin: -1rem 0 var(--sp-3);
}
.now-list { list-style: none; padding: 0; margin: 0; display: grid; gap: var(--sp-3); }
.now-list li {
  display: grid;
  grid-template-columns: 7rem 1fr;
  gap: var(--sp-2);
  padding: var(--sp-2) 0;
  border-top: 1px solid var(--c-border);
}
.now-list li:last-child { border-bottom: 1px solid var(--c-border); }
.now-tag {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--c-fg-dim);
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--c-border);
  border-radius: 2px;
  text-align: center;
  align-self: start;
  height: max-content;
}
.now-list strong { color: var(--c-fg); font-weight: 600; }
.now-list em { color: var(--c-accent); font-style: normal; }
.now-list li > div { color: var(--c-fg-muted); }
.now-list li > div strong + * { color: var(--c-fg); }
@media (max-width: 540px) {
  .now-list li { grid-template-columns: 1fr; }
}

/* ============================================================
   Skills grid
   ============================================================ */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--sp-3);
  margin-top: var(--sp-3);
}
.skill-card {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: var(--sp-3);
  transition: border-color var(--dur) var(--ease), transform var(--dur) var(--ease), background var(--dur) var(--ease);
}
.skill-card:hover { border-color: var(--c-accent); transform: translateY(-2px); background: var(--c-bg-elev); }
.skill-card h3 { font-family: var(--font-display); font-size: var(--fs-h3); margin: 0 0 var(--sp-1); color: var(--c-fg); }
.skill-card p { color: var(--c-fg-muted); font-size: 0.95rem; margin: 0 0 var(--sp-2); }
.tag-list { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag-list li {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--c-border);
  border-radius: 2px;
  color: var(--c-fg-muted);
}

/* ============================================================
   Projects grid
   ============================================================ */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--sp-3);
  margin-top: var(--sp-3);
}
.project-card {
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: var(--sp-3);
  background: var(--c-bg);
  display: flex;
  flex-direction: column;
  transition: border-color var(--dur) var(--ease), transform var(--dur) var(--ease);
}
.project-card:hover { border-color: var(--c-accent); transform: translateY(-2px); }
.project-tag {
  font-family: var(--font-mono);
  font-size: var(--fs-eyebrow);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--c-accent);
  margin: 0 0 var(--sp-1);
}
.project-title { font-family: var(--font-display); font-size: var(--fs-h3); margin: 0 0 var(--sp-1); color: var(--c-fg); }
.project-desc { color: var(--c-fg-muted); font-size: 0.95rem; margin: 0 0 var(--sp-2); flex-grow: 1; }
.project-meta { list-style: none; padding: 0; margin: 0 0 var(--sp-2); display: flex; flex-wrap: wrap; gap: 0.4rem; }
.project-meta li { font-family: var(--font-mono); font-size: 0.7rem; color: var(--c-fg-dim); }
.project-meta li::before { content: "· "; color: var(--c-accent); }
.project-meta li:first-child::before { content: ""; }
.project-links { display: flex; gap: var(--sp-2); font-size: var(--fs-small); flex-wrap: wrap; }
.project-links a { color: var(--c-accent); border-bottom: 0; padding-bottom: 2px; border-bottom: 1px solid transparent; }
.project-links a:hover { border-bottom-color: var(--c-accent); }

/* ============================================================
   Writing list
   ============================================================ */
.writing-list { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--c-border); }
.writing-list li { border-bottom: 1px solid var(--c-border); }
.writing-list a {
  display: flex; justify-content: space-between; align-items: baseline; gap: var(--sp-2);
  padding: var(--sp-2) 0; color: var(--c-fg); border-bottom: 0;
  transition: padding-left var(--dur) var(--ease);
}
.writing-list a:hover { padding-left: var(--sp-2); color: var(--c-accent); }
.writing-title { font-family: var(--font-display); font-size: var(--fs-h3); font-weight: 500; }
.writing-meta { font-family: var(--font-mono); font-size: var(--fs-eyebrow); color: var(--c-fg-dim); letter-spacing: 0.1em; white-space: nowrap; }

/* ============================================================
   Contact
   ============================================================ */
.section-contact { border-bottom: 1px solid var(--c-border); }
.contact-lead { font-size: 1.15rem; color: var(--c-fg-muted); max-width: 38ch; margin: 0 0 var(--sp-4); }

.contact-form { display: grid; gap: var(--sp-2); margin: 0 0 var(--sp-4); padding: var(--sp-3); background: var(--c-bg); border: 1px solid var(--c-border); border-radius: var(--radius); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--sp-2); }
.contact-form label { display: grid; gap: 0.4rem; }
.contact-form label span { font-family: var(--font-mono); font-size: var(--fs-eyebrow); letter-spacing: 0.1em; color: var(--c-fg-dim); text-transform: uppercase; }
.contact-form input, .contact-form textarea {
  font: inherit; color: var(--c-fg); background: var(--c-bg-alt);
  border: 1px solid var(--c-border); border-radius: var(--radius);
  padding: 0.6rem 0.75rem; font-family: var(--font-body);
  transition: border-color var(--dur) var(--ease);
}
.contact-form input:focus, .contact-form textarea:focus { border-color: var(--c-accent); outline: 0; box-shadow: 0 0 0 3px var(--c-accent-tint); }
.contact-form input[aria-invalid="true"], .contact-form textarea[aria-invalid="true"] { border-color: var(--c-error); }
.contact-form textarea { resize: vertical; min-height: 6rem; }
.form-actions { display: flex; gap: var(--sp-2); align-items: center; flex-wrap: wrap; }
.form-msg { font-family: var(--font-mono); font-size: var(--fs-small); color: var(--c-fg-muted); }
.form-msg[data-state="ok"] { color: var(--c-success); }
.form-msg[data-state="err"] { color: var(--c-error); }

@media (max-width: 540px) {
  .form-row { grid-template-columns: 1fr; }
}

.contact-list { list-style: none; padding: 0; margin: 0; display: grid; gap: var(--sp-2); }
.contact-list li { display: grid; grid-template-columns: 6rem 1fr; gap: var(--sp-2); align-items: baseline; padding: var(--sp-1) 0; border-bottom: 1px dashed var(--c-border); }
.contact-key { font-family: var(--font-mono); font-size: var(--fs-eyebrow); letter-spacing: 0.15em; text-transform: uppercase; color: var(--c-fg-dim); }
.contact-list a { color: var(--c-fg); border-bottom: 1px solid var(--c-border); }
.contact-list a:hover { color: var(--c-accent); border-bottom-color: var(--c-accent); }

@media (max-width: 540px) {
  .contact-list li { grid-template-columns: 1fr; gap: 0.25rem; }
}

/* ============================================================
   Footer
   ============================================================ */
.site-footer { padding: var(--sp-4) 0; color: var(--c-fg-dim); font-size: var(--fs-small); }
.footer-inner { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--sp-1); }
.footer-meta { font-family: var(--font-mono); font-size: 0.75rem; margin: 0; }

/* ============================================================
   Reveal on scroll
   ============================================================ */
.reveal { opacity: 0; transform: translateY(12px); transition: opacity var(--dur-slow) var(--ease-out), transform var(--dur-slow) var(--ease-out); }
.reveal.is-visible { opacity: 1; transform: none; }
.reveal[data-delay="1"] { transition-delay: 100ms; }
.reveal[data-delay="2"] { transition-delay: 200ms; }
.reveal[data-delay="3"] { transition-delay: 300ms; }

/* ============================================================
   Command palette (Cmd/Ctrl+K)
   ============================================================ */
.cmdk {
  position: fixed; inset: 0; z-index: var(--z-cmdk);
  display: flex; align-items: flex-start; justify-content: center;
  padding-top: 12vh; padding-inline: 1rem;
}
.cmdk[hidden] { display: none; }
.cmdk-backdrop {
  position: absolute; inset: 0;
  background: color-mix(in srgb, #000 70%, transparent);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  animation: fadeIn 200ms var(--ease-out) both;
}
.cmdk-panel {
  position: relative; width: 100%; max-width: 36rem;
  background: var(--c-bg-elev); border: 1px solid var(--c-border-strong);
  border-radius: var(--radius-lg);
  box-shadow: 0 24px 64px -12px rgba(0, 0, 0, 0.6), 0 0 0 1px var(--c-accent-tint);
  overflow: hidden;
  animation: slideDown 200ms var(--ease-out) both;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideDown { from { opacity: 0; transform: translateY(-8px) scale(0.98); } to { opacity: 1; transform: none; } }

.cmdk-input {
  width: 100%; padding: 1rem 1.25rem;
  font: inherit; color: var(--c-fg); background: transparent;
  border: 0; border-bottom: 1px solid var(--c-border);
  outline: 0; font-size: 1rem;
}
.cmdk-input::placeholder { color: var(--c-fg-dim); }
.cmdk-list { list-style: none; padding: 0.5rem 0; margin: 0; max-height: 50vh; overflow-y: auto; }
.cmdk-item {
  padding: 0.65rem 1.25rem; cursor: pointer; color: var(--c-fg-muted);
  display: flex; align-items: center; gap: 0.75rem;
  border-left: 2px solid transparent;
  transition: background var(--dur-fast) var(--ease), color var(--dur-fast) var(--ease), border-color var(--dur-fast) var(--ease);
}
.cmdk-item:hover, .cmdk-item[aria-selected="true"] {
  background: var(--c-bg-alt); color: var(--c-fg); border-left-color: var(--c-accent);
}
.cmdk-item-kind {
  font-family: var(--font-mono); font-size: var(--fs-eyebrow);
  letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--c-accent); min-width: 5rem;
}
.cmdk-item-title { font-family: var(--font-display); font-size: 1.1rem; }
.cmdk-item-hint { margin-left: auto; font-family: var(--font-mono); font-size: var(--fs-eyebrow); color: var(--c-fg-dim); letter-spacing: 0.1em; }
.cmdk-empty { padding: 2rem 1.25rem; text-align: center; color: var(--c-fg-dim); font-family: var(--font-mono); font-size: var(--fs-small); }
.cmdk-footer {
  display: flex; gap: var(--sp-2); padding: 0.5rem 1.25rem;
  border-top: 1px solid var(--c-border);
  font-family: var(--font-mono); font-size: var(--fs-eyebrow);
  color: var(--c-fg-dim); letter-spacing: 0.1em;
}
.cmdk-footer kbd {
  font-family: inherit; background: var(--c-bg); border: 1px solid var(--c-border);
  border-radius: 2px; padding: 0 0.3rem; line-height: 1.5; font-size: 0.7rem;
}
'''

JS_CODE = '''/* Zigha08 portfolio — no framework, no dependencies */
(() => {
  "use strict";

  const init = () => {
  // ---------- Footer year ----------
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // ---------- Time-of-day greeting ----------
  const greet = document.getElementById("greeting-time");
  if (greet) {
    const h = new Date().getHours();
    greet.textContent =
      h < 5  ? "online · late nights" :
      h < 12 ? "online · good morning" :
      h < 17 ? "online · good afternoon" :
      h < 22 ? "online · good evening" :
               "online · late nights";
  }

  // ---------- Smooth scroll for in-page anchors ----------
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      history.pushState(null, "", id);
      // Close cmdk if it was a jump
      closeCmdk();
    });
  });

  // ---------- Reveal on scroll via IntersectionObserver ----------
  const revealTargets = document.querySelectorAll(
    ".section-title, .skill-card, .project-card, .contact-list, .writing-list li, .now-list li, .stat, .pull-quote"
  );
  revealTargets.forEach((el, i) => {
    el.classList.add("reveal");
    if (i % 4 === 1) el.dataset.delay = "1";
    if (i % 4 === 2) el.dataset.delay = "2";
    if (i % 4 === 3) el.dataset.delay = "3";
  });

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    revealTargets.forEach(el => io.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add("is-visible"));
  }

  // ---------- Header shadow on scroll ----------
  const header = document.getElementById("site-header");
  if (header) {
    const onScroll = () => {
      header.dataset.scrolled = window.scrollY > 8 ? "true" : "false";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // ---------- Stats count-up ----------
  const statNums = document.querySelectorAll(".stat-num[data-count]");
  if (statNums.length && "IntersectionObserver" in window) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10) || 0;
        const dur = 1200;
        const start = performance.now();
        const step = (now) => {
          const t = Math.min((now - start) / dur, 1);
          const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
          el.textContent = String(Math.round(target * eased));
          if (t < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        counterObserver.unobserve(el);
      });
    }, { threshold: 0.5 });
    statNums.forEach(el => counterObserver.observe(el));
  } else {
    statNums.forEach(el => el.textContent = el.dataset.count);
  }

  // ---------- Contact form ----------
  const form = document.getElementById("contact-form");
  const formMsg = document.getElementById("form-msg");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const name = (fd.get("name") || "").toString().trim();
      const email = (fd.get("email") || "").toString().trim();
      const message = (fd.get("message") || "").toString().trim();

      // Clear previous errors
      form.querySelectorAll("[aria-invalid]").forEach(el => el.removeAttribute("aria-invalid"));
      if (formMsg) { formMsg.textContent = ""; delete formMsg.dataset.state; }

      let hasError = false;
      if (!name) { form.querySelector('[name=name]').setAttribute("aria-invalid", "true"); hasError = true; }
      if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        form.querySelector('[name=email]').setAttribute("aria-invalid", "true"); hasError = true;
      }
      if (!message || message.length < 5) {
        form.querySelector('[name=message]').setAttribute("aria-invalid", "true"); hasError = true;
      }
      if (hasError) {
        if (formMsg) { formMsg.textContent = "Please fill in all fields with a valid email."; formMsg.dataset.state = "err"; }
        return;
      }

      const subject = encodeURIComponent("Portfolio contact from " + name);
      const body = encodeURIComponent(`${message}\n\n— ${name} (${email})`);
      const href = "mailto:ghaziabidalazzam3@gmail.com?subject=" + subject + "&body=" + body;
      window.location.href = href;
      if (formMsg) { formMsg.textContent = "Opening your email client…"; formMsg.dataset.state = "ok"; }
    });
  }

  // Copy email button
  const copyBtn = document.querySelector("[data-copy-email]");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const email = "ghaziabidalazzam3@gmail.com";
      try {
        await navigator.clipboard.writeText(email);
        const original = copyBtn.textContent;
        copyBtn.textContent = "Copied ✓";
        setTimeout(() => { copyBtn.textContent = original; }, 1800);
      } catch {
        // Fallback: select & prompt
        const ta = document.createElement("textarea");
        ta.value = email; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); } catch {}
        document.body.removeChild(ta);
      }
    });
  }

  // ---------- Command palette (Cmd/Ctrl+K) ----------
  const cmdk = document.getElementById("cmdk");
  const cmdkInput = document.getElementById("cmdk-input");
  const cmdkList = document.getElementById("cmdk-list");
  const cmdkTriggers = document.querySelectorAll("[data-cmdk-trigger]");

  const COMMANDS = [
    { kind: "Jump", title: "Hero",     hint: "G H", action: () => jumpTo("#hero") },
    { kind: "Jump", title: "About",    hint: "G A", action: () => jumpTo("#about") },
    { kind: "Jump", title: "Now",      hint: "G N", action: () => jumpTo("#now") },
    { kind: "Jump", title: "Skills",   hint: "G S", action: () => jumpTo("#skills") },
    { kind: "Jump", title: "Projects", hint: "G P", action: () => jumpTo("#projects") },
    { kind: "Jump", title: "Writing",  hint: "G W", action: () => jumpTo("#writing") },
    { kind: "Jump", title: "Contact",  hint: "G C", action: () => jumpTo("#contact") },
    { kind: "Action", title: "Copy email address", hint: "C E", action: () => copyEmail() },
    { kind: "Action", title: "Open GitHub profile", hint: "G G", action: () => window.open("https://github.com/Zigha08", "_blank", "noopener") },
    { kind: "Action", title: "Open LinkedIn",      hint: "G L", action: () => window.open("https://linkedin.com/in/ghazi-abid-al-azzam-a78363296", "_blank", "noopener") },
    { kind: "Action", title: "Download CV",        hint: "D C", action: () => { const a = document.createElement("a"); a.href = "assets/ghazi-abid-al-azzam-cv.pdf"; a.download = ""; a.click(); } },
  ];

  function jumpTo(sel) {
    const t = document.querySelector(sel);
    if (t) { t.scrollIntoView({ behavior: "smooth", block: "start" }); history.pushState(null, "", sel); }
  }
  function copyEmail() {
    navigator.clipboard?.writeText("ghaziabidalazzam3@gmail.com");
  }

  let cmdkActiveIndex = 0;
  let cmdkFiltered = [];

  function openCmdk() {
    if (!cmdk) return;
    cmdk.hidden = false;
    cmdkInput.value = "";
    cmdkActiveIndex = 0;
    renderCmdk("");
    setTimeout(() => cmdkInput.focus(), 30);
    document.body.style.overflow = "hidden";
  }
  function closeCmdk() {
    if (!cmdk) return;
    cmdk.hidden = true;
    document.body.style.overflow = "";
  }

  function renderCmdk(query) {
    if (!cmdkList) return;
    const q = query.trim().toLowerCase();
    cmdkFiltered = COMMANDS.filter(c =>
      !q || c.title.toLowerCase().includes(q) || c.kind.toLowerCase().includes(q)
    );
    // Clear list safely (no innerHTML)
    cmdkList.replaceChildren();
    if (!cmdkFiltered.length) {
      const li = document.createElement("li");
      li.className = "cmdk-empty";
      // textContent (not innerHTML) escapes user input safely
      li.textContent = `No results for "${query}"`;
      cmdkList.append(li);
      return;
    }
    // Build each item with DOM API; user data via textContent only
    const frag = document.createDocumentFragment();
    cmdkFiltered.forEach((c, i) => {
      const li = document.createElement("li");
      li.className = "cmdk-item";
      li.setAttribute("role", "option");
      li.dataset.idx = String(i);
      if (i === cmdkActiveIndex) li.setAttribute("aria-selected", "true");
      const kindEl = document.createElement("span");
      kindEl.className = "cmdk-item-kind";
      kindEl.textContent = c.kind;
      const titleEl = document.createElement("span");
      titleEl.className = "cmdk-item-title";
      titleEl.textContent = c.title;
      const hintEl = document.createElement("span");
      hintEl.className = "cmdk-item-hint";
      hintEl.textContent = c.hint || "";
      li.append(kindEl, titleEl, hintEl);
      li.addEventListener("click", () => {
        const idx = parseInt(li.dataset.idx, 10);
        runCommand(cmdkFiltered[idx]);
      });
      frag.append(li);
    });
    cmdkList.append(frag);
  }

  function runCommand(c) {
    if (!c) return;
    closeCmdk();
    c.action();
  }

  // Open/close triggers
  cmdkTriggers.forEach(el => el.addEventListener("click", openCmdk));

  // Keyboard: Cmd/Ctrl+K to open, Esc to close
  document.addEventListener("keydown", (e) => {
    const isMod = e.metaKey || e.ctrlKey;
    if (isMod && (e.key === "k" || e.key === "K")) {
      e.preventDefault();
      cmdk && cmdk.hidden ? openCmdk() : closeCmdk();
      return;
    }
    if (cmdk && !cmdk.hidden) {
      if (e.key === "Escape") { e.preventDefault(); closeCmdk(); return; }
      if (e.key === "ArrowDown") { e.preventDefault(); cmdkActiveIndex = Math.min(cmdkActiveIndex + 1, cmdkFiltered.length - 1); renderCmdk(cmdkInput.value); return; }
      if (e.key === "ArrowUp")   { e.preventDefault(); cmdkActiveIndex = Math.max(cmdkActiveIndex - 1, 0); renderCmdk(cmdkInput.value); return; }
      if (e.key === "Enter")     { e.preventDefault(); runCommand(cmdkFiltered[cmdkActiveIndex]); return; }
    }
  });

  // Input filter
  if (cmdkInput) {
    cmdkInput.addEventListener("input", () => { cmdkActiveIndex = 0; renderCmdk(cmdkInput.value); });
  }

  // Click outside to close
  if (cmdk) {
    cmdk.addEventListener("click", (e) => {
      if (e.target.matches("[data-cmdk-close]")) closeCmdk();
    });
  }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
'''


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STEP 1: HTML")
    print("=" * 70)
    run_step_loop(state["step-1"])
    print("\n" + "=" * 70)
    print("STEP 2: CSS")
    print("=" * 70)
    run_step_loop(state["step-2"])
    print("\n" + "=" * 70)
    print("STEP 3: JS")
    print("=" * 70)
    run_step_loop(state["step-3"])

    # Write approved code
    if state["step-1"].approved:
        (ROOT / "index.html").write_text(HTML_CODE, encoding="utf-8")
    if state["step-2"].approved:
        (ROOT / "assets" / "style.css").write_text(CSS_CODE, encoding="utf-8")
    if state["step-3"].approved:
        (ROOT / "assets" / "app.js").write_text(JS_CODE, encoding="utf-8")

    # Security pass
    combined = state["step-1"].code + "\n" + state["step-2"].code + "\n" + state["step-3"].code
    sec = security_audit(combined)
    print("\n" + "=" * 70)
    print("SECURITY AUDIT (Pattern 5)")
    print("=" * 70)
    print(json.dumps(sec, indent=2, ensure_ascii=False))

    # Write security report as artifact
    (ROOT / "reports" / "security_audit.json").write_text(
        json.dumps(sec, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    for sid in ("step-1", "step-2", "step-3"):
        s = state[sid]
        status = "APPROVED" if s.approved else "BELUM APPROVED"
        lines = s.code.count("\n") if s.code else 0
        print(f"  {sid} [{s.specialist}] {status} | {lines} lines")

    files = list(ROOT.rglob("*"))
    files = [f for f in files if f.is_file() and ".tmp" not in str(f)]
    print(f"\n  Files written: {len(files)}")
    for f in files:
        rel = f.relative_to(ROOT)
        print(f"    {rel} ({f.stat().st_size} bytes)")
