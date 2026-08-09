document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const dateSelect = document.getElementById('dateSelect');
  const searchInput = document.getElementById('searchInput');
  const currentDateDisplay = document.getElementById('currentDateDisplay');
  const updateTimeDisplay = document.getElementById('updateTimeDisplay');
  const totalCountDisplay = document.getElementById('totalCountDisplay');
  const refreshBtn = document.getElementById('refreshBtn');
  const articleGrid = document.getElementById('articleGrid');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const emptyState = document.getElementById('emptyState');

  // Counts
  const countAll = document.getElementById('countAll');
  const countAi = document.getElementById('countAi');
  const countProgramming = document.getElementById('countProgramming');
  const countTech = document.getElementById('countTech');
  const countSaved = document.getElementById('countSaved');

  // State
  let allArticles = [];
  let currentCategory = 'all';
  let searchQuery = '';
  let savedArticles = JSON.parse(localStorage.getItem('saved_articles') || '[]');

  // Initialize
  init();

  async function init() {
    setupEventListeners();
    await loadDateList();
    await loadNewsData('latest');
  }

  function setupEventListeners() {
    // Category Tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        const targetTab = e.currentTarget;
        targetTab.classList.add('active');
        currentCategory = targetTab.dataset.category;
        renderArticles();
      });
    });

    // Date Select
    dateSelect.addEventListener('change', (e) => {
      loadNewsData(e.target.value);
    });

    // Search Input
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderArticles();
    });

    // Refresh Button
    refreshBtn.addEventListener('click', () => {
      loadNewsData(dateSelect.value);
    });
  }

  // Load Date List for Archive Dropdown
  async function loadDateList() {
    try {
      const res = await fetch('data/dates.json');
      if (!res.ok) throw new Error('dates.json not found');
      const dates = await res.json();
      
      dateSelect.innerHTML = '<option value="latest">最新 (本日)</option>';
      dates.forEach(d => {
        const option = document.createElement('option');
        option.value = escapeHTML(d);
        option.textContent = escapeHTML(d);
        dateSelect.appendChild(option);
      });
    } catch (err) {
      console.warn('Could not load dates archive list:', err);
    }
  }

  // Fetch JSON news data
  async function loadNewsData(targetDate) {
    showLoading(true);
    let url = 'data/latest.json';
    if (targetDate && targetDate !== 'latest') {
      const safeDate = encodeURIComponent(targetDate);
      url = `data/${safeDate}.json`;
    }

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      allArticles = data.items || [];
      
      // Update UI Header Stats
      currentDateDisplay.textContent = formatDateJapanese(data.date);
      updateTimeDisplay.textContent = data.updated_at ? data.updated_at.split(' ')[1] || '' : '';
      totalCountDisplay.textContent = data.total_count || allArticles.length;

      updateCategoryCounts(data.categories);
      renderArticles();

    } catch (err) {
      console.error('Failed to load news:', err);
      showLoading(false);
      emptyState.classList.remove('hidden');
      articleGrid.innerHTML = '';
    }
  }

  function updateCategoryCounts(cats) {
    countAll.textContent = allArticles.length;
    countSaved.textContent = savedArticles.length;

    if (cats) {
      countAi.textContent = cats.ai_count || 0;
      countProgramming.textContent = cats.programming_count || 0;
      countTech.textContent = cats.tech_count || 0;
    } else {
      countAi.textContent = allArticles.filter(a => a.categories.includes('ai')).length;
      countProgramming.textContent = allArticles.filter(a => a.categories.includes('programming')).length;
      countTech.textContent = allArticles.filter(a => a.categories.includes('tech')).length;
    }
  }

  function renderArticles() {
    showLoading(false);

    let filtered = [];

    if (currentCategory === 'saved') {
      filtered = allArticles.filter(a => savedArticles.includes(a.link));
    } else if (currentCategory === 'all') {
      filtered = [...allArticles];
    } else {
      filtered = allArticles.filter(a => a.categories.includes(currentCategory));
    }

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(a => 
        a.title.toLowerCase().includes(searchQuery) ||
        a.description.toLowerCase().includes(searchQuery) ||
        a.domain.toLowerCase().includes(searchQuery)
      );
    }

    if (filtered.length === 0) {
      emptyState.classList.remove('hidden');
      articleGrid.innerHTML = '';
      return;
    }

    emptyState.classList.add('hidden');
    articleGrid.innerHTML = filtered.map(item => createArticleCardHTML(item)).join('');

    // Attach bookmark toggle listeners
    document.querySelectorAll('.save-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const link = btn.dataset.link;
        toggleSaveArticle(link, btn);
      });
    });
  }

  function createArticleCardHTML(item) {
    const safeLink = safeURL(item.link);
    const isSaved = savedArticles.includes(item.link);
    const categoryBadges = item.categories.map(c => {
      const label = c === 'ai' ? 'AI' : c === 'programming' ? 'PROG' : 'TECH';
      return `<span class="tag-pill">${label}</span>`;
    }).join('');

    return `
      <article class="article-card">
        <div>
          <div class="card-header">
            <span class="domain-badge">${escapeHTML(item.domain)}</span>
            <span class="hatebu-badge">🔖 ${item.bookmark_count}</span>
          </div>
          <h2 class="card-title">
            <a href="${safeLink}" target="_blank" rel="noopener noreferrer">
              ${escapeHTML(item.title)}
            </a>
          </h2>
          <p class="card-desc">${escapeHTML(item.description || '概要なし')}</p>
        </div>
        <div class="card-footer">
          <div class="card-tags">
            ${categoryBadges}
          </div>
          <button class="save-btn ${isSaved ? 'saved' : ''}" data-link="${escapeHTML(item.link)}" title="あとで読む">
            ${isSaved ? '★' : '☆'}
          </button>
        </div>
      </article>
    `;
  }

  function toggleSaveArticle(link, btn) {
    if (savedArticles.includes(link)) {
      savedArticles = savedArticles.filter(url => url !== link);
      btn.classList.remove('saved');
      btn.textContent = '☆';
    } else {
      savedArticles.push(link);
      btn.classList.add('saved');
      btn.textContent = '★';
    }
    localStorage.setItem('saved_articles', JSON.stringify(savedArticles));
    countSaved.textContent = savedArticles.length;
    if (currentCategory === 'saved') {
      renderArticles();
    }
  }

  function showLoading(isLoading) {
    if (isLoading) {
      loadingSpinner.classList.remove('hidden');
      emptyState.classList.add('hidden');
      articleGrid.innerHTML = '';
    } else {
      loadingSpinner.classList.add('hidden');
    }
  }

  function formatDateJapanese(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      return `${parts[0]}年${parts[1]}月${parts[2]}日`;
    }
    return dateStr;
  }

  // Security Helper: Safe URL Validation
  function safeURL(urlStr) {
    if (!urlStr) return '#';
    try {
      const parsed = new URL(urlStr, window.location.href);
      if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
        return escapeHTML(parsed.href);
      }
    } catch (e) {
      // Invalid URL
    }
    return '#';
  }

  // Security Helper: HTML Entity Escaping
  function escapeHTML(str) {
    if (typeof str !== 'string') return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
