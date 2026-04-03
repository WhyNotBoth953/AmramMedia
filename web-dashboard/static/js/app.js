let downloadInterval = null;

// Tab routing
window.addEventListener('hashchange', route);
window.addEventListener('DOMContentLoaded', route);

function route() {
    // Clear auto-refresh if leaving downloads tab
    if (downloadInterval) {
        clearInterval(downloadInterval);
        downloadInterval = null;
    }

    const tab = location.hash.slice(1) || 'dashboard';
    document.querySelectorAll('nav a').forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === `#${tab}`);
    });

    const content = document.getElementById('content');
    content.innerHTML = '<div class="loading">Loading...</div>';

    switch (tab) {
        case 'dashboard': renderDashboard(); break;
        case 'movies': renderMovies(); break;
        case 'series': renderSeries(); break;
        case 'downloads': renderDownloads(); break;
        case 'wishlist': renderWishlist(); break;
        case 'search': renderSearch(); break;
        default: renderDashboard();
    }
}

// Dashboard
async function renderDashboard() {
    const content = document.getElementById('content');
    try {
        const [dash, upcoming, subs] = await Promise.all([
            fetch('/api/dashboard').then(r => r.json()),
            fetch('/api/upcoming?days=7').then(r => r.json()),
            fetch('/api/subtitles/wanted').then(r => r.json()).catch(() => null),
        ]);

        let html = '<div class="stats-grid">';
        html += statCard('Movies', dash.movies.total, `${dash.movies.downloaded} downloaded`);
        html += statCard('Series', dash.series.total, `${dash.series.downloadedEpisodes}/${dash.series.totalEpisodes} episodes`);
        html += statCard('Downloads', dash.downloads.active, `↓ ${formatSpeed(dash.transfer.downloadSpeed)}`);
        html += statCard('Disk Used', `${dash.disk.percent}%`, `${formatSize(dash.disk.free)} free`);
        if (subs && !subs.error) {
            html += statCard('Missing Subs', subs.wantedMovies + subs.wantedEpisodes, `${subs.wantedMovies} movies · ${subs.wantedEpisodes} episodes`);
        }
        html += '</div>';

        // Disk bar
        html += `
            <div class="section">
                <h2>Storage</h2>
                <div>${formatSize(dash.disk.used)} / ${formatSize(dash.disk.total)}</div>
                <div class="disk-bar"><div class="fill" style="width:${dash.disk.percent}%"></div></div>
            </div>`;

        // Upcoming
        if (upcoming.length > 0) {
            html += '<div class="section"><h2>Upcoming Episodes</h2>';
            html += upcoming.map(upcomingItem).join('');
            html += '</div>';
        }

        content.innerHTML = html;
    } catch (e) {
        content.innerHTML = `<div class="empty">Failed to load dashboard: ${e.message}</div>`;
    }
}

// Movies
async function renderMovies() {
    const content = document.getElementById('content');
    try {
        const movies = await fetch('/api/movies').then(r => r.json());
        let html = `
            <div class="toolbar">
                <h2>Movies (${movies.length})</h2>
                <input type="text" class="filter-input" placeholder="Filter..." oninput="filterCards(this.value)">
            </div>
            <div class="card-grid">`;
        html += movies.map(movieCard).join('');
        html += '</div>';
        content.innerHTML = html;
    } catch (e) {
        content.innerHTML = `<div class="empty">Failed to load movies: ${e.message}</div>`;
    }
}

// Series
async function renderSeries() {
    const content = document.getElementById('content');
    try {
        const series = await fetch('/api/series').then(r => r.json());
        let html = `
            <div class="toolbar">
                <h2>Series (${series.length})</h2>
                <input type="text" class="filter-input" placeholder="Filter..." oninput="filterCards(this.value)">
            </div>
            <div class="card-grid">`;
        html += series.map(seriesCard).join('');
        html += '</div>';
        content.innerHTML = html;
    } catch (e) {
        content.innerHTML = `<div class="empty">Failed to load series: ${e.message}</div>`;
    }
}

// Downloads (auto-refreshes every 5s)
async function renderDownloads() {
    await updateDownloads();
    downloadInterval = setInterval(updateDownloads, 5000);
}

async function updateDownloads() {
    const content = document.getElementById('content');
    try {
        const data = await fetch('/api/downloads').then(r => r.json());
        let html = `
            <div class="toolbar">
                <h2>Active Downloads (${data.items.length})</h2>
                <div style="color:var(--text-muted);font-size:0.85rem">
                    ↓ ${formatSpeed(data.globalDownloadSpeed)} · ↑ ${formatSpeed(data.globalUploadSpeed)}
                </div>
            </div>`;

        if (data.items.length === 0) {
            html += '<div class="empty">No active downloads</div>';
        } else {
            html += data.items.map(downloadItem).join('');
        }
        content.innerHTML = html;
    } catch (e) {
        content.innerHTML = `<div class="empty">Failed to load downloads: ${e.message}</div>`;
    }
}

// Search
function renderSearch() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="search-bar">
            <input type="text" id="search-input" placeholder="Search movies & series..." autofocus>
            <button onclick="doSearch()">Search</button>
        </div>
        <div id="search-results"></div>`;

    document.getElementById('search-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') doSearch();
    });
}

async function doSearch() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;

    const results = document.getElementById('search-results');
    results.innerHTML = '<div class="loading">Searching...</div>';

    try {
        const data = await fetch(`/api/search?q=${encodeURIComponent(query)}`).then(r => r.json());
        if (data.length === 0) {
            results.innerHTML = '<div class="empty">No results found</div>';
        } else {
            results.innerHTML = data.map(searchResultCard).join('');
        }
    } catch (e) {
        results.innerHTML = `<div class="empty">Search failed: ${e.message}</div>`;
    }
}

// Wishlist
async function renderWishlist() {
    const content = document.getElementById('content');
    try {
        const items = await fetch('/api/wishlist').then(r => r.json());
        let html = `
            <div class="toolbar">
                <h2>Wishlist (${items.length})</h2>
                <input type="text" class="filter-input" placeholder="Filter..." oninput="filterCards(this.value)">
            </div>`;
        if (items.length === 0) {
            html += '<div class="empty">Wishlist is empty. Use Search to add items.</div>';
        } else {
            html += '<div class="card-grid">';
            html += items.map(wishlistCard).join('');
            html += '</div>';
        }
        content.innerHTML = html;
    } catch (e) {
        content.innerHTML = `<div class="empty">Failed to load wishlist: ${e.message}</div>`;
    }
}

async function wishlistDownload(type, id, btn) {
    btn.disabled = true;
    btn.textContent = 'Starting...';
    try {
        const resp = await fetch(`/api/wishlist/${type}/${id}/download`, { method: 'POST' });
        if (resp.ok) {
            const card = btn.closest('.media-card');
            if (card) card.remove();
            const countEl = document.querySelector('.toolbar h2');
            if (countEl) {
                const remaining = document.querySelectorAll('.media-card').length;
                countEl.textContent = `Wishlist (${remaining})`;
            }
        } else {
            btn.textContent = 'Failed';
            btn.disabled = false;
        }
    } catch (e) {
        btn.textContent = 'Failed';
        btn.disabled = false;
    }
}

function wishlistRemove(type, id, title) {
    showModal(
        `Remove ${title}?`,
        'This will remove it from your wishlist (no files will be deleted).',
        async () => {
            try {
                await fetch(`/api/wishlist/${type}/${id}`, { method: 'DELETE' });
                const card = document.querySelector(`.media-card[data-id="${id}"][data-type="${type}"]`);
                if (card) card.remove();
            } catch (e) {
                alert(`Remove failed: ${e.message}`);
            }
        }
    );
}

// Add media from search results (adds to wishlist)
async function addMedia(type, id, btn) {
    btn.disabled = true;
    btn.textContent = 'Adding...';
    const endpoint = type === 'movie' ? '/api/movies' : '/api/series';
    const body = type === 'movie' ? { tmdbId: id } : { tvdbId: id };

    try {
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (resp.ok) {
            btn.textContent = 'Wishlisted!';
            btn.className = 'btn btn-sm';
            btn.style.background = 'var(--success)';
        } else {
            const err = await resp.json();
            btn.textContent = err.detail || 'Error';
            btn.style.background = 'var(--warning)';
            btn.disabled = false;
        }
    } catch (e) {
        btn.textContent = 'Failed';
        btn.disabled = false;
    }
}

// Delete confirmation
function confirmDelete(id, type, title) {
    showModal(
        `Delete ${title}?`,
        'This will remove the item and all associated files from disk.',
        async () => {
            const endpoint = type === 'movie' ? `/api/movies/${id}` : `/api/series/${id}`;
            try {
                await fetch(endpoint, { method: 'DELETE' });
                // Remove card from DOM
                const card = document.querySelector(`.media-card[data-id="${id}"][data-type="${type}"]`);
                if (card) card.remove();
            } catch (e) {
                alert(`Delete failed: ${e.message}`);
            }
        }
    );
}

// Filter cards by title
function filterCards(query) {
    const q = query.toLowerCase();
    document.querySelectorAll('.media-card').forEach(card => {
        const title = card.querySelector('.title')?.textContent?.toLowerCase() || '';
        card.style.display = title.includes(q) ? '' : 'none';
    });
}
