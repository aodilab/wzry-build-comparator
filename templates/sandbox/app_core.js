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

  initHeroArcana(currentHero);
  updateSpotlight();
  renderArcanaBar();
  renderHeroes();
  renderItems();
  renderSlots();
  recalculate();
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
        <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg" onerror="this.style.display='none'">
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
        <img alt="${item.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${item.item_id}.jpg">
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
  if (currentSlots.length >= 6) {
    alert("局内神装上限仅限 6 格！请先点击右侧槽位中的装备进行卸下或替换。");
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

  // 铭文加成汇总（支持自由混搭任意颗数，如 9 异变 + 1 纷争）
  let arcanaTotals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, crit:0, crit_effect:0, aspeed:0, cdr:0, percent_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce_flat:0, m_pierce_flat:0, hp_regen:0 };
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        arcanaTotals.atk += (s.phys_atk || 0) * count;
        arcanaTotals.ap += (s.magic_atk || 0) * count;
        arcanaTotals.pdef += (s.phys_def || 0) * count;
        arcanaTotals.mdef += (s.magic_def || 0) * count;
        arcanaTotals.hp += (s.max_hp || 0) * count;
        arcanaTotals.crit += (s.crit_rate_pct || 0) * count;
        arcanaTotals.crit_effect += (s.crit_effect_pct || 0) * count;
        arcanaTotals.aspeed += (s.atk_speed_pct || 0) * count;
        arcanaTotals.cdr += (s.cd_reduction_pct || 0) * count;
        arcanaTotals.percent_speed += (s.move_speed_pct || 0) * count;
        arcanaTotals.p_lifesteal += (s.phys_vamp_pct || 0) * count;
        arcanaTotals.m_lifesteal += (s.magic_vamp_pct || 0) * count;
        arcanaTotals.p_pierce_flat += (s.phys_pierce || 0) * count;
        arcanaTotals.m_pierce_flat += (s.magic_pierce || 0) * count;
        arcanaTotals.hp_regen += (s.hp_regen || 0) * count;
      }
    }
  });
  // 消除浮点数精度累加误差
  for (let k in arcanaTotals) {
    arcanaTotals[k] = Math.round(arcanaTotals[k] * 10) / 10;
  }

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

  const rawAp = totals.ap + arcanaTotals.ap;
  const finalAp = totals.has_hat ? Math.floor(rawAp * 1.3) : rawAp;
  const totalCdr = totals.cdr + arcanaTotals.cdr;
  const cappedCdr = Math.min(Math.floor(totalCdr), 40);

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
  const totalAspeed = heroSelfAspeed + Math.floor(totals.aspeed) + Math.floor(arcanaTotals.aspeed);

  // 二次转化加成
  let extraPdef = 0;
  let extraMdef = 0;
  let extraPdefNote = "";
  let extraMdefNote = "";
  if (effectiveItems.some(i => i.item_name === '时之预言')) {
    const propVal = Math.min(Math.floor(finalAp * 0.1), 250);
    extraPdef += propVal; extraMdef += propVal;
    extraPdefNote = `(时之预言+${propVal}) `;
  }
  if (effectiveItems.some(i => i.item_name === '破魔刀')) {
    const pmVal = Math.min(Math.floor((bAtk + totals.atk + arcanaTotals.atk) * 0.5), 250);
    extraMdef += pmVal;
    extraMdefNote = `(破魔刀+${pmVal}) `;
  }

  const finalHp = bHp + totals.hp + arcanaTotals.hp;
  const totPdef = bPdef + totals.pdef + arcanaTotals.pdef + extraPdef;
  const totMdef = bMdef + totals.mdef + arcanaTotals.mdef + extraMdef;
  const pReduction = (totPdef / (totPdef + 602) * 100).toFixed(1);
  const mReduction = (totMdef / (totMdef + 602) * 100).toFixed(1);

  const totalSpeedPct = totals.percent_speed + arcanaTotals.percent_speed;
  const pspeedStr = totalSpeedPct > 0 ? totalSpeedPct.toFixed(1).replace(/\\.0$/, '') : '0';
  const calcSpeed = Math.floor((bSpeed + totals.flat_speed) * (1 + totalSpeedPct / 100));

  const totalCrit = Math.round((totals.crit + arcanaTotals.crit) * 10) / 10;
  const totalPhysPierce = Math.round((totals.p_pierce_flat + arcanaTotals.p_pierce_flat) * 10) / 10;
  const totalMagicPierce = Math.round((totals.m_pierce_flat + arcanaTotals.m_pierce_flat) * 10) / 10;
  const totalPhysVamp = Math.round((totals.p_lifesteal + arcanaTotals.p_lifesteal) * 10) / 10;
  const totalMagicVamp = Math.round((totals.m_lifesteal + arcanaTotals.m_lifesteal) * 10) / 10;

  // 渲染总金币
  document.getElementById('totalGold').innerText = `${totalGold.toLocaleString()} G`;
  
  // 渲染 Apple Health 风格属性面板 (基础 + 装备 + 铭文 复合精准呈现)
  const statsBox = document.getElementById('statsContainer');
  statsBox.innerHTML = `
    <!-- 生存健康面板 -->
    <div class="metric-section">
      <div class="metric-section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-green)" stroke-width="2.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
        生存与抗性指标
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终最大生命值</span>
          <span class="metric-sub">${bHp}基 + ${totals.hp}装 + ${arcanaTotals.hp}铭</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${finalHp.toLocaleString()}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">物理防御 (物抗)</span>
          <span class="metric-sub">${extraPdefNote}${bPdef}基 + ${totals.pdef}装 + ${arcanaTotals.pdef}铭 ｜ 免伤率 ${pReduction}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totPdef}</span>
          <div class="bar-track"><div class="bar-fill bar-fill-armor" style="width: ${Math.min(pReduction, 100)}%;"></div></div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">法术防御 (魔抗)</span>
          <span class="metric-sub">${extraMdefNote}${bMdef}基 + ${totals.mdef}装 + ${arcanaTotals.mdef}铭 ｜ 免伤率 ${mReduction}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totMdef}</span>
          <div class="bar-track"><div class="bar-fill bar-fill-marmor" style="width: ${Math.min(mReduction, 100)}%;"></div></div>
        </div>
      </div>
    </div>

    <!-- 进攻与爆发面板 -->
    <div class="metric-section">
      <div class="metric-section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-amber)" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
        输出与攻击强度
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终物理攻击</span>
          <span class="metric-sub">${bAtk}基 + ${totals.atk}装 + ${arcanaTotals.atk}铭</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${bAtk + totals.atk + arcanaTotals.atk}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终法术攻击</span>
          <span class="metric-sub">${totals.has_hat ? '含帽子+30% ｜ ' : ''}${totals.ap}装 + ${arcanaTotals.ap}铭</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val" style="color: ${finalAp > 0 ? 'var(--color-purple)' : 'inherit'};">${finalAp}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">暴击率 / 攻速总计</span>
          <span class="metric-sub">暴击(装${Math.floor(totals.crit)}+铭${Math.floor(arcanaTotals.crit)}) ｜ 攻速(成${heroSelfAspeed}+装${Math.floor(totals.aspeed)}+铭${Math.floor(arcanaTotals.aspeed)})</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totalCrit}% ｜ ${totalAspeed}%</span>
        </div>
      </div>
    </div>

    <!-- 机动与特殊属性 -->
    <div class="metric-section">
      <div class="metric-section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-blue)" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        机动、冷却与穿透
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">实战极限移速</span>
          <span class="metric-sub">(${bSpeed}+${totals.flat_speed}鞋) × (1+${pspeedStr}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${calcSpeed}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">冷却缩减</span>
          <span class="metric-sub">装+${Math.floor(totals.cdr)}% ｜ 铭+${Math.floor(arcanaTotals.cdr)}%${cappedCdr >= 40 ? ' (满冷缩)' : ''}</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${cappedCdr}%</span>
          <div class="bar-track"><div class="bar-fill bar-fill-cdr" style="width: ${(cappedCdr / 40 * 100)}%;"></div></div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">双穿透 (固定/百分比)</span>
          <span class="metric-sub">物穿 ${totalPhysPierce}点(${totals.p_pierce_percent}%) ｜ 魔穿 ${totalMagicPierce}点(${totals.m_pierce_percent}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-highlight">双抗穿透生效</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">续航吸血</span>
          <span class="metric-sub">物吸 ${totalPhysVamp}% (含铭+${arcanaTotals.p_lifesteal}%) ｜ 法吸 ${totalMagicVamp}% (含铭+${arcanaTotals.m_lifesteal}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totalPhysVamp || totalMagicVamp ? `${totalPhysVamp}% / ${totalMagicVamp}%` : '0%'}</span>
        </div>
      </div>
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
  consumedNotes.forEach(note => issues.push({ type: 'info', text: note }));

  // 强击
  const qj = effNames.filter(n => ["宗师之力", "冰痕之握", "巫术法杖", "光辉之剑"].includes(n));
  if (qj.length > 1) issues.push({ type: 'warn', text: `【强击被动互斥】同时出了 ${qj.join(' 与 ')}，伤害仅生效一件！` });

  // 双鞋
  const boots = effNames.filter(n => BOOTS_MAP[n]);
  if (boots.length > 1) issues.push({ type: 'warn', text: `【神速双鞋互斥】同时出了 ${boots.join(' 与 ')}，移动速度不叠加！` });

  // 主动共存
  const actives = effNames.filter(n => ACTIVE_ITEMS.includes(n));
  if (actives.length > 1) issues.push({ type: 'warn', text: `【多主动按键共存】出了 ${actives.join(' 与 ')}，局内默认只能设置 1 个主动按键！` });

  // 打野惩击
  const jungles = effNames.filter(n => JUNGLE_ITEMS.includes(n));
  if (jungles.length > 0) issues.push({ type: 'warn', text: `【召唤师技能提示】出了打野刀（${jungles.join('、')}），局内必须携带【惩击】方可购买！` });

  if (issues.length === 0) {
    diagBox.innerHTML = `
      <div class="diag-card diag-card-pass">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <span>当前 6 件成装无被动互斥与按键冲突，契合度 100%！</span>
      </div>`;
  } else {
    issues.forEach(iss => {
      const el = document.createElement('div');
      el.className = `diag-card ${iss.type === 'warn' ? 'diag-card-warn' : (iss.type === 'info' ? 'diag-card-info' : 'diag-card-pass')}`;
      const icon = iss.type === 'warn' 
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
      el.innerHTML = `${icon}<span>${iss.text}</span>`;
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
