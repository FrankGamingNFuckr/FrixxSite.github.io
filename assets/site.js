(() => {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  const menuButton = document.getElementById('menuButton');

  if (!sidebar || !overlay || !menuButton) return;

  const menuLinks = [...sidebar.querySelectorAll('a[href]')];

  function setSidebarOpen(isOpen) {
    sidebar.classList.toggle('open', isOpen);
    overlay.classList.toggle('open', isOpen);
    overlay.hidden = !isOpen;
    menuButton.setAttribute('aria-expanded', String(isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
    menuButton.textContent = isOpen ? '✕ Close' : '☰ Menu';

    if (isOpen) {
      menuLinks[0]?.focus();
    } else if (sidebar.contains(document.activeElement)) {
      menuButton.focus();
    }
  }

  menuButton.addEventListener('click', () => {
    setSidebarOpen(!sidebar.classList.contains('open'));
  });

  overlay.addEventListener('click', () => setSidebarOpen(false));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      setSidebarOpen(false);
      return;
    }

    if (event.key !== 'Tab' || !sidebar.classList.contains('open') || !menuLinks.length) return;

    const firstLink = menuLinks[0];
    const lastLink = menuLinks[menuLinks.length - 1];
    if (event.shiftKey && document.activeElement === firstLink) {
      event.preventDefault();
      lastLink.focus();
    } else if (!event.shiftKey && document.activeElement === lastLink) {
      event.preventDefault();
      firstLink.focus();
    }
  });

  sidebar.addEventListener('click', (event) => {
    if (event.target instanceof HTMLAnchorElement) setSidebarOpen(false);
  });
})();
