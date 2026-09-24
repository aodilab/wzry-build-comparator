// ==============================================================================
// 王者出装箱 ｜ 局内六神装配装沙盒 - 战术协同弹窗与视图装配层 (app_synergy.js)
// 专注 UI 交互生命周期、DOM 挂载与 Canvas 雷达图渲染
// 评分计算下沉至 synergy_evaluator.js，实操连招下沉至 synergy_combos.js
// ==============================================================================
function openSynergyModal() {
  const modal = document.getElementById('synergyModalOverlay') || document.getElementById('synergyModal');
  if (!modal) return;
  modal.classList.add('active');
  if (document.body) document.body.style.overflow = 'hidden';
  // 渲染内容
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
  // 汇总当前装备 (支持官方名与常用别名双向自适应容错)
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
  // 同步模态框顶部英雄概览
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
      ? `${effItems.length}/6件已装配 · ${effItems.length > 0 ? '战术协同' : '待装配推演'}`
      : `装备栏: ${effItems.length} / 6 件已装配 ｜ 技能机制与被动乘区深度诊断`;
  }
  // 1. 技能卡片列表 HTML 组装
  let skillsCardsHtml = '';
  skills.forEach((sk, idx) => {
    const skType = sk.type || (idx === 0 || (sk.name && sk.name.includes('被动')) ? '被动技能' : `主动技能 ${idx}`);
    const isPassive = skType.includes('被动') || (sk.name && sk.name.includes('被动'));
    const badgeColor = isPassive ? '#ff9500' : '#0071e3';
    // 阶梯冷却展示
    let cdDisplay = sk.cd || '无冷却';
    if (cdDisplay.includes('｜')) {
      const parts = cdDisplay.split('｜').map(p => p.trim());
      cdDisplay = parts.join(' <span style="color:var(--text-tertiary);margin:0 2px;">/</span> ');
    }
    // 标签展示
    let tagsHtml = '';
    (sk.tags || []).forEach(t => {
      let tColor = 'var(--text-secondary)';
      let tBg = 'rgba(0,0,0,0.04)';
      if (t === '技能回血') { tColor = '#34c759'; tBg = 'rgba(52, 199, 89, 0.1)'; }
      else if (t === '硬控') { tColor = '#ff3b30'; tBg = 'rgba(255, 59, 48, 0.1)'; }
      else if (t === '真实伤害') { tColor = '#af52de'; tBg = 'rgba(175, 82, 222, 0.1)'; }
      else if (t === '免伤' || t === '护盾') { tColor = '#ff9500'; tBg = 'rgba(255, 149, 0, 0.1)'; }
      else if (t === '强化普攻') { tColor = '#0071e3'; tBg = 'rgba(0, 113, 227, 0.1)'; }
      tagsHtml += `<span class="synergy-tag" style="color:${tColor};background:${tBg};border-color:transparent;">${t}</span>`;
    });
    skillsCardsHtml += `
      <div class="synergy-skill-card">
        <div class="synergy-skill-header">
          <div class="synergy-skill-name-wrap">
            <span class="synergy-type-badge" style="background:${badgeColor}">${skType}</span>
            <span class="synergy-skill-name">${sk.name || `技能 ${idx + 1}`}</span>
          </div>
          <div class="synergy-skill-cd">CD: ${cdDisplay}</div>
        </div>
        <div class="synergy-skill-desc">${sk.desc || '暂无描述'}</div>
        ${tagsHtml ? `<div class="synergy-tags-row">${tagsHtml}</div>` : ''}
      </div>
    `;
  });

  // 2. 调用解耦评分引擎 (synergy_evaluator.js)
  const cappedCdr = typeof calculateCompositeStats === 'function' ? calculateCompositeStats().cdr : 0;
  const evalResult = calculateSynergyScore(hero, effItems, slots, skills, cappedCdr);
  const { score, rankBadge, rankColor, rankSub, penaltyReasons, synergyContext, radarStats, insights } = evalResult;

  // 3. 装备专属机制联动卡片 (由评估引擎动态输出)
  const svgStar = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.26 12 2"></polygon></svg>';
  const svgShield = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>';
  const svgHeart = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>';
  
  let synergyLinksHtml = '';
  const effInsights = (insights && insights.length > 0) ? insights : [
    { tag: '基础属性协同', item: '属性装配', desc: '当前装备提供稳固的攻防基础数值，建议补齐核心质变神装。' }
  ];
  effInsights.forEach(item => {
    synergyLinksHtml += `
      <div class="synergy-link-card">
        <div class="synergy-link-icon-box">${svgShield}</div>
        <div class="synergy-link-content">
          <div class="synergy-link-title">
            <span>${item.tag} · ${item.item}</span>
            <span class="synergy-link-sub">${item.item}</span>
          </div>
          <div class="synergy-link-desc">${item.desc}</div>
        </div>
      </div>
    `;
  });

  // 4. 调用解耦连招策略引擎 (synergy_combos.js)
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

  // 5. 组装完整模态框 HTML
  const bodyEl = document.getElementById('synergyModalScroll') || document.getElementById('synergyModalBody');
  if (!bodyEl) return;

  if (window.innerWidth <= 768) {
    const isEmp = effItems.length === 0;
    const finalScore = isEmp ? 0 : score;
    const finalBadge = isEmp ? '未选装' : rankBadge.split(' ')[0];
    const finalTitle = isEmp ? '待装配推演' : rankBadge;
    const finalDesc = isEmp ? '暂未选配装备，请点击一键神装或在下方挑选装备入槽。' : rankSub;
    const cardBorderColor = isEmp ? '#aeaeb2' : rankColor;

    const bVal = isEmp ? 20 : (radarStats ? (radarStats.burst || radarStats[0] || 20) : 20);
    const sVal = isEmp ? 20 : (radarStats ? (radarStats.survive || radarStats[1] || 20) : 20);
    const cVal = isEmp ? 20 : (radarStats ? (radarStats.control || radarStats[2] || 20) : 20);
    const mVal = isEmp ? 20 : (radarStats ? (radarStats.mobility || radarStats[3] || 20) : 20);
    const tVal = isEmp ? 20 : (radarStats ? (radarStats.sustain || radarStats[4] || 20) : 20);

    bodyEl.innerHTML = `
      <div class="synergy-mobile-container">
        <!-- 综合评分与战术评级 (对齐真机图 6) -->
        <div class="synergy-score-overview" style="border-left: 4px solid ${cardBorderColor};">
          <div class="score-overview-left">
            <div class="overview-score-num">${finalScore}分</div>
            <div class="overview-grade-tag" style="background:${isEmp ? '#8e8e93' : rankColor}">${finalBadge}</div>
          </div>
          <div class="score-overview-right">
            <div class="overview-summary-title">${finalTitle}</div>
            <div class="overview-summary-desc">${finalDesc}</div>
          </div>
        </div>
        <!-- 五维实战能力推演 (对齐真机图 6: 进度条) -->
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
        <!-- 英雄技能与机制矩阵 (对齐真机图 6) -->
        <div class="synergy-block-card">
          <div class="synergy-block-title">英雄技能与机制矩阵 (${skills.length}个技能)</div>
          <div class="modal-skills-list">
            ${skillsCardsHtml}
          </div>
        </div>
        ${!isEmp && synergyLinksHtml ? `
          <div class="synergy-block-card">
            <div class="synergy-block-title">核心被动机制全景联动 (${effItems.length}项已激活)</div>
            <div class="modal-insights-list">${synergyLinksHtml}</div>
          </div>
        ` : ''}
        ${!isEmp && comboHtml ? `
          <div class="synergy-block-card">
            <div class="synergy-block-title">实战连招与打法策略建议</div>
            <div class="modal-combo-list">${comboHtml}</div>
          </div>
        ` : ''}
      </div>
    `;
    return;
  }
  bodyEl.innerHTML = `
    <div class="synergy-container">
      <!-- 配装综合契合度总览 -->
      <div class="synergy-score-card">
        <div class="synergy-score-left">
          <div class="synergy-score-circle" style="border-color:${rankColor};box-shadow: 0 4px 20px ${rankColor}33;">
            <div class="synergy-score-num" style="color:${rankColor};">${score}</div>
            <div class="synergy-score-label">契合评分</div>
          </div>
          <div class="synergy-score-detail">
            <div class="synergy-score-badge" style="background:${rankColor}15;color:${rankColor};border: 1px solid ${rankColor}33;">${rankBadge}</div>
            <div class="synergy-score-sub">${rankSub}</div>
            ${penaltyReasons.length > 0 ? `
              <div class="synergy-penalty-box">
                <div class="synergy-penalty-title">诊断惩罚扣分明细：</div>
                ${penaltyReasons.map(r => `<div class="synergy-penalty-item">• ${r}</div>`).join('')}
              </div>
            ` : ''}
          </div>
        </div>
        <div class="synergy-radar-box">
          <canvas id="synergyRadarCanvas" width="160" height="160"></canvas>
          <div class="synergy-radar-legend">五维战力雷达图</div>
        </div>
      </div>
      <!-- 核心被动与装备机制质变联动 -->
      <div class="synergy-section-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
        装备专属机制与被动质变联动
      </div>
      <div class="synergy-links-list">
        ${synergyLinksHtml}
      </div>
      <!-- 官方技能权威成长梯队与机制明细 -->
      <div class="synergy-section-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.26 12 2"></polygon></svg>
        英雄技能机制与满级成长阶梯 (S34-S35 权威同步)
      </div>
      <div class="synergy-skills-grid">
        ${skillsCardsHtml}
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
  // 6. 异步渲染 Canvas 雷达图
  setTimeout(() => {
    drawSynergyRadar(radarStats, rankColor);
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
  const labels = ['爆发', '生存', '续航', '机动', '控场'];
  const sides = 5;
  ctx.clearRect(0, 0, w, h);
  // 绘制雷达网格背景
  for (let step = 1; step <= 4; step++) {
    const curR = (r / 4) * step;
    ctx.beginPath();
    for (let i = 0; i < sides; i++) {
      const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
      const x = cx + curR * Math.cos(angle);
      const y = cy + curR * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }
  // 绘制轴线与文字
  ctx.font = '10px -apple-system, sans-serif';
  ctx.fillStyle = 'var(--text-tertiary)';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (let i = 0; i < sides; i++) {
    const angle = (Math.PI * 2 / sides) * i - Math.PI / 2;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.stroke();
    const lx = cx + (r + 14) * Math.cos(angle);
    const ly = cy + (r + 14) * Math.sin(angle);
    ctx.fillText(labels[i], lx, ly);
  }
  // 绘制数据多边形
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
// 复制战术协同报告
function copySynergyReport() {
  const hero = (typeof currentHero !== 'undefined' && currentHero) ? currentHero : HEROES_DATA[0];
  const slots = (typeof currentSlots !== 'undefined' && currentSlots) ? currentSlots : [];
  const itemsText = slots.map(s => s.item_name).join(' + ') || '暂无装备';
  const text = `【王者出装箱 · 战术协同诊断报告】\n英雄：${hero.cname}（${hero.title || ''}）\n出装：${itemsText}\n状态：已完成机制核定与雷达评估\n报告源自：王者出装箱 (https://13253374290.github.io/wzry-knowledge-base/)`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      if (typeof showToast === 'function') showToast('战术协同报告已复制到剪贴板！');
      else alert('战术协同报告已复制！');
    });
  } else {
    alert(text);
  }
}
