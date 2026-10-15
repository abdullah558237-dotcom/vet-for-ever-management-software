'use strict';
document.addEventListener('DOMContentLoaded', () => {
  // ── Active link highlighting (sidebar + bottom nav) ────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.side-link, .bottom-nav a').forEach(link => {
    if (link.getAttribute('href') && link.getAttribute('href') !== '#') {
      if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
      }
    }
  });
  // ── Auto-dismiss alerts after 4 s ─────────────────────────
  document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 4000);
  });
  // ── Confirm on logout form (optional UX) ──────────────────
  const logoutForm = document.querySelector('form[action*="logout"]');
  if (logoutForm) {
