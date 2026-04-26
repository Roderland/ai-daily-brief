/** AI 创业每日简报 - 前端应用 */

const DATA_BASE = 'data';
let allBriefs = {};
let currentDate = '';
let activeFilter = '全部';

document.addEventListener('DOMContentLoaded', init);

async function init() {
    await loadData();
    setupDateSelector();
    setupFilters();
    setupSearch();
    render();
    await loadCompletedDives();
}

async function loadData() {
    try {
        const resp = await fetch(`${DATA_BASE}/index.json`);
        if (!resp.ok) throw new Error('No data yet');
        const index = await resp.json();
        const dates = index.briefs.map(b => b.date).sort().reverse();

        if (dates.length === 0) {
            showEmpty();
            return;
        }

        await Promise.all(dates.map(async (date) => {
            try {
                const r = await fetch(`${DATA_BASE}/brief_${date}.json`);
                allBriefs[date] = await r.json();
            } catch { /* skip missing */ }
        }));

        currentDate = dates[0];
    } catch {
        showEmpty();
    }
}

function showEmpty() {
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('briefList').style.display = 'none';
    document.getElementById('updateBadge').textContent = '暂无数据';
}

function setupDateSelector() {
    const dates = Object.keys(allBriefs).sort().reverse();
    const container = document.getElementById('dateSelector');
    if (dates.length === 0) return;

    dates.forEach(date => {
        const btn = document.createElement('button');
        btn.className = 'date-btn' + (date === currentDate ? ' active' : '');
        const d = new Date(date + 'T00:00:00');
        const label = `${d.getMonth()+1}/${d.getDate()}`;
        btn.textContent = label;
        btn.dataset.date = date;
        btn.addEventListener('click', () => {
            currentDate = date;
            container.querySelectorAll('.date-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            render();
        });
        container.appendChild(btn);
    });
}

function setupFilters() {
    const categories = ['全部', '工具类', '商业模式', '行业动态', '观点'];
    const container = document.getElementById('filters');

    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn' + (cat === activeFilter ? ' active' : '');
        btn.textContent = cat;
        btn.addEventListener('click', () => {
            activeFilter = cat;
            container.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            render();
        });
        container.appendChild(btn);
    });
}

function setupSearch() {
    const input = document.getElementById('searchInput');
    let timer;
    input.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(render, 300);
    });
}

function getFilteredItems() {
    const brief = allBriefs[currentDate];
    if (!brief) return [];

    let items = brief.items || [];
    const query = document.getElementById('searchInput').value.trim().toLowerCase();

    if (activeFilter !== '全部') {
        items = items.filter(item => item.category === activeFilter);
    }
    if (query) {
        items = items.filter(item =>
            (item.title || '').toLowerCase().includes(query) ||
            (item.summary || '').toLowerCase().includes(query) ||
            (item.analysis || '').toLowerCase().includes(query)
        );
    }

    return items.sort((a, b) => (b.importance || 3) - (a.importance || 3));
}

function render() {
    const container = document.getElementById('briefList');
    const badge = document.getElementById('updateBadge');
    const countBadge = document.getElementById('countBadge');

    if (currentDate) {
        const d = new Date(currentDate + 'T00:00:00');
        const weekday = ['日','一','二','三','四','五','六'][d.getDay()];
        badge.textContent = `${currentDate} 周${weekday}`;
    }

    const items = getFilteredItems();
    countBadge.textContent = `${items.length} 条`;

    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>没有匹配的内容</h3>
                <p>试试其他分类或关键词</p>
            </div>`;
        return;
    }

    container.innerHTML = items.map(item => renderCard(item)).join('');

    // Bind deep dive buttons
    container.querySelectorAll('.deep-dive-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            openDeepDive(btn.dataset.id, btn.dataset.title, btn.dataset.summary);
        });
    });
}

function importanceClass(val) {
    return `importance-${Math.max(1, Math.min(5, val || 3))}`;
}

function renderCard(item) {
    const importance = item.importance || 3;
    const id = item.id || '';
    return `
        <div class="brief-card">
            <div class="card-header">
                <a href="${item.original_url || '#'}" target="_blank" rel="noopener" class="card-title">
                    ${escapeHtml(item.title || '')}
                </a>
                <span class="importance-badge ${importanceClass(importance)}">${importance}</span>
            </div>
            <div class="card-summary">${escapeHtml(item.summary || '')}</div>
            ${item.analysis ? `<div class="card-analysis">💡 ${escapeHtml(item.analysis)}</div>` : ''}
            <div class="card-footer">
                <div class="card-tags">
                    ${(item.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
                </div>
                <span class="card-source">${escapeHtml(item.source || '')}</span>
            </div>
            <div class="card-actions">
                <button class="deep-dive-btn"
                    data-id="${escapeHtml(id)}"
                    data-title="${escapeHtml(item.title || '')}"
                    data-summary="${escapeHtml(item.summary || '')}">
                    🔍 深挖
                </button>
                ${item.original_url ? `<a href="${item.original_url}" target="_blank" rel="noopener" class="read-more">阅读原文 →</a>` : ''}
            </div>
        </div>`;
}
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* === Deep Dive Modal === */

const DEEP_DIVE_GITHUB = 'https://github.com/roderland/ai-daily-brief/actions/workflows/deep-dive.yml';

const COMPLETED_DIVES = [];

async function loadCompletedDives() {
    try {
        const resp = await fetch(`${DATA_BASE}/deep_dives_index.json`);
        if (resp.ok) {
            const index = await resp.json();
            COMPLETED_DIVES.length = 0;
            COMPLETED_DIVES.push(...(index.dives || []));
            renderCompletedDives();
        }
    } catch {}
}

function openDeepDive(id, title, summary) {
    const modal = document.getElementById('deepDiveModal');
    modal.style.display = 'flex';

    document.getElementById('deepDiveTitle').textContent = title || '分析中...';
    document.getElementById('deepDiveContent').querySelector('.deep-dive-loading').style.display = 'block';
    document.getElementById('deepDiveReport').style.display = 'none';

    const encodedTitle = encodeURIComponent(title || '');
    const encodedId = encodeURIComponent(id || '');
    const encodedSummary = encodeURIComponent(summary || '');
    const url = `${DEEP_DIVE_GITHUB}?workflow=deep-dive.yml&inputs[topic]=${encodedTitle}&inputs[item_id]=${encodedId}&inputs[context]=${encodedSummary}`;

    fetchAndRenderDeepDive(id, title);
}

async function fetchAndRenderDeepDive(id, title) {
    // 先按 id 匹配
    if (id) {
        const existing = COMPLETED_DIVES.find(d => d.item_id === id);
        if (existing) {
            try {
                const r = await fetch(`${DATA_BASE}/deep_dives/${existing.file}`);
                if (r.ok) {
                    const data = await r.json();
                    renderDeepDiveReport(data);
                    return;
                }
            } catch {}
        }
    }

    // fallback: 匹配 topic（兼容旧的深挖结果）
    if (title) {
        const normalized = t => t.trim().replace(/\s+/g, '');
        const existing = COMPLETED_DIVES.find(d => normalized(d.topic) === normalized(title));
        if (existing) {
            try {
                const r = await fetch(`${DATA_BASE}/deep_dives/${existing.file}`);
                if (r.ok) {
                    const data = await r.json();
                    renderDeepDiveReport(data);
                    return;
                }
            } catch {}
        }
    }

    // 没有缓存结果，引导用户触发深挖
    showDeepDiveGuide(title);
}

function renderCompletedDives() {
    if (COMPLETED_DIVES.length === 0) return;
    const container = document.getElementById('completedDives');
    if (!container) return;
    container.innerHTML = `
        <h2 style="margin-bottom:16px;">📊 已完成深度分析</h2>
        ${COMPLETED_DIVES.map(d => `
            <div class="brief-card" style="cursor:pointer;" onclick="openCompletedDeepDive('${d.file}', '${escapeHtml(d.topic)}')">
                <div class="card-title" style="font-size:14px;">${escapeHtml(d.topic)}</div>
                <div style="font-size:12px;color:var(--text-tertiary);margin-top:4px;">${d.date || ''}</div>
            </div>
        `).join('')}
    `;
}

async function openCompletedDeepDive(file, topic) {
    const modal = document.getElementById('deepDiveModal');
    modal.style.display = 'flex';
    document.getElementById('deepDiveTitle').textContent = topic || '深度分析';
    document.getElementById('deepDiveContent').querySelector('.deep-dive-loading').style.display = 'block';
    document.getElementById('deepDiveReport').style.display = 'none';
    try {
        const r = await fetch(`${DATA_BASE}/deep_dives/${file}`);
        if (r.ok) {
            const data = await r.json();
            renderDeepDiveReport(data);
            return;
        }
    } catch {}
    showDeepDiveGuide(topic);
}

function showDeepDiveGuide(topic) {
    const loadingEl = document.getElementById('deepDiveContent').querySelector('.deep-dive-loading');
    const reportEl = document.getElementById('deepDiveReport');

    loadingEl.style.display = 'none';
    reportEl.style.display = 'block';

    const encoded = encodeURIComponent(topic);
    const deepDiveUrl = `${DEEP_DIVE_GITHUB}?workflow=deep-dive.yml&inputs[topic]=${encoded}`;

    reportEl.innerHTML = `
        <div style="text-align:center;padding:40px 20px;">
            <div style="font-size:48px;margin-bottom:16px;">🚀</div>
            <h3 style="margin-bottom:12px;">需要触发深挖分析</h3>
            <p style="color:var(--text-secondary);margin-bottom:20px;">
                点击下方按钮，前往 GitHub Actions 手动触发深挖分析。
                <br>分析完成后刷新本页面即可查看结果。
            </p>
            <a href="${deepDiveUrl}" target="_blank" rel="noopener"
               style="display:inline-block;padding:12px 24px;background:var(--accent);color:white;
                      border-radius:8px;text-decoration:none;font-weight:600;">
                → 前往 GitHub 触发深挖
            </a>
        </div>`;
}

function renderDeepDiveReport(data) {
    const loadingEl = document.getElementById('deepDiveContent').querySelector('.deep-dive-loading');
    const reportEl = document.getElementById('deepDiveReport');

    loadingEl.style.display = 'none';
    reportEl.style.display = 'block';

    const content = data.content || {};
    if (!content.overview) {
        reportEl.innerHTML = `<p style="color:var(--text-secondary);">分析结果格式异常，请稍后重试。</p>`;
        return;
    }

    reportEl.innerHTML = `
        <div class="report-section">
            <h3>📋 概述</h3>
            <p>${escapeHtml(content.overview || '')}</p>
        </div>
        <div class="report-section">
            <h3>💼 商业模式分析</h3>
            <p>${escapeHtml(content.business_model_analysis || '')}</p>
        </div>
        <div class="report-section">
            <h3>🎯 目标用户</h3>
            <p>${escapeHtml(content.target_users || '')}</p>
        </div>
        <div class="report-section">
            <h3>🔑 核心洞察</h3>
            <ul>${(content.key_insights || []).map(i => `<li>${escapeHtml(i)}</li>`).join('')}</ul>
        </div>
        <div class="report-section">
            <h3>⚡ 挑战</h3>
            <ul>${(content.challenges || []).map(c => `<li>${escapeHtml(c)}</li>`).join('')}</ul>
        </div>
        <div class="report-section">
            <h3>🌟 机会</h3>
            <ul>${(content.opportunities || []).map(o => `<li>${escapeHtml(o)}</li>`).join('')}</ul>
        </div>
        <div class="report-section">
            <h3>🛠 技术可行性</h3>
            <p>${escapeHtml(content.technical_feasibility || '')} · 难度等级: ${content.difficulty_level || 'N/A'}/5</p>
        </div>
        <div class="report-section">
            <h3>🏷 类似案例</h3>
            <p>${escapeHtml(content.similar_cases || '')}</p>
        </div>
        <div class="report-section">
            <h3>🎯 行动建议</h3>
            <p>${escapeHtml(content.recommendation || '')}</p>
        </div>`;
}

function closeDeepDive() {
    document.getElementById('deepDiveModal').style.display = 'none';
}
