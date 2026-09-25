// ==============================================================================
// 王者出装箱 ｜ 移动端抽屉交互、一键官方神装与战术简报同步 (app_mobile.js)
// 专注：移动端换英雄抽屉、分路切换联动一键神装、主视图自选VS推荐简报渲染
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 250 行以内
// ==============================================================================

let currentHeroActiveLane = '对抗路';
currentBenchmarkPresetId = 'preset_1';

// === 动态渲染英雄支持的官方分路胶囊 ===
function renderHeroLanePills(hero) {
  const container = document.getElementById('heroLaneSwitchPills');
  if (!container) return;
  container.innerHTML = '';

  // 获取英雄真实官方支持的分路
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

  // 若当前分路不在支持名册中，重置为第一个有效分路
  if (!supported.includes(currentHeroActiveLane)) {
    currentHeroActiveLane = supported[0];
  }

  supported.forEach(lane => {
    const btn = document.createElement('button');
    btn.className = `lane-pill-btn ${lane === currentHeroActiveLane ? 'active' : ''}`;
    btn.dataset.lane = lane;
    btn.innerText = lane;
    btn.onclick = () => changeHeroActiveLane(lane, btn);
    container.appendChild(btn);
  });
}

// === 主玩分路切换联动 ===
function changeHeroActiveLane(lane, btn) {
  currentHeroActiveLane = lane;
  document.querySelectorAll('#heroLaneSwitchPills .lane-pill-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.lane === lane);
  });
  // 切换分路时重置预设方案为第1套，并联动装配神装与铭文
  currentBenchmarkPresetId = 'preset_1';
  loadRecommendedEquips();
}

// === 渲染官方3套推荐出装卡片 ===
function renderOfficialPresetCards() {
  const container = document.getElementById('officialPresetCards');
  if (!container) return;
  container.innerHTML = '';

  const presets = (typeof getHeroOfficialPresets === 'function') ? getHeroOfficialPresets(currentHero, currentHeroActiveLane) : [];
  if (!presets || presets.length === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-tertiary); padding:6px 0;">当前分路暂无官方套装推荐</div>';
    return;
  }

  presets.forEach((p, idx) => {
    const isAct = (p.id === currentBenchmarkPresetId) || (idx === 0 && !currentBenchmarkPresetId);
    const tagClass = p.tag === '生存' ? 'tag-survival' : (p.tag === '输出' ? 'tag-output' : 'tag-balance');
    const card = document.createElement('div');
    card.className = `official-preset-card ${isAct ? 'active' : ''}`;
    card.onclick = () => applyOfficialPreset(p.id);

    // 迷你装备图标预览
    let itemsHtml = '';
    (p.items || []).slice(0, 6).forEach(it => {
      itemsHtml += `<img class="preset-mini-item-icon" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${it.item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg'" alt="${it.item_name}" title="${it.item_name}">`;
    });

    card.innerHTML = `
      <div class="preset-meta-top">
        <span class="preset-genre-name">${p.genre || `推荐${idx + 1}`}</span>
        <span class="preset-tag-pill ${tagClass}">${p.tag || '推荐'}</span>
      </div>
      <div class="preset-desc-line" title="${p.desc || ''}">${p.desc || '官方实战经典方案'}</div>
      <div class="preset-items-preview">${itemsHtml}</div>
      <div class="preset-arcana-pill" title="推荐铭文：${p.arcana_desc || '标准属性'}">${p.arcana_desc || '官方铭文'}</div>
    `;
    container.appendChild(card);
  });
}

// === 点击装配官方推荐套装方案（装备与推荐铭文联动强装配） ===
function applyOfficialPreset(presetId) {
  currentBenchmarkPresetId = presetId;
  const presets = (typeof getHeroOfficialPresets === 'function') ? getHeroOfficialPresets(currentHero, currentHeroActiveLane) : [];
  const chosen = presets.find(p => p.id === presetId) || presets[0];
  if (!chosen) return;

  // 1. 装载6件神装
  currentSlots = [...(chosen.items || [])].slice(0, 6);

  // 2. 联动装载强绑定的官方推荐铭文
  if (chosen.arcana) {
    currentArcana = JSON.parse(JSON.stringify(chosen.arcana));
  } else if (currentHero && currentHero.recommended_arcana) {
    initHeroArcana(currentHero);
  }

  renderSlots();
  renderItems();
  renderArcanaBar();
  renderOfficialPresetCards();
  recalculate();
  if (typeof updateSynergyBrief === 'function') {
    updateSynergyBrief();
  }
}

// === 一键对齐当前方案绑定的官方铭文 ===
function alignArcanaWithCurrentBuild(e) {
  if (e && e.stopPropagation) e.stopPropagation();
  const presets = (typeof getHeroOfficialPresets === 'function') ? getHeroOfficialPresets(currentHero, currentHeroActiveLane) : [];
  const activePreset = presets.find(p => p.id === currentBenchmarkPresetId) || presets[0];

  if (activePreset && activePreset.arcana) {
    currentArcana = JSON.parse(JSON.stringify(activePreset.arcana));
    renderArcanaBar();
    recalculate();
    if (typeof updateSynergyBrief === 'function') updateSynergyBrief();
    alert(`已将铭文一键对齐【${activePreset.genre || activePreset.title}】官方推荐铭文！`);
  } else if (currentHero && currentHero.recommended_arcana) {
    initHeroArcana(currentHero);
    renderArcanaBar();
    recalculate();
    if (typeof updateSynergyBrief === 'function') updateSynergyBrief();
    alert(`已将铭文一键恢复为【${currentHero.cname}】基准推荐铭文！`);
  }
}

// === 一键神装 (基于所选分路，优先装填王者官方对应推荐方案) ===
function loadRecommendedEquips() {
  if (!currentHero) return;
  const presets = (typeof getHeroOfficialPresets === 'function') ? getHeroOfficialPresets(currentHero, currentHeroActiveLane) : [];
  let chosenPreset = presets.find(p => p.id === currentBenchmarkPresetId) || (presets.length > 0 ? presets[0] : null);

  if (chosenPreset && chosenPreset.items && chosenPreset.items.length > 0) {
    currentBenchmarkPresetId = chosenPreset.id;
    currentSlots = [...chosenPreset.items].slice(0, 6);
    if (chosenPreset.arcana) {
      currentArcana = JSON.parse(JSON.stringify(chosenPreset.arcana));
    }
  } else {
    // 通用 fallback
    const r = (currentHero.role || '') + (currentHero.lane || '');
    let recNames = ['抵抗之靴', '暗影战斧', '暴烈之甲', '宗师之力', '纯净苍穹', '永夜守护'];
    if (currentHeroActiveLane === '打野') recNames = ['贪婪之噬', '抵抗之靴', '暗影战斧', '纯净苍穹', '宗师之力', '破军'];
    else if (currentHeroActiveLane === '游走') recNames = ['极影·救赎', '影忍之足', '红莲斗篷', '霸者重装', '魔女斗篷', '不祥征兆'];
    else if (currentHeroActiveLane === '中路' || r.includes('法师')) recNames = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
    else if (currentHeroActiveLane === '发育路' || r.includes('射手')) recNames = ['急速战靴', '影刃', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];

    const aliasMap = { '强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴' };
    currentSlots = [];
    recNames.forEach(name => {
      const it = ITEMS_DATA.find(i => i.item_name === name || i.item_name === aliasMap[name]);
      if (it && currentSlots.length < 6) currentSlots.push(it);
    });
  }

  renderSlots();
  renderItems();
  renderArcanaBar();
  renderOfficialPresetCards();
  recalculate();
  if (typeof updateSynergyBrief === 'function') {
    updateSynergyBrief();
  }
}

// === 切换对标的王者官方推荐方案 ===
function cycleBenchmarkPreset() {
  const presets = typeof getHeroOfficialPresets === 'function' ? getHeroOfficialPresets(currentHero, currentHeroActiveLane) : [];
  if (!presets || presets.length === 0) return;
  const curIdx = presets.findIndex(p => p.id === currentBenchmarkPresetId);
  const nextIdx = (curIdx + 1) % presets.length;
  currentBenchmarkPresetId = presets[nextIdx].id;
  updateSynergyBrief();
  renderOfficialPresetCards();
}

// === 同步主视图【自选方案 VS 王者推荐方案】实时全维对比看板 ===
function updateSynergyBrief() {
  const container = document.getElementById('compareGridCards');
  const verdictBox = document.getElementById('compareVerdictText');
  const benchNameEl = document.getElementById('compareBenchmarkName');

  const officialPresets = typeof getHeroOfficialPresets === 'function' ? getHeroOfficialPresets(currentHero, currentHeroActiveLane) : [];
  const activePreset = officialPresets.find(p => p.id === currentBenchmarkPresetId) || officialPresets[0] || { items: [] };

  if (benchNameEl) {
    benchNameEl.innerText = `${activePreset.genre || activePreset.title || '官方推荐'} ▾`;
  }

  if (!currentSlots || currentSlots.length === 0) {
    if (container) container.innerHTML = '';
    if (verdictBox) verdictBox.innerText = '暂未装配装备。挑选装备入槽或点击上方“王者官方推荐方案”，实时演算全维对比。';
    return;
  }

  if (typeof compareUserBuildWithOfficial === 'function') {
    const diff = compareUserBuildWithOfficial(currentSlots, activePreset, currentHero, typeof currentArcana !== 'undefined' ? currentArcana : {});
    const u = diff.uStat;
    const b = diff.bStat;
    const cb = diff.comboResult;

    const isMag = (currentHero && (currentHero.role || '').includes('法师')) || (u.ap > u.ad);
    const atkName = isMag ? '法术攻击' : '物理攻击';
    const uAtk = isMag ? u.ap : u.ad;
    const bAtk = isMag ? b.ap : b.ad;
    const atkDiff = uAtk - bAtk;

    const penName = isMag ? '法术穿透' : '物理穿透';
    const uPen = isMag ? u.mpen : u.pen;
    const bPen = isMag ? b.mpen : b.pen;
    const penDiff = uPen - bPen;

    const hpDiff = u.hp - b.hp;
    const cdrDiff = u.cdr - b.cdr;

    function renderDiffBadge(val, suffix = '') {
      if (val > 0) return `<span class="compare-diff-badge plus">+${val}${suffix} 领先</span>`;
      if (val < 0) return `<span class="compare-diff-badge minus">${val}${suffix} 落后</span>`;
      return `<span class="compare-diff-badge even">持平</span>`;
    }

    if (container) {
      container.innerHTML = `
        <!-- 核心攻击 -->
        <div class="compare-stat-card">
          <div class="compare-stat-name">
            <span>${atkName}</span>
            ${renderDiffBadge(atkDiff)}
          </div>
          <div class="compare-stat-values">
            <span class="compare-user-val">${uAtk}</span>
            <span class="compare-base-val">官方: ${bAtk}</span>
          </div>
        </div>

        <!-- 连招总伤害 -->
        <div class="compare-stat-card">
          <div class="compare-stat-name">
            <span>连招总爆发</span>
            ${(cb && typeof cb.dmgDiff === 'number') ? renderDiffBadge(cb.dmgDiff) : '<span class="compare-diff-badge even">持平</span>'}
          </div>
          <div class="compare-stat-values">
            <span class="compare-user-val">${(cb && cb.userCombat && typeof cb.userCombat.totalDmg !== 'undefined') ? cb.userCombat.totalDmg : '-'}</span>
            <span class="compare-base-val">官方: ${(cb && cb.officialCombat && typeof cb.officialCombat.totalDmg !== 'undefined') ? cb.officialCombat.totalDmg : '-'}</span>
          </div>
        </div>

        <!-- 生存生命 -->
        <div class="compare-stat-card">
          <div class="compare-stat-name">
            <span>额外生命</span>
            ${renderDiffBadge(hpDiff)}
          </div>
          <div class="compare-stat-values">
            <span class="compare-user-val">+${u.hp}</span>
            <span class="compare-base-val">官方: +${b.hp}</span>
          </div>
        </div>

        <!-- 冷却缩减 -->
        <div class="compare-stat-card">
          <div class="compare-stat-name">
            <span>冷却缩减</span>
            ${renderDiffBadge(cdrDiff, '%')}
          </div>
          <div class="compare-stat-values">
            <span class="compare-user-val">${u.cdr}%</span>
            <span class="compare-base-val">官方: ${b.cdr}%</span>
          </div>
        </div>
      `;
    }

    // 智能战术结论
    if (verdictBox) {
      const tokens = [];
      if (atkDiff > 20) tokens.push(`攻击高出 ${atkDiff}`);
      if (cdrDiff > 4) tokens.push(`冷缩领先 ${cdrDiff}%`);
      if (hpDiff < -400) tokens.push(`生命偏低 ${Math.abs(hpDiff)} 点`);
      if (hpDiff > 400) tokens.push(`血量多出 ${hpDiff} 点`);

      let text = `相较官方【${activePreset.genre || activePreset.title || '推荐方案'}】：`;
      if (diff.pros && diff.pros.length > 0) {
        text += `自选方案${diff.pros[0].title}（${diff.pros[0].desc}）。`;
      } else if (tokens.length > 0) {
        text += `自选方案${tokens.join('，')}。`;
      } else {
        text += '自选出装与官方推荐数值基本相当。';
      }
      verdictBox.innerText = text;
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
    const matchRole = (currentHeroModalFilter === '全部') || (h.role && h.role.includes(currentHeroModalFilter));
    const matchQuery = !query || h.cname.toLowerCase().includes(query) || (h.title && h.title.toLowerCase().includes(query));
    return matchRole && matchQuery;
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
