// ==============================================================================
// 王者出装箱 ｜ 移动端抽屉交互、一键权威神装与战术简报同步 (app_mobile.js)
// 专注：移动端换英雄抽屉、权威经典配装智能速配、战术协同简报主卡片渲染
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 150 行以内
// ==============================================================================

// === 一键权威神装 (微信小程序同款，根据当前英雄流派智能速配) ===
function loadRecommendedEquips() {
  if (!currentHero) return;
  let recNames = [];
  const r = (currentHero.role || '') + (currentHero.lane || '');
  const cname = currentHero.cname;

  if (cname === '貂蝉') {
    recNames = ['冷静之靴', '圣杯', '时之预言', '噬神之书', '破茧之衣', '博学者之怒'];
  } else if (cname === '吕布') {
    recNames = ['抵抗之靴', '纯净苍穹', '破军', '暴烈之甲', '铸梦·逐风', '极寒风暴'];
  } else if (cname === '马可波罗') {
    recNames = ['急速战靴', '末世', '影刃', '破晓', '冰痕之握', '暴烈之甲'];
  } else if (cname === '王维') {
    recNames = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
  } else if (cname === '李白') {
    recNames = ['贪婪之噬', '急速战靴', '泣血之刃', '暗影战斧', '宗师之力', '破军'];
  } else if (cname === '孙尚香') {
    recNames = ['急速战靴', '宗师之力', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];
  } else if (r.includes('射手') || r.includes('发育路')) {
    recNames = ['急速战靴', '影刃', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];
  } else if (r.includes('法师') || r.includes('中路')) {
    recNames = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
  } else if (r.includes('刺客') || (r.includes('打野') && !r.includes('坦克'))) {
    recNames = ['贪婪之噬', '抵抗之靴', '暗影战斧', '宗师之力', '无尽战刃', '破军'];
  } else if (r.includes('坦克') || (r.includes('肉') && r.includes('游走'))) {
    recNames = ['极影·救赎', '抵抗之靴', '红莲斗篷', '霸者重装', '魔女斗篷', '不祥征兆'];
  } else if (r.includes('游走') || r.includes('辅助')) {
    recNames = ['极影·救赎', '冷静之靴', '凝冰之息', '梦魇之牙', '霸者重装', '魔女斗篷'];
  } else {
    // 战士/通用对抗路
    recNames = ['抵抗之靴', '暗影战斧', '暴烈之甲', '宗师之力', '纯净苍穹', '永夜守护'];
  }

  const aliasMap = {
    '强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴',
    '破军': '强者破军', '破晓': '仁者破晓', '贤者之书': '贤者天书', '急速战靴': '急速之靴'
  };

  currentSlots = [];
  recNames.forEach(name => {
    const it = ITEMS_DATA.find(i => i.item_name === name) || ITEMS_DATA.find(i => i.item_name === aliasMap[name]);
    if (it && currentSlots.length < 6) currentSlots.push(it);
  });

  renderSlots();
  renderItems();
  recalculate();
}

// === 同步主视图战术协同简报卡片 (微信小程序同款高品质提炼) ===
function updateSynergyBrief() {
  const card = document.getElementById('synergyBriefCard');
  if (!card) return;
  const badge = document.getElementById('synergyBriefBadge');
  const styleTag = document.getElementById('synergyBriefStyleTag');
  const summary = document.getElementById('synergyBriefSummary');
  const highlights = document.getElementById('synergyBriefHighlights');

  if (!currentSlots || currentSlots.length === 0) {
    if (badge) {
      badge.innerText = '待选装';
      badge.style.background = 'var(--text-tertiary)';
    }
    if (styleTag) styleTag.innerText = '待装配推演';
    if (summary) summary.innerText = '点击下方装备入槽，系统将实时演算技能机制与被动乘区协同。';
    if (highlights) highlights.innerHTML = '';
    return;
  }

  // 汇总有效装备
  const effItems = currentSlots;
  const skills = (typeof HERO_SKILLS_DATA !== 'undefined' && currentHero) ? (HERO_SKILLS_DATA[currentHero.cname] || []) : [];

  if (typeof calculateSynergyScore === 'function') {
    const syn = calculateSynergyScore(currentHero, effItems, currentSlots, skills, 0);
    if (badge) {
      const shortGrade = (syn.rankBadge || '').split(' ')[0] || '';
      badge.innerText = `${syn.score}分 · ${shortGrade}`;
      badge.style.background = syn.rankColor || 'var(--color-blue)';
    }
    if (styleTag) styleTag.innerText = syn.rankBadge || '战术协同';
    if (summary) summary.innerText = syn.rankSub || '装备成型，核心战术乘区全面生效。';
    if (highlights) {
      const activeTags = [];
      const sc = syn.synergyContext || {};
      if (sc.hasSpellblade) activeTags.push('强击爆发');
      if (sc.hasBaoLie) activeTags.push('受击增伤');
      if (sc.hasPhoenix) activeTags.push('低血回春');
      if (sc.hasYellowShield) activeTags.push('神盾重击');
      if (sc.hasBloodRage) activeTags.push('狂怒逆转');
      if (activeTags.length === 0) activeTags.push('基础属性协同');

      highlights.innerHTML = activeTags.map(t => 
        `<span class="synergy-highlight-badge">${t}</span>`
      ).join('');
    }
  }
}

// === 移动端英雄选择抽屉系统 (Hero Modal Bottom Sheet) ===
let currentHeroModalFilter = "全部";

function onHeroSpotlightClick(e) {
  if (window.innerWidth <= 768) {
    openHeroModal(e);
  }
}

function openHeroModal(e) {
  if (e && e.stopPropagation) e.stopPropagation();
  const overlay = document.getElementById('heroModalOverlay');
  if (!overlay) return;
  overlay.classList.add('active');
  renderModalHeroes();
}

function closeHeroModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('arcana-modal-close') && !e.target.closest('.arcana-modal-close')) {
    return;
  }
  const overlay = document.getElementById('heroModalOverlay');
  if (overlay) overlay.classList.remove('active');
}

function setHeroModalFilter(lane, el) {
  currentHeroModalFilter = lane;
  document.querySelectorAll('#heroModalTabs .seg-item').forEach(b => b.classList.remove('active'));
  if (el) el.classList.add('active');
  renderModalHeroes();
}

function filterModalHeroes() {
  renderModalHeroes();
}

function renderModalHeroes() {
  const searchInput = document.getElementById('heroModalSearch');
  const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
  const container = document.getElementById('heroModalListContainer');
  if (!container) return;
  container.innerHTML = '';

  const filtered = HEROES_DATA.filter(h => {
    const matchLane = (currentHeroModalFilter === '全部') || (h.lane === currentHeroModalFilter) || (h.role && h.role.includes(currentHeroModalFilter));
    const matchQuery = !query || h.cname.toLowerCase().includes(query) || (h.title && h.title.toLowerCase().includes(query));
    return matchLane && matchQuery;
  });

  const countBadge = document.getElementById('heroModalCountBadge');
  if (countBadge) countBadge.innerText = `${filtered.length}位`;

  filtered.forEach(h => {
    const card = document.createElement('div');
    card.className = `hero-card ${currentHero.ename === h.ename ? 'selected' : ''}`;
    card.onclick = () => {
      selectHero(h);
      closeHeroModal();
    };
    card.innerHTML = `
      <img class="hero-avatar" alt="${h.cname}" src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg'">
      <div class="hero-card-name">${h.cname}</div>
    `;
    container.appendChild(card);
  });
}
