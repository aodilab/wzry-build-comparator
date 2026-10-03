  if (!hero) return;
  const avatar = document.getElementById('hallSelectedAvatar');
  if (avatar) avatar.src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${hero.ename}/${hero.ename}.jpg`;
  const name = document.getElementById('hallSelectedName');
  if (name) name.innerText = hero.cname || '英雄';
  const role = document.getElementById('hallSelectedRole');
  if (role) role.innerText = hero.role || '职业';

  const container = document.getElementById('hallLanePills');
  if (!container) return;
  container.innerHTML = '';

  const lanes = getSupportedLanesForHero(hero);
  lanes.forEach(lane => {
    const btn = document.createElement('button');
    btn.className = `hall-lane-pill-btn ${lane === currentHeroActiveLane ? 'active' : ''}`;
    btn.innerHTML = `<span>${lane}</span><span style="font-size:11px;opacity:0.8;">›</span>`;
    btn.onclick = () => confirmHeroLaneAndEnter(lane);
    container.appendChild(btn);
  });
}

function openLanePicker(hero) {
  if (!hero) return;
  const overlay = document.getElementById('lanePickerOverlay');
  if (!overlay) return;

  const avatar = document.getElementById('pickerHeroAvatar');
  if (avatar) avatar.src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${hero.ename}/${hero.ename}.jpg`;
  const name = document.getElementById('pickerHeroName');
  if (name) name.innerText = hero.cname || '英雄';
  const role = document.getElementById('pickerHeroRole');
  if (role) role.innerText = hero.role || '职业';

  const container = document.getElementById('pickerLaneOptions');
  if (container) {
    container.innerHTML = '';
    const lanes = getSupportedLanesForHero(hero);
    lanes.forEach((lane, idx) => {
      const btn = document.createElement('button');
      btn.className = `lane-picker-btn ${lane === currentHeroActiveLane ? 'active' : ''}`;
      btn.onclick = () => confirmHeroLaneAndEnter(lane);
      btn.innerHTML = `
        <div class="lane-picker-btn-name">${lane}</div>
        <div class="lane-picker-btn-tip">${idx === 0 ? '官方首选分路' : '实战推荐流派'} · 点击进入</div>
      `;
      container.appendChild(btn);
    });
  }

  overlay.classList.add('active');
}

function closeLanePicker(e) {
  if (e && e.target && e.target.classList && !e.target.classList.contains('lane-picker-overlay') && !e.target.classList.contains('arcana-modal-close')) {
    return;
  }
  const overlay = document.getElementById('lanePickerOverlay');
  if (overlay) overlay.classList.remove('active');
}

function confirmHeroLaneAndEnter(lane) {
  currentHeroActiveLane = lane;
  const overlay = document.getElementById('lanePickerOverlay');
  if (overlay) overlay.classList.remove('active');

  // 同步分路胶囊状态
  if (typeof renderHeroLanePills === 'function') {
    renderHeroLanePills(currentHero);
  }
  renderHeroHallLaneBar(currentHero);

  // 联动加载官方出装与专属铭文
  if (typeof loadRecommendedEquips === 'function') {
    loadRecommendedEquips();
  } else {
    recalculate();
  }

  // 选好分路后，正式滑入层级 2 推演室
  switchView('studio');
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

  document.getElementById('itemCountBadge').innerText = window.innerWidth <= 768 ? `${filtered.length}件` : `${filtered.length} 件装备`;

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

    if (window.innerWidth <= 768) {
      card.innerHTML = `
        <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${it.item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg'">
        <div class="item-info">
          <div class="item-title-row">
            <div class="item-name-box">
              <span class="item-cname">${it.item_name}</span>
              ${inSlot ? '<span class="item-equipped-badge">已装配</span>' : ''}
            </div>
            <span class="item-gold-pill">${it.total_price || 0} 金币</span>
          </div>
          <div class="item-des">${it.des1 || it.des2 || '基础属性加成'}</div>
        </div>
        <div class="item-add-btn ${inSlot ? 'equipped-btn' : ''}">${inSlot ? '✓' : '+'}</div>
      `;
    } else {
      card.innerHTML = `
        <span class="item-equipped-badge">已装配</span>
        <div class="item-top">
          <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${it.item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg'">
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
    }
    container.appendChild(card);
  });
}

function renderSlots() {
  const grid = document.getElementById('slotsGrid');
  if (!grid) return;
  grid.innerHTML = '';
  
  const countBadge = document.getElementById('slotCount');
  if (countBadge) countBadge.innerText = `已选 ${currentSlots.length} / 6 件`;
  const countDisplay = document.getElementById('slotCountDisplay');
  if (countDisplay) countDisplay.innerText = `(${currentSlots.length}/6)`;

  for (let i = 0; i < 6; i++) {
    const item = currentSlots[i];
    const slot = document.createElement('div');
    if (item) {
      slot.className = 'slot filled';
      slot.title = `点击卸下: ${item.item_name}`;
      slot.onclick = () => removeSlot(i);
      slot.innerHTML = `
        <img alt="${item.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${item.item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${item.item_id}.jpg'">
        <span class="slot-item-name">${item.item_name}</span>
        <span class="slot-remove-badge">×</span>
      `;
    } else {
      slot.className = 'slot';
      slot.innerHTML = `
        <div class="empty-plus">+</div>
        <div class="empty-txt">空槽 ${i + 1}</div>
      `;
    }
    grid.appendChild(slot);
  }
}

function addItem(item) {
  // 1. 已装配状态下再次点击 -> 直接卸下 (Toggle，体验与微信小程序对齐)
  const existingIdx = currentSlots.findIndex(s => s.item_name === item.item_name);
  if (existingIdx !== -1) {
    currentSlots.splice(existingIdx, 1);
    renderSlots();
    renderItems();
    recalculate();
    return;
  }

  // 2. 检查槽位上限
  if (currentSlots.length >= 6) {
    alert("局内神装上限仅限 6 格！请先点击槽位中的装备进行卸下或替换。");
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

// [模块说明] 一键神装、战术协同简报卡片与移动端抽屉交互已下沉解耦至 app_mobile.js 驱动


// 核心数值计算、属性面板渲染与被动互斥诊断逻辑
// 遵循单一职责原则，已下沉解耦至 app_stats.js 驱动

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

// === 搜索引擎静态大典与全局英雄直达路由助手 ===
window.selectHeroById = function(ename) {
  if (typeof HEROES_DATA === 'undefined') return;
  const target = HEROES_DATA.find(h => String(h.ename) === String(ename) || h.cname === ename);
  if (target) {
    selectHero(target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

window.toggleSeoDirectory = function() {
  const content = document.getElementById('seoDirectoryContent');
  const btn = document.getElementById('seoToggleBtn');
  if (!content || !btn) return;
  const isExpanded = content.classList.contains('active');
  if (isExpanded) {
    content.classList.remove('active');
    btn.classList.remove('expanded');
    btn.setAttribute('aria-expanded', 'false');
  } else {
    content.classList.add('active');
    btn.classList.add('expanded');
    btn.setAttribute('aria-expanded', 'true');
  }
};
