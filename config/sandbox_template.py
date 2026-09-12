# -*- coding: utf-8 -*-
"""
王者荣耀局内配装沙盒网页静态模板与样式
专供 sandbox_builder.py 进行数据编译嵌入
"""

SANDBOX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚔️</text></svg>">
<title>王者荣耀局内六神装配装沙盒模拟器 | Honor of Kings Gear Sandbox</title>
<style>
:root {
  --bg-main: #0c0f17;
  --bg-card: rgba(22, 28, 43, 0.85);
  --bg-card-hover: rgba(32, 41, 64, 0.95);
  --border-gold: #c69c52;
  --border-dim: rgba(198, 156, 82, 0.25);
  --text-primary: #f0f3fa;
  --text-secondary: #9aa5be;
  --gold-highlight: #f5cf87;
  --gold-glow: 0 0 15px rgba(245, 207, 135, 0.35);
  --danger-red: #ff5e62;
  --success-green: #38ef7d;
  --slot-bg: rgba(10, 13, 20, 0.9);
}
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif; }
body { background: radial-gradient(circle at top center, #1b2438 0%, var(--bg-main) 70%); color: var(--text-primary); min-height: 100vh; padding: 20px; overflow-x: hidden; }
header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border-dim); margin-bottom: 20px; }
.logo-title h1 { font-size: 24px; font-weight: 700; color: var(--gold-highlight); letter-spacing: 1px; display: flex; align-items: center; gap: 10px; }
.logo-title p { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.header-actions { display: flex; gap: 12px; }
.btn { background: linear-gradient(135deg, #a77c35, #cfa85e); color: #0c0f17; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn:hover { filter: brightness(1.15); box-shadow: var(--gold-glow); transform: translateY(-1px); }
.btn-secondary { background: rgba(255,255,255,0.08); color: var(--text-primary); border: 1px solid var(--border-dim); }
.btn-secondary:hover { background: rgba(255,255,255,0.15); }

/* 主体网格 */
.sandbox-grid { display: grid; grid-template-columns: 290px 1fr 340px; gap: 20px; height: calc(100vh - 110px); }
.panel { background: var(--bg-card); border: 1px solid var(--border-dim); border-radius: 12px; backdrop-filter: blur(12px); display: flex; flex-direction: column; overflow: hidden; }
.panel-header { padding: 14px 16px; border-bottom: 1px solid var(--border-dim); background: rgba(0,0,0,0.25); display: flex; justify-content: space-between; align-items: center; }
.panel-title { font-size: 15px; font-weight: 700; color: var(--gold-highlight); display: flex; align-items: center; gap: 8px; }
.search-input { width: 100%; background: rgba(0,0,0,0.35); border: 1px solid var(--border-dim); border-radius: 6px; padding: 7px 12px; color: #fff; font-size: 13px; outline: none; transition: border 0.2s; }
.search-input:focus { border-color: var(--border-gold); }

/* 左侧：英雄选择 */
.filter-tabs { display: flex; gap: 6px; padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.06); flex-wrap: wrap; }
.tab-btn { background: rgba(255,255,255,0.05); border: 1px solid transparent; color: var(--text-secondary); padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; }
.tab-btn.active { background: rgba(198, 156, 82, 0.2); color: var(--gold-highlight); border-color: var(--border-gold); }
.hero-scroll { flex: 1; overflow-y: auto; padding: 12px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.hero-card { display: flex; flex-direction: column; align-items: center; padding: 8px 4px; border-radius: 8px; border: 1px solid transparent; cursor: pointer; transition: all 0.2s; background: rgba(0,0,0,0.2); }
.hero-card:hover { border-color: var(--border-gold); background: var(--bg-card-hover); transform: translateY(-2px); }
.hero-card.selected { border-color: var(--border-gold); background: rgba(198, 156, 82, 0.25); box-shadow: var(--gold-glow); }
.hero-avatar { width: 50px; height: 50px; border-radius: 50%; border: 2px solid var(--border-gold); object-fit: cover; background: #222; }
.hero-name { font-size: 12px; margin-top: 6px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; }

/* 中间：装备商店 */
.item-scroll { flex: 1; overflow-y: auto; padding: 14px; display: grid; grid-template-columns: repeat(auto-fill, minmax(135px, 1fr)); gap: 12px; align-content: start; }
.item-card { background: rgba(10, 13, 20, 0.65); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; cursor: pointer; transition: all 0.2s; position: relative; }
.item-card:hover { border-color: var(--border-gold); background: var(--bg-card-hover); transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
.item-card.in-slots { border-color: var(--success-green); box-shadow: 0 0 10px rgba(56, 239, 125, 0.25); }
.item-top { display: flex; gap: 8px; align-items: center; }
.item-icon { width: 38px; height: 38px; border-radius: 6px; border: 1px solid var(--border-dim); background: #111; }
.item-info-meta { flex: 1; min-width: 0; }
.item-name { font-size: 13px; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-price { font-size: 11px; color: var(--gold-highlight); font-weight: 600; margin-top: 2px; }
.item-desc { font-size: 11px; color: var(--text-secondary); margin-top: 6px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* 右侧：6神装槽位与实时面板 */
.slots-container { padding: 14px; background: rgba(0,0,0,0.3); border-bottom: 1px solid var(--border-dim); }
.slots-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.slot { aspect-ratio: 1; background: var(--slot-bg); border: 1px dashed var(--border-dim); border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; position: relative; transition: all 0.2s; }
.slot.filled { border-style: solid; border-color: var(--border-gold); background: rgba(22, 28, 43, 0.9); }
.slot.filled:hover { border-color: var(--danger-red); }
.slot img { width: 36px; height: 36px; border-radius: 6px; }
.slot-badge { position: absolute; top: -5px; right: -5px; background: var(--danger-red); color: #fff; width: 16px; height: 16px; border-radius: 50%; font-size: 10px; display: none; align-items: center; justify-content: center; }
.slot.filled:hover .slot-badge { display: flex; }
.slot-placeholder { font-size: 10px; color: var(--text-secondary); }

.summary-card { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.summary-gold { color: var(--gold-highlight); font-weight: 700; font-size: 15px; }

.stats-scroll { flex: 1; overflow-y: auto; padding: 14px 16px; }
.stat-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 12px; }
.stat-name { color: var(--text-secondary); }
.stat-val { color: #fff; font-weight: 600; text-align: right; }
.stat-calc { font-size: 11px; color: var(--gold-highlight); }

.diagnose-box { padding: 12px 16px; background: rgba(0,0,0,0.4); border-top: 1px solid var(--border-dim); max-height: 140px; overflow-y: auto; }
.diag-title { font-size: 12px; font-weight: 700; margin-bottom: 6px; color: var(--gold-highlight); }
.diag-item { font-size: 11px; line-height: 1.5; margin-bottom: 4px; padding: 4px 8px; border-radius: 4px; }
.diag-warn { background: rgba(255, 94, 98, 0.15); color: var(--danger-red); border-left: 3px solid var(--danger-red); }
.diag-pass { background: rgba(56, 239, 125, 0.15); color: var(--success-green); border-left: 3px solid var(--success-green); }

/* 滚动条 */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-thumb { background: rgba(198, 156, 82, 0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-gold); }
</style>
</head>
<body>

<header>
  <div class="logo-title">
    <h1>⚔️ 王者荣耀局内六神装配装沙盒模拟器</h1>
    <p>实时微观数值演算 ｜ 6 格生效栏限制 ｜ 小件吞噬规则 ｜ 动态被动转化 ｜ 唯一被动互斥诊断</p>
  </div>
  <div class="header-actions">
    <button class="btn btn-secondary" onclick="resetSlots()">清空装备栏</button>
    <button class="btn" onclick="exportMarkdown()">导出为 Markdown</button>
  </div>
</header>

<main class="sandbox-grid">
  <!-- 左栏：英雄选择 -->
  <section class="panel">
    <div class="panel-header">
      <div class="panel-title">👤 英雄基准属性 (15级满级)</div>
    </div>
    <div style="padding: 10px 14px;">
      <input type="text" id="heroSearch" class="search-input" placeholder="输入英雄名字检索 (如: 孙尚香 / 李白)..." oninput="filterHeroes()">
    </div>
    <div class="filter-tabs" id="heroTabs">
      <button class="tab-btn active" onclick="setHeroFilter('全部', this)">全部</button>
      <button class="tab-btn" onclick="setHeroFilter('对抗路', this)">对抗路</button>
      <button class="tab-btn" onclick="setHeroFilter('打野', this)">打野</button>
      <button class="tab-btn" onclick="setHeroFilter('中路', this)">中路</button>
      <button class="tab-btn" onclick="setHeroFilter('发育路', this)">发育路</button>
      <button class="tab-btn" onclick="setHeroFilter('游走', this)">游走</button>
    </div>
    <div class="hero-scroll" id="heroListContainer"></div>
  </section>

  <!-- 中栏：装备商店 -->
  <section class="panel">
    <div class="panel-header">
      <div class="panel-title">🛒 局内装备商店</div>
      <input type="text" id="itemSearch" class="search-input" style="width: 180px;" placeholder="搜索装备..." oninput="filterItems()">
    </div>
    <div class="filter-tabs" id="itemTabs">
      <button class="tab-btn active" onclick="setItemFilter('全部', this)">全部</button>
      <button class="tab-btn" onclick="setItemFilter('攻击装备', this)">攻击</button>
      <button class="tab-btn" onclick="setItemFilter('法术装备', this)">法术</button>
      <button class="tab-btn" onclick="setItemFilter('防御装备', this)">防御</button>
      <button class="tab-btn" onclick="setItemFilter('移动装备', this)">移动</button>
      <button class="tab-btn" onclick="setItemFilter('打野装备', this)">打野</button>
      <button class="tab-btn" onclick="setItemFilter('游走装备', this)">游走</button>
    </div>
    <div class="item-scroll" id="itemListContainer"></div>
  </section>

  <!-- 右栏：装备栏与实战面板 -->
  <section class="panel">
    <div class="panel-header">
      <div class="panel-title">🛡️ 局内出装生效栏 (上限 6 格)</div>
      <span style="font-size: 12px; color: var(--gold-highlight);" id="slotCount">已选 0 / 6 件</span>
    </div>
    <div class="slots-container">
      <div class="slots-grid" id="slotsGrid"></div>
    </div>
    <div class="summary-card">
      <span>成型总造价</span>
      <span class="summary-gold" id="totalGold">0 金币</span>
    </div>
    <div class="stats-scroll" id="statsContainer"></div>
    <div class="diagnose-box">
      <div class="diag-title">🔍 装备契合与互斥诊断</div>
      <div id="diagnoseContainer"></div>
    </div>
  </section>
</main>

<script>
// === 静态内嵌数据 ===
const HEROES_DATA = __HEROES_DATA_PLACEHOLDER__;
const ITEMS_DATA = __ITEMS_DATA_PLACEHOLDER__;
const RECIPES_MAP = __RECIPES_MAP_PLACEHOLDER__;
const BOOTS_MAP = __BOOTS_MAP_PLACEHOLDER__;
const ACTIVE_ITEMS = __ACTIVE_ITEMS_PLACEHOLDER__;
const JUNGLE_ITEMS = __JUNGLE_ITEMS_PLACEHOLDER__;

// === 状态机 ===
let currentHero = HEROES_DATA[0] || {};
let currentSlots = [];
let currentHeroFilter = "全部";
let currentItemFilter = "全部";

// 初始化
window.onload = () => {
  renderHeroTabs();
  renderHeroes();
  renderItems();
  renderSlots();
  recalculate();
};

function setHeroFilter(lane, btn) {
  currentHeroFilter = lane;
  document.querySelectorAll('#heroTabs .tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderHeroes();
}

function setItemFilter(cat, btn) {
  currentItemFilter = cat;
  document.querySelectorAll('#itemTabs .tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
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
      <div class="hero-name">${h.cname}</div>
    `;
    container.appendChild(card);
  });
}

function selectHero(hero) {
  currentHero = hero;
  renderHeroes();
  recalculate();
}

function renderItems() {
  const query = (document.getElementById('itemSearch').value || '').trim().toLowerCase();
  const container = document.getElementById('itemListContainer');
  container.innerHTML = '';

  const filtered = ITEMS_DATA.filter(it => {
    const matchCat = (currentItemFilter === '全部') || (it.category === currentItemFilter);
    const matchQuery = !query || it.item_name.toLowerCase().includes(query);
    return matchCat && matchQuery;
  });

  filtered.forEach(it => {
    const inSlot = currentSlots.some(s => s.item_name === it.item_name);
    const card = document.createElement('div');
    card.className = `item-card ${inSlot ? 'in-slots' : ''}`;
    card.onclick = () => addItem(it);
    card.innerHTML = `
      <div class="item-top">
        <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg" onerror="this.style.display='none'">
        <div class="item-info-meta">
          <div class="item-name">${it.item_name}</div>
          <div class="item-price">${it.total_price} G</div>
        </div>
      </div>
      <div class="item-desc">${it.des1 || '基础装备'}</div>
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
        <img alt="${item.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${item.item_id}.jpg">
        <span class="slot-badge">×</span>
      `;
    } else {
      slot.className = 'slot';
      slot.innerHTML = `<span class="slot-placeholder">${i + 1}</span>`;
    }
    grid.appendChild(slot);
  }
}

function addItem(item) {
  if (currentSlots.length >= 6) {
    alert("局内背包上限仅限 6 格！请先点击右侧槽位中的装备进行卸下或替换。");
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

// 核心计算与吞噬算法
function recalculate() {
  const names = currentSlots.map(s => s.item_name);
  
  // 小件原料吞噬过滤
  const effectiveItems = [];
  const consumedNotes = [];
  for (let i = 0; i < currentSlots.length; i++) {
    const curr = currentSlots[i].item_name;
    let isConsumed = false;
    for (let j = i + 1; j < currentSlots.length; j++) {
      const later = currentSlots[j].item_name;
      const recipes = RECIPES_MAP[later] || [];
      if (recipes.includes(curr)) {
        isConsumed = true;
        consumedNotes.push(`原料【${curr}】已被大件【${later}】合成吞噬，属性已覆盖`);
        break;
      }
    }
    if (!isConsumed) effectiveItems.push(currentSlots[i]);
  }

  // 属性累加
  let totalGold = 0;
  let totals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, mp:0, crit:0, aspeed:0, cdr:0, percent_speed:0, flat_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce_flat:0, p_pierce_percent:0, m_pierce_flat:0, m_pierce_percent:0, has_hat:false };
  let bootsCounted = false;

  currentSlots.forEach(it => totalGold += (it.total_price || 0));

  effectiveItems.forEach(it => {
    const st = it.stats || {};
    totals.atk += st.atk || 0;
    totals.ap += st.ap || 0;
    totals.pdef += st.pdef || 0;
    totals.mdef += st.mdef || 0;
    totals.hp += st.hp || 0;
    totals.mp += st.mp || 0;
    totals.crit += st.crit || 0;
    totals.aspeed += st.aspeed || 0;
    totals.cdr += st.cdr || 0;
    totals.percent_speed += st.percent_speed || 0;
    totals.p_lifesteal += st.p_lifesteal || 0;
    totals.m_lifesteal += st.m_lifesteal || 0;
    totals.p_pierce_flat += st.p_pierce_flat || 0;
    totals.p_pierce_percent = Math.max(totals.p_pierce_percent, st.p_pierce_percent || 0);
    totals.m_pierce_flat += st.m_pierce_flat || 0;
    totals.m_pierce_percent = Math.max(totals.m_pierce_percent, st.m_pierce_percent || 0);
    if (it.item_name === '博学者之怒') totals.has_hat = true;

    if (BOOTS_MAP[it.item_name] && !bootsCounted) {
      totals.flat_speed = BOOTS_MAP[it.item_name];
      bootsCounted = true;
    }
  });

  const finalAp = totals.has_hat ? Math.floor(totals.ap * 1.3) : totals.ap;
  const cappedCdr = Math.min(Math.floor(totals.cdr), 40);

  // 英雄 15 级基础属性
  const b = currentHero.base_stats || { hp:[3200,7000], atk:[170,380], pdef:[100,400], mdef:[50,169], speed:370, aspeed:"+2.0%" };
  const bHp = b.hp[1];
  const bAtk = b.atk[1];
  const bPdef = b.pdef[1];
  const bMdef = b.mdef[1];
  const bSpeed = b.speed;
  const growthMatch = (b.aspeed || '+1.0%').match(/([\\d\\.]+)%/);
  const growthVal = growthMatch ? parseFloat(growthMatch[1]) : 1.0;
  const heroSelfAspeed = Math.floor(growthVal * 14);
  const totalAspeed = heroSelfAspeed + Math.floor(totals.aspeed);

  // 二次转化加成
  let extraPdef = 0;
  let extraMdef = 0;
  let extraPdefNote = "";
  let extraMdefNote = "";
  if (effectiveItems.some(i => i.item_name === '时之预言')) {
    const propVal = Math.min(Math.floor(finalAp * 0.1), 250);
    extraPdef += propVal; extraMdef += propVal;
    extraPdefNote = `(含时之预言+${propVal}) `;
    extraMdefNote = `(含时之预言+${propVal}) `;
  }
  if (effectiveItems.some(i => i.item_name === '破魔刀')) {
    const pmVal = Math.min(Math.floor((bAtk + totals.atk) * 0.5), 250);
    extraMdef += pmVal;
    extraMdefNote = `(含破魔刀+${pmVal}) `;
  }

  const totPdef = bPdef + totals.pdef + extraPdef;
  const totMdef = bMdef + totals.mdef + extraMdef;
  const pReduction = (totPdef / (totPdef + 602) * 100).toFixed(1);
  const mReduction = (totMdef / (totMdef + 602) * 100).toFixed(1);

  const pspeedStr = totals.percent_speed > 0 ? totals.percent_speed.toFixed(1).replace(/\\.0$/, '') : '0';
  const calcSpeed = Math.floor((bSpeed + totals.flat_speed) * (1 + totals.percent_speed / 100));

  // 渲染统计
  document.getElementById('totalGold').innerText = `${totalGold} 金币`;
  
  const statsBox = document.getElementById('statsContainer');
  statsBox.innerHTML = `
    <div class="stat-row">
      <span class="stat-name">最终物理攻击力</span>
      <div><span class="stat-val">${bAtk + totals.atk}</span> <span class="stat-calc">(${bAtk}基础 + ${totals.atk}装)</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">最终法术攻击力</span>
      <div><span class="stat-val">${finalAp}</span> <span class="stat-calc">${totals.has_hat ? '(含帽子+30%)' : ''}</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">最终最大生命值</span>
      <div><span class="stat-val">${bHp + totals.hp}</span> <span class="stat-calc">(${bHp}基础 + ${totals.hp}装)</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">最终物理防御(物抗)</span>
      <div><span class="stat-val">${totPdef}</span> <span class="stat-calc">${extraPdefNote}(免伤 ${pReduction}%)</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">最终法术防御(魔抗)</span>
      <div><span class="stat-val">${totMdef}</span> <span class="stat-calc">${extraMdefNote}(免伤 ${mReduction}%)</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">最终实战移速</span>
      <div><span class="stat-val">${calcSpeed}</span> <span class="stat-calc">(${bSpeed}+${totals.flat_speed}鞋)×(1+${pspeedStr}%)</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">最终攻击速度</span>
      <div><span class="stat-val">${totalAspeed}%</span> <span class="stat-calc">(${heroSelfAspeed}%自带 + ${Math.floor(totals.aspeed)}%装)</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">暴击率 / 冷却缩减</span>
      <div><span class="stat-val">${Math.floor(totals.crit)}% ｜ ${cappedCdr}% ${totals.cdr >= 40 ? '(已满40%)' : ''}</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">物理吸血 / 法术吸血</span>
      <div><span class="stat-val">${totals.p_lifesteal}% ｜ ${totals.m_lifesteal}%</span></div>
    </div>
    <div class="stat-row">
      <span class="stat-name">物理穿透 / 法术穿透</span>
      <div><span class="stat-val">${totals.p_pierce_flat}点(${totals.p_pierce_percent}%) ｜ ${totals.m_pierce_flat}点(${totals.m_pierce_percent}%)</span></div>
    </div>
  `;

  // 诊断互斥
  renderDiagnosis(effectiveItems, consumedNotes);
}

function renderDiagnosis(effectiveItems, consumedNotes) {
  const diagBox = document.getElementById('diagnoseContainer');
  diagBox.innerHTML = '';
  const effNames = effectiveItems.map(i => i.item_name);
  const issues = [];

  // 小件吞噬
  consumedNotes.forEach(note => issues.push({ type: 'pass', text: note }));

  // 强击
  const qj = effNames.filter(n => ["宗师之力", "冰痕之握", "巫术法杖", "光辉之剑"].includes(n));
  if (qj.length > 1) issues.push({ type: 'warn', text: `⚠️ 【强击被动互斥】：同时出了 ${qj.join(' 与 ')}，伤害仅生效一件！` });

  // 双鞋
  const boots = effNames.filter(n => BOOTS_MAP[n]);
  if (boots.length > 1) issues.push({ type: 'warn', text: `⚠️ 【神速双鞋互斥】：同时出了 ${boots.join(' 与 ')}，移动速度不叠加！` });

  // 主动共存
  const actives = effNames.filter(n => ACTIVE_ITEMS.includes(n));
  if (actives.length > 1) issues.push({ type: 'warn', text: `⚠️ 【多主动按键共存】：出了 ${actives.join(' 与 ')}，局内默认只能设置 1 个主动按键！` });

  // 打野惩击
  const jungles = effNames.filter(n => JUNGLE_ITEMS.includes(n));
  if (jungles.length > 0) issues.push({ type: 'warn', text: `⚡ 【召唤师技能提示】：出了打野刀（${jungles.join('、')}），局内必须携带【惩击】方可购买！` });

  if (issues.length === 0) {
    diagBox.innerHTML = `<div class="diag-item diag-pass">✅ 当前 6 件成装无被动互斥与技能冲突，契合度 100%！</div>`;
  } else {
    issues.forEach(iss => {
      const el = document.createElement('div');
      el.className = `diag-item ${iss.type === 'warn' ? 'diag-warn' : 'diag-pass'}`;
      el.innerText = iss.text;
      diagBox.appendChild(el);
    });
  }
}

function exportMarkdown() {
  if (currentSlots.length === 0) {
    alert("请先选择至少 1 件装备再导出！");
    return;
  }
  const eff = currentSlots.map(s => s.item_name).join(' + ');
  const text = `### 自定义出装方案：${currentHero.cname}\\n- 装备配置：${eff}\\n- 总金币造价：${document.getElementById('totalGold').innerText}\\n- 导出来源：王者荣耀沙盒模拟器`;
  navigator.clipboard.writeText(text).then(() => {
    alert("已将配装 Markdown 方案复制到剪贴板！可直接粘贴至 NotebookLM。");
  }).catch(() => {
    prompt("请手动复制配装 Markdown：", text);
  });
}
</script>
</body>
</html>
"""
