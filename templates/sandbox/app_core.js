// === 静态内嵌数据 ===
const HEROES_DATA = __HEROES_DATA_PLACEHOLDER__;
const ITEMS_DATA = __ITEMS_DATA_PLACEHOLDER__;
const ARCANA_DATA = __ARCANA_DATA_PLACEHOLDER__;
const HERO_SKILLS_DATA = __HERO_SKILLS_DATA_PLACEHOLDER__;
const RECIPES_MAP = __RECIPES_MAP_PLACEHOLDER__;
const BOOTS_MAP = __BOOTS_MAP_PLACEHOLDER__;
const ACTIVE_ITEMS = __ACTIVE_ITEMS_PLACEHOLDER__;
const JUNGLE_ITEMS = __JUNGLE_ITEMS_PLACEHOLDER__;
const OFFICIAL_HERO_BUILDS = __OFFICIAL_HERO_BUILDS_PLACEHOLDER__;

// === 状态机 ===
let currentHero = HEROES_DATA[0] || {};
let currentSlots = [];
let currentHeroFilter = "全部";
let currentItemFilter = "全部";
let currentArcana = { red: { "异变": 10 }, green: { "鹰眼": 10 }, blue: { "隐匿": 10 } };

// === 资产安全与反扒防御系统 (Anti-Theft & DevTools Trap) ===
(function initSecurityShield() {
  // 1. 禁用右键上下文菜单（阻断“检查元素”与“查看源码”）
  document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    return false;
  }, { capture: true });

  // 2. 封锁快捷键：F12、Ctrl+Shift+I/J/C、Ctrl+U、Ctrl+S 及 Mac Command 组合键
  document.addEventListener('keydown', function(e) {
    const key = e.key ? e.key.toLowerCase() : '';
    const code = e.keyCode || e.which;
    const isCtrlOrMeta = e.ctrlKey || e.metaKey;
    const isShift = e.shiftKey;
    const isAlt = e.altKey;

    if (key === 'f12' || code === 123) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    if (isCtrlOrMeta && isShift && (key === 'i' || key === 'j' || key === 'c' || code === 73 || code === 74 || code === 67)) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    if (isCtrlOrMeta && (key === 'u' || key === 's' || code === 85 || code === 83)) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    if (isCtrlOrMeta && isAlt && (key === 'i' || key === 'j')) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
  }, { capture: true });

  // 3. 动态反调试断点陷阱 (Debugger Trap)
  function launchDebuggerLoop() {
    function trap() {
      (function() {
        return false;
      }['constructor']('debugger')());
    }
    try {
      trap();
    } catch (_) {}
  }
  setInterval(launchDebuggerLoop, 800);

  // 4. 控制台水印警告声明
  try {
    const style1 = 'color: #ff3b30; font-size: 16px; font-weight: bold;';
    const style2 = 'color: #6e6e73; font-size: 12px;';
    console.log('%c🛡️ 王者出装箱安全保护系统已就绪', style1);
    console.log('%c本站点算分引擎与战术图谱受知识产权保护，严禁未经授权的商业逆向与恶意爬取。', style2);
  } catch (_) {}
})();

window.onload = () => {
  // 读取用户本地保存的主题偏好（默认浅色）
  const savedTheme = localStorage.getItem('apple_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeBtnIcon(savedTheme);

  // 移动端环境检测与适配 (宽度 <= 768px 或移动端 UA)
  const isMobile = window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  if (isMobile) {
    document.body.classList.add('is-mobile');
  }

  // 检查 URL 是否携带专属英雄参数 (如 ?hero=105 或 ?hero=孙悟空)，赋能搜索引擎深层直达与玩家定向分享
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const heroParam = urlParams.get('hero');
    if (heroParam) {
      const matched = HEROES_DATA.find(h => String(h.ename) === heroParam || h.cname === heroParam);
      if (matched) {
        currentHero = matched;
      }
    }
  } catch (_) {}

  initHeroArcana(currentHero);
  updateSpotlight();
  renderArcanaBar();
  renderHeroes();
  renderItems();
  renderHeroHallLaneBar(currentHero);
  if (typeof renderHeroLanePills === 'function') {
    renderHeroLanePills(currentHero);
  }
  if (typeof loadRecommendedEquips === 'function') {
    loadRecommendedEquips();
  } else {
    renderSlots();
    recalculate();
    updateSynergyBrief();
  }
};

function toggleTheme() {
  const cur = document.documentElement.getAttribute('data-theme') || 'light';
  const next = cur === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('apple_theme', next);
  updateThemeBtnIcon(next);
}

function updateThemeBtnIcon(theme) {
  const btn = document.getElementById('themeBtn');
  if (!btn) return;
  if (theme === 'light') {
    btn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
  } else {
    btn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
  }
}

function updateSpotlight() {
  if (!currentHero) return;
  const avatar = document.getElementById('spotAvatar');
  if (avatar) avatar.src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${currentHero.ename}/${currentHero.ename}.jpg`;
  const name = document.getElementById('spotName');
  if (name) name.innerText = currentHero.cname || '未知英雄';
  const title = document.getElementById('spotTitle');
  if (title) title.innerText = currentHero.title || '正义爆轰';
  const role = document.getElementById('spotRole');
  if (role) role.innerText = currentHero.role || '坦克';
  const navBadge = document.getElementById('navHeroBadge');
  if (navBadge) navBadge.innerText = currentHero.cname || '英雄';
}

// === 多层级流转控制器 (Two-Stage View Flow) ===
let currentView = 'hero_select';

function switchView(viewName) {
  currentView = viewName;
  const viewHero = document.getElementById('viewHeroSelect');
  const viewStudio = document.getElementById('viewStudio');
  const btnHero = document.getElementById('navStepHero');
  const btnStudio = document.getElementById('navStepStudio');
  const navBadge = document.getElementById('navHeroBadge');

  if (navBadge && currentHero) {
    navBadge.innerText = currentHero.cname || '英雄';
  }

  if (viewName === 'hero_select') {
    if (viewHero) viewHero.classList.add('active');
    if (viewStudio) viewStudio.classList.remove('active');
    if (btnHero) btnHero.classList.add('active');
    if (btnStudio) btnStudio.classList.remove('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    if (viewHero) viewHero.classList.remove('active');
    if (viewStudio) viewStudio.classList.add('active');
    if (btnHero) btnHero.classList.remove('active');
    if (btnStudio) btnStudio.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function setHeroFilter(lane, el) {
  currentHeroFilter = lane;
  document.querySelectorAll('#heroTabs .seg-item').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  renderHeroes();
}

function setItemFilter(cat, el) {
  currentItemFilter = cat;
  document.querySelectorAll('#itemTabs .seg-item').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  renderItems();
}

function filterHeroes() { renderHeroes(); }
function filterItems() { renderItems(); }

function renderHeroes() {
  const query = (document.getElementById('heroSearch').value || '').trim().toLowerCase();
  const container = document.getElementById('heroListContainer');
  if (!container) return;
  container.innerHTML = '';
  
  const filtered = HEROES_DATA.filter(h => {
    const matchRole = (currentHeroFilter === '全部') || (h.role && h.role.includes(currentHeroFilter));
    const matchQuery = !query || h.cname.toLowerCase().includes(query) || (h.title && h.title.toLowerCase().includes(query));
    return matchRole && matchQuery;
  });

  filtered.forEach(h => {
    const card = document.createElement('div');
    card.className = `hero-card ${currentHero.ename === h.ename ? 'selected' : ''}`;
    card.onclick = () => selectHero(h);
    card.innerHTML = `
      <img class="hero-avatar" alt="${h.cname}" src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg'">
      <div class="hero-card-name">${h.cname}</div>
      <div class="hero-card-role-tag">${h.role || '英雄'}</div>
    `;
    container.appendChild(card);
  });
}

function initHeroArcana(hero) {
  if (hero && hero.recommended_arcana) {
    const rec = hero.recommended_arcana;
    currentArcana = {
      red: { [rec.red]: 10 },
      green: { [rec.green]: 10 },
      blue: { [rec.blue]: 10 }
    };
  } else {
    currentArcana = {
      red: { "异变": 10 },
      green: { "鹰眼": 10 },
      blue: { "隐匿": 10 }
    };
  }
}

function selectHero(hero) {
  currentHero = hero;
  initHeroArcana(hero);
  updateSpotlight();
  renderArcanaBar();
  renderHeroes();
  renderHeroHallLaneBar(hero);

  // 在层级 1 立即唤出实战分路轻量选择浮层，先定分路再进入推演室
  openLanePicker(hero);
}

// === 层级 1 实战分路决策控制器 ===
function getSupportedLanesForHero(hero) {
  let supported = [];
  const cname = hero ? hero.cname : '';
  if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
    const hData = OFFICIAL_HERO_BUILDS[cname];
    if (hData.supported_lanes && hData.supported_lanes.length > 0) {
      supported = hData.supported_lanes;
    } else if (hData.lanes) {
      supported = Object.keys(hData.lanes);
    }
  }
  if (!supported || supported.length === 0) {
    supported = hero && hero.lane ? [hero.lane] : ['对抗路'];
  }
  return supported;
}

function renderHeroHallLaneBar(hero) {
