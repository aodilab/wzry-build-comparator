// ==============================================================================
// 王者出装箱 ｜ 自选方案 VS 王者推荐方案 对比推演弹窗 (app_synergy.js)
// 专注：王者推荐方案(展示6件出装)、3列全维数值Diff表、核心机制差异与连招实战总伤害推演
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 350 行以内
// ==============================================================================

let currentBenchmarkPresetId = 'official_1';

function switchBenchmarkPreset(presetId) {
  currentBenchmarkPresetId = presetId;
  renderSynergyContent();
}

function openSynergyModal() {
  const modal = document.getElementById('synergyModalOverlay') || document.getElementById('synergyModal');
  if (!modal) return;
  modal.classList.add('active');
  if (document.body) {
    document.body.style.overflow = 'hidden';
    document.body.style.touchAction = 'none';
  }
  renderSynergyContent();
}

function closeSynergyModal(e) {
  if (e && e.target && e.target !== e.currentTarget && !e.target.classList.contains('arcana-modal-close') && !e.target.closest('.arcana-modal-close')) {
    return;
  }
  const modal = document.getElementById('synergyModalOverlay') || document.getElementById('synergyModal');
  if (modal) modal.classList.remove('active');
  if (document.body) {
    document.body.style.overflow = '';
    document.body.style.touchAction = '';
  }
}

function renderSynergyContent() {
  const hero = (typeof currentHero !== 'undefined' && currentHero) ? currentHero : HEROES_DATA[0];
  const slots = (typeof currentSlots !== 'undefined' && currentSlots) ? currentSlots : [];

  const aliasMap = {
    '强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴',
    '破军': '强者破军', '破晓': '仁者破晓', '贤者之书': '贤者天书', '急速战靴': '急速之靴'
  };
  const effItems = [];
  slots.forEach(s => {
    const targetName = s.item_name || s;
    const it = ITEMS_DATA.find(i => i.item_name === targetName) || 
               ITEMS_DATA.find(i => i.item_name === aliasMap[targetName]) ||
               (s.stats ? s : null);
    if (it) effItems.push(it);
  });

  const avatar = document.getElementById('synergyHeroAvatar');
  const name = document.getElementById('synergyHeroName');
  const role = document.getElementById('synergyHeroRole');
  const sub = document.getElementById('synergyHeroSub');
  if (avatar) avatar.src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${hero.ename}/${hero.ename}.jpg`;
  if (name) name.innerText = `${hero.cname} 自选 VS 王者推荐`;
  if (role) {
    if (window.innerWidth <= 768) role.style.display = 'none';
    else { role.innerText = `${hero.lane || ''} · ${hero.role || ''}`; role.style.display = ''; }
  }
  if (sub) {
    sub.innerText = `自选 ${effItems.length}/6 件 · 对标王者官方推荐出装机制全维对比`;
  }

  // 1. 获取王者推荐方案列表与当前选中的基准 (联动当前选中的主玩分路)
  const currentLane = (typeof currentHeroActiveLane !== 'undefined') ? currentHeroActiveLane : (hero.lane || '对抗路');
  const officialPresets = typeof getHeroOfficialPresets === 'function' ? getHeroOfficialPresets(hero, currentLane) : [];
  const activePreset = officialPresets.find(p => p.id === currentBenchmarkPresetId) || officialPresets[0] || { items: [] };

  // 2. 调用全维对比核心引擎
  const uArc = (typeof currentArcana !== 'undefined') ? currentArcana : {};
  const diffResult = typeof compareUserBuildWithOfficial === 'function'
    ? compareUserBuildWithOfficial(effItems, activePreset, hero, uArc)
    : { tableRows: [], pros: [], cons: [], uStat: {}, bStat: {}, isArcanaSame: true, arcanaDiffNotice: '', comboResult: null };

  const bodyEl = document.getElementById('synergyModalScroll') || document.getElementById('synergyModalBody');
  if (!bodyEl) return;

  const isEmp = effItems.length === 0;

  // 3. 渲染王者推荐方案 (iOS 原生分段控制器切换方案 + 100% 容器宽度单卡片，彻底消灭横向滚动与晃动)
  const presetsHtml = `
    <div class="benchmark-section">
      <div class="benchmark-header-row">
        <span class="benchmark-header-title">王者推荐方案</span>
        <span class="benchmark-hint">点击标签切换对标</span>
      </div>
      <div class="benchmark-segmented-bar">
        ${officialPresets.map(p => `
          <div class="benchmark-tab-item ${p.id === activePreset.id ? 'active' : ''}" onclick="switchBenchmarkPreset('${p.id}')">
            ${p.title}
          </div>
        `).join('')}
      </div>
      <div class="benchmark-active-card">
        ${activePreset.desc ? `<div class="benchmark-active-desc">${activePreset.desc}</div>` : ''}
        <div class="benchmark-items-wrap">
          ${(activePreset.items || []).map(it => `
            <div class="benchmark-mini-item" title="${it.item_name}">
              <img src="${it.icon || 'https://game.gtimg.cn/images/yxzj/img201606/itemimg/' + it.item_id + '.jpg'}" alt="${it.item_name}" class="benchmark-mini-img" onerror="this.style.opacity='0.5'">
              <span class="benchmark-mini-name">${it.item_name}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  // 4. 渲染铭文差异提示 (若一致则不显示，若不一致显示综合说明)
  const arcanaNoticeHtml = (!diffResult.isArcanaSame && diffResult.arcanaDiffNotice) ? `
    <div class="arcana-diff-alert">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0071e3" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      <span>${diffResult.arcanaDiffNotice}</span>
    </div>
  ` : '';

  // 5. 渲染 3 列数值对照表 (属性指标 ｜ 自选数值 ｜ 王者推荐数值 ｜ 差异对比)
  const diffTableHtml = `
    <div class="diff-table-card">
      <div class="diff-table-header">
        <div class="col-metric">属性指标</div>
        <div class="col-user">自选数值</div>
        <div class="col-base">王者推荐数值</div>
        <div class="col-diff">相比推荐差异</div>
      </div>
      <div class="diff-table-body">
        ${diffResult.tableRows.map(r => `
          <div class="diff-table-row">
            <div class="col-metric">${r.label}</div>
            <div class="col-user font-bold">${r.userDisplay}</div>
            <div class="col-base">${r.baseDisplay}</div>
            <div class="col-diff">
              <span class="diff-status-pill status-${r.status}">${r.diffStr}</span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  // 6. 渲染核心装备机制效果差异 (PROS / CONS)
  const mechanicsHtml = `
    <div class="mechanics-diff-section">
      <div class="mechanics-section-title">核心装备机制效果差异</div>
      ${diffResult.pros.length > 0 ? `
        <div class="mechanic-group">
          <div class="mechanic-group-title pro-group-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            自选专属效果优势 (领先机制)
          </div>
          <div class="mechanic-items-list">
            ${diffResult.pros.map(p => `
              <div class="mechanic-card pro-card">
                <div class="mechanic-card-header">
                  <span class="mechanic-pill pro-pill">优势</span>
                  <span class="mechanic-card-title">${p.title}</span>
                </div>
                <div class="mechanic-card-desc">${p.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      ${diffResult.cons.length > 0 ? `
        <div class="mechanic-group" style="margin-top: 10px;">
          <div class="mechanic-group-title con-group-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            相比推荐缺失效果 (短板预警)
          </div>
          <div class="mechanic-items-list">
            ${diffResult.cons.map(c => `
              <div class="mechanic-card con-card">
                <div class="mechanic-card-header">
                  <span class="mechanic-pill con-pill">短板</span>
                  <span class="mechanic-card-title">${c.title}</span>
                </div>
                <div class="mechanic-card-desc">${c.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      ${diffResult.pros.length === 0 && diffResult.cons.length === 0 ? `
        <div class="mechanic-empty-box">当前出装的核心机制与王者推荐基本契合，主要体现在基础数值维度的增减。</div>
      ` : ''}
    </div>
  `;

  // 7. 渲染实战连招总伤害与技能回复推演 (Requirement 9)
  let comboHtml = '';
  if (diffResult.comboResult) {
    const cb = diffResult.comboResult;
    const dmgDiff = cb.dmgDiff;
    const healDiff = cb.healDiff;

    let dmgDiffStr = '持平';
    let dmgDiffCls = 'status-equal';
    if (dmgDiff > 0) { dmgDiffStr = `+${dmgDiff} (爆发领先)`; dmgDiffCls = 'status-plus'; }
    else if (dmgDiff < 0) { dmgDiffStr = `${dmgDiff} (爆发落后)`; dmgDiffCls = 'status-minus'; }

    let healDiffStr = '持平';
    let healDiffCls = 'status-equal';
    if (healDiff > 0) { healDiffStr = `+${healDiff} HP (续航更优)`; healDiffCls = 'status-plus'; }
    else if (healDiff < 0) { healDiffStr = `${healDiff} HP (续航偏弱)`; healDiffCls = 'status-minus'; }

    comboHtml = `
      <div class="combo-calc-section">
        <div class="combo-calc-header">
          <div class="combo-calc-title">实战连招总伤害与技能回复推演</div>
          <div class="combo-calc-tag">${cb.comboName}</div>
        </div>

        <div class="combo-metrics-grid">
          <div class="combo-metric-card">
            <span class="combo-metric-label">连招全套理论总伤害</span>
            <div class="combo-metric-values">
              <span class="combo-metric-val">${cb.userCombat.totalDmg}</span>
              <span class="combo-metric-sub">推荐方案: ${cb.officialCombat.totalDmg}</span>
            </div>
            <div class="combo-diff-pill ${dmgDiffCls}">${dmgDiffStr}</div>
          </div>

          <div class="combo-metric-card">
            <span class="combo-metric-label">连招技能吸血与护盾回复</span>
            <div class="combo-metric-values">
              <span class="combo-metric-val">+${cb.userCombat.totalHeal} HP</span>
              <span class="combo-metric-sub">推荐方案: +${cb.officialCombat.totalHeal} HP</span>
            </div>
            <div class="combo-diff-pill ${healDiffCls}">${healDiffStr}</div>
          </div>
        </div>

        <div class="combo-steps-box">
          <div class="combo-steps-title">技能与普攻分步伤害拆解 (自选配装)</div>
          ${cb.steps.map((st, idx) => `
            <div class="combo-step-row">
              <div class="combo-step-num">${idx + 1}</div>
              <div class="combo-step-info">
                <div class="combo-step-name">${st.name}</div>
                <div class="combo-step-desc">${st.desc}</div>
              </div>
              <div class="combo-step-stat">
                <span class="combo-step-dmg">${st.dmg} 伤</span>
                ${st.heal > 0 ? `<span class="combo-step-heal">+${st.heal} 回复</span>` : ''}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  // 8. 组装整体内容
  bodyEl.innerHTML = `
    <div class="synergy-view-container">
      ${presetsHtml}
      ${arcanaNoticeHtml}
      <div class="synergy-section-title">自选方案 VS 王者推荐方案 数值对照</div>
      ${diffTableHtml}
      ${mechanicsHtml}
      ${comboHtml}
    </div>
  `;
}
