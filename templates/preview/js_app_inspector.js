Object.assign(App, {
  renderAppleSpecsTable(statsA, statsB) {
    const isMage = (this.hero.role && this.hero.role.includes("法师")) || statsA.ap > statsA.atk || statsB.ap > statsB.atk;
    const powName = isMage ? "法术攻击" : "物理攻击";
    const powA = isMage ? statsA.ap : statsA.atk;
    const powB = isMage ? statsB.ap : statsB.atk;

    const ppenA = statsA.percentPen > 0 ? `${statsA.flatPen}点 / ${(statsA.percentPen*100).toFixed(0)}%` : `${statsA.flatPen}点`;
    const ppenB = statsB.percentPen > 0 ? `${statsB.flatPen}点 / ${(statsB.percentPen*100).toFixed(0)}%` : `${statsB.flatPen}点`;
    const mpenA = statsA.mPercentPen > 0 ? `${statsA.mFlatPen}点 / ${(statsA.mPercentPen*100).toFixed(0)}%` : `${statsA.mFlatPen}点`;
    const mpenB = statsB.mPercentPen > 0 ? `${statsB.mFlatPen}点 / ${(statsB.mPercentPen*100).toFixed(0)}%` : `${statsB.mFlatPen}点`;

    const pdrA = Math.round((statsA.pdef / (statsA.pdef + 602)) * 100);
    const pdrB = Math.round((statsB.pdef / (statsB.pdef + 602)) * 100);
    const mdrA = Math.round((statsA.mdef / (statsA.mdef + 602)) * 100);
    const mdrB = Math.round((statsB.mdef / (statsB.mdef + 602)) * 100);

    const rows = [
      { name: powName, valA: `${powA}`, valB: `${powB}`, numA: powA, numB: powB, diff: powA !== powB },
      { name: "最大生命", valA: `${statsA.hp.toLocaleString()}`, valB: `${statsB.hp.toLocaleString()}`, numA: statsA.hp, numB: statsB.hp, diff: statsA.hp !== statsB.hp },
      { name: "物理防御", valA: `${statsA.pdef} (${pdrA}%)`, valB: `${statsB.pdef} (${pdrB}%)`, numA: statsA.pdef, numB: statsB.pdef, diff: statsA.pdef !== statsB.pdef },
      { name: "法术防御", valA: `${statsA.mdef} (${mdrA}%)`, valB: `${statsB.mdef} (${mdrB}%)`, numA: statsA.mdef, numB: statsB.mdef, diff: statsA.mdef !== statsB.mdef },
      { name: "物理穿透", valA: ppenA, valB: ppenB, numA: statsA.flatPen + statsA.percentPen * 1000, numB: statsB.flatPen + statsB.percentPen * 1000, diff: ppenA !== ppenB },
      { name: "法术穿透", valA: mpenA, valB: mpenB, numA: statsA.mFlatPen + statsA.mPercentPen * 1000, numB: statsB.mFlatPen + statsB.mPercentPen * 1000, diff: mpenA !== mpenB },
      { name: "冷却缩减", valA: `${statsA.cdr}%`, valB: `${statsB.cdr}%`, numA: statsA.cdr, numB: statsB.cdr, diff: statsA.cdr !== statsB.cdr },
      { name: "暴击率", valA: `${statsA.critRate}%`, valB: `${statsB.critRate}%`, numA: statsA.critRate, numB: statsB.critRate, diff: statsA.critRate !== statsB.critRate },
      { name: "暴击效果", valA: `${statsA.critEff}%`, valB: `${statsB.critEff}%`, numA: statsA.critEff, numB: statsB.critEff, diff: statsA.critEff !== statsB.critEff },
      { name: "攻击速度", valA: `+${statsA.aspeed.toFixed(1)}%`, valB: `+${statsB.aspeed.toFixed(1)}%`, numA: statsA.aspeed, numB: statsB.aspeed, diff: statsA.aspeed !== statsB.aspeed },
      { name: isMage ? "法术吸血" : "物理吸血", valA: `${isMage ? statsA.mLifesteal : statsA.pLifesteal}%`, valB: `${isMage ? statsB.mLifesteal : statsB.pLifesteal}%`, numA: isMage ? statsA.mLifesteal : statsA.pLifesteal, numB: isMage ? statsB.mLifesteal : statsB.pLifesteal, diff: (isMage ? statsA.mLifesteal : statsA.pLifesteal) !== (isMage ? statsB.mLifesteal : statsB.pLifesteal) },
      { name: "移动速度", valA: `${statsA.moveSpeed}`, valB: `${statsB.moveSpeed}`, numA: statsA.moveSpeed, numB: statsB.moveSpeed, diff: statsA.moveSpeed !== statsB.moveSpeed }
    ];

    const displayRows = this.filterStatsDiffOnly ? rows.filter(r => r.diff) : rows;
    const tableEl = document.getElementById('dStatsTable');
    if (displayRows.length === 0) {
      tableEl.innerHTML = `<div style="text-align:center; padding:20px 0; color:var(--apple-text-secondary); font-size:13px;">两套方案基础面板参数完全一致</div>`;
      return;
    }
    tableEl.innerHTML = displayRows.map(r => {
      const aWinStyle = r.diff && r.numA > r.numB ? 'color:var(--apple-blue); font-weight:700;' : '';
      const bWinStyle = r.diff && r.numB > r.numA ? 'color:var(--apple-green-dark); font-weight:700;' : '';
      return `
        <div class="spec-item-row">
          <div class="spec-left-val" style="${aWinStyle}">${r.valA === '0%' || r.valA === '+0' || r.valA === '0点' ? '—' : r.valA}</div>
          <div class="spec-mid-name">${r.name}</div>
          <div class="spec-right-val" style="${bWinStyle}">${r.valB === '0%' || r.valB === '+0' || r.valB === '0点' ? '—' : r.valB}</div>
        </div>
      `;
    }).join('');
  },

  renderSlots(side, items, elId) {
    const el = document.getElementById(elId);
    if (!el) return;
    el.innerHTML = Array.from({ length: 6 }).map((_, idx) => {
      const it = items[idx];
      if (it) {
        return `
          <div class="slot-item filled" onclick="App.openItemInspector('${side}', ${idx})" title="${it.item_name} · 点击查看详情与机制">
            <img class="slot-img" src="${it.icon}" alt="${it.item_name}">
          </div>
        `;
      } else {
        return `
          <div class="slot-item" onclick="App.openShopSheet('${side}', ${idx})" title="为第 ${idx + 1} 格装配神装">
            <svg class="slot-plus-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          </div>
        `;
      }
    }).join('');
  },

  openItemInspector(side, idx) {
    this.inspectorSide = side;
    this.inspectorSlotIdx = idx;
    const items = side === 'left' ? this.leftItems : this.rightItems;
    const it = items[idx];
    if (!it) return;

    const contentEl = document.getElementById('itemInspectorContent');
    if (!contentEl) return;

    // 格式化基础属性为纯净单元格
    const statCells = (it.stats_chips && it.stats_chips.length > 0)
      ? it.stats_chips.map(s => {
          const m = s.match(/^([+-]?\d+(?:\.\d+)?%?)\s*(.*)$/);
          if (m) {
            return `<div class="inspector-stat-cell"><span class="inspector-stat-val">${m[1]}</span><span class="inspector-stat-name">${m[2]}</span></div>`;
          }
          return `<div class="inspector-stat-cell"><span class="inspector-stat-val">${s}</span></div>`;
        }).join('')
      : '<div class="inspector-stat-cell" style="color:#8e8e93;">基础属性配件</div>';

    // 机制被动与描述高亮
    const passives = it.passives || [];
    let passivesHtml = '';
    if (passives.length === 0) {
      passivesHtml = `
        <div style="font-size:12.5px; color:#8e8e93; padding:8px 0;">
          该装备为纯数值加成，无附带被动机制，适合作为核心大件的前置过渡。
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

        // 机制数值与冷却时间精准高亮
        cleanDesc = cleanDesc.replace(/(\d+(?:\.\d+)?%(?:最大生命|物理伤害|生命)?|冷却\d+(?:\.\d+)?秒)/g, '<strong class="mech-hl">$1</strong>');

        let titleTxt = (p.title || p.name || '被动机制').replace(/^唯一被动[—–-]/, '').replace(/^被动[—–-]/, '').trim();

        return `
          <div class="inspector-mech-row">
            <div class="inspector-mech-title-bar">
              <span class="inspector-mech-title-text"><span class="inspector-mech-badge-icon">◈</span> ${titleTxt}</span>
              ${p.cd ? `<span class="inspector-mech-cd">${p.cd}</span>` : ''}
            </div>
            <div class="inspector-mech-desc">${cleanDesc}</div>
          </div>
        `;
      }).join('');

      if (ruleItems.length > 0) {
        itemsHtml += `
          <div class="inspector-mech-row" style="background:#f2f2f7;">
            <div class="inspector-mech-title-bar">
              <span class="inspector-mech-title-text" style="color:#636366;"><span class="inspector-mech-badge-icon" style="color:#8e8e93;">ℹ</span> 通用规则机制</span>
            </div>
            <div class="inspector-mech-desc" style="color:#636366;">
              ${ruleItems.join(' · ')}
            </div>
          </div>
        `;
      }
      passivesHtml = itemsHtml;
    }

    const slotLabel = `${side === 'left' ? '方案 A' : '方案 B'} · 槽位 ${idx + 1}`;
    const priceFormatted = (it.total_price || 0).toLocaleString();

    contentEl.innerHTML = `
      <div class="inspector-header">
        <img class="inspector-icon" src="${it.icon}" alt="${it.item_name}">
        <div class="inspector-info-col">
          <div class="inspector-name">${it.item_name}</div>
          <div class="inspector-subtitle">${it.category}装备 · 顶级神装</div>
          <div class="inspector-meta-line">
            <span class="price-gold-txt">${priceFormatted} 金币</span>
          </div>
        </div>
      </div>

      <div class="item-inspector-section">
        <div class="item-inspector-section-label">基础属性</div>
        <div class="inspector-stats-grid">
          ${statCells}
        </div>
      </div>

      <div class="item-inspector-section">
        <div class="item-inspector-section-label">唯一被动与专属机制</div>
        <div class="inspector-mechanics-wrap">
          ${passivesHtml}
        </div>
      </div>
    `;

    const modal = document.getElementById('itemInspectorModal');
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

  closeItemInspector() {
    const modal = document.getElementById('itemInspectorModal');
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

  openShopFromInspector() {
    const side = this.inspectorSide;
    const idx = this.inspectorSlotIdx;
    this.closeItemInspector();
    this.openShopSheet(side, idx);
  },

  unequipFromInspector() {
    const side = this.inspectorSide;
    const idx = this.inspectorSlotIdx;
    this.closeItemInspector();
    if (side === 'left') {
      this.leftItems[idx] = null;
      this.isLeftCustomMode = true;
      this.officialSchemeIdx = -1;
      const tEl = document.getElementById("leftBuildTitle");
      if (tEl) {
        tEl.textContent = "我的实战方案";
        tEl.classList.remove("is-prompt");
      }
      this.renderSchemeTabs();
    } else {
      this.rightItems[idx] = null;
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
    this.recalculateAll();
  },

  deleteSlotItem(e, side, idx) {
    e.stopPropagation();
    if (side === 'left') {
      this.leftItems[idx] = null;
      this.isLeftCustomMode = true;
      this.officialSchemeIdx = -1;
      const tEl = document.getElementById("leftBuildTitle");
      if (tEl) {
        tEl.textContent = "我的实战方案";
        tEl.classList.remove("is-prompt");
      }
      this.renderSchemeTabs();
    } else {
      this.rightItems[idx] = null;
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
    this.recalculateAll();
  },

});
