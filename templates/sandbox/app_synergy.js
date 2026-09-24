// ==============================================================================
// 王者出装箱 ｜ 局内六神装配装沙盒 - 战术流派与实战优劣势剖析弹窗 (app_synergy.js)
// 专注：战术流派定性展示、实战核心优势PROS、潜在短板CONS、五维能力推演与连招指引
// ==============================================================================

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
  const skills = HERO_SKILLS_DATA[hero.cname] || [];
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
  if (name) {
    name.innerText = window.innerWidth <= 768 ? `${hero.cname} 战术机制深度推演` : hero.cname;
  }
  if (role) {
    if (window.innerWidth <= 768) {
      role.style.display = 'none';
    } else {
      role.innerText = `${hero.lane || ''} · ${hero.role || ''}`;
      role.style.display = '';
    }
  }
  if (sub) {
    sub.innerText = window.innerWidth <= 768
      ? `${effItems.length}/6件已装配 · ${effItems.length > 0 ? '实战流派推演' : '待装配推演'}`
      : `装备栏: ${effItems.length} / 6 件已装配 ｜ 实战流派定位与优劣势深度诊断`;
  }

  // 1. 调用评估引擎获取流派定性与优劣势
  const cappedCdr = typeof calculateCompositeStats === 'function' ? calculateCompositeStats().cdr : 0;
  const evalResult = calculateSynergyScore(hero, effItems, slots, skills, cappedCdr);
  const { tacticGenre, genreDesc, genreColor, pros, cons, radarStats, synergyContext } = evalResult;

  // 2. 调用连招策略引擎
  const comboSteps = generateComboSteps(hero, skills, synergyContext);
  let comboHtml = '';
  comboSteps.forEach((st, idx) => {
    comboHtml += `
      <div class="synergy-combo-item">
        <div class="synergy-combo-num">${idx + 1}</div>
        <div class="synergy-combo-text">${st}</div>
      </div>
    `;
  });

  const bodyEl = document.getElementById('synergyModalScroll') || document.getElementById('synergyModalBody');
  if (!bodyEl) return;

  const isEmp = effItems.length === 0;
  const finalGenre = isEmp ? '待选装推演' : tacticGenre;
  const finalDesc = isEmp ? '暂未选配装备，请点击一键神装或挑选装备入槽开始推演。' : genreDesc;
  const themeColor = isEmp ? '#8e8e93' : genreColor;

  const bVal = isEmp ? 20 : (radarStats ? (radarStats.burst || radarStats[0] || 20) : 20);
  const sVal = isEmp ? 20 : (radarStats ? (radarStats.survive || radarStats[1] || 20) : 20);
  const cVal = isEmp ? 20 : (radarStats ? (radarStats.control || radarStats[2] || 20) : 20);
  const mVal = isEmp ? 20 : (radarStats ? (radarStats.mobility || radarStats[3] || 20) : 20);
  const tVal = isEmp ? 20 : (radarStats ? (radarStats.sustain || radarStats[4] || 20) : 20);

  const prosList = (pros && pros.length > 0) ? pros : [
    { title: '基础三维属性稳固', desc: '所选装备提供稳定的基础攻防面板，支撑基础作战需求。' }
  ];
  const consList = (cons && cons.length > 0) ? cons : [
    { title: '走位与团战容错', desc: '实战中需防范长手英雄走位拉扯或高频连环硬控。' }
  ];

  // 移动端排版
  if (window.innerWidth <= 768) {
    bodyEl.innerHTML = `
      <div class="synergy-mobile-container">
        <!-- 战术流派定性大卡片 (替代生硬打分) -->
        <div class="synergy-score-overview" style="border-left: 4px solid ${themeColor};">
          <div class="score-overview-left">
            <span class="overview-genre-tag" style="background:${themeColor};">${isEmp ? '未选装' : '流派定位'}</span>
          </div>
          <div class="score-overview-right">
            <div class="overview-summary-title" style="color:${themeColor};">${finalGenre}</div>
            <div class="overview-summary-desc">${finalDesc}</div>
          </div>
        </div>

        <!-- 实战核心优势 (PROS - 优势在哪里) -->
        ${!isEmp ? `
          <div class="synergy-block-card">
            <div class="synergy-block-title pro-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
              实战核心优势剖析 (PROS)
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

          <!-- 潜在短板与防克制 (CONS - 劣势在哪里) -->
          <div class="synergy-block-card">
            <div class="synergy-block-title con-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
              潜在短板与防克制预警 (CONS)
            </div>
            <div class="synergy-points-box">
              ${consList.map(c => `
                <div class="point-card con-card">
                  <div class="point-header">
                    <span class="point-badge con-badge">劣势</span>
                    <span class="point-title">${c.title}</span>
                  </div>
                  <div class="point-desc">${c.desc}</div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- 五维实战能力推演 (平滑进度条) -->
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
                <div class="radar-track">
                  <div class="radar-fill" style="width: ${r.val}%;"></div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 实战核心打法与最佳连招 -->
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
      <!-- 战术流派定性大卡片 -->
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

      <!-- 实战核心优势与潜在短板深度剖析 (PROS & CONS) -->
      <div class="synergy-pros-cons-grid">
        <div class="synergy-pros-col">
          <div class="synergy-section-title" style="color:#2e7d32;display:flex;align-items:center;gap:6px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            实战核心优势剖析 (PROS)
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
            潜在短板与防克制预警 (CONS)
          </div>
          <div class="synergy-points-box">
            ${consList.map(c => `
              <div class="point-card con-card">
                <div class="point-header">
                  <span class="point-badge con-badge">劣势</span>
                  <span class="point-title">${c.title}</span>
                </div>
                <div class="point-desc">${c.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- 实战核心连招与打法指引 -->
      <div class="synergy-section-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
        实战核心打法与最佳连招流派
      </div>
      <div class="synergy-combo-box">
        ${comboHtml}
      </div>
    </div>
  `;

  setTimeout(() => {
    drawSynergyRadar(radarStats, themeColor);
  }, 50);
}

// 绘制五维雷达图
function drawSynergyRadar(stats, primaryColor) {
  const canvas = document.getElementById('synergyRadarCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const r = 55;
  const labels = ['爆发', '生存', '循环', '机动', '控场'];
  const sides = 5;
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = '#e5e5ea';
  ctx.lineWidth = 1;
  for (let s = 1; s <= 4; s++) {
    const curR = (r / 4) * s;
    ctx.beginPath();
    for (let i = 0; i < sides; i++) {
      const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
      const x = cx + curR * Math.cos(angle);
      const y = cy + curR * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
  ctx.fillStyle = '#8e8e93';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (let i = 0; i < sides; i++) {
    const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
    ctx.stroke();
    const lx = cx + (r + 14) * Math.cos(angle);
    const ly = cy + (r + 14) * Math.sin(angle);
    ctx.fillText(labels[i], lx, ly);
  }

  ctx.beginPath();
  for (let i = 0; i < sides; i++) {
    const val = Math.max(10, Math.min(100, stats[i] || 20));
    const curR = (val / 100) * r;
    const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
    const x = cx + curR * Math.cos(angle);
    const y = cy + curR * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fillStyle = primaryColor + '33';
  ctx.fill();
  ctx.strokeStyle = primaryColor;
  ctx.lineWidth = 2;
  ctx.stroke();
}
