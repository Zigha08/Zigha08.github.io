# Zigha08.github.io

This repository is the **deployment artifact** for the personal portfolio site at
**[https://zigha08.github.io/](https://zigha08.github.io/)**.

It is **not** where the source code lives.

---

## Source code

Source code (HTML, CSS, JS, build scripts) lives in a private repository:
**[Zigha08/portfolio-source](https://github.com/Zigha08/portfolio-source)** (private).

A GitHub Action in that repo automatically builds and deploys the site to the
`gh-pages` branch of this repo whenever source changes are pushed.

## Branches

| Branch | Purpose |
|---|---|
| `main` | This README + minimal metadata. **Not used for Pages.** |
| `gh-pages` | Deployed static site content, served by GitHub Pages. |

## Architecture

```
portfolio-source (private)  →  GitHub Action  →  Zigha08.github.io (this, gh-pages branch)
                                                       │
                                                       └─→ https://zigha08.github.io/
```

## License

Site content © Ghazi Abid Al Azzam. Source code is MIT-licensed — see
[portfolio-source](https://github.com/Zigha08/portfolio-source) for the canonical copy.

---

*If you're a recruiter or collaborator looking for code review, please contact
me directly via the [contact form on the site](https://zigha08.github.io/#contact)
— I'll provide access to the source repo on a case-by-case basis.*
