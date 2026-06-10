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
