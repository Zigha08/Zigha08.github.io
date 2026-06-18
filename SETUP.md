# Setup: Auto-sync GitHub repos → portfolio

Dokumen ini menjelaskan cara mengaktifkan workflow `.github/workflows/sync-repos.yml` di repo `Zigha08.github.io`. Workflow akan otomatis menarik daftar repo publik Anda dari GitHub, render ke project cards, dan update portfolio — setiap hari pukul 06:00 UTC, atau manual dari tab Actions, atau via trigger dari repo lain.

---

## Apa yang dilakukan workflow ini

1. Fetch semua repo publik akun `Zigha08` via GitHub REST API.
2. Filter: exclude `Zigha08.github.io` (portfolio sendiri) dan repo archived.
3. Sort by `pushed_at` desc (paling aktif duluan), keep top 6.
4. Render ke HTML via `scripts/render_projects.py`.
5. Patch blok `<div class="projects-grid">...</div>` di `index.html`.
6. Commit & push ke `main` → GitHub Pages auto-rebuild dalam ~30 detik.

---

## Prasyarat

Workflow ini butuh **Personal Access Token (PAT)** dengan izin `public_repo` agar bisa push commit ke `Zigha08.github.io` (default `GITHUB_TOKEN` dari Actions tidak bisa trigger build Pages untuk push dari workflow ke repo yang sama).

---

## Setup step-by-step

### 1. Generate PAT (Personal Access Token)

1. Buka https://github.com/settings/tokens → klik **Generate new token**.
2. Pilih **Fine-grained token** (disarankan; lebih aman dari classic).
3. Isi form:
   - **Token name**: `repo-sync-portfolio` (atau nama lain yang deskriptif)
   - **Expiration**: pilih durasi. Untuk workflow ini, 90 hari cukup; nanti tinggal rotate.
   - **Resource owner**: pilih akun `Zigha08`
   - **Repository access**: pilih **All repositories** atau spesifik ke `Zigha08/Zigha08.github.io`. Kalau pilih spesifik, aman — workflow ini cuma push ke 1 repo.
   - **Permissions → Repository permissions**:
     - `Contents`: **Read and write** ← wajib, supaya bisa push commit
     - `Metadata`: otomatis Read-only (default)
     - Sisanya biarkan default (tidak perlu permission lain).
4. Klik **Generate token**.
5. **Salin token sekarang** — GitHub tidak akan menampilkannya lagi.

### 2. Tambahkan PAT sebagai secret di repo portfolio

1. Buka https://github.com/Zigha08/Zigha08.github.io/settings/secrets/actions → klik **New repository secret**.
2. Isi:
   - **Name**: `REPO_SYNC_TOKEN`
   - **Secret**: paste token dari step 1.
3. Klik **Add secret**.

### 3. (Opsional) Aktifkan trigger dari repo lain

Secara default workflow trigger dari:
- Cron harian jam 06:00 UTC.
- Manual dari tab Actions.

Kalau mau push ke repo Sentinel langsung juga trigger sync portfolio:

1. Buka https://github.com/Zigha08/Sentinel/settings/hooks → **Add webhook**.
2. **Payload URL**: `https://api.github.com/repos/Zigha08/Zigha08.github.io/dispatches`
3. **Content type**: `application/json`
4. **Secret**: sama dengan PAT (atau secret lain yang dedicated).
5. **Which events**: pilih **Just the push event.**
6. **Active**: centang.
7. Klik **Add webhook**.

Ulangi untuk repo `VulnSeeker`, `reconX`, `AuthHacker`, `ai-coding-team`.

**Alternatif yang lebih simpel (recommended):**
Cukup pakai cron harian. Untuk portfolio yang update tidak terlalu sering, ini sudah cukup dan tidak menambah surface webhook yang harus di-maintain.

### 4. Trigger pertama kali (manual)

1. Buka https://github.com/Zigha08/Zigha08.github.io/actions
2. Pilih workflow **Sync GitHub repos to portfolio** di sidebar kiri.
3. Klik **Run workflow** → tombol hijau **Run workflow**.
4. Tunggu ~30-60 detik. Kalau berhasil, akan muncul commit baru di tab Commits: `Sync GitHub repos to portfolio (2026-06-18T...)`.
5. Cek https://zigha08.github.io/#projects — kartu project sekarang menampilkan semua repo publik.

---

## Cara kerja & struktur file

```
Zigha08.github.io/
├── .github/
│   └── workflows/
│       └── sync-repos.yml        # Workflow definition
├── scripts/
│   └── render_projects.py        # Render JSON → HTML cards
├── index.html                    # Di-patch otomatis (blok projects-grid)
└── SETUP.md                      # File ini
```

### Apa yang akan berubah di index.html?

Setiap kali workflow jalan, blok:

```html
<div class="projects-grid">
  ... cards statis yang lama ...
</div>
```

Akan diganti dengan cards baru di-render dari data GitHub. Cards statis yang dulu (Sentinel, AI Coding Team, Vulnerable Login Lab) akan hilang — diganti cards dari semua repo publik. Ini **by design**: portfolio sekarang auto-sync, tidak perlu maintenance manual.

Kalau Anda ingin menyimpan satu card manual (mis. "Vulnerable Login Lab" yang tidak di-GitHub), tambahkan ke `EXCLUDED_REPOS`... wait, EXCLUDED adalah untuk repo GitHub. Untuk card non-GitHub, tambahkan sebelum `<div class="projects-grid">` di `index.html` sebagai card terpisah (lihat `index.html` baris ~240).

---

## Customization

### Tambah repo yang di-pin (selalu muncul di atas)

Edit `scripts/render_projects.py`, tambahkan nama repo ke `PINNED_REPOS`:

```python
PINNED_REPOS: set[str] = {"Sentinel", "ai-coding-team"}
```

### Ubah jumlah maksimum cards

```python
MAX_CARDS = 6   # ubah sesuai kebutuhan
```

### Tambah repo yang di-exclude

```python
EXCLUDED_REPOS: set[str] = {"Zigha08.github.io", "old-project-archive"}
```

### Ubah jadwal cron

Edit `.github/workflows/sync-repos.yml`:

```yaml
schedule:
  - cron: "0 */6 * * *"   # setiap 6 jam, bukan harian
```

Format cron: `menit jam hari-bulan hari-minggu`. Dokumentasi: https://crontab.guru/

### Trigger workflow dari repo lain via API (tanpa webhook)

```bash
gh api repos/Zigha08/Zigha08.github.io/dispatches \
  -f event_type=sync-repos
```

Bisa di-add sebagai post-push hook lokal atau di-CI repo lain.

---

## Troubleshooting

### Workflow gagal "GITHUB_REPOS_JSON env var is empty"
Render script dijalankan di step berbeda dari yang set env var. Periksa urutan step di workflow — env var harus di-set sebelum step render.

### Workflow gagal "Resource not accessible by integration"
PAT tidak punya izin `Contents: Read and write`. Generate PAT baru dengan permission yang benar, atau pastikan classic PAT punya scope `public_repo` + `workflow`.

### Cards tidak update di portfolio setelah workflow sukses
GitHub Pages butuh ~30-60 detik untuk rebuild. Tunggu, lalu hard-refresh browser (Ctrl+Shift+R).

### Workflow jalan tapi tidak ada perubahan (commit)
Ini normal — kalau isi `projects-grid` sudah sama dengan render terbaru, workflow skip commit (cek log: "No changes to commit").

### Rate limit GitHub API
Workflow pakai PAT Anda, jadi limit 5000/jam. Cukup untuk 1× jalan/hari. Kalau Anda tambah schedule lebih sering, monitor usage.

---

## Security notes

- **PAT disimpan sebagai secret**, tidak pernah di-expose di logs.
- Workflow hanya baca repo publik — tidak pernah akses repo private.
- Workflow push ke 1 repo saja (`Zigha08.github.io`), sesuai permission yang di-set di PAT.
- Kalau PAT bocor, **segera revoke** di https://github.com/settings/tokens dan generate yang baru.
- Untuk rotasi berkala, set expiration 90 hari di step 1 dan ulang tiap 3 bulan.
