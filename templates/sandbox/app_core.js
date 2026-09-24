// === 静态内嵌数据 ===
const HEROES_DATA = __HEROES_DATA_PLACEHOLDER__;
const ITEMS_DATA = __ITEMS_DATA_PLACEHOLDER__;
const ARCANA_DATA = __ARCANA_DATA_PLACEHOLDER__;
const HERO_SKILLS_DATA = __HERO_SKILLS_DATA_PLACEHOLDER__;
const RECIPES_MAP = __RECIPES_MAP_PLACEHOLDER__;
const BOOTS_MAP = __BOOTS_MAP_PLACEHOLDER__;
const ACTIVE_ITEMS = __ACTIVE_ITEMS_PLACEHOLDER__;
const JUNGLE_ITEMS = __JUNGLE_ITEMS_PLACEHOLDER__;

// === 状态机 ===
let currentHero = HEROES_DATA[0] || {};
let currentSlots = [];
let currentHeroFilter = "全部";
let currentItemFilter = "全部";
// 铭文状态：每种颜色支持混搭，记录各铭文具体颗数，如 { red: { '异变': 9, '纷争': 1 }, green: { '鹰眼': 10 }, blue: { '狩猎': 7, '夺萃': 3 } }
let currentArcana = { red: { "异变": 10 }, green: { "鹰眼": 10 }, blue: { "隐匿": 10 } };

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

  initHeroArcana(currentHero);
  updateSpotlight();
  renderArcanaBar();
  renderHeroes();
  renderItems();
  renderSlots();
  recalculate();
  updateSynergyBrief();
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
  document.getElementById('spotAvatar').src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${currentHero.ename}/${currentHero.ename}.jpg`;
  document.getElementById('spotName').innerText = currentHero.cname || '未知英雄';
  document.getElementById('spotTitle').innerText = currentHero.title ? `${currentHero.title} · Lv.15 满级` : 'Lv.15 满级状态';
  document.getElementById('spotLane').innerText = `${currentHero.lane || '对抗路'} ｜ ${currentHero.role || '战士'}`;
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
  container.innerHTML = '';
  
  const filtered = HEROES_DATA.filter(h => {
    const matchLane = (currentHeroFilter === '全部') || (h.lane === currentHeroFilter);
    const matchQuery = !query || h.cname.toLowerCase().includes(query) || (h.title && h.title.toLowerCase().includes(query));
    return matchLane && matchQuery;
  });

  filtered.forEach(h => {
    const card = document.createElement('div');
    card.className = `hero-card ${currentHero.ename === h.ename ? 'selected' : ''}`;
    card.onclick = () => selectHero(h);
    card.innerHTML = `
      <img class="hero-avatar" alt="${h.cname}" src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg'">
      <div class="hero-card-name">${h.cname}</div>
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
  recalculate();
}


// === 铭文管理与复合模态框系统 (支持自由混搭任意颗数) ===

// [模块说明] 铭文交互算法已拆分至 app_arcana.js
// [模块说明] 二级联动分析引擎已拆分至 app_synergy.js

function renderItems() {
  const query = (document.getElementById('itemSearch').value || '').trim().toLowerCase();
  const container = document.getElementById('itemListContainer');
  container.innerHTML = '';

  const filtered = ITEMS_DATA.filter(it => {
    const matchCat = (currentItemFilter === '全部') || (it.category === currentItemFilter);
    const matchQuery = !query || it.item_name.toLowerCase().includes(query);
    return matchCat && matchQuery;
  });

  document.getElementById('itemCountBadge').innerText = `${filtered.length} 件装备`;

  filtered.forEach(it => {
    const inSlot = currentSlots.some(s => s.item_name === it.item_name);
    const card = document.createElement('div');
    card.className = `item-card ${inSlot ? 'equipped' : ''}`;
    card.onclick = () => addItem(it);
    // 标准静默原生浮层提示（不遮挡卡片）
    card.title = `${it.item_name} (${it.total_price || 0} G)\n${it.des1 || ''}\n${it.des2 || ''}`;

    // 格式化卡片内展示（所有的框大小完全一致，统一三段式苹果官网规范排版）
    const lines = (it.des1_lines && it.des1_lines.length > 0) ? it.des1_lines : (it.des1 ? it.des1.split(' ') : ['基础属性']);
    const line1 = lines[0] || '基础属性';
    const line2 = lines.slice(1).join(' · ') || (it.category || '基础件');

    const passiveClean = (it.des2 || '').replace(/唯一被动[：:-]/g, '').trim();
    const passivePillHtml = passiveClean 
      ? `<div class="item-passive-pill" title="${it.des2}">${passiveClean}</div>` 
      : `<div class="item-passive-pill pill-subtle">${it.category || '基础装备'}</div>`;

    card.innerHTML = `
      <span class="item-equipped-badge">已装配</span>
      <div class="item-top">
        <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${it.item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg'">
        <div class="item-meta">
          <div class="item-name">${it.item_name}</div>
          <div class="item-price-pill">${it.total_price || 0} G</div>
        </div>
      </div>
      <div class="item-body">
        <div class="item-stat-line item-stat-primary">${line1}</div>
        <div class="item-stat-line">${line2}</div>
      </div>
      ${passivePillHtml}
    `;
    container.appendChild(card);
  });
}

function renderSlots() {
  const grid = document.getElementById('slotsGrid');
  grid.innerHTML = '';
  document.getElementById('slotCount').innerText = `已选 ${currentSlots.length} / 6 件`;

  for (let i = 0; i < 6; i++) {
    const item = currentSlots[i];
    const slot = document.createElement('div');
    if (item) {
      slot.className = 'slot filled';
      slot.title = `点击卸下: ${item.item_name}`;
      slot.onclick = () => removeSlot(i);
      slot.innerHTML = `
        <img alt="${item.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${item.item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${item.item_id}.jpg'">
        <span class="slot-remove-badge">×</span>
      `;
    } else {
      slot.className = 'slot';
      slot.innerHTML = `<span class="slot-num">${i + 1}</span>`;
    }
    grid.appendChild(slot);
  }
}

function addItem(item) {
  // 1. 已装配状态下再次点击 -> 直接卸下 (Toggle，体验与微信小程序对齐)
  const existingIdx = currentSlots.findIndex(s => s.item_name === item.item_name);
  if (existingIdx !== -1) {
    currentSlots.splice(existingIdx, 1);
    renderSlots();
    renderItems();
    recalculate();
    return;
  }

  // 2. 检查槽位上限
  if (currentSlots.length >= 6) {
    alert("局内神装上限仅限 6 格！请先点击槽位中的装备进行卸下或替换。");
    return;
  }
  currentSlots.push(item);
  renderSlots();
  renderItems();
  recalculate();
}

function removeSlot(index) {
  currentSlots.splice(index, 1);
  renderSlots();
  renderItems();
  recalculate();
}

function resetSlots() {
  currentSlots = [];
  renderSlots();
  renderItems();
  recalculate();
}

// [模块说明] 一键神装、战术协同简报卡片与移动端抽屉交互已下沉解耦至 app_mobile.js 驱动


// 核心数值计算、属性面板渲染与被动互斥诊断逻辑
// 遵循单一职责原则，已下沉解耦至 app_stats.js 驱动

function exportMarkdown() {
  if (currentSlots.length === 0) {
    alert("请先选择至少 1 件装备再导出！");
    return;
  }
  const eff = currentSlots.map(s => s.item_name).join(' + ');
  const arcParts = [];
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    const sub = Object.entries(map).filter(([_, c]) => c > 0).map(([n, c]) => `${c}${n}`).join('+');
    if (sub) arcParts.push(sub);
  });
  const arcStr = arcParts.join(' ｜ ') || '无铭文';
  const text = `### 自定义配装方案：${currentHero.cname}\\n- 英雄定位：${currentHero.lane} / ${currentHero.role}\\n- 铭文搭配：${arcStr}\\n- 装备配置：${eff}\\n- 总金币造价：${document.getElementById('totalGold').innerText}\\n- 导出来源：王者出装箱 ｜ 局内六神装配装沙盒`;
  navigator.clipboard.writeText(text).then(() => {
    alert("已将配装方案复制到剪贴板！可直接粘贴至 NotebookLM。");
  }).catch(() => {
    prompt("请手动复制配装方案：", text);
  });
}
