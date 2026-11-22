// Optional extras for the pre-rendered portfolio. The page works without this file.
(function () {
  var LIGHT = {
      "--color-bg": "#e4e7f5", "--color-surface": "#f3f5fe", "--color-text": "#292b31", "--color-accent": "#5d5294",
      "--color-divider": "color-mix(in srgb, #292b31 18%, transparent)",
      "--color-neutral-100": "#292b31", "--color-neutral-200": "#292b31", "--color-neutral-300": "#3f424d", "--color-neutral-400": "#595d6c",
      "--color-neutral-500": "#75798c", "--color-neutral-600": "#9397ab", "--color-neutral-700": "#b2b6ca", "--color-neutral-800": "#d6d9ea", "--color-neutral-900": "#cfd3e5",
      "--color-accent-100": "#2b2741", "--color-accent-200": "#423a6a", "--color-accent-300": "#5d5294", "--color-accent-400": "#796cbf",
      "--color-accent-500": "#968ae0", "--color-accent-600": "#b5abfc", "--color-accent-700": "#d2cefd", "--color-accent-800": "#e1defb", "--color-accent-900": "#f5f4ff",
      "--shadow-sm": "0 0 0 1px #cfd3e5", "--shadow-md": "0 0 0 1px #b2b6ca, 0 6px 18px rgba(41,43,49,0.12)", "--shadow-lg": "0 0 0 1px #9397ab, 0 16px 40px rgba(41,43,49,0.2)"
    };
  var root = document.documentElement;
  root.classList.add('js');
  function apply(t) {
    Object.keys(LIGHT).forEach(function (k) {
      if (t === 'light') root.style.setProperty(k, LIGHT[k]); else root.style.removeProperty(k);
    });
    root.style.colorScheme = t;
    var b = document.querySelector('[data-theme-toggle]');
    if (b) {
      var label = t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
      b.setAttribute('aria-label', label); b.setAttribute('title', label);
      var i = b.querySelector('i');
      if (i) { i.classList.remove('ph-sun', 'ph-moon'); i.classList.add(t === 'dark' ? 'ph-sun' : 'ph-moon'); }
    }
  }
  var theme = null;
  try { theme = localStorage.getItem('mt-theme'); } catch (e) {}
  if (!theme) theme = window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  apply(theme);

  // Old links to an open panel (#project-<id>) now go to that project's page.
  var m = location.hash.match(/^#project-([\w-]+)$/);
  if (m && !/\/projects\//.test(location.pathname)) location.replace('projects/' + m[1] + '.html');

  document.addEventListener('DOMContentLoaded', function () {
    apply(theme);
    var b = document.querySelector('[data-theme-toggle]');
    if (b) b.addEventListener('click', function () {
      theme = theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('mt-theme', theme); } catch (e) {}
      apply(theme);
    });
    var c = document.querySelector('[data-copy-email]');
    if (c) c.addEventListener('click', function () {
      var a = document.querySelector('a[href^="mailto:"]');
      var addr = a ? a.getAttribute('href').replace('mailto:', '') : '';
      if (!addr || !navigator.clipboard) return;
      navigator.clipboard.writeText(addr).then(function () {
        var s = c.querySelector('span'); if (s) s.textContent = 'Copied';
        var live = document.querySelector('[aria-live]'); if (live) live.textContent = 'Email address copied';
        setTimeout(function () { if (s) s.textContent = 'Copy address'; }, 2000);
      });
    });
  });
})();
