(function() {
  var STORAGE_KEY = 'desidwarfs-dark-mode';
  // Theme class lives on <html> (document.documentElement) so the pre-paint
  // guard in each page's <head> can apply it before <body> exists.
  var root = document.documentElement;

  function isDark() {
    return root.classList.contains('dark-mode');
  }

  function setDark(enabled) {
    if (enabled) {
      root.classList.add('dark-mode');
      try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    } else {
      root.classList.remove('dark-mode');
      try { localStorage.setItem(STORAGE_KEY, '0'); } catch (e) {}
    }
    updateButton();
    // Notify theme-aware components (e.g. Plotly charts) to restyle in place
    // without losing zoom/pan or re-fetching data.
    try {
      window.dispatchEvent(new CustomEvent('themechange', { detail: { dark: enabled } }));
    } catch (e) {}
  }

  function toggle() {
    setDark(!isDark());
  }

  function updateButton() {
    var btn = document.getElementById('dark-mode-toggle-btn');
    if (!btn) return;
    btn.setAttribute('aria-label', isDark() ? 'Switch to light mode' : 'Switch to dark mode');
    btn.setAttribute('title', isDark() ? 'Switch to light mode' : 'Switch to dark mode');
    btn.textContent = isDark() ? '☼' : '☾';  /* sun / moon */
  }

  function init() {
    // The pre-paint guard in <head> normally applies the saved theme already;
    // re-read here as a fallback in case a page is missing the guard.
    var saved = null;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (saved === '1') {
      root.classList.add('dark-mode');
    }

    var btn = document.createElement('button');
    btn.id = 'dark-mode-toggle-btn';
    btn.className = 'dark-mode-toggle';
    btn.setAttribute('aria-label', isDark() ? 'Switch to light mode' : 'Switch to dark mode');
    btn.setAttribute('title', isDark() ? 'Switch to light mode' : 'Switch to dark mode');
    btn.textContent = isDark() ? '☼' : '☾';
    btn.onclick = toggle;
    document.body.appendChild(btn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
