/* Zigha08 portfolio — no framework, no dependencies */
(() => {
  "use strict";

  const init = () => {
  // ---------- Footer year ----------
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // ---------- Footer last-updated ----------
  // Pakai document.lastModified (otomatis di-set oleh GitHub Pages dari
  // Last-Modified HTTP header = waktu push terakhir). Format: "Jun 18, 2026".
  const updatedEl = document.getElementById("last-updated");
  if (updatedEl) {
    const lm = new Date(document.lastModified);
    if (!isNaN(lm.getTime())) {
      updatedEl.textContent = lm.toLocaleDateString("en-US", {
        year: "numeric", month: "short", day: "numeric",
      });
      updatedEl.setAttribute("datetime", lm.toISOString());
    } else {
      updatedEl.textContent = "recently";
    }
  }

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

      // Progressive enhancement: if form has data-endpoint (e.g. Formspree ID),
      // POST as JSON; on failure fall back to mailto: so the user is never stranded.
      const endpoint = form.dataset.endpoint;
      const submit = async () => {
        if (endpoint) {
          try {
            const ctrl = new AbortController();
            const t = setTimeout(() => ctrl.abort(), 8000);
            const res = await fetch(endpoint, {
              method: "POST",
              headers: { "Accept": "application/json", "Content-Type": "application/json" },
              body: JSON.stringify({ name, email, message, _subject: "Portfolio contact from " + name }),
              signal: ctrl.signal,
            });
            clearTimeout(t);
            if (res.ok) {
              if (formMsg) { formMsg.textContent = "Thanks — message sent. I'll reply within a few days."; formMsg.dataset.state = "ok"; }
              form.reset();
              return;
            }
            // Non-2xx: fall through to mailto fallback below
          } catch (_err) {
            // Network/CORS/timeout: fall through to mailto fallback below
          }
        }
        const subject = encodeURIComponent("Portfolio contact from " + name);
        const body = encodeURIComponent(`${message}

— ${name} (${email})`);
        const href = "mailto:ghaziabidalazzam3@gmail.com?subject=" + subject + "&body=" + body;
        window.location.href = href;
        if (formMsg) { formMsg.textContent = "Opening your email client..."; formMsg.dataset.state = "ok"; }
      };
      submit();
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
    { kind: "Action", title: "Open LinkedIn",      hint: "G L", action: () => window.open("https://www.linkedin.com/in/ghazi-abid-al-azzam-a78363296", "_blank", "noopener") },
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
