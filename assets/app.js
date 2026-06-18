/* Zigha08 portfolio — no framework, no dependencies */
(() => {
  "use strict";

  const init = () => {
  // Footer year
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Smooth scroll for in-page anchors (with native fallback)
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      // Update URL hash without jumping
      history.pushState(null, "", id);
    });
  });

  // Reveal on scroll via IntersectionObserver
  const revealTargets = document.querySelectorAll(
    ".section-title, .skill-card, .project-card, .contact-list"
  );
  revealTargets.forEach(el => el.classList.add("reveal"));

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.05 });

    revealTargets.forEach(el => io.observe(el));
  } else {
    // Fallback: just show everything
    revealTargets.forEach(el => el.classList.add("is-visible"));
  }

  // Header shadow on scroll
  const header = document.getElementById("site-header");
  if (header) {
    let lastY = 0;
    const onScroll = () => {
      const y = window.scrollY;
      header.dataset.scrolled = y > 8 ? "true" : "false";
      lastY = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
