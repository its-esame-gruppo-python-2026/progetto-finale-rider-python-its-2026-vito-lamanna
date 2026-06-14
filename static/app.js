// ─────────────────────────────────────────────────────────
//  RIDERS DASHBOARD — app.js
//  Gestione stato, chiamate API, animazioni, interazioni
// ─────────────────────────────────────────────────────────

const API = {
  listRiders:    (vehicle = '') => `/riders/list_rider${vehicle ? `?vehicle=${vehicle}` : ''}`,
  insertRider:   () => `/riders/insert_rider`,
  deleteRider:   (id) => `/riders/delete_rider/${id}`,
  insertReview:  () => `/riders/insert_review`,
  updateReview:  () => `/riders/update_review`,
  mediaVoti:     (id) => `/riders/media_voti/${id}`,
};

// ── State ─────────────────────────────────────────────────
const state = {
  riders: [],
  currentSection: 'riders',
  currentFilter: '',
  totalRiders: 0,
};

// ── Toast ─────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon"></span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('hide');
    toast.addEventListener('animationend', () => toast.remove());
  }, 3500);
}

// ── Navigation ────────────────────────────────────────────
function navigateTo(section) {
  if (state.currentSection === section) return;
  state.currentSection = section;

  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.section === section);
  });

  if (document.startViewTransition) {
    document.startViewTransition(() => renderSection(section));
  } else {
    renderSection(section);
  }
}

function renderSection(section) {
  const main = document.getElementById('main-content');
  const headerTitle = document.getElementById('header-title');
  const headerSub   = document.getElementById('header-sub');

  switch (section) {
    case 'riders':
      headerTitle.textContent = 'Riders';
      headerSub.textContent = 'Gestione e filtraggio';
      renderRiders(main);
      break;
  }
}

// ── Fetch helpers ─────────────────────────────────────────
async function apiFetch(url, options = {}) {
  const method = options.method || 'GET';
  let bodyData = null;
  try { if (options.body) bodyData = JSON.parse(options.body); } catch (e) {}
  
  let res, data, isError = false;
  
  try {
    res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    data = await res.json();
    if (!res.ok) isError = true;
  } catch (e) {
    isError = true;
    data = { "Errore connessione": e.message };
  }
  
  logToApiMonitor(method, url, bodyData, res ? res.status : 'ERR', data, isError);

  if (isError) {
    throw new Error(data?.Errore || data?.['Errore validazione dati'] || JSON.stringify(data));
  }
  
  return data;
}

// ── API Monitor ───────────────────────────────────────────
function toggleApiMonitor() {
  const monitor = document.getElementById('api-monitor');
  if (monitor) monitor.classList.toggle('collapsed');
}

function clearApiLogs(event) {
  event.stopPropagation();
  const container = document.getElementById('api-logs-container');
  if (container) {
    container.innerHTML = '<div class="api-log-empty">In attesa di richieste API...</div>';
  }
}

function logToApiMonitor(method, url, reqBody, status, resBody, isError) {
  const container = document.getElementById('api-logs-container');
  if (!container) return;
  
  const emptyMsg = container.querySelector('.api-log-empty');
  if (emptyMsg) emptyMsg.remove();
  
  const entry = document.createElement('div');
  entry.className = 'api-log-entry';
  
  const statusClass = isError ? 'error' : 'success';
  const reqBodyHtml = reqBody ? `<div class="api-log-body">${JSON.stringify(reqBody, null, 2)}</div>` : '';
  const resBodyHtml = resBody ? `<div class="api-log-body">${JSON.stringify(resBody, null, 2)}</div>` : '';
  
  entry.innerHTML = `
    <div class="api-log-req">[${method}] ${url}</div>
    ${reqBodyHtml}
    <div class="api-log-res">
      Status: <span class="api-log-status ${statusClass}">${status}</span>
    </div>
    ${resBodyHtml}
  `;
  
  container.prepend(entry);
}

// ── Riders ────────────────────────────────────────────────
async function renderRiders(container) {
  const vehicles = ['', 'auto', 'moto', 'scooter', 'bicicletta', 'furgone'];
  const vehicleLabels = { '': 'Tutti', auto: '🚗 Auto', moto: '🏍️ Moto', scooter: '🛵 Scooter', bicicletta: '🚲 Bici', furgone: '🚐 Furgone' };

  container.innerHTML = `
    <div class="section-header">
      <div>
        <div class="section-title">Lista Riders</div>
        <div class="section-subtitle" id="riders-count">Caricamento...</div>
      </div>
      <button class="btn btn-primary" id="btn-add-rider">
        ＋ Aggiungi Rider
      </button>
    </div>

    <div class="filter-bar" style="margin-bottom:20px">
      ${vehicles.map(v => `
        <button class="filter-chip ${state.currentFilter === v ? 'active' : ''}"
                data-vehicle="${v}">${vehicleLabels[v]}</button>
      `).join('')}
    </div>

    <div id="riders-grid" class="riders-grid">
      <div class="loading"><div class="spinner"></div> Caricamento riders...</div>
    </div>
  `;

  // Filter chips
  container.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      state.currentFilter = chip.dataset.vehicle;
      container.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      loadRidersGrid(container.querySelector('#riders-grid'));
    });
  });

  // Add rider button
  container.querySelector('#btn-add-rider').addEventListener('click', openAddRiderDialog);

  await loadRidersGrid(container.querySelector('#riders-grid'));
}

async function loadRidersGrid(gridEl) {
  gridEl.innerHTML = `<div class="loading"><div class="spinner"></div> Caricamento...</div>`;
  try {
    const data = await apiFetch(API.listRiders(state.currentFilter));
    const riders = data.Risultati || [];
    state.riders = riders;

    const countEl = document.getElementById('riders-count');
    if (countEl) countEl.textContent = `${riders.length} rider${riders.length !== 1 ? 's' : ''} trovati`;

    // Update nav badge
    const badge = document.getElementById('riders-badge');
    if (badge) badge.textContent = riders.length;

    if (!riders.length) {
      gridEl.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
        <div class="empty-state-icon">🏍️</div>
        <div class="empty-state-title">Nessun rider trovato</div>
        <p>Prova a cambiare il filtro o aggiungi un nuovo rider</p>
      </div>`;
      return;
    }

    gridEl.innerHTML = riders.map(r => buildRiderCard(r)).join('');

    // Attach delete buttons
    gridEl.querySelectorAll('.btn-delete-rider').forEach(btn => {
      btn.addEventListener('click', () => confirmDeleteRider(btn.dataset.id, btn.dataset.name, gridEl));
    });
    
    // Attach media voti buttons
    gridEl.querySelectorAll('.btn-media-voti').forEach(btn => {
      btn.addEventListener('click', () => fetchMediaVoti(btn.dataset.id, btn.dataset.name));
    });

  } catch (err) {
    gridEl.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <div class="empty-state-icon">⚠️</div>
      <div class="empty-state-title">Errore</div><p>${err.message}</p>
    </div>`;
  }
}

function buildRiderCard(r) {
  const vehicleIcons = { auto: '🚗', moto: '🏍️', scooter: '🛵', bicicletta: '🚲', furgone: '🚐' };
  const stars = Array.from({ length: 5 }, (_, i) =>
    `<span class="star ${i < Math.round(r.rating_average) ? 'filled' : ''}">★</span>`
  ).join('');

  const vehicleType = r.vehicle ? r.vehicle.toLowerCase() : 'moto';
  const imgUrl = `/static/avatar_${vehicleType}.png`;

  return `
    <div class="rider-card">
      <div class="rider-card-header">
        <img src="${imgUrl}" alt="Avatar" class="rider-avatar" style="object-fit:cover; border: 2px solid var(--accent); padding: 2px;">
        <div>
          <div class="rider-name">${r.name}</div>
          <div class="rider-id">#${r.id}</div>
        </div>
        <span class="vehicle-badge ${r.vehicle}">${vehicleIcons[r.vehicle] || ''} ${r.vehicle}</span>
      </div>

      <div class="rider-stats">
        <div class="rider-stat">
          <span class="rider-stat-label">Consegne</span>
          <span class="rider-stat-value">${r.total_deliveries}</span>
        </div>
        <div class="rider-stat">
          <span class="rider-stat-label">Rating</span>
          <span class="rider-stat-value">${r.rating_average > 0 ? r.rating_average : '—'}</span>
        </div>
        <div class="rider-stat">
          <span class="rider-stat-label">Recensioni</span>
          <span class="rider-stat-value">${r.total_reviews}</span>
        </div>
      </div>

      <div class="rider-card-footer" style="flex-wrap: wrap; gap: 8px;">
        <button class="btn btn-primary btn-sm" onclick="openAddReviewModal(${r.id}, '${r.name.replace(/'/g, "\\'")}')" style="width:100%; justify-content:center; margin-bottom:4px;">
          ⭐ Lascia Recensione
        </button>
        <button class="btn btn-secondary btn-sm btn-media-voti" data-id="${r.id}" data-name="${r.name}" style="flex:1; justify-content:center;">
          📊 Media Voti
        </button>
        <button class="btn btn-danger btn-sm btn-delete-rider" data-id="${r.id}" data-name="${r.name}" style="flex:1; justify-content:center;">
          🗑 Elimina
        </button>
      </div>
    </div>
  `;
}

// ── Add Rider Dialog ──────────────────────────────────────
function openAddRiderDialog() {
  const dialog = document.getElementById('dialog-add-rider');
  dialog.querySelector('form').reset();
  dialog.showModal();
}

async function submitAddRider() {
  const form = document.getElementById('form-add-rider');
  const name = form.querySelector('#input-name').value.trim();
  const vehicle = form.querySelector('#input-vehicle').value;
  const deliveries = parseInt(form.querySelector('#input-deliveries').value) || 0;



  const btn = document.getElementById('btn-submit-rider');
  btn.disabled = true;
  btn.textContent = 'Salvataggio...';

  try {
    await apiFetch(API.insertRider(), {
      method: 'POST',
      body: JSON.stringify({ name, vehicle, total_deliveries: deliveries }),
    });
    document.getElementById('dialog-add-rider').close();
    showToast(`Rider "${name}" aggiunto con successo!`, 'success');
    if (state.currentSection === 'riders') {
      const grid = document.getElementById('riders-grid');
      if (grid) await loadRidersGrid(grid);
    }
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Aggiungi Rider';
  }
}

// ── Delete Rider ──────────────────────────────────────────
function confirmDeleteRider(id, name, gridEl) {
  const dialog = document.getElementById('dialog-confirm');
  dialog.querySelector('.confirm-text').innerHTML =
    `Vuoi eliminare il rider <strong>${name}</strong> (#${id})?<br>
     <small style="color:var(--danger)">Questa azione eliminerà anche tutte le sue recensioni.</small>`;

  const confirmBtn = dialog.querySelector('#btn-confirm-ok');
  confirmBtn.onclick = async () => {
    dialog.close();
    try {
      await apiFetch(API.deleteRider(id), { method: 'DELETE' });
      showToast(`Rider "${name}" eliminato`, 'success');
      await loadRidersGrid(gridEl);
    } catch (err) {
      showToast(err.message, 'error');
    }
  };
  dialog.showModal();
}

// ── Reviews ───────────────────────────────────────────────

function openAddReviewModal(riderId, riderName) {
  const dialog = document.getElementById('dialog-add-review');
  dialog.querySelector('form').reset();
  document.getElementById('modal-rev-rider-id').value = riderId;
  document.getElementById('dialog-review-subtitle').innerHTML = `Stai recensendo il rider <strong>${riderName}</strong> (#${riderId})`;
  dialog.showModal();
}

async function submitModalReview() {
  const riderId  = parseInt(document.getElementById('modal-rev-rider-id').value);
  const customer = document.getElementById('modal-rev-customer').value.trim();
  const rating   = parseInt(document.querySelector('input[name="modal-rating"]:checked')?.value);
  const comment  = document.getElementById('modal-rev-comment').value.trim() || null;



  const btn = document.getElementById('btn-submit-modal-review');
  btn.disabled = true; btn.textContent = 'Invio...';

  try {
    await apiFetch(API.insertReview(), {
      method: 'POST',
      body: JSON.stringify({ rider_id: riderId, customer_name: customer, rating, comment }),
    });
    document.getElementById('dialog-add-review').close();
    showToast('Recensione aggiunta con successo!', 'success');
    if (state.currentSection === 'riders') {
      const grid = document.getElementById('riders-grid');
      if (grid) await loadRidersGrid(grid);
    }
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = '✉️ Invia Recensione';
  }
}



async function fetchMediaVoti(id, name) {
  try {
    const data = await apiFetch(API.mediaVoti(id));
    if (data.messaggio) {
      showToast(`${name}: ${data.messaggio}`, 'info');
    } else {
      showToast(`Media voti per ${name}: ⭐ ${data.media_voti}`, 'info');
    }
  } catch (err) {
    showToast(`Errore: ${err.message}`, 'error');
  }
}

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Nav click
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigateTo(item.dataset.section));
  });

  // Dialog close on backdrop click
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.addEventListener('click', e => {
      const rect = dialog.getBoundingClientRect();
      if (e.clientX < rect.left || e.clientX > rect.right ||
          e.clientY < rect.top  || e.clientY > rect.bottom) {
        dialog.close();
      }
    });
  });

  // Confirm cancel
  document.getElementById('btn-confirm-cancel')?.addEventListener('click', () => {
    document.getElementById('dialog-confirm').close();
  });

  // Render initial section
  renderSection('riders');
});
