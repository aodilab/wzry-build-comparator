function getColorTotalCount(colorKey) {
  const map = currentArcana[colorKey] || {};
  return Object.values(map).reduce((sum, val) => sum + val, 0);
}

function renderArcanaBar() {
  const container = document.getElementById('arcanaChipsBar');
  if (!container) return;
  container.innerHTML = '';

  const colors = [
    { key: 'red', name: '红', cls: 'arcana-chip-red' },
    { key: 'green', name: '绿', cls: 'arcana-chip-green' },
    { key: 'blue', name: '蓝', cls: 'arcana-chip-blue' }
  ];

  colors.forEach(c => {
    const map = currentArcana[c.key] || {};
    const entries = Object.entries(map).filter(([_, cnt]) => cnt > 0);
    const totalCount = getColorTotalCount(c.key);
    const chip = document.createElement('div');
    chip.className = `arcana-chip ${c.cls}`;

    if (entries.length === 0) {
      chip.innerHTML = `<span>${c.name}: 未配置</span>`;
    } else {
      // 找到颗数最多的铭文用来展示图标
      entries.sort((a, b) => b[1] - a[1]);
      const mainArc = ARCANA_DATA[entries[0][0]] || {};
      const label = entries.map(([name, count]) => `${count}${name}`).join(' · ');
      chip.title = `${c.name}色铭文 (${totalCount}/10颗): ` + entries.map(([name, count]) => `${name} ×${count}`).join(' ｜ ');
      chip.innerHTML = `
        <img class="arcana-chip-img" src="${mainArc.icon || ''}" onerror="this.style.display='none'">
        <span>${label}</span>
      `;
    }
    container.appendChild(chip);
  });
}

let currentArcanaMobileTab = 'red';

function switchArcanaMobileTab(tab) {
  currentArcanaMobileTab = tab;
  renderArcanaModal();
}

function applyArcanaPreset(name) {
  if (name === '官方推荐') {
    initHeroArcana(currentHero);
  } else if (name === '物理百穿') {
    currentArcana = { red: { '异变': 10 }, green: { '鹰眼': 10 }, blue: { '隐匿': 10 } };
  } else if (name === '暴击流') {
    currentArcana = { red: { '无双': 3, '祸源': 7 }, green: { '鹰眼': 10 }, blue: { '夺萃': 10 } };
  } else if (name === '攻速暴击') {
    currentArcana = { red: { '红月': 10 }, green: { '鹰眼': 10 }, blue: { '狩猎': 10 } };
  } else if (name === '法术爆发') {
    currentArcana = { red: { '梦魇': 10 }, green: { '心眼': 10 }, blue: { '狩猎': 10 } };
  } else if (name === '坦克千血') {
    currentArcana = { red: { '宿命': 10 }, green: { '虚空': 10 }, blue: { '调和': 10 } };
  }
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function openArcanaModal() {
  const overlay = document.getElementById('arcanaModalOverlay');
  if (!overlay) return;
  overlay.classList.add('active');
  if (document.body) {
    document.body.style.overflow = 'hidden';
    document.body.style.touchAction = 'none';
  }
  const sub = document.getElementById('arcanaModalSub');
  if (sub) {
    sub.innerText = window.innerWidth <= 768 
      ? '各色满配10颗 · 支持微调混搭' 
      : `【${currentHero.cname || ''}】铭文方案，支持自由增减颗数混搭，修改后立即实时重新演算面板`;
  }
  renderArcanaModal();
}

function closeArcanaModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('arcana-modal-close') && !e.target.closest('.arcana-modal-close')) return;
  const overlay = document.getElementById('arcanaModalOverlay');
  if (overlay) overlay.classList.remove('active');
  if (document.body) {
    document.body.style.overflow = '';
    document.body.style.touchAction = '';
  }
}

function renderArcanaModal() {
  const body = document.getElementById('arcanaModalBody');
  if (!body) return;
  body.innerHTML = '';

  if (window.innerWidth <= 768) {
    const rTot = getColorTotalCount('red');
    const gTot = getColorTotalCount('green');
    const bTot = getColorTotalCount('blue');
    const presets = ['官方推荐', '物理百穿', '暴击流', '攻速暴击', '法术爆发', '坦克千血'];
    const activeTab = currentArcanaMobileTab || 'red';
    const activeMap = currentArcana[activeTab] || {};
    const colorArcanas = Object.values(ARCANA_DATA).filter(a => a.color_type === activeTab);

    body.innerHTML = `
      <div class="arcana-mobile-header-sub">流派快捷预设：</div>
      <div class="arcana-presets-bar">
        ${presets.map(p => `<div class="arcana-preset-pill" onclick="applyArcanaPreset('${p}')">${p}</div>`).join('')}
      </div>
      <div class="arcana-mobile-tabs">
        <div class="arcana-mobile-tab ${activeTab==='red'?'active':''}" onclick="switchArcanaMobileTab('red')">
          <span class="dot red-dot"></span>红色 (${rTot}/10)
        </div>
        <div class="arcana-mobile-tab ${activeTab==='green'?'active':''}" onclick="switchArcanaMobileTab('green')">
          <span class="dot green-dot"></span>绿色 (${gTot}/10)
        </div>
        <div class="arcana-mobile-tab ${activeTab==='blue'?'active':''}" onclick="switchArcanaMobileTab('blue')">
          <span class="dot blue-dot"></span>蓝色 (${bTot}/10)
        </div>
      </div>
      <div class="arcana-mobile-grid">
        ${colorArcanas.map(a => {
          const cnt = activeMap[a.name] || 0;
          return `
            <div class="arcana-pick-card ${cnt > 0 ? 'active' : ''}">
              <div class="arcana-pick-top">
                <img class="arcana-pick-img" src="${a.icon}" alt="${a.name}">
                <div class="arcana-stepper">
                  <button class="stepper-btn ${cnt > 0 ? '' : 'disabled'}" onclick="modifyArcanaCount('${activeTab}', '${a.name}', -1)">-</button>
                  <span class="stepper-count">${cnt}</span>
                  <button class="stepper-btn" onclick="modifyArcanaCount('${activeTab}', '${a.name}', 1)">+</button>
                </div>
              </div>
              <div class="arcana-pick-name">${a.name}</div>
              <div class="arcana-pick-des">${a.raw_des}</div>
            </div>
          `;
        }).join('')}
      </div>
      <div class="modal-footer-box">
        <button class="arcana-confirm-btn" onclick="closeArcanaModal()">确定装配并生效</button>
      </div>
    `;
    return;
  }

  const sections = [
    { key: 'red', title: '红色铭文 (上限10颗)', colClass: 'arcana-col-red', activeClass: 'arcana-active-red' },
    { key: 'green', title: '绿色铭文 (上限10颗)', colClass: 'arcana-col-green', activeClass: 'arcana-active-green' },
    { key: 'blue', title: '蓝色铭文 (上限10颗)', colClass: 'arcana-col-blue', activeClass: 'arcana-active-blue' }
  ];

  sections.forEach(sec => {
    const col = document.createElement('div');
    col.className = 'arcana-col';

    const map = currentArcana[sec.key] || {};
    const totalCount = getColorTotalCount(sec.key);
    const countTagClass = totalCount === 10 ? 'count-tag-full' : 'count-tag-partial';

    // 1. 计算当前颜色下已选铭文的汇总属性
    let colTotals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, crit:0, crit_effect:0, aspeed:0, cdr:0, percent_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce:0, m_pierce:0, hp_regen:0 };
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        colTotals.atk += (s.phys_atk || 0) * count;
        colTotals.ap += (s.magic_atk || 0) * count;
        colTotals.pdef += (s.phys_def || 0) * count;
        colTotals.mdef += (s.magic_def || 0) * count;
        colTotals.hp += (s.max_hp || 0) * count;
        colTotals.crit += (s.crit_rate_pct || 0) * count;
        colTotals.crit_effect += (s.crit_effect_pct || 0) * count;
        colTotals.aspeed += (s.atk_speed_pct || 0) * count;
        colTotals.cdr += (s.cd_reduction_pct || 0) * count;
        colTotals.percent_speed += (s.move_speed_pct || 0) * count;
        colTotals.p_lifesteal += (s.phys_vamp_pct || 0) * count;
        colTotals.m_lifesteal += (s.magic_vamp_pct || 0) * count;
        colTotals.p_pierce += (s.phys_pierce || 0) * count;
        colTotals.m_pierce += (s.magic_pierce || 0) * count;
        colTotals.hp_regen += (s.hp_regen || 0) * count;
      }
    }

    const statSummaryLines = [];
    if (colTotals.atk) statSummaryLines.push(`物攻 +${Math.round(colTotals.atk*10)/10}`);
    if (colTotals.ap) statSummaryLines.push(`法攻 +${Math.round(colTotals.ap*10)/10}`);
    if (colTotals.max_hp || colTotals.hp) statSummaryLines.push(`生命 +${Math.round(colTotals.hp*10)/10}`);
    if (colTotals.pdef) statSummaryLines.push(`物防 +${Math.round(colTotals.pdef*10)/10}`);
    if (colTotals.mdef) statSummaryLines.push(`魔防 +${Math.round(colTotals.mdef*10)/10}`);
    if (colTotals.p_pierce) statSummaryLines.push(`物穿 +${Math.round(colTotals.p_pierce*10)/10}`);
    if (colTotals.m_pierce) statSummaryLines.push(`法穿 +${Math.round(colTotals.m_pierce*10)/10}`);
    if (colTotals.aspeed) statSummaryLines.push(`攻速 +${Math.round(colTotals.aspeed*10)/10}%`);
    if (colTotals.percent_speed) statSummaryLines.push(`移速 +${Math.round(colTotals.percent_speed*10)/10}%`);
    if (colTotals.crit) statSummaryLines.push(`暴击率 +${Math.round(colTotals.crit*10)/10}%`);
    if (colTotals.crit_effect) statSummaryLines.push(`暴效 +${Math.round(colTotals.crit_effect*10)/10}%`);
    if (colTotals.cdr) statSummaryLines.push(`冷缩 +${Math.round(colTotals.cdr*10)/10}%`);
    if (colTotals.p_lifesteal) statSummaryLines.push(`物吸 +${Math.round(colTotals.p_lifesteal*10)/10}%`);
    if (colTotals.m_lifesteal) statSummaryLines.push(`法吸 +${Math.round(colTotals.m_lifesteal*10)/10}%`);
    if (colTotals.hp_regen) statSummaryLines.push(`回血 +${Math.round(colTotals.hp_regen*10)/10}`);

    const statSummaryStr = statSummaryLines.join(' ｜ ') || '暂无已生效属性';

    // 2. 生成已选组合条目 HTML
    const activeEntries = Object.entries(map).filter(([_, cnt]) => cnt > 0);
    let activeRowsHtml = '';
    if (activeEntries.length === 0) {
      activeRowsHtml = `<div style="font-size: 11px; color: var(--text-tertiary); text-align: center; padding: 10px 0;">当前槽位为空，请从下方选择添加（最多10颗）</div>`;
    } else {
      activeEntries.forEach(([name, cnt]) => {
        const arcData = ARCANA_DATA[name] || {};
        activeRowsHtml += `
          <div class="arcana-active-item-row">
            <div class="arcana-item-mini-info">
              <img class="arcana-active-img-sm" src="${arcData.icon}" alt="${name}">
              <div>
                <span class="arcana-item-name-bold">${name}</span>
                <span style="font-size: 10px; color: var(--text-tertiary); margin-left: 4px;">(${arcData.raw_des})</span>
              </div>
            </div>
            <div class="arcana-stepper">
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${name}', -1)">-</button>
              <span class="stepper-val">${cnt}</span>
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${name}', 1)" ${totalCount >= 10 ? 'disabled' : ''}>+</button>
            </div>
          </div>
        `;
      });
    }

    // 3. 筛选出属于当前颜色的全部 10 款五级铭文
    const colorArcanas = Object.values(ARCANA_DATA).filter(a => a.color_type === sec.key);
    let optionsHtml = '';
    colorArcanas.forEach(opt => {
      const currentCount = map[opt.name] || 0;
      const isSelected = currentCount > 0;
      optionsHtml += `
        <div class="arcana-option-item ${isSelected ? 'selected' : ''}">
          <img class="arcana-option-img" src="${opt.icon}" alt="${opt.name}">
          <div class="arcana-option-meta">
            <div class="arcana-option-name">${opt.name}</div>
            <div class="arcana-option-desc">${opt.raw_des}</div>
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <button class="arcana-full-btn" onclick="setArcanaFull('${sec.key}', '${opt.name}')" title="将该铭文直接设为 10 颗满配">满配10</button>
            <div class="arcana-stepper">
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${opt.name}', -1)" ${currentCount <= 0 ? 'disabled' : ''}>-</button>
              <span class="stepper-val" style="${currentCount > 0 ? 'color: var(--color-blue);' : 'color: var(--text-tertiary);'}">${currentCount}</span>
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${opt.name}', 1)" ${totalCount >= 10 ? 'disabled' : ''}>+</button>
            </div>
          </div>
        </div>
      `;
    });

    col.innerHTML = `
      <div class="arcana-col-header ${sec.colClass}">
        <span class="arcana-col-dot ${sec.key}-dot"></span> ${sec.title}
      </div>
      <div class="arcana-active-card ${sec.activeClass}">
        <div class="arcana-active-header">
          <span class="arcana-active-count-tag ${countTagClass}">已配 ${totalCount} / 10 颗</span>
          <button class="arcana-clear-btn" onclick="clearArcanaSlot('${sec.key}')" title="清空该颜色铭文">清空</button>
        </div>
        <div class="arcana-active-list">
          ${activeRowsHtml}
        </div>
        <div class="arcana-active-stats-box">
          <strong>槽位加成</strong>：${statSummaryStr}
        </div>
      </div>
      <div class="arcana-options-title">五级铭文库（可自由加减混搭）：</div>
      <div class="arcana-options-grid">
        ${optionsHtml}
      </div>
    `;
    body.appendChild(col);
  });
}

function showToast(msg) {
  let toast = document.getElementById('sandboxToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'sandboxToast';
    toast.style.cssText = "position:fixed; bottom:40px; left:50%; transform:translateX(-50%); background:rgba(30,30,32,0.88); backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px); color:#fff; padding:10px 22px; border-radius:980px; font-size:13px; font-weight:500; box-shadow:0 10px 30px rgba(0,0,0,0.25); z-index:99999; pointer-events:none; transition:all 0.3s cubic-bezier(0.16,1,0.3,1); opacity:0;";
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.style.opacity = '1';
  toast.style.transform = 'translateX(-50%) translateY(0)';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-50%) translateY(10px)';
  }, 2200);
}

function modifyArcanaCount(colorKey, arcanaName, delta) {
  if (!currentArcana[colorKey]) currentArcana[colorKey] = {};
  const curr = currentArcana[colorKey][arcanaName] || 0;
  const total = getColorTotalCount(colorKey);

  if (delta > 0) {
    if (total >= 10) {
      showToast("当前槽位已满 10 颗！请先点击 [-] 减少其他铭文，再增加。");
      return;
    }
    currentArcana[colorKey][arcanaName] = curr + 1;
  } else if (delta < 0) {
    if (curr > 1) {
      currentArcana[colorKey][arcanaName] = curr - 1;
    } else {
      delete currentArcana[colorKey][arcanaName];
    }
  }

  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function setArcanaFull(colorKey, arcanaName) {
  currentArcana[colorKey] = { [arcanaName]: 10 };
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function clearArcanaSlot(colorKey) {
  currentArcana[colorKey] = {};
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function resetToHeroDefaultArcana() {
  initHeroArcana(currentHero);
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}


// === 二级页面：技能×出装战术联动分析引擎 ===
