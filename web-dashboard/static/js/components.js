function formatSize(bytes) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    let size = bytes;
    while (Math.abs(size) >= 1024 && i < units.length - 1) {
        size /= 1024;
        i++;
    }
    return `${size.toFixed(1)} ${units[i]}`;
}

function formatSpeed(bytesPerSec) {
    return `${formatSize(bytesPerSec)}/s`;
}

function formatEta(seconds) {
    if (seconds <= 0 || seconds >= 8640000) return '—';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

function statCard(label, value, sub = '') {
    return `
        <div class="stat-card">
            <div class="label">${label}</div>
            <div class="value">${value}</div>
            ${sub ? `<div class="sub">${sub}</div>` : ''}
        </div>`;
}

function movieCard(m) {
    const badge = m.hasFile
        ? '<span class="badge badge-ok">OK</span>'
        : '<span class="badge badge-missing">Missing</span>';
    const poster = m.poster || '';
    const imgTag = poster
        ? `<img src="${poster}" alt="${m.title}" loading="lazy">`
        : `<img src="" alt="${m.title}" style="background:var(--bg-input)">`;
    return `
        <div class="media-card" data-id="${m.id}" data-type="movie">
            <button class="delete-btn" onclick="confirmDelete(${m.id}, 'movie', '${m.title.replace(/'/g, "\\'")}')">✕</button>
            ${badge}
            ${imgTag}
            <div class="info">
                <div class="title" title="${m.title}">${m.title}</div>
                <div class="meta">${m.year} · ${formatSize(m.sizeOnDisk)}</div>
            </div>
        </div>`;
}

function seriesCard(s) {
    const pct = s.totalEpisodes > 0
        ? Math.round(s.downloadedEpisodes / s.totalEpisodes * 100)
        : 0;
    const badge = pct === 100
        ? '<span class="badge badge-ok">Complete</span>'
        : `<span class="badge badge-missing">${s.downloadedEpisodes}/${s.totalEpisodes}</span>`;
    const poster = s.poster || '';
    const imgTag = poster
        ? `<img src="${poster}" alt="${s.title}" loading="lazy">`
        : `<img src="" alt="${s.title}" style="background:var(--bg-input)">`;
    return `
        <div class="media-card" data-id="${s.id}" data-type="series">
            <button class="delete-btn" onclick="confirmDelete(${s.id}, 'series', '${s.title.replace(/'/g, "\\'")}')">✕</button>
            ${badge}
            ${imgTag}
            <div class="info">
                <div class="title" title="${s.title}">${s.title}</div>
                <div class="meta">${s.year} · ${s.seasonCount} seasons</div>
            </div>
        </div>`;
}

function downloadItem(d) {
    return `
        <div class="download-item">
            <div class="name">${d.name}</div>
            <div class="progress-bar">
                <div class="fill" style="width:${d.progress}%"></div>
            </div>
            <div class="details">
                <span>${d.progress}%</span>
                <span>↓ ${formatSpeed(d.downloadSpeed)}</span>
                <span>${formatSize(d.size)}</span>
                <span>ETA: ${formatEta(d.eta)}</span>
            </div>
        </div>`;
}

function wishlistCard(item) {
    const poster = item.poster || '';
    const imgTag = poster
        ? `<img src="${poster}" alt="${item.title}" loading="lazy">`
        : `<img src="" alt="${item.title}" style="background:var(--bg-input)">`;
    const typeLabel = item.type === 'movie' ? 'Movie' : 'Series';
    const extra = item.type === 'series' ? ` · ${item.seasonCount} seasons` : '';
    return `
        <div class="media-card" data-id="${item.id}" data-type="${item.type}">
            <button class="delete-btn" onclick="wishlistRemove('${item.type}', ${item.id}, '${item.title.replace(/'/g, "\\'")}')">✕</button>
            <span class="badge badge-wishlist">${typeLabel}</span>
            ${imgTag}
            <div class="info">
                <div class="title" title="${item.title}">${item.title}</div>
                <div class="meta">${item.year}${extra}</div>
                <button class="btn btn-sm btn-success wishlist-dl-btn" onclick="wishlistDownload('${item.type}', ${item.id}, this)">Download</button>
            </div>
        </div>`;
}

function searchResultCard(item) {
    const poster = item.poster || '';
    const imgTag = poster
        ? `<img src="${poster}" alt="${item.title}" loading="lazy">`
        : `<img src="" alt="${item.title}">`;
    const typeLabel = item.type === 'movie' ? 'Movie' : 'Series';
    const addId = item.type === 'movie' ? item.tmdbId : item.tvdbId;
    const extra = item.type === 'series' ? ` · ${item.seasonCount} seasons` : '';
    return `
        <div class="search-result">
            ${imgTag}
            <div class="result-info">
                <div>
                    <span class="result-title">${item.title}</span>
                    <span class="result-type">${typeLabel}</span>
                </div>
                <div class="result-year">${item.year}${extra}</div>
                <div class="result-overview">${item.overview || ''}</div>
            </div>
            <div class="result-actions">
                <button class="btn btn-sm btn-success" onclick="addMedia('${item.type}', ${addId}, this)">+ Wishlist</button>
                <button class="btn btn-sm btn-download" onclick="downloadMedia('${item.type}', ${addId}, this)">⬇ Download</button>
            </div>
        </div>`;
}

function upcomingItem(ep) {
    return `
        <div class="upcoming-item">
            <div>
                <div class="ep-info">${ep.seriesTitle} — S${String(ep.season).padStart(2,'0')}E${String(ep.episode).padStart(2,'0')}</div>
                <div class="ep-title">${ep.title}</div>
            </div>
            <div class="ep-date">${ep.airDate}</div>
        </div>`;
}

function serviceCard(svc) {
    const statusClass = svc.status === 'running' ? 'badge-ok' : svc.status === 'restarting' ? 'badge-warn' : 'badge-missing';
    const statusLabel = svc.status === 'not_found' ? 'not found' : svc.status;
    const icon = {
        plex: '📺', sonarr: '📡', radarr: '🎬', qbittorrent: '⬇️',
        bazarr: '💬', prowlarr: '🔍', 'telegram-bot': '🤖', 'web-dashboard': '🖥️',
    }[svc.name] || '⚙️';
    return `
        <div class="service-card">
            <div class="service-icon">${icon}</div>
            <div class="service-name">${svc.name}</div>
            <span class="badge ${statusClass}">${statusLabel}</span>
            <button class="btn btn-sm btn-restart" onclick="restartService('${svc.name}', this)">Restart</button>
        </div>`;
}

function showModal(title, message, onConfirm) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal">
            <h3>${title}</h3>
            <p>${message}</p>
            <div class="actions">
                <button class="btn btn-sm" id="modal-cancel">Cancel</button>
                <button class="btn btn-sm btn-danger" id="modal-confirm">Delete</button>
            </div>
        </div>`;
    document.body.appendChild(overlay);
    overlay.querySelector('#modal-cancel').onclick = () => overlay.remove();
    overlay.querySelector('#modal-confirm').onclick = () => { onConfirm(); overlay.remove(); };
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
}
