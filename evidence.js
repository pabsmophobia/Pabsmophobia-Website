async function loadEvidenceVault() {
  const gridContainer = document.getElementById('evidence-grid');
  
  try {
    const response = await fetch('evidence-data.json');
    const evidenceList = await response.json();

    if (!evidenceList || evidenceList.length === 0) {
      gridContainer.innerHTML = '<p>No evidence entries found.</p>';
      return;
    }

    // Store evidence globally for filtering
    window.allEvidence = evidenceList;
    renderEvidence(evidenceList);
    setupFilters();
    setupAdvancedFilters();

  } catch (err) {
    console.error('Error loading evidence:', err);
    gridContainer.innerHTML = '<p>Unable to load evidence vault.</p>';
  }
}

function renderEvidence(evidenceList) {
  const gridContainer = document.getElementById('evidence-grid');
  
  gridContainer.innerHTML = evidenceList.map(item => {
    const statusClass = item.status === 'debunked' ? 'badge-debunked' : 'badge-paranormal';
    const statusLabel = item.status === 'debunked' ? 'Debunked' : 'Unexplained';

    const mediaMarkup = item.mediaUrl ? `
      <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 6px; margin: 1rem 0; background: #000;">
        <iframe 
          src="${item.mediaUrl}" 
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
          allowfullscreen>
        </iframe>
      </div>` : '';

    return `
      <article class="card" data-type="${item.type}" data-status="${item.status}" data-location="${item.location}" data-date="${item.date}" style="border: 1px solid #333; padding: 1rem; border-radius: 8px; background: #181818; text-align: left;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span class="badge ${statusClass}" style="padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; text-transform: uppercase; font-weight: bold;">${statusLabel}</span>
          <span style="font-size: 0.8rem; color: #888;">${item.date}</span>
        </div>
        <h3 style="margin: 0.75rem 0 0.25rem 0; color: #fff;">${item.title}</h3>
        <p style="font-size: 0.85rem; color: #aaa; margin: 0;">📍 ${item.location}</p>
        ${mediaMarkup}
        <p style="font-size: 0.9rem; line-height: 1.4; color: #ccc;">${item.description}</p>
      </article>
    `;
  }).join('');
}

function setupFilters() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      filterBtns.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');

      const filter = e.target.getAttribute('data-filter');
      const cards = document.querySelectorAll('#evidence-grid .card');

      cards.forEach(card => {
        const type = card.getAttribute('data-type');
        const status = card.getAttribute('data-status');

        if (filter === 'all' || type === filter || status === filter) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

function setupAdvancedFilters() {
  const searchInput = document.getElementById('evidence-search');
  const locationFilter = document.getElementById('location-filter');
  const statusFilter = document.getElementById('status-filter');
  
  if (searchInput) {
    searchInput.addEventListener('input', applyAdvancedFilters);
  }
  if (locationFilter) {
    locationFilter.addEventListener('change', applyAdvancedFilters);
    populateLocationFilter();
  }
  if (statusFilter) {
    statusFilter.addEventListener('change', applyAdvancedFilters);
  }
}

function populateLocationFilter() {
  const locationFilter = document.getElementById('location-filter');
  if (!locationFilter || !window.allEvidence) return;
  
  const locations = [...new Set(window.allEvidence.map(item => item.location))].sort();
  
  locations.forEach(location => {
    const option = document.createElement('option');
    option.value = location;
    option.textContent = location;
    locationFilter.appendChild(option);
  });
}

function applyAdvancedFilters() {
  const searchTerm = (document.getElementById('evidence-search')?.value || '').toLowerCase();
  const selectedLocation = document.getElementById('location-filter')?.value || '';
  const selectedStatus = document.getElementById('status-filter')?.value || '';
  
  const cards = document.querySelectorAll('#evidence-grid .card');
  
  cards.forEach(card => {
    const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
    const description = card.textContent.toLowerCase();
    const location = card.getAttribute('data-location') || '';
    const status = card.getAttribute('data-status') || '';
    
    const matchesSearch = searchTerm === '' || title.includes(searchTerm) || description.includes(searchTerm);
    const matchesLocation = selectedLocation === '' || location === selectedLocation;
    const matchesStatus = selectedStatus === '' || status === selectedStatus;
    
    card.style.display = (matchesSearch && matchesLocation && matchesStatus) ? 'block' : 'none';
  });
}

document.addEventListener('DOMContentLoaded', loadEvidenceVault);
