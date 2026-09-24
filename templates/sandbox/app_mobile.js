// ==============================================================================
// 王者出装箱 ｜ 移动端抽屉交互、一键权威神装与战术简报同步 (app_mobile.js)
// 专注：移动端换英雄抽屉、分路切换联动一键神装、主视图自选VS推荐简报渲染
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 250 行以内
// ==============================================================================

let currentHeroActiveLane = '对抗路';

// === 主玩分路切换联动 ===
function changeHeroActiveLane(lane, btn) {
  currentHeroActiveLane = lane;
  document.querySelectorAll('#heroLaneSwitchPills .lane-pill-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  else {
    const targetBtn = document.querySelector(`#heroLaneSwitchPills .lane-pill-btn[data-lane="${lane}"]`);
    if (targetBtn) targetBtn.classList.add('active');
  }
  // 联动一键神装与推荐出装
  loadRecommendedEquips();
}

// === 一键神装 (基于所选分路，优先装填王者官方对应推荐方案) ===
function loadRecommendedEquips() {
  if (!currentHero) return;

  const presets = (typeof getHeroOfficialPresets === 'function') ? getHeroOfficialPresets(currentHero) : [];
  let chosenPreset = null;

  // 1. 根据当前主玩分路智能匹配最贴切的官方推荐方案
  if (currentHeroActiveLane === '打野') {
    chosenPreset = presets.find(p => (p.items || []).some(it => {
      const n = it.item_name || '';
      return n.includes('贪婪之噬') || n.includes('追击刀锋') || n.includes('利斧') || n.includes('巨人之握') || n.includes('打野');
    })) || presets[0];
  } else if (currentHeroActiveLane === '游走') {
    chosenPreset = presets.find(p => (p.items || []).some(it => {
      const n = it.item_name || '';
      return n.includes('极影') || n.includes('救赎') || n.includes('近卫') || n.includes('形昭');
    })) || presets.find(p => p.genre && p.genre.includes('肉')) || presets[0];
  } else if (currentHeroActiveLane === '中路') {
    chosenPreset = presets.find(p => p.genre && p.genre.includes('法')) || presets[0];
  } else if (currentHeroActiveLane === '发育路') {
    chosenPreset = presets.find(p => p.genre && (p.genre.includes('暴击') || p.genre.includes('穿透') || p.genre.includes('攻速'))) || presets[0];
  } else {
    // 对抗路
    chosenPreset = presets.find(p => p.genre && (p.genre.includes('半肉') || p.genre.includes('战阵') || p.genre.includes('坦伤'))) || presets[0];
  }

  if (chosenPreset && chosenPreset.items && chosenPreset.items.length > 0) {
    currentSlots = [...chosenPreset.items].slice(0, 6);
  } else {
    // 通用 fallback
    const r = (currentHero.role || '') + (currentHero.lane || '');
    let recNames = ['抵抗之靴', '暗影战斧', '暴烈之甲', '宗师之力', '纯净苍穹', '永夜守护'];
    if (r.includes('射手') || currentHeroActiveLane === '发育路') recNames = ['急速战靴', '影刃', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];
    else if (r.includes('法师') || currentHeroActiveLane === '中路') recNames = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
    else if (currentHeroActiveLane === '打野') recNames = ['贪婪之噬', '急速战靴', '暗影战斧', '宗师之力', '无尽战刃', '破军'];
    else if (currentHeroActiveLane === '游走') recNames = ['极影·救赎', '抵抗之靴', '红莲斗篷', '霸者重装', '魔女斗篷', '不祥征兆'];

    const aliasMap = { '强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴' };
    currentSlots = [];
    recNames.forEach(name => {
      const it = ITEMS_DATA.find(i => i.item_name === name || i.item_name === aliasMap[name]);
      if (it && currentSlots.length < 6) currentSlots.push(it);
    });
  }

  renderSlots();
  renderItems();
  recalculate();
}

// === 同步主视图【自选方案 VS 王者推荐方案】简报卡片 ===
function updateSynergyBrief() {
  const card = document.getElementById('synergyBriefCard');
  if (!card) return;
  const summary = document.getElementById('synergyBriefSummary');
  const highlights = document.getElementById('synergyBriefHighlights');

  if (!currentSlots || currentSlots.length === 0) {
    if (summary) {
      summary.innerText = '暂未选配装备。点击“一键神装”或挑选装备入槽，实时演算方案对比。';
      summary.className = 'synergy-brief-summary';
    }
    if (highlights) highlights.innerHTML = '';
    return;
  }

  const effItems = currentSlots;
  const officialPresets = typeof getHeroOfficialPresets === 'function' ? getHeroOfficialPresets(currentHero) : [];
  const activePreset = officialPresets.find(p => p.id === (typeof currentBenchmarkPresetId !== 'undefined' ? currentBenchmarkPresetId : 'official_1')) || officialPresets[0] || { items: [] };

  if (typeof compareUserBuildWithOfficial === 'function') {
    const diff = compareUserBuildWithOfficial(effItems, activePreset, currentHero, typeof currentArcana !== 'undefined' ? currentArcana : {});
    const cb = diff.comboResult;

    if (summary) {
      // 提取核心关键数值差
      const adDiff = diff.uStat.ad - diff.bStat.ad;
      const hpDiff = diff.uStat.hp - diff.bStat.hp;
      const cdrDiff = diff.uStat.cdr - diff.bStat.cdr;

      const numTokens = [];
      numTokens.push(`物理攻击 ${adDiff >= 0 ? '+' : ''}${adDiff}`);
      if (hpDiff !== 0) numTokens.push(`额外生命 ${hpDiff >= 0 ? '+' : ''}${hpDiff}`);
      numTokens.push(`冷却缩减 ${cdrDiff >= 0 ? '+' : ''}${cdrDiff}%`);

      summary.innerText = `相较【${activePreset.title || '王者推荐'}】：${numTokens.join(' ｜ ')}`;
    }

    if (highlights) {
      let hlHtml = '';
      // 1. 连招伤害对比
      if (cb) {
        const dmgDiff = cb.dmgDiff;
        const dmgStr = dmgDiff > 0 ? `领先 +${dmgDiff} 爆发` : (dmgDiff < 0 ? `落后 ${dmgDiff}` : '持平');
        hlHtml += `
          <div class="synergy-highlight-row">
            <span class="synergy-highlight-badge" style="background:#0071e3;">连招</span>
            <span class="synergy-highlight-desc"><b>全套总伤害 ${cb.userCombat.totalDmg}</b> (${dmgStr}) · 回复 +${cb.userCombat.totalHeal} HP</span>
          </div>
        `;
      }
      // 2. 核心机制优势
      if (diff.pros && diff.pros.length > 0) {
        hlHtml += `
          <div class="synergy-highlight-row">
            <span class="synergy-highlight-badge" style="background:#16a34a;">优势</span>
            <span class="synergy-highlight-desc"><b>${diff.pros[0].title}</b> · ${diff.pros[0].desc}</span>
          </div>
        `;
      } else if (diff.cons && diff.cons.length > 0) {
        hlHtml += `
          <div class="synergy-highlight-row">
            <span class="synergy-highlight-badge" style="background:#d97706;">提示</span>
            <span class="synergy-highlight-desc"><b>${diff.cons[0].title}</b> · ${diff.cons[0].desc}</span>
          </div>
        `;
      }
      highlights.innerHTML = hlHtml;
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
  document.body.style.overflow = 'hidden';
  document.body.style.touchAction = 'none';
  renderModalHeroes();
}

function closeHeroModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('arcana-modal-close') && !e.target.closest('.arcana-modal-close')) {
    return;
  }
  const overlay = document.getElementById('heroModalOverlay');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
  document.body.style.touchAction = '';
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
      document.body.style.overflow = '';
      document.body.style.touchAction = '';
    };
    card.innerHTML = `
      <img class="hero-avatar" alt="${h.cname}" src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg'">
      <div class="hero-card-name">${h.cname}</div>
    `;
    container.appendChild(card);
  });
}
