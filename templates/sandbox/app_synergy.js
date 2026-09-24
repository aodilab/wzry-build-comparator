// ==============================================================================
// 王者出装箱 ｜ 局内六神装配装沙盒 - 官方出装横向对比与机制推演弹窗 (app_synergy.js)
// 专注：多套官方经典出装对标切换、全维数值Diff对比、核心机制差异(PROS/CONS)与实战连招
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
  if (document.body) document.body.style.overflow = 'hidden';
  renderSynergyContent();
}

function closeSynergyModal(e) {
  if (e && e.target && e.target !== e.currentTarget && !e.target.classList.contains('arcana-modal-close') && !e.target.closest('.arcana-modal-close')) {
    return;
  }
  const modal = document.getElementById('synergyModalOverlay') || document.getElementById('synergyModal');
  if (modal) modal.classList.remove('active');
  if (document.body) document.body.style.overflow = '';
}

function renderSynergyContent() {
  const hero = (typeof currentHero !== 'undefined' && currentHero) ? currentHero : HEROES_DATA[0];
  const skills = (typeof HERO_SKILLS_DATA !== 'undefined' && HERO_SKILLS_DATA[hero.cname]) ? HERO_SKILLS_DATA[hero.cname] : [];
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
  if (name) name.innerText = window.innerWidth <= 768 ? `${hero.cname} 实战配装深度推演` : hero.cname;
  if (role) {
    if (window.innerWidth <= 768) role.style.display = 'none';
    else { role.innerText = `${hero.lane || ''} · ${hero.role || ''}`; role.style.display = ''; }
  }
  if (sub) {
    sub.innerText = window.innerWidth <= 768
      ? `${effItems.length}/6件已配 · 对标官方出装全维横向对比`
      : `装备栏: ${effItems.length} / 6 件已装配 ｜ 对标王者官方推荐出装全维机制对比`;
  }

  // 1. 获取官方推荐预设方案与当前选中的基准
  const officialPresets = typeof getHeroOfficialPresets === 'function' ? getHeroOfficialPresets(hero) : [];
  const activePreset = officialPresets.find(p => p.id === currentBenchmarkPresetId) || officialPresets[0] || { items: [] };

  // 2. 调用全维横向对比引擎
  const diffResult = typeof compareUserBuildWithOfficial === 'function'
    ? compareUserBuildWithOfficial(effItems, activePreset, hero)
    : { numDiff: {}, pros: [], cons: [], uStat: {}, bStat: {} };

  // 3. 基础流派定性与能力雷达
  const cappedCdr = typeof calculateCompositeStats === 'function' ? calculateCompositeStats().cdr : 0;
  const evalResult = typeof calculateSynergyScore === 'function'
    ? calculateSynergyScore(hero, effItems, slots, skills, cappedCdr)
    : { tacticGenre: '常规平衡流派', genreDesc: '', genreColor: '#0071e3', radarStats: {} };
  const { tacticGenre, genreDesc, genreColor, radarStats, synergyContext } = evalResult;

  // 4. 连招指引
  const comboSteps = typeof generateComboSteps === 'function' ? generateComboSteps(hero, skills, synergyContext) : [];
  let comboHtml = '';
  comboSteps.forEach((st, idx) => {
    comboHtml += `<div class="synergy-combo-item"><div class="synergy-combo-num">${idx + 1}</div><div class="synergy-combo-text">${st}</div></div>`;
  });

  const bodyEl = document.getElementById('synergyModalScroll') || document.getElementById('synergyModalBody');
  if (!bodyEl) return;

  const isEmp = effItems.length === 0;
  const finalGenre = isEmp ? '待选装推演' : tacticGenre;
  const finalDesc = isEmp ? '暂未选配装备，请点击“一键神装”或自选装备后与官方方案横向对比。' : genreDesc;
  const themeColor = isEmp ? '#8e8e93' : genreColor;

  const prosList = (diffResult.pros && diffResult.pros.length > 0) ? diffResult.pros : evalResult.pros;
  const consList = (diffResult.cons && diffResult.cons.length > 0) ? diffResult.cons : evalResult.cons;

  // 渲染官方预设 Tab 选择器
  const presetsTabsHtml = `
    <div class="benchmark-section">
      <div class="benchmark-header-row">
        <span>对标官方基准出装</span>
        <span class="benchmark-hint">点击可切换对比方案</span>
      </div>
      <div class="benchmark-presets-grid" style="grid-template-columns: repeat(${Math.max(1, officialPresets.length)}, 1fr);">
        ${officialPresets.map(p => `
          <div class="benchmark-preset-card ${p.id === activePreset.id ? 'active' : ''}" onclick="switchBenchmarkPreset('${p.id}')">
            <div class="benchmark-preset-top">
              <span class="benchmark-preset-tag">${p.tag}</span>
              ${p.id === activePreset.id ? '<span style="font-size:10px;color:#0071e3;font-weight:700;">对标中</span>' : ''}
            </div>
            <div class="benchmark-preset-name">${p.title}</div>
            <div class="benchmark-preset-desc">${p.desc}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  // 渲染全维数值 Diff 对比卡片
  function renderDiffItem(key, label) {
    const it = diffResult.numDiff[key] || { user: 0, base: 0, diff: 0 };
    const diffVal = typeof it.diffVal !== 'undefined' ? it.diffVal : it.diff;
    let pillClass = 'diff-pill-equal';
    let pillText = '持平';
    if (diffVal > 0) {
      pillClass = 'diff-pill-plus';
      pillText = `+${diffVal}${key.includes('cdr') || key.includes('crit') ? '%' : (key === 'gold' ? 'g' : '')}`;
    } else if (diffVal < 0) {
      pillClass = 'diff-pill-minus';
      pillText = `${diffVal}${key.includes('cdr') || key.includes('crit') ? '%' : (key === 'gold' ? 'g' : '')}`;
    }
    return `
      <div class="diff-metric-card">
        <span class="diff-metric-label">${label}</span>
        <div class="diff-metric-values">
          <span class="diff-metric-user">${it.user}</span>
          <span class="diff-pill ${pillClass}">${pillText}</span>
        </div>
      </div>
    `;
  }

  const diffGridHtml = `
    <div class="diff-metrics-grid">
      ${renderDiffItem('ad', '物理攻击')}
      ${renderDiffItem('ap', '法术攻击')}
      ${renderDiffItem('hp', '额外生命')}
      ${renderDiffItem('pdef', '物理防御')}
      ${renderDiffItem('mdef', '法术防御')}
      ${renderDiffItem('cdr', '最终冷缩')}
      ${renderDiffItem('crit', '暴击率')}
      ${renderDiffItem('gold', '六神总价')}
    </div>
  `;

  // 五维能力推演条
  const bVal = isEmp ? 20 : (radarStats ? (radarStats.burst || 20) : 20);
  const sVal = isEmp ? 20 : (radarStats ? (radarStats.survive || 20) : 20);
  const cVal = isEmp ? 20 : (radarStats ? (radarStats.control || 20) : 20);
  const mVal = isEmp ? 20 : (radarStats ? (radarStats.mobility || 20) : 20);
  const tVal = isEmp ? 20 : (radarStats ? (radarStats.sustain || 20) : 20);

  // 移动端排版
  if (window.innerWidth <= 768) {
    bodyEl.innerHTML = `
      <div class="synergy-mobile-container">
        <!-- 战术流派定性大卡片 -->
        <div class="synergy-score-overview" style="border-left: 4px solid ${themeColor};">
          <div class="score-overview-left">
            <span class="overview-genre-tag" style="background:${themeColor};">${isEmp ? '未选装' : '流派定位'}</span>
          </div>
          <div class="score-overview-right">
            <div class="overview-summary-title" style="color:${themeColor};">${finalGenre}</div>
            <div class="overview-summary-desc">${finalDesc}</div>
          </div>
        </div>

        <!-- 官方基准方案切换 Tabs -->
        ${presetsTabsHtml}

        <!-- 全维数值 Diff 仪表盘 -->
        <div class="synergy-block-card">
          <div class="synergy-block-title" style="display:flex;justify-content:space-between;align-items:center;">
            <span>相较官方方案数值对比</span>
            <span style="font-size:11px;color:var(--text-secondary);font-weight:normal;">绿色为高出 · 红色为落后</span>
          </div>
          ${diffGridHtml}
        </div>

        <!-- 核心机制优势 (PROS) -->
        ${!isEmp ? `
          <div class="synergy-block-card">
            <div class="synergy-block-title pro-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
              实战核心机制优势 (PROS)
            </div>
            <div class="synergy-points-box">
              ${prosList.map(p => `
                <div class="point-card pro-card">
                  <div class="point-header">
                    <span class="point-badge pro-badge">优势</span>
                    <span class="point-title">${p.title}</span>
                  </div>
                  <div class="point-desc">${p.desc}</div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- 潜在机制短板 (CONS) -->
          <div class="synergy-block-card">
            <div class="synergy-block-title con-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
              相较官方潜在短板预警 (CONS)
            </div>
            <div class="synergy-points-box">
              ${consList.map(c => `
                <div class="point-card con-card">
                  <div class="point-header">
                    <span class="point-badge con-badge">短板</span>
                    <span class="point-title">${c.title}</span>
                  </div>
                  <div class="point-desc">${c.desc}</div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- 五维实战能力推演 -->
        <div class="synergy-block-card">
          <div class="synergy-block-title">实战能力五维推演</div>
          <div class="radar-bars-grid">
            ${[
              { label: '输出爆发', val: bVal },
              { label: '生存抗伤', val: sVal },
              { label: '技能循环', val: cVal },
              { label: '机动拉扯', val: mVal },
              { label: '控制留人', val: tVal }
            ].map(r => `
              <div class="radar-bar-item">
                <div class="radar-bar-label-row">
                  <span class="radar-label">${r.label}</span>
                  <span class="radar-val">${r.val}%</span>
                </div>
                <div class="radar-track"><div class="radar-fill" style="width: ${r.val}%;"></div></div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 实战连招与打法指引 -->
        ${!isEmp && comboHtml ? `
          <div class="synergy-block-card">
            <div class="synergy-block-title">实战连招与打法策略指引</div>
            <div class="modal-combo-list">${comboHtml}</div>
          </div>
        ` : ''}
      </div>
    `;
    return;
  }

  // 桌面端排版
  bodyEl.innerHTML = `
    <div class="synergy-container">
      <div class="synergy-score-card">
        <div class="synergy-score-left">
          <div class="synergy-score-circle" style="border-color:${themeColor};box-shadow: 0 4px 20px ${themeColor}33;">
            <div class="synergy-score-num" style="color:${themeColor};font-size:20px;">${isEmp ? '待配' : '流派'}</div>
            <div class="synergy-score-label">战术定位</div>
          </div>
          <div class="synergy-score-detail">
            <div class="synergy-score-badge" style="background:${themeColor}15;color:${themeColor};border: 1px solid ${themeColor}33;font-size:14px;padding:4px 10px;">${finalGenre}</div>
            <div class="synergy-score-sub" style="font-size:12.5px;margin-top:6px;line-height:1.5;">${finalDesc}</div>
          </div>
        </div>
        <div class="synergy-radar-box">
          <canvas id="synergyRadarCanvas" width="160" height="160"></canvas>
          <div class="synergy-radar-legend">五维战力雷达图</div>
        </div>
      </div>

      <!-- 官方基准方案切换 Tabs -->
      ${presetsTabsHtml}

      <!-- 全维数值横向 Diff 对比卡片 -->
      <div class="synergy-section-title" style="margin-top:10px;margin-bottom:8px;font-size:14px;font-weight:700;">相较官方基准出装数值横向比对</div>
      ${diffGridHtml}

      <!-- 核心机制优势与潜在短板 -->
      <div class="synergy-pros-cons-grid">
        <div class="synergy-pros-col">
          <div class="synergy-section-title" style="color:#2e7d32;display:flex;align-items:center;gap:6px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            实战核心机制优势 (PROS)
          </div>
          <div class="synergy-points-box">
            ${prosList.map(p => `
              <div class="point-card pro-card">
                <div class="point-header">
                  <span class="point-badge pro-badge">优势</span>
                  <span class="point-title">${p.title}</span>
                </div>
                <div class="point-desc">${p.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
        <div class="synergy-cons-col">
          <div class="synergy-section-title" style="color:#d97706;display:flex;align-items:center;gap:6px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            相较官方潜在短板预警 (CONS)
          </div>
          <div class="synergy-points-box">
            ${consList.map(c => `
              <div class="point-card con-card">
                <div class="point-header">
                  <span class="point-badge con-badge">短板</span>
                  <span class="point-title">${c.title}</span>
                </div>
                <div class="point-desc">${c.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- 实战核心打法与最佳连招 -->
      ${!isEmp && comboHtml ? `
        <div class="synergy-section-title" style="margin-top:14px;margin-bottom:8px;font-size:14px;font-weight:700;">实战连招与打法策略指引</div>
        <div class="modal-combo-list">${comboHtml}</div>
      ` : ''}
    </div>
  `;

  // 渲染桌面端雷达图
  const canvas = document.getElementById('synergyRadarCanvas');
  if (canvas && typeof drawSynergyRadar === 'function') {
    drawSynergyRadar(canvas, radarStats, themeColor);
  }
}
