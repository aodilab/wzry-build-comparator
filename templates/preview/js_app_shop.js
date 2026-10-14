Object.assign(App, {
  renderArcanaSummary(side, arcCfg, elId) {
    const el = document.getElementById(elId);
    if (!el) return;
    const arc = arcCfg || { red: {}, blue: {}, green: {} };
    const rHas = Object.values(arc.red || {}).some(v => v > 0);
    const bHas = Object.values(arc.blue || {}).some(v => v > 0);
    const gHas = Object.values(arc.green || {}).some(v => v > 0);
    const hasAny = rHas || bHas || gHas;

    if (!hasAny) {
      el.innerHTML = `
        <div class="arcana-list">
          <span class="arcana-label-title">五级铭文</span>
          <div class="arcana-chips-group">
            <span class="arcana-empty-tip" onclick="App.openArcanaSheet('${side}', 'red')">未配置铭文</span>
          </div>
        </div>
        <button class="btn-edit-arcana" onclick="App.openArcanaSheet('${side}', 'red')">编辑 ›</button>
      `;
      return;
    }

    const tags = [];
    if (rHas) tags.push(`<span class="arcana-tag" onclick="App.openArcanaSheet('${side}', 'red')">${this.formatArcanaSummaryText(arc.red)}</span>`);
    if (bHas) tags.push(`<span class="arcana-tag" onclick="App.openArcanaSheet('${side}', 'blue')">${this.formatArcanaSummaryText(arc.blue)}</span>`);
    if (gHas) tags.push(`<span class="arcana-tag" onclick="App.openArcanaSheet('${side}', 'green')">${this.formatArcanaSummaryText(arc.green)}</span>`);

    el.innerHTML = `
      <div class="arcana-list">
        <span class="arcana-label-title">五级铭文</span>
        <div class="arcana-chips-group">
          ${tags.join('<span class="arcana-sep">·</span>')}
        </div>
      </div>
      <button class="btn-edit-arcana" onclick="App.openArcanaSheet('${side}', 'red')">编辑 ›</button>
    `;
  },

  formatArcanaSummaryText(colorMap) {
    const entries = Object.entries(colorMap || {}).filter(([_, count]) => count > 0);
    if (entries.length === 0) return '';
    return entries.map(([name, c]) => `<span class="arc-count">${c}</span> ${name}`).join(' ');
  },

  openShopSheet(side, idx) {
    this.targetSide = side;
    this.targetSlotIdx = idx;
    this.shopKw = '';
    const searchInp = document.getElementById('shopSearchInput');
    if (searchInp) searchInp.value = '';

    const curItem = side === 'left' ? this.leftItems[idx] : this.rightItems[idx];
    const unequipBtn = document.getElementById('btnUnequipCurrentSlot');
    if (unequipBtn) unequipBtn.style.display = curItem ? 'block' : 'none';

    const tEl = document.getElementById('shopModalTitle');
    if (tEl) tEl.textContent = `装配神装`;
    const sEl = document.getElementById('shopModalSub');
    if (sEl) sEl.textContent = `点选上方装备检视 · 查阅属性被动后装配`;

    // 默认高亮检视当前槽位已装的装备，若为空则默认检视第一件
    if (curItem) {
      this.previewingItemName = curItem.item_name;
    } else {
      this.previewingItemName = '';
    }

    this.renderShopTabs();
    this.renderShopList();
    const modal = document.getElementById('shopModal');
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

  closeShopSheet() {
    const modal = document.getElementById('shopModal');
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
  },

  unequipCurrentSlot() {
    if (this.targetSide === 'left') {
      this.leftItems[this.targetSlotIdx] = null;
      this.isLeftCustomMode = true;
      this.officialSchemeIdx = -1;
      const tEl = document.getElementById("leftBuildTitle");
      if (tEl) {
        tEl.textContent = "我的实战方案";
        tEl.classList.remove("is-prompt");
      }
      this.renderSchemeTabs();
    } else {
      this.rightItems[this.targetSlotIdx] = null;
      const countB = this.rightItems.filter(Boolean).length;
      const rTitleEl = document.getElementById("rightBuildTitle");
      if (rTitleEl) {
        if (countB === 0) {
          rTitleEl.textContent = "请搭配您的实战出装";
          rTitleEl.classList.add("is-prompt");
        } else {
          rTitleEl.textContent = "我的实战方案";
          rTitleEl.classList.remove("is-prompt");
        }
      }
    }
    this.closeShopSheet();
    this.recalculateAll();
  },

  renderShopTabs() {
    const cats = ['全部', '攻击', '法术', '防御', '移动', '打野', '游走'];
    const el = document.getElementById('shopCatTabs');
    el.innerHTML = cats.map(c => `
      <div class="apple-seg-item ${c === this.shopCat ? 'active' : ''}" onclick="App.setShopCat('${c}')">${c}</div>
    `).join('');
  },

  setShopCat(c) {
    this.shopCat = c;
    this.renderShopTabs();
    this.renderShopList();
  },

  onShopSearch(kw) {
    this.shopKw = (kw || '').trim().toLowerCase();
    this.renderShopList();
  },

  previewShopItem(itemName) {
    this.previewingItemName = itemName;
    const cards = document.querySelectorAll('.shop-grid-card');
    cards.forEach(card => {
      if (card.dataset.name === itemName) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
    this.renderShopInspector();
  },

  renderShopList() {
    let list = window.DATASET.ITEMS_DATA || [];
    if (this.shopCat !== '全部') list = list.filter(it => it.category === this.shopCat);
    if (this.shopKw) {
      list = list.filter(it =>
        (it.item_name && it.item_name.toLowerCase().includes(this.shopKw)) ||
        (it.des1 && it.des1.toLowerCase().includes(this.shopKw)) ||
        (it.des2 && it.des2.toLowerCase().includes(this.shopKw))
      );
    }

    const grid = document.getElementById('shopItemsGrid');
    if (list.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1; text-align:center; padding:40px 0; color:var(--apple-text-secondary); font-size:13px;">
          未检索到符合条件的装备
        </div>
      `;
      this.renderShopInspector();
      return;
    }

    // 若当前未选或选中的不在当前过滤结果中，则默认选中第一个
    if (!this.previewingItemName || !list.some(it => it.item_name === this.previewingItemName)) {
      this.previewingItemName = list[0].item_name;
    }

    grid.innerHTML = list.map(it => {
      const isActive = it.item_name === this.previewingItemName;
      return `
        <div class="shop-grid-card ${isActive ? 'active' : ''}" data-name="${it.item_name}" onclick="App.previewShopItem('${it.item_name}')" ondblclick="App.confirmEquipItem('${it.item_name}')" title="双击直接装配">
          <img class="shop-card-icon" src="${it.icon}" alt="${it.item_name}">
          <div class="shop-card-meta">
            <span class="shop-card-name">${it.item_name}</span>
            <span class="shop-card-price-pill">${it.total_price || 0}</span>
          </div>
        </div>
      `;
    }).join('');

    this.renderShopInspector();
  },

});
