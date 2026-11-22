# mthompsen.github.io

Personal blog, built with [Jekyll](https://jekyllrb.com/) and the
[minima](https://github.com/jekyll/minima) theme, deployed to GitHub Pages by
the workflow in `.github/workflows/pages.yml` on every push to `main`.

## Adding a post

1. Copy `_posts/2026-06-10-example-post.md` to a new file named
   `_posts/YYYY-MM-DD-your-title.md` (today's date, hyphenated title).
2. Update the front matter: `title:`, `date:` (must match the filename date),
   and delete the `published: false` line.
3. Write the body in Markdown below the front matter.
4. Commit and push — the site rebuilds and deploys automatically.

## Previewing locally (WSL/Ubuntu)

One-time setup:

```sh
sudo apt install ruby-full build-essential zlib1g-dev
echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
gem install bundler
bundle install          # from the repo root
```

Then to preview:

```sh
bundle exec jekyll serve --unpublished --livereload
```

Open http://127.0.0.1:4000 — `--unpublished` also renders drafts that still
have `published: false`, and `--livereload` refreshes the browser on save.

## Layout

- `/` is the portfolio. `index.html` and `projects/<id>.html` are **pre-rendered static HTML**, so the site
  works with JavaScript turned off. `assets/site.js` only adds extras (theme toggle, copy-email button,
  redirect for old `#project-<id>` links).
- `app.html` is the source page: it renders itself from `data/portfolio.json` with `support.js` and React
  from `lib/` (served locally, no CDN). Edit the data or `app.html`, then regenerate the static pages:

  ```sh
  bundle exec jekyll build
  python3 tools/prerender.py      # needs Google Chrome
  bundle exec jekyll build
  ```

- `/blog/` is the Jekyll blog (minima theme). Posts live at `/blog/YYYY/MM/DD/title.html`; older post URLs
  redirect there through `jekyll-redirect-from`. The feed stays at `/feed.xml`.
