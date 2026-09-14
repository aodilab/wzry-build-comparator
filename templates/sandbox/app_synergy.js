function openSynergyModal() {
  const overlay = document.getElementById('synergyModalOverlay');
  if (!overlay) return;
  overlay.classList.add('active');

  // 1. 填充头部英雄基本信息
  document.getElementById('synergyHeroAvatar').src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${currentHero.ename}/${currentHero.ename}.jpg`;
  document.getElementById('synergyHeroName').innerText = currentHero.cname;
  document.getElementById('synergyHeroRole').innerText = `${currentHero.lane} ｜ ${currentHero.role}`;
  document.getElementById('synergyHeroSub').innerText = `${currentHero.title || '英雄'} · 六神装被动效果与技能机制联动实战报告`;

  renderSynergyContent();
}

function closeSynergyModal(e) {
  if (e && e.target !== e.currentTarget) return;
  const overlay = document.getElementById('synergyModalOverlay');
  if (overlay) overlay.classList.remove('active');
}

function renderSynergyContent() {
  const container = document.getElementById('synergyModalScroll');
  if (!container) return;

  const skills = HERO_SKILLS_DATA[currentHero.cname] || [];
  const effItems = [];
  // 获取当前生效装备（排除吞噬件）
  for (let i = 0; i < currentSlots.length; i++) {
    const curr = currentSlots[i].item_name;
    let isConsumed = false;
    for (let j = i + 1; j < currentSlots.length; j++) {
      const later = currentSlots[j].item_name;
      const recipes = RECIPES_MAP[later] || [];
      if (recipes.includes(curr)) { isConsumed = true; break; }
    }
    if (!isConsumed) effItems.push(currentSlots[i]);
  }

  // 计算冷却缩减与属性
  let totalCdr = 0;
  let totalPhysPierce = 0;
  let totalMagicPierce = 0;
  let hasSpellblade = false;
  let spellbladeItem = '';
  let hasHealBoost = false;
  let hasDamageReduce = false;
  let hasOnHit = false;

  effItems.forEach(it => {
    const st = it.stats || {};
    totalCdr += st.cdr || 0;
    totalPhysPierce += st.p_pierce_flat || 0;
    totalMagicPierce += st.m_pierce_flat || 0;
    if (['宗师之力', '冰痕之握', '巫术法杖', '光辉之剑'].includes(it.item_name)) {
      hasSpellblade = true;
      spellbladeItem = it.item_name;
    }
    if (it.item_name === '不死鸟之眼') hasHealBoost = true;
    if (it.item_name === '纯净苍穹') hasDamageReduce = true;
    if (['末世', '闪电匕首', '金色圣剑', '寒霜袭侵'].includes(it.item_name)) hasOnHit = true;
  });

  // 加上铭文冷缩与穿透
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        totalCdr += (s.cd_reduction_pct || 0) * count;
        totalPhysPierce += (s.phys_pierce || 0) * count;
        totalMagicPierce += (s.magic_pierce || 0) * count;
      }
    }
  });

  const cappedCdr = Math.min(Math.round(totalCdr * 10) / 10, 40);
  const cdrRatio = cappedCdr / 100;

  // 1. 横幅：当前出装与铭文展示
  let itemThumbsHtml = '';
  for (let i = 0; i < 6; i++) {
    if (currentSlots[i]) {
      itemThumbsHtml += `<img class="synergy-item-thumb" src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/${currentSlots[i].item_id}.png" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/itemimg/${currentSlots[i].item_id}.jpg'" alt="${currentSlots[i].item_name}" title="${currentSlots[i].item_name}">`;
    } else {
      itemThumbsHtml += `<div class="synergy-empty-thumb">+</div>`;
    }
  }

  const arcDescParts = [];
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    const sub = Object.entries(map).filter(([_, c]) => c > 0).map(([n, c]) => `${c}${n}`).join('+');
    if (sub) arcDescParts.push(sub);
  });
  const arcDescStr = arcDescParts.join(' · ') || '未配置铭文';

  const bannerHtml = `
    <div class="synergy-banner">
      <div class="synergy-items-strip">
        <span style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">已配装备：</span>
        ${itemThumbsHtml}
      </div>
      <div style="font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 10px;">
        <span style="display: inline-flex; align-items: center; gap: 4px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
          <strong>铭文搭配</strong>：${arcDescStr}
        </span>
        <span style="background: var(--color-blue-bg); color: var(--color-blue); font-weight: 600; padding: 2px 8px; border-radius: 6px;">实战冷缩 ${cappedCdr}%</span>
      </div>
    </div>
  `;

  // 2. 英雄技能机制与动态冷却折算卡片
  let skillsCardsHtml = '';
  skills.forEach((sk, idx) => {
    let cdDisplay = '';
    if (sk.type === '被动') {
      if (sk.cd_sec > 0) {
        cdDisplay = `
          <div style="text-align: right;">
            <div style="font-size: 12px; font-weight: 600; color: var(--text-primary);">
              内置冷却 <span class="synergy-cd-highlight">${sk.cd_sec}s</span>
            </div>
            <div style="font-size: 10.5px; color: var(--text-tertiary); margin-top: 1px;">固定机制 · 不受冷缩影响</div>
          </div>
        `;
      } else {
        cdDisplay = `<div style="font-size: 12px; color: var(--text-tertiary);">常驻被动生效 · 无冷却</div>`;
      }
    } else if (sk.cd_sec > 0) {
      const reduced = Math.round(sk.cd_sec * (1 - cdrRatio) * 10) / 10;
      const diff = Math.round((sk.cd_sec - reduced) * 10) / 10;
      let extraGrowth = '';
      if (sk.lv1_cd && sk.lv1_cd > sk.cd_sec) {
        const lv1Reduced = Math.round(sk.lv1_cd * (1 - cdrRatio) * 10) / 10;
        extraGrowth = `<div style="font-size: 10.5px; color: var(--text-tertiary); margin-top: 2px;">成长阶梯: ${sk.cd} · Lv1实战 ${lv1Reduced}s</div>`;
      }
      cdDisplay = `
        <div style="text-align: right;">
          <div style="font-size: 12px; font-weight: 600; color: var(--text-primary);">
            实战冷却 <span class="synergy-cd-highlight">${reduced}s</span>
            <span style="color: var(--text-tertiary); font-size: 11px; font-weight: 400; margin-left: 4px;">(满级基准 ${sk.cd_sec}s ｜ 缩短 ${diff}s)</span>
          </div>
          ${extraGrowth}
        </div>
      `;
    } else {
      cdDisplay = `<span style="color: var(--text-tertiary); font-size: 12px;">${sk.cd || '无冷却'}</span>`;
    }

    const tagsHtml = (sk.tags || []).map(t => `<span class="synergy-tag">${t}</span>`).join('');
    skillsCardsHtml += `
      <div class="synergy-skill-card">
        <div class="synergy-skill-top">
          <div class="synergy-skill-name-row">
            <span class="synergy-skill-badge">${sk.type}</span>
            <span class="synergy-skill-name">${sk.name}</span>
          </div>
          <div class="synergy-skill-tags">${tagsHtml}</div>
        </div>
        <div class="synergy-cd-bar">
          <span style="font-size: 11.5px; font-weight: 600; color: var(--text-secondary); white-space: nowrap;">冷却折算</span>
          <div>${cdDisplay}</div>
        </div>
        <div class="synergy-skill-desc">${sk.desc}</div>
      </div>
    `;
  });

  const effNames = effItems.map(it => it.item_name);
  const hasYellowShield = effNames.some(n => ['怒龙剑盾', '熔炼之心'].includes(n));
  const hasPhoenix = effNames.includes('不死鸟之眼');
  const hasBaZhe = effNames.includes('霸者重装');
  const hasBaoLie = effNames.includes('暴烈之甲');
  const hasBloodRage = effNames.some(n => ['血魔之怒', '侵掠·怒魂'].includes(n));
  const hasRedLotus = effNames.some(n => ['红莲斗篷', '巨人之握'].includes(n));
  const hasIceHeart = effNames.includes('极寒风暴');

  // 3. 动态装备被动联动实战深度剖析 (Apple HIG 矢量图标规范)
  const synergyItems = [];
  const hasSkillHeal = skills.some(s => (s.tags || []).includes('技能回血'));

  // A. 【三重永动质变：怒龙剑盾 (黄盾) × 不死鸟之眼 × 英雄技能机制】
  if (hasYellowShield && hasPhoenix) {
    if (currentHero.cname === '杨戬') {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="M12 8v4"></path><path d="M12 16h.01"></path></svg>',
        title: '三重永动狂潮 · 黄盾血量重击 × 不死鸟血统 × 大招激光吸血',
        item: '怒龙剑盾 + 不死鸟之眼',
        desc: `【杨戬】最核心实战质变出装！黄盾(+1100生命)+不死鸟(+1200生命)构筑万血大血包：①【平A真伤+重击混伤】：杨戬2技能命中后获得5秒真伤平A，黄盾使每次平A额外附带最大生命百分比物理重击并回复生命，双重混伤攻防兼备，更彻底解决杨戬缺乏AOE清野清兵缓慢的发育硬伤；②【医学奇迹双重回血】：不死鸟【血统】在血量低于50%时提供高达30%~60%全源治疗翻倍！残血开出3技能大招三道激光（基础转化50%伤害为生命），配合黄盾普攻回血，瞬间从濒死血线爆拉至满血；③【控血必中眩晕】：完美契合2技能“自身血量百分比低于目标必定范围眩晕”机制，可故意控残血进场打出群体眩晕，反手大招+黄盾平A瞬间满血反杀！`
      });
    } else if (hasSkillHeal) {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="M12 8v4"></path><path d="M12 16h.01"></path></svg>',
        title: '双向续航永动机 · 黄盾生命回血 × 不死鸟残血治疗翻倍',
        item: '怒龙剑盾 + 不死鸟之眼',
        desc: `【怒龙剑盾】提供巨量生命值使每次普攻附带生命百分比回复，与【不死鸟之眼】的【血统】被动（血量低于50%受治疗翻倍30%~60%）和【${currentHero.cname}】的技能回血形成三重复合增益！残血时普攻回血与技能回血双重爆发，血条越残回血越猛，极具残血反打与团战拉扯统治力！`
      });
    } else {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        title: '重装攻防永动 · 黄盾生命重击 × 不死鸟法抗屏障',
        item: '怒龙剑盾 + 不死鸟之眼',
        desc: `双防与生命值全维度拉升，黄盾提供平A最大生命物理重击与续航，不死鸟构筑高额法术屏障并放大残血回复，形成攻守兼备的肉装作战矩阵。`
      });
    }
  } else if (hasYellowShield) {
    if (currentHero.cname === '杨戬') {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.26 12 2"></polygon></svg>',
        title: '怒龙剑盾 (黄盾) · 真实伤害与重击双重普攻质变',
        item: '怒龙剑盾',
        desc: `杨戬 2技能【虚妄破灭】命中后获得 5秒真实伤害普攻，与黄盾【神力/重击】形成双重混伤！每次普攻附加最大生命百分比物理重击并回复生命，真伤刀刀穿透护甲，重击大幅提高清线与刷野效率，彻底扫清杨戬对线被压线、清线慢的发育痛点！`
      });
    } else {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.26 12 2"></polygon></svg>',
        title: '怒龙剑盾 (黄盾) · 普攻生命重击与快速发育',
        item: '怒龙剑盾',
        desc: `【重击】被动让【${currentHero.cname}】的普攻附带最大生命值百分比物理伤害，对兵线与野怪清剿效率质变提升，并在近身肉搏中提供持续普攻回复。`
      });
    }
  } else if (hasPhoenix) {
    if (hasSkillHeal) {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>',
        title: '不死鸟之眼 · 残血治疗翻倍与极限反杀',
        item: '不死鸟之眼',
        desc: `【${currentHero.cname}】自身拥有回血机制，与不死鸟之眼的唯一被动【血统】形成质变联动！血量每损失 10%，受到的所有治疗效果额外增加 6%。在血量低于 50% 时治疗量提升高达 30%~60%，残血开出技能回血可瞬间拉满血线，创造医学奇迹与极限残血反杀！`
      });
    } else {
      synergyItems.push({
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>',
        title: '不死鸟之眼 · 法抗支撑与受治疗增益',
        item: '不死鸟之眼',
        desc: `提供高额法术防御与最大生命值，配合铭文或吸血装，在残血时获得高额受治疗提升，增强对法师的抗击打与赖线能力。`
      });
    }
  }

  // B. 暴烈之甲
  if (hasBaoLie) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
      title: '暴烈之甲 · 挨打叠层最高 10%全增伤与移速',
      item: '暴烈之甲',
      desc: `受到伤害时叠加【无畏】印记（最高 5层增加 10%伤害与 10%移速）。在近战肉搏与抗集火中轻松叠满，不仅使【${currentHero.cname}】的真实伤害与技能爆发直接提升 10%，更通过 10% 额外移速大幅强化残血拉扯与追击黏人！`
    });
  }

  // C. 强击被动
  if (hasSpellblade) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
      title: '强击被动 · 连招强化与减速留人',
      item: spellbladeItem,
      desc: `核心装备【${spellbladeItem}】的【强击】被动与【${currentHero.cname}】的技能机制天然契合！在释放任意技能后 5 秒内，下一次普攻将附带额外强击爆发伤害，并附带强力减速。实战建议在释放技能后务必穿插一次强化普攻，实现伤害最大化与无缝黏人！`
    });
  }

  // D. 穿透破甲
  if (totalPhysPierce > 50) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="22" y1="12" x2="18" y2="12"></line><line x1="6" y1="12" x2="2" y2="12"></line><line x1="12" y1="6" x2="12" y2="2"></line><line x1="12" y1="22" x2="12" y2="18"></line></svg>',
      title: '物理穿透乘区 · 无视抗性破甲爆发',
      item: `总物理穿透 ${Math.round(totalPhysPierce)} 点`,
      desc: `当前出装与铭文合计提供 ${Math.round(totalPhysPierce)} 点固定物理穿透！对局中敌方射手与法师在满级时的基础物理护甲仅为 350 点左右，此套穿透可直接削减敌方大半护甲，使【${currentHero.cname}】的技能物理伤害无限逼近真实伤害，斩杀脆皮犹如切菜！`
    });
  } else if (totalMagicPierce > 50) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.26 12 2"></polygon></svg>',
      title: '法术穿透乘区 · 全额贯穿魔法抗性',
      item: `总法术穿透 ${Math.round(totalMagicPierce)} 点`,
      desc: `当前配置拥有 ${Math.round(totalMagicPierce)} 点高额法穿，让敌方魔抗形同虚设，全面激发英雄全套技能与法球的最高 AP 爆发！`
    });
  }

  // E. 纯净苍穹免伤
  if (hasDamageReduce) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
      title: '纯净苍穹 · 40%高额免伤与受控解控',
      item: '纯净苍穹',
      desc: `纯净苍穹【驱散】主动技能可在受到控制状态下释放，获得 40% 极高免伤并减速周围敌人，同时首个技能命中敌人对其造成残废减速与自身伤害降低 20%。进场打团或被集火时开启，可硬抗敌方一整套爆发伤害完成逆风反打！`
    });
  }

  // F. 血魔之怒 / 侵掠·怒魂
  if (hasBloodRage) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
      title: '血魔之怒 · 40%最大生命绝境护盾与血怒加成',
      item: '血魔之怒',
      desc: `生命低于 50% 时普攻附带最大生命物理伤害翻倍；主动释放消耗 30%当前生命换取高达 40%最大生命的巨额护盾。配合不死鸟与技能回血：开出血魔护盾抵挡第一波致命爆发，在护盾掩护下安心反打并借助回血机制将血量吸满！`
    });
  }

  // G. 红莲斗篷 / 巨人之握
  if (hasRedLotus) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
      title: '红莲斗篷/肉刀 · 范围灼烧与 35%重伤压制',
      item: '红莲斗篷 / 巨人之握',
      desc: `贴身肉搏时每秒对周围敌人造成基于最大生命值的范围法术伤害，并附带 35% 减疗重伤效果。既强化持续近战输出，又精准克制敌方回血续航英雄！`
    });
  }

  // H. 霸者重装
  if (hasBaZhe) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>',
      title: '霸者重装 · +2000生命血池支撑与永动机脱战回血',
      item: '霸者重装',
      desc: `提供全局最高额度的 +2000 最大生命与双抗，脱战后每秒百分比回血彻底告别回城，使【${currentHero.cname}】成为无限赖线压制野区的战场永动机。`
    });
  }

  // I. 极寒风暴
  if (hasIceHeart) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
      title: '极寒风暴 (冰心) · 20%高冷缩与范围降攻速减速',
      item: '极寒风暴',
      desc: `直接提供 +20% 冷却缩减拉满技能周转，受到单次伤害超 10% 触发范围寒冰冲击，降低敌方 30% 攻速与 30% 移速，强力克制后排射手与刺客贴身普攻！`
    });
  }

  // J. 冷却周转联动
  if (cappedCdr >= 30) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
      title: '极限制动周转 · 高冷缩加速技能循环',
      item: `实战冷缩 ${cappedCdr}%`,
      desc: `当前配装使技能冷却缩减达到 ${cappedCdr}%（接近 40% 极限制动上限）！核心主动技能真空期由原来的数秒大幅缩短至眨眼之间，小技能几乎可以不断穿插释放，团战周转效率与拉扯容错提升至极限！`
    });
  }

  // K. 普攻法球
  if (hasOnHit) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
      title: '多段法球乘区 · 普攻高频附带额外伤害',
      item: '法球装备组',
      desc: `配合英雄高攻速与普攻穿插动作，高频次触发附带的百分比当前生命伤害或额外魔法伤害，前排坦克血量也能快速蒸发！`
    });
  }

  // 若装备被动较少，做保底呈现
  if (synergyItems.length === 0) {
    synergyItems.push({
      icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>',
      title: '基础属性支撑 · 稳固英雄基本作战维面',
      item: '基础属性套装',
      desc: `当前所选装备稳步提升基础攻击、生命与防御数值，建议补充暗影战斧、冰痕之握、纯净苍穹或无尽战刃等核心成装，激发全量被动联动特效！`
    });
  }

  let synergyLinksHtml = '';
  synergyItems.forEach(item => {
    synergyLinksHtml += `
      <div class="synergy-link-card">
        <div class="synergy-link-icon-box">${item.icon}</div>
        <div class="synergy-link-content">
          <div class="synergy-link-title">
            <span>${item.title}</span>
            <span class="synergy-link-sub">${item.item}</span>
          </div>
          <div class="synergy-link-desc">${item.desc}</div>
        </div>
      </div>
    `;
  });

  // 4. 契合度评分与连招打法
  const isSustainGod = (currentHero.cname === '杨戬' || hasSkillHeal) && hasYellowShield && hasPhoenix;
  const score = Math.min(88 + effItems.length * 2 + (isSustainGod ? 5 : 0) + (hasSpellblade ? 2 : 0) + (hasDamageReduce ? 2 : 0) + (cappedCdr >= 30 ? 2 : 0), 99);
  
  // 连招生成逻辑
  let comboSteps = [];
  const hasDash = skills.some(s => (s.tags || []).includes('位移突进'));
  const hasCc = skills.some(s => (s.tags || []).includes('硬控'));

  if (currentHero.cname === '杨戬') {
    if (hasYellowShield && hasPhoenix) {
      comboSteps = [
        '1技能哮天犬远程预判标记目标 (施加已损生命 16% 斩杀印记)',
        '1技能二段飞狗突进接近敌人身旁',
        '故意控半血/残血释放 2技能横扫，必定触发 0.75s 范围眩晕并激活 5秒真实伤害普攻',
        '贴脸连续平A打出【黄盾·重击】最大生命百分比物理伤害与真实伤害双重混伤，并触发普攻回血',
        '在血线压低至 50% 以下时开启 3技能大招三道激光，触发【不死鸟之眼·血统】30%~60% 巨量治疗翻倍，瞬间把血条吸满',
        '刷新或二段 1技能对残血目标造成致命百分比斩杀收割！'
      ];
    } else if (hasYellowShield) {
      comboSteps = [
        '1技能哮天犬远程预判标记目标 (施加斩杀印记)',
        '1技能二段飞狗突进接近敌人',
        '2技能近身真实伤害横扫，造成 0.75s 范围眩晕',
        '贴脸打出【黄盾·重击】最大生命额外物理伤害与真实伤害，并触发平A回血',
        '3技能大招三道激光压低敌方血线并回复自身生命',
        '刷新或二段 1技能残血斩杀收割'
      ];
    } else {
      comboSteps = [
        '1技能哮天犬远程预判标记目标 (施加斩杀印记)',
        '1技能二段飞狗突进接近敌人',
        '2技能近身真实伤害横扫，造成 0.75s 范围眩晕',
        hasSpellblade ? '立刻穿插普攻打出【强击】100%减速与高额物理伤害' : '立刻接普攻打出真实伤害',
        '3技能大招三道激光扫射压低血线并回复自身生命',
        '刷新或二段 1技能进行残血百分比斩杀收割'
      ];
    }
  } else if (currentHero.cname === '赵云') {
    comboSteps = [
      '3技能大招跃空雷霆击飞目标，造成感电标记',
      '2技能连续刺出龙枪打出多段感电附加伤害并回血',
      '1技能向前冲锋减速追击',
      hasSpellblade ? '冲锋后接强化普攻打出【强击】爆发' : '接平A补足伤害',
      '被动低血量高额免伤支撑反打'
    ];
  } else if (currentHero.cname === '孙尚香') {
    comboSteps = [
      '1技能翻滚存枪并寻找安全输出身位',
      '2技能投掷红莲爆弹减速并破甲 25%',
      '打出 1技能强化远距离重炮普攻',
      hasSpellblade ? '触发【宗师强击】+20%移速拉扯拉开距离' : '接普通攻击持续走A',
      '3技能远程轰击收割残血逃生敌人'
    ];
  } else if (currentHero.cname === '诸葛亮') {
    comboSteps = [
      '1技能贴脸贴身打出三颗法球叠加印记',
      '2技能时空穿梭突进踩中敌人叠加二层印记并减速',
      '触发被动五颗谋略法球环绕自动轰击',
      hasSpellblade ? '穿插【巫术法杖】强化普攻压低血线' : '保持走位风筝',
      '3技能元气弹锁定残血目标，完成击杀并刷新被动法球'
    ];
  } else {
    comboSteps = [
      hasDash ? '1技能或突进技能接近目标起手' : '远程技能探草与消耗压低血线',
      hasCc ? '释放核心控制技能控制敌人，限制走位' : '释放输出技能打出第一波爆发',
      hasYellowShield ? '穿插普通攻击打出【黄盾·重击】最大生命百分比伤害与续航' : (hasSpellblade ? '技能间隙穿插普通攻击，无缝触发【强击】伤害' : '走位穿插普攻补充伤害'),
      '根据战场局势开启免伤/位移技能拉扯规避致命伤害',
      '释放大招锁定敌方核心进行集火或收割'
    ];
  }

  let comboHtml = '';
  comboSteps.forEach((step, idx) => {
    comboHtml += `
      <div class="synergy-combo-step">
        <span class="combo-step-num">${idx + 1}</span>
        <span>${step}</span>
      </div>
    `;
  });

  const sustainBarPct = isSustainGod ? 100 : (hasPhoenix && (hasSkillHeal || currentHero.cname === '杨戬') ? 96 : (hasYellowShield ? 88 : 80));
  const defenseBarPct = (hasYellowShield && hasPhoenix) ? 96 : (hasDamageReduce || hasBloodRage ? 94 : 88);
  const burstBarPct = (totalPhysPierce > 50 || hasSpellblade) ? 95 : 88;
  const kitingBarPct = (hasYellowShield || hasSpellblade || hasBaoLie) ? 92 : 85;

  const bottomGridHtml = `
    <div class="synergy-bottom-grid">
      <div class="synergy-rating-card">
        <div class="synergy-section-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
          出装战术协同度评估
        </div>
        <div class="synergy-score-circle">
          <span class="synergy-score-big">${score}</span>
          <div>
            <div style="font-size: 14px; font-weight: 700; color: var(--color-green);">${score >= 95 ? 'S+ 卓越级战术协同' : 'S 强力战术协同'}</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">被动特效与技能动作链契合度极高</div>
          </div>
        </div>
        <div class="synergy-radar-bars">
          <div class="synergy-radar-row">
            <span>爆发斩杀 (Burst)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: ${burstBarPct}%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>技能周转 (CDR)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: ${Math.min(cappedCdr * 2.4, 100)}%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>持续拉扯 (Kiting)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: ${kitingBarPct}%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>生存容错 (Defense)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: ${defenseBarPct}%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>续航反打 (Sustain)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: ${sustainBarPct}%;"></div></div>
          </div>
        </div>
      </div>

      <div class="synergy-combo-card">
        <div class="synergy-section-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          实战黄金连招与打法要点
        </div>
        <div>
          ${comboHtml}
        </div>
      </div>
    </div>
  `;

  // 拼接全量内容
  container.innerHTML = `
    ${bannerHtml}
    <div>
      <div class="synergy-section-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        技能机制与实战冷却折算
      </div>
      <div class="synergy-skills-grid">
        ${skillsCardsHtml}
      </div>
    </div>
    <div>
      <div class="synergy-section-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
        装备核心被动与机制联动
      </div>
      <div class="synergy-links-list">
        ${synergyLinksHtml}
      </div>
    </div>
    ${bottomGridHtml}
  `;
}

function copySynergyReport() {
  const heroName = currentHero.cname;
  const eff = currentSlots.map(s => s.item_name).join(' + ') || '无装备';
  const text = `### 【王者出装箱】英雄技能×出装联动战术分析报告\n- 英雄：${heroName} (${currentHero.lane} / ${currentHero.role})\n- 六神装：${eff}\n- 总造价：${document.getElementById('totalGold').innerText}\n- 战术亮点：技能冷却时间全面缩短，被动特效形成控制与爆发连招链闭环，实战表现极其强劲！\n- 报告来源：王者出装箱沙盒系统`;
  navigator.clipboard.writeText(text).then(() => {
    showToast("已成功复制联动战术分析报告至剪贴板！");
  }).catch(() => {
    prompt("请手动复制战术报告：", text);
  });
}
