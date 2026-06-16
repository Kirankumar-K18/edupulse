/* Smart Lecturer Review System — main.js */
'use strict';

// ─── THEME TOGGLE ──────────────────────────────────────────────────
(function () {
  const html  = document.documentElement;
  const btn   = document.getElementById('themeToggle');
  const icon  = document.getElementById('themeIcon');
  const saved = localStorage.getItem('theme') || 'light';

  function applyTheme(t) {
    html.setAttribute('data-bs-theme', t);
    if (icon) {
      icon.className = t === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
    localStorage.setItem('theme', t);
  }

  applyTheme(saved);

  btn?.addEventListener('click', () => {
    const current = html.getAttribute('data-bs-theme');
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });
})();

// ─── CSRF HELPER ───────────────────────────────────────────────────
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.content;
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

// ─── CONFIRM DELETE ────────────────────────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    const msg = el.dataset.confirm || 'Are you sure?';
    if (!confirm(msg)) e.preventDefault();
  });
});

// ─── STAR RATING UI ────────────────────────────────────────────────
document.querySelectorAll('.star-rating-input').forEach(container => {
  const stars = container.querySelectorAll('.star-btn');
  const input = container.querySelector('input[type="hidden"]');

  stars.forEach((star, idx) => {
    star.addEventListener('mouseenter', () => highlightStars(stars, idx));
    star.addEventListener('mouseleave', () => highlightStars(stars, (input?.value || 0) - 1));
    star.addEventListener('click', () => {
      if (input) input.value = idx + 1;
      highlightStars(stars, idx);
    });
  });

  function highlightStars(stars, upTo) {
    stars.forEach((s, i) => {
      s.querySelector('i').className = i <= upTo ? 'bi bi-star-fill text-warning' : 'bi bi-star text-secondary';
    });
  }
});

// ─── AUTO-DISMISS ALERTS ───────────────────────────────────────────
setTimeout(() => {
  document.querySelectorAll('.alert.auto-dismiss').forEach(el => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
    bsAlert.close();
  });
}, 4000);

// ─── ATTENDANCE FORM: SELECT ALL / DESELECT ALL ───────────────────
const selectAll = document.getElementById('selectAllPresent');
if (selectAll) {
  selectAll.addEventListener('change', () => {
    document.querySelectorAll('.att-status-select').forEach(sel => {
      sel.value = selectAll.checked ? 'present' : 'absent';
    });
  });
}

// ─── ARQ ANIMATION ─────────────────────────────────────────────────
window.animateARQ = function (events, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';
  const icons = {
    send:       { cls: 'send',       icon: 'bi-send-fill',         label: 'SEND' },
    ack:        { cls: 'ack',        icon: 'bi-check-circle-fill', label: 'ACK' },
    timeout:    { cls: 'timeout',    icon: 'bi-clock-fill',        label: 'TIMEOUT' },
    retransmit: { cls: 'retransmit', icon: 'bi-arrow-repeat',      label: 'RETRANSMIT' },
    drop:       { cls: 'drop',       icon: 'bi-x-circle-fill',     label: 'DROP' },
    success:    { cls: 'success',    icon: 'bi-patch-check-fill',  label: 'SUCCESS' },
  };
  events.forEach((ev, i) => {
    const meta = icons[ev.event_type] || { cls: '', icon: 'bi-circle', label: ev.event_type };
    const div = document.createElement('div');
    div.className = `arq-event ${meta.cls}`;
    div.style.opacity = '0';
    div.style.transition = 'opacity .3s';
    div.innerHTML = `
      <i class="bi ${meta.icon} arq-event-icon"></i>
      <div>
        <span class="fw-500">[P${ev.packet_number}]</span>
        <span class="badge bg-secondary ms-1">${meta.label}</span>
        <span class="ms-1">${ev.message}</span>
      </div>
      <span class="arq-event-time">+${ev.timestamp_ms}ms</span>
    `;
    container.appendChild(div);
    setTimeout(() => { div.style.opacity = '1'; }, i * 80);
  });
};
