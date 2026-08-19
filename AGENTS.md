# funny

Korean stock-market lecture notes. `scripts/generate_aug18_lecture.py` builds a
styled Word document (`.docx`) with `python-docx` and writes it into `lectures/`.

## Cursor Cloud specific instructions

- This is a script-based project, not a long-running service. The "app" is the
  generator in `scripts/`, run with `python3 scripts/generate_aug18_lecture.py`.
- Only dependency is `python-docx` (see `requirements.txt`); `pip install` uses a
  user-site install here (system site-packages are not writeable) — this is
  expected and works fine.
- `scripts/generate_aug18_lecture.py` writes to an absolute path
  (`/workspace/lectures/...`), so run it from the repo checked out at `/workspace`.
- The committed `.docx` under `lectures/` is a generated artifact. Regenerating it
  changes only zip timestamps (binary diff, same content), so do not commit that
  re-run unless the document content actually changed.
- There are no automated tests, lint config, or build step in this repo.
