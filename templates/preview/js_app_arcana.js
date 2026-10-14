Object.assign(App, {
  renderShopInspector() {
    const panel = document.getElementById('shopInspectorPanel');
    if (!panel) return;
    const it = (window.DATASET.ITEMS_DATA || []).find(x => x.item_name === this.previewingItemName);
    if (!it) {
      panel.innerHTML = `<div style="text-align:center; color:var(--apple-text-secondary); padding:20px; font-size:12px;">请点选上方装备查看加成与被动</div>`;
      return;
    }

    // 基础属性药丸 (统一中性灰阶微胶囊)
    const statChips = (it.stats_chips && it.stats_chips.length > 0)
      ? it.stats_chips.map(s => `<span class="inspector-stat-chip">${s}</span>`).join('')
      : '<span class="inspector-stat-chip">基础属性配件</span>';

    // 格式化被动/主动机制 (合并同类通用机制规则)
    const passives = it.passives || [];
    let passivesHtml = '';
    if (passives.length === 0) {
      passivesHtml = `
        <div class="inspector-empty-hint">
          <div class="empty-hint-tag">基础配件 · 核心增益</div>
          <div class="empty-hint-desc">本装备为基础核心构件，提供纯正属性加成，可向上合成高阶神装。</div>
        </div>
      `;
    } else {
      const regularPassives = [];
      const ruleItems = [];
      passives.forEach(p => {
        if (p.title === '机制效果' || p.kind === '机制' || p.name === '机制效果') {
          ruleItems.push(p.desc);
        } else {
          regularPassives.push(p);
        }
      });

      let itemsHtml = regularPassives.map(p => {
        let cleanDesc = (p.desc || '').trim();
        cleanDesc = cleanDesc
          .replace(/[(（]\s*(?:CD|冷却时间?)[：:]\s*\d+(?:\.\d+)?秒?\s*[)）]/gi, '')
          .replace(/[,，\s]*(?:CD|冷却时间?)[：:]\s*\d+(?:\.\d+)?秒?/gi, '')
          .trim();

        const isActive = p.kind === '主动' || (p.title && p.title.includes('主动'));
        const badgeClass = isActive ? 'badge-active' : 'badge-passive';

        return `
          <div class="inspector-mech-row">
            <div class="inspector-mech-title-bar">
              <span class="inspector-mech-badge ${badgeClass}">${p.title}</span>
              ${p.cd ? `<span class="inspector-mech-cd">${p.cd}</span>` : ''}
            </div>
            <div class="inspector-mech-desc">${cleanDesc}</div>
          </div>
        `;
      }).join('');

      if (ruleItems.length > 0) {
        itemsHtml += `
          <div class="inspector-mech-row">
            <div class="inspector-mech-title-bar">
              <span class="inspector-mech-badge badge-rule">通用规则机制</span>
            </div>
            <div class="inspector-mech-desc" style="color:#636366;">
              ${ruleItems.join(' · ')}
            </div>
          </div>
        `;
      }
      passivesHtml = itemsHtml;
    }

    const slotLabel = `${this.targetSide === 'left' ? '方案 A' : '方案 B'} 第 ${this.targetSlotIdx + 1} 格`;

    panel.innerHTML = `
      <div class="inspector-header">
        <img class="inspector-icon" src="${it.icon}" alt="${it.item_name}">
        <div class="inspector-info-col">
          <div class="inspector-name-row">
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="inspector-name">${it.item_name}</span>
              <span class="inspector-cat-badge">${it.category}</span>
            </div>
            <span class="inspector-price-capsule">🪙 ${it.total_price || 0}</span>
          </div>
          <div class="inspector-stats-row">
            ${statChips}
          </div>
        </div>
      </div>

      <div class="inspector-mechanics-wrap">
        ${passivesHtml}
      </div>

      <button class="inspector-equip-btn" onclick="App.confirmEquipItem('${it.item_name}')">
        装配到当前格 (${slotLabel})
      </button>
    `;
  },

  confirmEquipItem(itemName) {
    const it = (window.DATASET.ITEMS_DATA || []).find(x => x.item_name === itemName);
    if (!it) return;
    if (this.targetSide === 'left') {
      this.leftItems[this.targetSlotIdx] = it;
      this.isLeftCustomMode = true;
      this.officialSchemeIdx = -1;
      const tEl = document.getElementById("leftBuildTitle");
      if (tEl) {
        tEl.textContent = "我的实战方案";
        tEl.classList.remove("is-prompt");
      }
      this.renderSchemeTabs();
    } else {
      this.rightItems[this.targetSlotIdx] = it;
      const rTitleEl = document.getElementById("rightBuildTitle");
      if (rTitleEl) {
        rTitleEl.textContent = "我的实战方案";
        rTitleEl.classList.remove("is-prompt");
      }
    }
    this.closeShopSheet();
    this.recalculateAll();
  },

  openArcanaSheet(side, color) {
    this.targetSide = side;
    this.arcColor = color || 'red';
    this.renderArcanaColorTabs();
    this.renderArcanaList();
    const modal = document.getElementById('arcanaModal');
    if (!modal) return;
    const sheet = modal.querySelector('.sheet-box');
    if (sheet) {
      sheet.style.transform = 'translateY(100%)';
      sheet.style.transition = 'none';
    }
    modal.classList.add('active');
    if (sheet) {
      void sheet.offsetHeight;
      requestAnimationFrame(() => {
        sheet.style.transition = 'transform 0.36s cubic-bezier(0.32, 0.72, 0, 1)';
        sheet.style.transform = 'translateY(0)';
      });
    }
  },

  closeArcanaSheet() {
    const modal = document.getElementById('arcanaModal');
    if (!modal) return;
    const sheet = modal.querySelector('.sheet-box');
    if (sheet) {
      sheet.style.transition = 'transform 0.28s cubic-bezier(0.32, 0.72, 0, 1)';
      sheet.style.transform = 'translateY(100%)';
    }
    modal.style.transition = 'opacity 0.28s cubic-bezier(0.32, 0.72, 0, 1)';
    modal.style.opacity = '0';
    setTimeout(() => {
      modal.classList.remove('active');
      modal.style.opacity = '';
      modal.style.transition = '';
      if (sheet) {
        sheet.style.transform = '';
        sheet.style.transition = '';
      }
    }, 280);
    this.recalculateAll();
  },

  renderArcanaColorTabs() {
    const tabs = [
      { key: 'red', label: '红色' },
      { key: 'blue', label: '蓝色' },
      { key: 'green', label: '绿色' }
    ];
    const el = document.getElementById('arcanaColorTabs');
    el.innerHTML = tabs.map(t => `
      <div class="apple-seg-item ${t.key === this.arcColor ? 'active' : ''}" onclick="App.setArcanaColor('${t.key}')">${t.key === 'red' ? '红色' : (t.key === 'blue' ? '蓝色' : '绿色')}</div>
    `).join('');
  },

  setArcanaColor(c) {
    this.arcColor = c;
    this.renderArcanaColorTabs();
    this.renderArcanaList();
  },

  renderArcanaList() {
    const allArc = window.DATASET.ARCANA_DATA || {};
    const filtered = Object.keys(allArc)
      .filter(k => (allArc[k].color_type === this.arcColor || allArc[k].color === this.arcColor))
      .map(k => ({ name: k, ...allArc[k] }));

    const curMap = (this.targetSide === 'left' ? this.leftArc : this.rightArc)[this.arcColor] || {};
    const totalCount = Object.values(curMap).reduce((a, b) => a + b, 0);

    const body = document.getElementById('arcanaListBody');
    body.innerHTML = `
      <div style="font-size:12px; color:var(--apple-text-secondary); margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
        <span>当前色系装配: <strong style="color:var(--apple-text-primary); font-weight:600;">${totalCount}/10</strong> 颗</span>
        <span style="color:#ff3b30; cursor:pointer; font-weight:500;" onclick="App.clearCurrentArcanaColor()">清空此色</span>
      </div>
      <div class="arcana-grid-list">
        ${filtered.map(a => {
          const cnt = curMap[a.name] || 0;
          return `
            <div class="arcana-item-row">
              <div class="arc-row-left">
                <img class="arc-row-icon" src="${a.icon}" alt="${a.name}" onerror="this.style.display='none'">
                <div class="arc-row-text">
                  <span class="arc-row-name">${a.name}</span>
                  <span class="arc-row-props">${a.raw_des || a.des || ''}</span>
                </div>
              </div>
              <div class="arc-row-counter">
                <button class="arc-cnt-btn" onclick="App.changeArcanaCount('${a.name}', -1)">-</button>
                <span class="arc-cnt-val">${cnt}</span>
                <button class="arc-cnt-btn" onclick="App.changeArcanaCount('${a.name}', 1)">+</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  },

  changeArcanaCount(name, delta) {
    const targetCfg = this.targetSide === 'left' ? this.leftArc : this.rightArc;
    if (!targetCfg[this.arcColor]) targetCfg[this.arcColor] = {};
    const curMap = targetCfg[this.arcColor];
    const curVal = curMap[name] || 0;
    const curTotal = Object.values(curMap).reduce((a, b) => a + b, 0);

    if (delta > 0 && curTotal >= 10) return;
    const newVal = Math.max(0, Math.min(10, curVal + delta));
    if (newVal === 0) {
      delete curMap[name];
    } else {
      curMap[name] = newVal;
    }
    if (this.targetSide === 'left') {
      this.isLeftCustomMode = true;
      this.officialSchemeIdx = -1;
      const tEl = document.getElementById("leftBuildTitle");
      if (tEl) {
        tEl.textContent = "我的实战方案";
        tEl.classList.remove("is-prompt");
      }
      this.renderSchemeTabs();
      this.renderArcanaSummary('left', this.leftArc, 'leftArcanaRow');
    } else {
      const rTitleEl = document.getElementById("rightBuildTitle");
      if (rTitleEl) {
        rTitleEl.textContent = "我的实战方案";
        rTitleEl.classList.remove("is-prompt");
      }
      this.renderArcanaSummary('right', this.rightArc, 'rightArcanaRow');
    }
    this.renderArcanaList();
    this.recalculateAll();
  },

  clearCurrentArcanaColor() {
    const targetCfg = this.targetSide === 'left' ? this.leftArc : this.rightArc;
    targetCfg[this.arcColor] = {};
    if (this.targetSide === 'left') {
      this.isLeftCustomMode = true;
      this.officialSchemeIdx = -1;
      const tEl = document.getElementById("leftBuildTitle");
      if (tEl) {
        tEl.textContent = "我的实战方案";
        tEl.classList.remove("is-prompt");
      }
      this.renderSchemeTabs();
      this.renderArcanaSummary('left', this.leftArc, 'leftArcanaRow');
    } else {
      const rTitleEl = document.getElementById("rightBuildTitle");
      if (rTitleEl) {
        rTitleEl.textContent = "我的实战方案";
        rTitleEl.classList.remove("is-prompt");
      }
      this.renderArcanaSummary('right', this.rightArc, 'rightArcanaRow');
    }
    this.renderArcanaList();
    this.recalculateAll();
  },

});
