Object.assign(App, {
  recalculateAll() {
    this.renderSlots('left', this.leftItems, 'leftSlots');
    this.renderSlots('right', this.rightItems, 'rightSlots');

    this.renderArcanaSummary('left', this.leftArc, 'leftArcanaRow');
    this.renderArcanaSummary('right', this.rightArc, 'rightArcanaRow');

    const btnResetA = document.getElementById('btnResetOfficial');
    if (btnResetA) {
      btnResetA.style.display = this.leftItems.some(Boolean) ? 'inline-flex' : 'none';
    }
    const btnClearB = document.getElementById('btnClearRight');
    if (btnClearB) {
      btnClearB.style.display = this.rightItems.some(Boolean) ? 'inline-flex' : 'none';
    }

    const hero = this.hero;
    const arcDict = window.DATASET.ARCANA_DATA;
    const statsA = calcBuildStats(hero, this.leftItems, this.leftArc, arcDict);
    const statsB = calcBuildStats(hero, this.rightItems, this.rightArc, arcDict);

    const combo = this.combos[this.activeComboIdx] || { keys: '1A2A', name: '常规爆发' };
    const outA = calcComboOutcome(combo, statsA, hero);
    const outB = calcComboOutcome(combo, statsB, hero);

    // 1. 实战对决板块动态分流 (辅助团队价值 vs 常规伤害对决，100% 对齐线上网页端)
    const isSupport = (hero.role && hero.role.includes("辅助")) || this.currentLane === "游走";

    const titleEl = document.getElementById('dPrimaryTitle');
    const descEl = document.getElementById('dPrimaryDesc');
    const comboWrap = document.getElementById('dComboWrap');
    const dmgBlock = document.getElementById('dDmgBlock');
    const supportBlock = document.getElementById('dSupportBlock');
    const skillEntryDesc = document.getElementById('dSkillEntryDesc');

    if (isSupport) {
      if (titleEl) titleEl.textContent = '辅助团队价值与承伤对决';
      if (descEl) descEl.textContent = '测算依据：全队护盾/治疗量 + 极限有效物理与法术承伤上限 (EHP) + 开团控制冷却';
      if (comboWrap) comboWrap.style.display = 'none';
      if (dmgBlock) dmgBlock.style.display = 'none';
      if (supportBlock) supportBlock.style.display = 'block';
      if (skillEntryDesc) skillEntryDesc.textContent = '团队光环 / 护盾治疗 / 承伤极限';

      const ehpPA = outA.ehpPhys || 0;
      const ehpPB = outB.ehpPhys || 0;
      document.getElementById('dEhpPhysA').innerHTML = `${ehpPA.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dEhpPhysB').innerHTML = `${ehpPB.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dEhpPhysPill').innerHTML = this.formatAppleWinnerPill(ehpPA, ehpPB, "点");

      const ehpMA = outA.ehpMagic || 0;
      const ehpMB = outB.ehpMagic || 0;
      document.getElementById('dEhpMagicA').innerHTML = `${ehpMA.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dEhpMagicB').innerHTML = `${ehpMB.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dEhpMagicPill').innerHTML = this.formatAppleWinnerPill(ehpMA, ehpMB, "点");

      const utA = outA.supportUtility || 0;
      const utB = outB.supportUtility || 0;
      document.getElementById('dSupportUtilA').innerHTML = `${utA.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dSupportUtilB').innerHTML = `${utB.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dSupportUtilPill').innerHTML = this.formatAppleWinnerPill(utA, utB, "点");
    } else {
      if (titleEl) titleEl.textContent = '实战伤害对决';
      if (descEl) descEl.textContent = '双抗折算实战净掉血';
      if (comboWrap) comboWrap.style.display = 'block';
      if (dmgBlock) dmgBlock.style.display = 'block';
      if (supportBlock) supportBlock.style.display = 'none';
      if (skillEntryDesc) skillEntryDesc.textContent = '伤害 / 控制 / 回复物理拆解';

      const sqA = outA.dmgSquishy || 0;
      const sqB = outB.dmgSquishy || 0;
      document.getElementById('dDmgSquishyA').innerHTML = `${sqA.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dDmgSquishyB').innerHTML = `${sqB.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dDmgSquishyPill').innerHTML = this.formatAppleWinnerPill(sqA, sqB, "点");

      const tkA = outA.dmgTank || 0;
      const tkB = outB.dmgTank || 0;
      document.getElementById('dDmgTankA').innerHTML = `${tkA.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dDmgTankB').innerHTML = `${tkB.toLocaleString()}<span class="metric-num-unit">点</span>`;
      document.getElementById('dDmgTankPill').innerHTML = this.formatAppleWinnerPill(tkA, tkB, "点");
    }

    // 2. 野区打怪耗时 (仅打野分路时呈现，与网页端完全对齐)
    const isJungle = this.currentLane === '打野';
    const jSection = document.getElementById('jungleSection');
    if (jSection) {
      jSection.style.display = isJungle ? 'block' : 'none';
      if (isJungle) {
        document.getElementById('dBuffTimeA').innerHTML = `${outA.buffTime || 0}<span class="metric-num-unit">s</span>`;
        document.getElementById('dBuffTimeB').innerHTML = `${outB.buffTime || 0}<span class="metric-num-unit">s</span>`;
        document.getElementById('dBuffTimePill').innerHTML = this.formatAppleWinnerPill(outA.buffTime || 0, outB.buffTime || 0, "s", true);

        document.getElementById('dDragonTimeA').innerHTML = `${outA.dragonTime || 0}<span class="metric-num-unit">s</span>`;
        document.getElementById('dDragonTimeB').innerHTML = `${outB.dragonTime || 0}<span class="metric-num-unit">s</span>`;
        document.getElementById('dDragonTimePill').innerHTML = this.formatAppleWinnerPill(outA.dragonTime || 0, outB.dragonTime || 0, "s", true);
      }
    }

    // 3. 生存与续航 (对齐网页版 4 大核心续航指标)
    const isMageHero = this.hero.role && this.hero.role.includes("法师");
    const vampTitleEl = document.getElementById('dVampTitle');
    const vampSubEl = document.getElementById('dVampSub');
    if (vampTitleEl) vampTitleEl.textContent = isMageHero ? "单次技能/普攻吸血" : "普攻单次吸血";
    if (vampSubEl) vampSubEl.textContent = isMageHero ? "法术吸血/物理吸血单次实算" : "物理吸血率单次普攻实算";

    const vA = outA.aHitVamp || 0;
    const vB = outB.aHitVamp || 0;
    document.getElementById('dVampA').innerHTML = `${vA}<span class="metric-num-unit">点</span>`;
    document.getElementById('dVampB').innerHTML = `${vB}<span class="metric-num-unit">点</span>`;
    document.getElementById('dVampPill').innerHTML = this.formatAppleWinnerPill(vA, vB, "点");

    const regA = outA.outOfCombatRegen || 0;
    const regB = outB.outOfCombatRegen || 0;
    const regenAEl = document.getElementById('dRegenA');
    const regenBEl = document.getElementById('dRegenB');
    const regenPillEl = document.getElementById('dRegenPill');
    if (regenAEl) regenAEl.innerHTML = `${regA}<span class="metric-num-unit">点/s</span>`;
    if (regenBEl) regenBEl.innerHTML = `${regB}<span class="metric-num-unit">点/s</span>`;
    if (regenPillEl) regenPillEl.innerHTML = this.formatAppleWinnerPill(regA, regB, "点/s");

    const rA = outA.regularHeal || 0;
    const rB = outB.regularHeal || 0;
    document.getElementById('dHealRegA').innerHTML = `${rA}<span class="metric-num-unit">点</span>`;
    document.getElementById('dHealRegB').innerHTML = `${rB}<span class="metric-num-unit">点</span>`;
    document.getElementById('dHealRegPill').innerHTML = this.formatAppleWinnerPill(rA, rB, "点");
    if (outA.healDef) document.getElementById('dHealTitleA').textContent = outA.healDef;

    const clA = outA.clutchHeal || 0;
    const clB = outB.clutchHeal || 0;
    const clAEl = document.getElementById('dClutchHealA');
    const clBEl = document.getElementById('dClutchHealB');
    const clPillEl = document.getElementById('dClutchHealPill');
    if (clAEl) clAEl.innerHTML = `${clA}<span class="metric-num-unit">点</span>`;
    if (clBEl) clBEl.innerHTML = `${clB}<span class="metric-num-unit">点</span>`;
    if (clPillEl) clPillEl.innerHTML = this.formatAppleWinnerPill(clA, clB, "点");

    // 4. 技能冷却时间 (动态读取当前英雄真实 1/2/3 技能名称与基准冷却)
    const heroSkillsRaw = (window.DATASET.HERO_SKILLS && window.DATASET.HERO_SKILLS[this.hero.cname]) || [];
    const activeSkills = heroSkillsRaw.length >= 4 ? heroSkillsRaw.slice(1, 4) : [];
    const baseCds = activeSkills.length === 3
      ? activeSkills.map((sk, i) => sk.cd_sec || [5.0, 6.0, 12.0][i])
      : [5.0, 6.0, 12.0];
    const skillTitles = activeSkills.length === 3
      ? activeSkills.map((sk, i) => `${i + 1}技能 · ${(sk.name || '').split('(')[0].split('（')[0].trim()}`)
      : ["1技能实际真空期", "2技能实际真空期", "3技能 (大招) 实际真空期"];
    const skillSubs = [
      `主力起手/主要消耗技能实战冷却 (基准 ${baseCds[0].toFixed(1)}s)`,
      `核心位移/保命控制技能实战冷却 (基准 ${baseCds[1].toFixed(1)}s)`,
      `团战决定性大招实战冷却 (基准 ${baseCds[2].toFixed(1)}s)`
    ];
    const cdA = baseCds.map(cd => +(cd * (1 - statsA.cdr / 100)).toFixed(1));
    const cdB = baseCds.map(cd => +(cd * (1 - statsB.cdr / 100)).toFixed(1));

    document.getElementById('dCdrSummaryText').textContent = `满级满装技能真空期 · 方案 A 冷却加成 ${statsA.cdr}% vs 方案 B ${statsB.cdr}%`;
    const cdGrid = document.getElementById('dCdGrid');
    cdGrid.innerHTML = skillTitles.map((t, idx) => `
      <div class="compare-metric-row">
        <div class="metric-card-head">${t}</div>
        <div class="metric-card-sub">${skillSubs[idx]}</div>
        <div class="metric-cols-row">
          <div class="metric-side-col">
            <div class="metric-num-val">${cdA[idx]}<span class="metric-num-unit">s</span></div>
          </div>
          <div class="metric-vs-sep">vs</div>
          <div class="metric-side-col">
            <div class="metric-num-val">${cdB[idx]}<span class="metric-num-unit">s</span></div>
          </div>
        </div>
        <div class="metric-winner-wrap">${this.formatAppleWinnerPill(cdA[idx], cdB[idx], "s", true)}</div>
      </div>
    `).join('');

    // 5. 核心机制协同差异 (严格对齐 wzry.aodilab.com 核心机制判定，统一为 compare-metric-row)
    this.renderMechanicDifferences(this.leftItems, this.rightItems);

    // 6. 综合属性规格清单
    this.renderAppleSpecsTable(statsA, statsB);
  },

  formatAppleWinnerPill(vA, vB, unit, lowerIsBetter) {
    const diff = vB - vA;
    if (Math.abs(diff) < 0.01) return `<span class="apple-winner-pill winner-tie">持平</span>`;
    const aBetter = lowerIsBetter ? (diff > 0) : (diff < 0);
    const delta = Math.abs(diff);
    const pct = vA > 0 ? ` (${((delta / vA) * 100).toFixed(1)}%)` : '';
    if (aBetter) {
      return `<span class="apple-winner-pill winner-a">方案 A 优 ${delta.toLocaleString()}${unit}${pct}</span>`;
    } else {
      return `<span class="apple-winner-pill winner-b">方案 B 优 ${delta.toLocaleString()}${unit}${pct}</span>`;
    }
  },

});
