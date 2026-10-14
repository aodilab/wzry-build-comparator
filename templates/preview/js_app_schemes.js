Object.assign(App, {
  renderSchemeTabs() {
    const schemeTabs = document.getElementById("officialSchemeTabs");
    if (!schemeTabs) return;
    let tabsHtml = '';
    (this.schemes || []).forEach((b, idx) => {
      const isActive = (!this.isLeftCustomMode && idx === this.officialSchemeIdx);
      tabsHtml += `
        <button class="scheme-btn ${isActive ? "active" : ""}" onclick="App.switchOfficialScheme(${idx})">${b.title || `方案${idx+1}`}</button>
      `;
    });
    tabsHtml += `
      <button class="scheme-btn scheme-btn-custom ${this.isLeftCustomMode ? "active" : ""}" onclick="App.enableLeftCustomMode()">自选方案</button>
    `;
    schemeTabs.innerHTML = tabsHtml;
  },

  switchOfficialScheme(idx) {
    this.officialSchemeIdx = idx;
    this.isLeftCustomMode = false;

    const activeOfficial = (this.schemes && this.schemes[idx]) || (this.schemes && this.schemes[0]) || { items: [] };

    const titleEl = document.getElementById("leftBuildTitle");
    if (titleEl) {
      titleEl.textContent = "王者官方推荐";
      titleEl.classList.remove("is-prompt");
    }

    this.leftItems = this.getItemsFromNames(activeOfficial.items || []);
    while (this.leftItems.length < 6) this.leftItems.push(null);

    if (activeOfficial.arcana && Object.keys(activeOfficial.arcana).length > 0) {
      this.leftArc = JSON.parse(JSON.stringify(activeOfficial.arcana));
    } else {
      const rec = this.hero.recommended_arcana || { red: "异变", blue: "隐匿", green: "鹰眼" };
      this.leftArc = {
        red: { [rec.red || "异变"]: 10 },
        blue: { [rec.blue || "隐匿"]: 10 },
        green: { [rec.green || "鹰眼"]: 10 }
      };
    }

    this.renderSchemeTabs();
    this.recalculateAll();
  },

  enableLeftCustomMode() {
    this.isLeftCustomMode = true;
    this.officialSchemeIdx = -1;
    const titleEl = document.getElementById("leftBuildTitle");
    if (titleEl) {
      titleEl.textContent = "我的实战方案";
      titleEl.classList.remove("is-prompt");
    }

    this.leftItems = [null, null, null, null, null, null];
    this.leftArc = { red: {}, blue: {}, green: {} };

    this.renderSchemeTabs();
    this.recalculateAll();
  },

  resetOfficial() {
    this.isLeftCustomMode = false;
    this.officialSchemeIdx = -1;
    const titleEl = document.getElementById("leftBuildTitle");
    if (titleEl) {
      titleEl.textContent = "请选择您对照的出装";
      titleEl.classList.add("is-prompt");
    }

    this.leftItems = [null, null, null, null, null, null];
    this.leftArc = { red: {}, blue: {}, green: {} };

    this.renderSchemeTabs();
    this.recalculateAll();
  },

  applyCopyAToB() {
    this.rightItems = JSON.parse(JSON.stringify(this.leftItems));
    this.rightArc = JSON.parse(JSON.stringify(this.leftArc));
    const rTitleEl = document.getElementById("rightBuildTitle");
    if (rTitleEl) {
      rTitleEl.textContent = "我的实战方案";
      rTitleEl.classList.remove("is-prompt");
    }
    this.recalculateAll();
  },

  clearRightScheme() {
    this.rightItems = [null, null, null, null, null, null];
    this.rightArc = { red: {}, blue: {}, green: {} };
    const rTitleEl = document.getElementById("rightBuildTitle");
    if (rTitleEl) {
      rTitleEl.textContent = "请搭配您的实战出装";
      rTitleEl.classList.add("is-prompt");
    }
    this.recalculateAll();
  },

  updateHeaderSchemeTitles() {},

  getItemsFromNames(names) {
    const all = window.DATASET.ITEMS_DATA || [];
    return (names || []).slice(0, 6).map(n => all.find(it => it.item_name === n) || null);
  },

  toggleComboMenu(e) {
    if (e) e.stopPropagation();
    const wrap = document.getElementById('dComboWrap');
    if (!wrap) return;
    wrap.classList.toggle('active');
  },

  closeComboMenu() {
    const wrap = document.getElementById('dComboWrap');
    if (wrap) wrap.classList.remove('active');
  },

  selectCombo(idx) {
    this.activeComboIdx = idx;
    this.renderComboSelector();
    this.closeComboMenu();
    this.recalculateAll();
  },

  renderComboSelector() {
    const combos = this.combos || [];
    const active = combos[this.activeComboIdx] || combos[0] || { name: '实战连招', title: '13A2A', desc: '核心爆发' };

    const nameEl = document.getElementById('dComboActiveName');
    if (nameEl) nameEl.textContent = active.name;

    const keyEl = document.getElementById('dComboActiveKey');
    if (keyEl) {
      const k = active.title || active.keys || '';
      keyEl.textContent = k;
      keyEl.style.display = k ? 'inline-block' : 'none';
    }

    const listEl = document.getElementById('dComboOptionsList');
    if (listEl) {
      listEl.innerHTML = combos.map((c, i) => {
        const isSelected = i === this.activeComboIdx;
        let cleanDesc = (c.desc || '').replace(/.*?(实战连招|爆发|技巧|说明)[：:]\s*/, '').trim();
        return `
          <div class="combo-menu-item ${isSelected ? 'active' : ''}" onclick="App.selectCombo(${i})">
            <div class="combo-item-info">
              <div class="combo-item-top">
                <span class="combo-item-name">${c.name}</span>
                ${(c.title || c.keys) ? `<span class="combo-item-key">${c.title || c.keys}</span>` : ''}
              </div>
              ${cleanDesc ? `<span class="combo-item-desc">${cleanDesc}</span>` : ''}
            </div>
            ${isSelected ? `<svg class="combo-check-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0071e3" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>` : ''}
          </div>
        `;
      }).join('');
    }
  },

  onComboChange(val) {
    this.selectCombo(parseInt(val, 10));
  },

  setStatsFilter(diffOnly) {
    this.filterStatsDiffOnly = diffOnly;
    document.getElementById('btnStatsDiff').classList.toggle('active', diffOnly);
    document.getElementById('btnStatsAll').classList.toggle('active', !diffOnly);
    this.recalculateAll();
  },

});
