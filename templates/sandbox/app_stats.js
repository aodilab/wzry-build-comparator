// ==============================================================================
// 王者出装箱 ｜ 局内六神装配装沙盒 - 属性计算与规则诊断引擎 (app_stats.js)
// 专注：装备/铭文属性叠加、上限截断、四维成长折算、被动互斥与小件吞噬诊断
// 符合 AGENTS.md 规范：横向解耦，行数维持在 250~350 行
// ==============================================================================

// 计算复合属性（提供给沙盒面板与协同引擎）
function calculateCompositeStats() {
  const effectiveItems = [];
  const consumedNotes = [];
  const slots = (typeof currentSlots !== 'undefined' && currentSlots) ? currentSlots : [];
  
  for (let i = 0; i < slots.length; i++) {
    const curr = slots[i].item_name;
    let isConsumed = false;
    for (let j = i + 1; j < slots.length; j++) {
      const later = slots[j].item_name;
      const recipes = RECIPES_MAP[later] || [];
      if (recipes.includes(curr)) {
        isConsumed = true;
        consumedNotes.push(`原料【${curr}】已被大件【${later}】合成吞噬，属性已覆盖`);
        break;
      }
    }
    if (!isConsumed) effectiveItems.push(slots[i]);
  }

  let totals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, mp:0, crit:0, aspeed:0, cdr:0, percent_speed:0, flat_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce_flat:0, p_pierce_percent:0, m_pierce_flat:0, m_pierce_percent:0, has_hat:false };
  let bootsCounted = false;

  // 铭文加成汇总（支持混搭）
  let arcanaTotals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, crit:0, crit_effect:0, aspeed:0, cdr:0, percent_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce_flat:0, m_pierce_flat:0, hp_regen:0 };
  const arcanaState = (typeof currentArcana !== 'undefined' && currentArcana) ? currentArcana : {};
  ['red', 'green', 'blue'].forEach(col => {
    const map = arcanaState[col] || {};
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        arcanaTotals.atk += (s.phys_atk || 0) * count;
        arcanaTotals.ap += (s.magic_atk || 0) * count;
        arcanaTotals.pdef += (s.phys_def || 0) * count;
        arcanaTotals.mdef += (s.magic_def || 0) * count;
        arcanaTotals.hp += (s.max_hp || 0) * count;
        arcanaTotals.crit += (s.crit_rate_pct || 0) * count;
        arcanaTotals.crit_effect += (s.crit_effect_pct || 0) * count;
        arcanaTotals.aspeed += (s.atk_speed_pct || 0) * count;
        arcanaTotals.cdr += (s.cd_reduction_pct || 0) * count;
        arcanaTotals.percent_speed += (s.move_speed_pct || 0) * count;
        arcanaTotals.p_lifesteal += (s.phys_vamp_pct || 0) * count;
        arcanaTotals.m_lifesteal += (s.magic_vamp_pct || 0) * count;
        arcanaTotals.p_pierce_flat += (s.phys_pierce || 0) * count;
        arcanaTotals.m_pierce_flat += (s.magic_pierce || 0) * count;
        arcanaTotals.hp_regen += (s.hp_regen || 0) * count;
      }
    }
  });
  for (let k in arcanaTotals) {
    arcanaTotals[k] = Math.round(arcanaTotals[k] * 10) / 10;
  }

  let totalGold = 0;
  slots.forEach(it => totalGold += (it.total_price || 0));

  effectiveItems.forEach(it => {
    const st = it.stats || {};
    totals.atk += st.atk || 0;
    totals.ap += st.ap || 0;
    totals.pdef += st.pdef || 0;
    totals.mdef += st.mdef || 0;
    totals.hp += st.hp || 0;
    totals.mp += st.mp || 0;
    totals.crit += st.crit || 0;
    totals.aspeed += st.aspeed || 0;
    totals.cdr += st.cdr || 0;
    totals.percent_speed += st.percent_speed || 0;
    totals.p_lifesteal += st.p_lifesteal || 0;
    totals.m_lifesteal += st.m_lifesteal || 0;
    totals.p_pierce_flat += st.p_pierce_flat || 0;
    totals.p_pierce_percent = Math.max(totals.p_pierce_percent, st.p_pierce_percent || 0);
    totals.m_pierce_flat += st.m_pierce_flat || 0;
    totals.m_pierce_percent = Math.max(totals.m_pierce_percent, st.m_pierce_percent || 0);
    if (it.item_name === '博学者之怒') totals.has_hat = true;

    if (BOOTS_MAP[it.item_name] && !bootsCounted) {
      totals.flat_speed = BOOTS_MAP[it.item_name];
      bootsCounted = true;
    }
  });

  const rawAp = totals.ap + arcanaTotals.ap;
  const finalAp = totals.has_hat ? Math.floor(rawAp * 1.3) : rawAp;
  const totalCdr = totals.cdr + arcanaTotals.cdr;
  const cappedCdr = Math.min(Math.floor(totalCdr), 40);

  const hero = (typeof currentHero !== 'undefined' && currentHero) ? currentHero : (HEROES_DATA[0] || {});
  const b = hero.base_stats || { hp:[3200,7000], atk:[170,380], pdef:[100,400], mdef:[50,169], speed:370, aspeed:"+2.0%" };
  const bHp = b.hp ? b.hp[1] : 7000;
  const bAtk = b.atk ? b.atk[1] : 380;
  const bPdef = b.pdef ? b.pdef[1] : 400;
  const bMdef = b.mdef ? b.mdef[1] : 169;
  const bSpeed = b.speed || 370;
  const growthMatch = (b.aspeed || '+1.0%').match(/([\d\.]+)%/);
  const growthVal = growthMatch ? parseFloat(growthMatch[1]) : 1.0;
  const heroSelfAspeed = Math.floor(growthVal * 14);
  const totalAspeed = heroSelfAspeed + Math.floor(totals.aspeed) + Math.floor(arcanaTotals.aspeed);

  let extraPdef = 0;
  let extraMdef = 0;
  let extraPdefNote = "";
  let extraMdefNote = "";
  if (effectiveItems.some(i => i.item_name === '时之预言')) {
    const propVal = Math.min(Math.floor(finalAp * 0.1), 250);
    extraPdef += propVal; extraMdef += propVal;
    extraPdefNote = `(时之预言+${propVal}) `;
  }
  if (effectiveItems.some(i => i.item_name === '破魔刀')) {
    const pmVal = Math.min(Math.floor((bAtk + totals.atk + arcanaTotals.atk) * 0.5), 250);
    extraMdef += pmVal;
    extraMdefNote = `(破魔刀+${pmVal}) `;
  }

  const finalHp = bHp + totals.hp + arcanaTotals.hp;
  const totPdef = bPdef + totals.pdef + arcanaTotals.pdef + extraPdef;
  const totMdef = bMdef + totals.mdef + arcanaTotals.mdef + extraMdef;
  const pReduction = (totPdef / (totPdef + 602) * 100).toFixed(1);
  const mReduction = (totMdef / (totMdef + 602) * 100).toFixed(1);

  const totalSpeedPct = totals.percent_speed + arcanaTotals.percent_speed;
  const pspeedStr = totalSpeedPct > 0 ? totalSpeedPct.toFixed(1).replace(/\.0$/, '') : '0';
  const calcSpeed = Math.floor((bSpeed + totals.flat_speed) * (1 + totalSpeedPct / 100));

  const totalCrit = Math.round((totals.crit + arcanaTotals.crit) * 10) / 10;
  const totalPhysPierce = Math.round((totals.p_pierce_flat + arcanaTotals.p_pierce_flat) * 10) / 10;
  const totalMagicPierce = Math.round((totals.m_pierce_flat + arcanaTotals.m_pierce_flat) * 10) / 10;
  const totalPhysVamp = Math.round((totals.p_lifesteal + arcanaTotals.p_lifesteal) * 10) / 10;
  const totalMagicVamp = Math.round((totals.m_lifesteal + arcanaTotals.m_lifesteal) * 10) / 10;

  return {
    effectiveItems,
    consumedNotes,
    totalGold,
    totals,
    arcanaTotals,
    finalAp,
    cappedCdr,
    totalCdr,
    bHp, bAtk, bPdef, bMdef, bSpeed, heroSelfAspeed, totalAspeed,
    extraPdefNote, extraMdefNote,
    finalHp, totPdef, totMdef, pReduction, mReduction,
    pspeedStr, calcSpeed,
    totalCrit, totalPhysPierce, totalMagicPierce, totalPhysVamp, totalMagicVamp,
    cdr: cappedCdr
  };
}

// 核心计算入口并刷新 UI
function recalculate() {
  const stats = calculateCompositeStats();
  const {
    effectiveItems, consumedNotes, totalGold, totals, arcanaTotals,
    finalAp, cappedCdr, bHp, bAtk, bPdef, bMdef, bSpeed, heroSelfAspeed, totalAspeed,
    extraPdefNote, extraMdefNote, finalHp, totPdef, totMdef, pReduction, mReduction,
    pspeedStr, calcSpeed, totalCrit, totalPhysPierce, totalMagicPierce, totalPhysVamp, totalMagicVamp
  } = stats;

  const goldEl = document.getElementById('totalGold');
  if (goldEl) goldEl.innerText = `${totalGold.toLocaleString()} G`;
  const mobileGoldEl = document.getElementById('mobileTotalGold');
  if (mobileGoldEl) mobileGoldEl.innerText = `${totalGold} 金币`;
  
  const statsBox = document.getElementById('statsContainer');
  if (statsBox) {
    if (window.innerWidth <= 768) {
      statsBox.innerHTML = `
        <div class="stats-grid">
          <div class="stat-cell"><span class="stat-name">物理攻击</span><div class="stat-num-box"><span class="stat-val">${totals.atk + arcanaTotals.atk + bAtk}</span>${(totals.atk + arcanaTotals.atk) > 0 ? `<span class="stat-plus">+${totals.atk + arcanaTotals.atk}</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">法术攻击</span><div class="stat-num-box"><span class="stat-val">${finalAp}</span>${finalAp > 0 ? `<span class="stat-plus">+${finalAp}</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">最大生命</span><div class="stat-num-box"><span class="stat-val">${finalHp}</span>${(totals.hp + arcanaTotals.hp) > 0 ? `<span class="stat-plus">+${totals.hp + arcanaTotals.hp}</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">物理防御</span><div class="stat-num-box"><span class="stat-val">${totPdef}</span>${(totals.pdef + arcanaTotals.pdef) > 0 ? `<span class="stat-plus">+${totals.pdef + arcanaTotals.pdef}</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">法术防御</span><div class="stat-num-box"><span class="stat-val">${totMdef}</span>${(totals.mdef + arcanaTotals.mdef) > 0 ? `<span class="stat-plus">+${totals.mdef + arcanaTotals.mdef}</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">冷却缩减</span><div class="stat-num-box"><span class="stat-val">${cappedCdr}%</span>${cappedCdr >= 40 ? `<span class="stat-cap">满CD</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">暴击率</span><div class="stat-num-box"><span class="stat-val">${totalCrit}%</span></div></div>
          <div class="stat-cell"><span class="stat-name">移动速度</span><div class="stat-num-box"><span class="stat-val">${calcSpeed}</span>${(calcSpeed - bSpeed) > 0 ? `<span class="stat-plus">+${calcSpeed - bSpeed}</span>` : ''}</div></div>
          <div class="stat-cell"><span class="stat-name">物理穿透</span><div class="stat-num-box"><span class="stat-val">${totalPhysPierce > 0 ? `+${totalPhysPierce}` : '0'}</span></div></div>
          ${totalMagicPierce > 0 ? `<div class="stat-cell"><span class="stat-name">法术穿透</span><div class="stat-num-box"><span class="stat-val">+${totalMagicPierce}</span></div></div>` : ''}
        </div>
      `;
    } else {
      statsBox.innerHTML = `
      <!-- 生存健康面板 -->
      <div class="metric-section">
        <div class="metric-section-title">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-green)" stroke-width="2.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
          生存与抗性指标
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">最终最大生命值</span>
            <span class="metric-sub">${bHp}基 + ${totals.hp}装 + ${arcanaTotals.hp}铭</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${finalHp.toLocaleString()}</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">物理防御 (物抗)</span>
            <span class="metric-sub">${extraPdefNote}${bPdef}基 + ${totals.pdef}装 + ${arcanaTotals.pdef}铭 ｜ 免伤率 ${pReduction}%</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${totPdef}</span>
            <div class="bar-track"><div class="bar-fill bar-fill-armor" style="width: ${Math.min(pReduction, 100)}%;"></div></div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">法术防御 (魔抗)</span>
            <span class="metric-sub">${extraMdefNote}${bMdef}基 + ${totals.mdef}装 + ${arcanaTotals.mdef}铭 ｜ 免伤率 ${mReduction}%</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${totMdef}</span>
            <div class="bar-track"><div class="bar-fill bar-fill-marmor" style="width: ${Math.min(mReduction, 100)}%;"></div></div>
          </div>
        </div>
      </div>

      <!-- 进攻与爆发面板 -->
      <div class="metric-section">
        <div class="metric-section-title">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-amber)" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          输出与攻击强度
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">最终物理攻击</span>
            <span class="metric-sub">${bAtk}基 + ${totals.atk}装 + ${arcanaTotals.atk}铭</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${bAtk + totals.atk + arcanaTotals.atk}</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">最终法术攻击</span>
            <span class="metric-sub">${totals.has_hat ? '含帽子+30% ｜ ' : ''}${totals.ap}装 + ${arcanaTotals.ap}铭</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val" style="color: ${finalAp > 0 ? 'var(--color-purple)' : 'inherit'};">${finalAp}</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">暴击率 / 攻速总计</span>
            <span class="metric-sub">暴击(装${Math.floor(totals.crit)}+铭${Math.floor(arcanaTotals.crit)}) ｜ 攻速(成${heroSelfAspeed}+装${Math.floor(totals.aspeed)}+铭${Math.floor(arcanaTotals.aspeed)})</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${totalCrit}% ｜ ${totalAspeed}%</span>
          </div>
        </div>
      </div>

      <!-- 机动与特殊属性 -->
      <div class="metric-section">
        <div class="metric-section-title">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-blue)" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          机动、冷却与穿透
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">实战极限移速</span>
            <span class="metric-sub">(${bSpeed}+${totals.flat_speed}鞋) × (1+${pspeedStr}%)</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${calcSpeed}</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">冷却缩减</span>
            <span class="metric-sub">装+${Math.floor(totals.cdr)}% ｜ 铭+${Math.floor(arcanaTotals.cdr)}%${cappedCdr >= 40 ? ' (满冷缩)' : ''}</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${cappedCdr}%</span>
            <div class="bar-track"><div class="bar-fill bar-fill-cdr" style="width: ${(cappedCdr / 40 * 100)}%;"></div></div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">双穿透 (固定/百分比)</span>
            <span class="metric-sub">物穿 ${totalPhysPierce}点(${totals.p_pierce_percent}%) ｜ 魔穿 ${totalMagicPierce}点(${totals.m_pierce_percent}%)</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-highlight">双抗穿透生效</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label-group">
            <span class="metric-name">续航吸血</span>
            <span class="metric-sub">物吸 ${totalPhysVamp}% (含铭+${arcanaTotals.p_lifesteal}%) ｜ 法吸 ${totalMagicVamp}% (含铭+${arcanaTotals.m_lifesteal}%)</span>
          </div>
          <div class="metric-value-group">
            <span class="metric-val">${totalPhysVamp || totalMagicVamp ? `${totalPhysVamp}% / ${totalMagicVamp}%` : '0%'}</span>
          </div>
        </div>
      </div>
    `;
    }
  }

  // 诊断互斥
  renderDiagnosis(effectiveItems, consumedNotes);

  // 同步主页面战术协同简报卡片 (微信小程序同款)
  if (typeof updateSynergyBrief === 'function') {
    updateSynergyBrief();
  }
}

// 诊断装备互斥与冲突提示
function renderDiagnosis(effectiveItems, consumedNotes) {
  const diagBox = document.getElementById('diagnoseContainer');
  if (!diagBox) return;
  diagBox.innerHTML = '';
  const diagPanel = diagBox.closest('.diag-panel');
  if (effectiveItems.length === 0) {
    if (diagPanel) diagPanel.style.display = 'none';
    return;
  }
  if (diagPanel) diagPanel.style.display = '';

  const effNames = effectiveItems.map(i => i.item_name);
  const issues = [];

  // 小件吞噬
  consumedNotes.forEach(note => issues.push({ type: 'info', text: note }));

  // 强击
  const qj = effNames.filter(n => ["宗师之力", "冰痕之握", "巫术法杖", "光辉之剑"].includes(n));
  if (qj.length > 1) issues.push({ type: 'warn', text: `【强击被动互斥】同时出了 ${qj.join(' 与 ')}，伤害仅生效一件！` });

  // 双鞋
  const boots = effNames.filter(n => BOOTS_MAP[n]);
  if (boots.length > 1) issues.push({ type: 'warn', text: `【神速双鞋互斥】同时出了 ${boots.join(' 与 ')}，移动速度不叠加！` });

  // 主动共存
  const actives = effNames.filter(n => ACTIVE_ITEMS.includes(n));
  if (actives.length > 1) issues.push({ type: 'warn', text: `【多主动按键共存】出了 ${actives.join(' 与 ')}，局内默认只能设置 1 个主动按键！` });

  // 打野惩击
  const jungles = effNames.filter(n => JUNGLE_ITEMS.includes(n));
  if (jungles.length > 0) issues.push({ type: 'warn', text: `【召唤师技能提示】出了打野刀（${jungles.join('、')}），局内必须携带【惩击】方可购买！` });

  if (issues.length === 0) {
    diagBox.innerHTML = `
      <div class="diag-card diag-card-pass">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <span>当前 6 件成装无被动互斥与按键冲突，契合度 100%！</span>
      </div>`;
  } else {
    issues.forEach(iss => {
      const el = document.createElement('div');
      el.className = `diag-card ${iss.type === 'warn' ? 'diag-card-warn' : (iss.type === 'info' ? 'diag-card-info' : 'diag-card-pass')}`;
      const icon = iss.type === 'warn' 
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
      el.innerHTML = `${icon}<span>${iss.text}</span>`;
      diagBox.appendChild(el);
    });
  }
}
