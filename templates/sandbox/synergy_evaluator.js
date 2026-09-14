// ==============================================================================
// 局内六神装配装战术协同评分引擎 (Synergy Evaluator Engine)
// 包含物法错位惩罚、重复鞋惩罚、大件成型度、核心机制协同与五维雷达评估
// ==============================================================================

function calculateSynergyScore(currentHero, effItems, currentSlots, skills, cappedCdr) {
  const heroRole = currentHero.role || '';
  const isPhysicalHero = ['战士', '刺客', '射手'].some(r => heroRole.includes(r)) && !['司空震', '芈月'].includes(currentHero.cname);
  const isMagicHero = heroRole.includes('法师') && !['司空震', '嬴政'].includes(currentHero.cname);
  const isTankOrSupport = heroRole.includes('坦克') || heroRole.includes('辅助');

  let totalAd = 0, totalAp = 0, totalBonusHp = 0, totalPdef = 0, totalMdef = 0;
  let totalLifesteal = 0, totalSpellLifesteal = 0, totalCrit = 0, totalPercentSpeed = 0;
  let tier3Count = 0, tier2Count = 0, tier1Count = 0;
  let bootsCount = 0;

  effItems.forEach(it => {
    const st = it.stats || {};
    totalAd += st.atk || 0;
    totalAp += st.ap || 0;
    totalBonusHp += st.hp || 0;
    totalPdef += st.pdef || 0;
    totalMdef += st.mdef || 0;
    totalLifesteal += st.p_lifesteal || 0;
    totalSpellLifesteal += st.m_lifesteal || 0;
    totalCrit += st.crit || 0;
    totalPercentSpeed += st.percent_speed || 0;
    if (typeof BOOTS_MAP !== 'undefined' && BOOTS_MAP[it.item_name]) bootsCount++;

    const price = it.total_price || 0;
    if (price >= 1800) tier3Count++;
    else if (price >= 700) tier2Count++;
    else tier1Count++;
  });

  // 检测物法错位、重复大件与唯一被动冲突
  let wastedApCount = 0;
  let wastedAdCount = 0;
  if (isPhysicalHero) {
    wastedApCount = effItems.filter(it => (it.category === '法术') || (it.stats && it.stats.ap >= 80)).length;
  }
  if (isMagicHero) {
    wastedAdCount = effItems.filter(it => (it.category === '攻击') && ((it.stats && it.stats.atk >= 80) || (it.stats && it.stats.crit >= 15))).length;
  }

  // 重复装备统计
  const slotItemNames = currentSlots.map(s => s.item_name);
  const nameCounts = {};
  slotItemNames.forEach(n => nameCounts[n] = (nameCounts[n] || 0) + 1);
  let duplicateItemCount = 0;
  for (let n in nameCounts) {
    if (nameCounts[n] > 1) duplicateItemCount += (nameCounts[n] - 1);
  }

  // 强击唯一被动冲突
  const spellbladeNames = ['宗师之力', '冰痕之握', '巫术法杖', '光辉之剑'];
  const spellbladeCount = effItems.filter(it => spellbladeNames.includes(it.item_name)).length;
  const spellbladeConflict = spellbladeCount > 1;

  // 装备与机制标识提取
  const effNames = effItems.map(it => it.item_name);
  const hasYellowShield = effNames.includes('怒龙剑盾') || effNames.includes('龙鳞利剑');
  const hasPhoenix = effNames.includes('不死鸟之眼');
  const hasBaoLie = effNames.includes('暴烈之甲');
  const hasSpellblade = spellbladeCount > 0;
  const hasBloodRage = effNames.includes('血魔之怒');
  const hasDamageReduce = effNames.includes('纯净苍穹') || effNames.includes('弱化');

  const totalPhysPierce = effItems.reduce((acc, it) => acc + (it.stats && it.stats.p_pen || 0), 0);
  const totalMagicPierce = effItems.reduce((acc, it) => acc + (it.stats && it.stats.m_pen || 0), 0);
  const hasSkillHeal = skills.some(s => (s.tags || []).includes('技能回血'));

  // A. 装备品质与成型基础分 (0 ~ 45分)
  let buildBaseScore = (tier3Count * 7.5) + (tier2Count * 3.5) + (tier1Count * 1.5);
  buildBaseScore = Math.min(45, buildBaseScore);

  // B. 机制契合与核心协同分 (0 ~ 30分)
  let synergyBonus = 0;
  if (currentHero.cname === '杨戬') {
    if (hasYellowShield) synergyBonus += 8;
    if (hasPhoenix) synergyBonus += 8;
    if (hasBaoLie) synergyBonus += 4;
    if (hasDamageReduce) synergyBonus += 4;
    if (hasSpellblade) synergyBonus += 4;
    if (totalPhysPierce >= 150) synergyBonus += 4;
  } else if (currentHero.cname === '赵云') {
    if (hasSpellblade) synergyBonus += 7;
    if (totalPhysPierce >= 150) synergyBonus += 7;
    if (hasPhoenix) synergyBonus += 6; // 飞龙在天溢出治疗转永久护盾质变
    if (hasDamageReduce || hasBloodRage) synergyBonus += 5;
    if (effNames.includes('破军')) synergyBonus += 5;
  } else if (currentHero.cname === '哪吒') {
    if (hasBloodRage) synergyBonus += 8; // 血魔之怒与火莲圣体盾厚上加厚
    if (hasBaoLie) synergyBonus += 7;
    if (hasDamageReduce) synergyBonus += 5;
    if (effNames.includes('红莲斗篷') || effNames.includes('暗影战斧')) synergyBonus += 6;
    if (totalBonusHp >= 2000) synergyBonus += 4;
  } else if (currentHero.cname === '孙尚香') {
    if (effNames.includes('宗师之力')) synergyBonus += 8;
    if (effNames.includes('无尽战刃')) synergyBonus += 8;
    if (effNames.includes('破晓')) synergyBonus += 8;
    if (totalCrit >= 40) synergyBonus += 5;
  } else if (currentHero.cname === '诸葛亮') {
    if (effNames.includes('博学者之怒')) synergyBonus += 8;
    if (effNames.includes('噬神之书')) synergyBonus += 8;
    if (effNames.includes('辉月')) synergyBonus += 6;
    if (totalMagicPierce >= 150) synergyBonus += 6;
  } else {
    if (hasYellowShield && (hasSkillHeal || totalBonusHp >= 2500)) synergyBonus += 7;
    if (hasPhoenix && (hasSkillHeal || totalLifesteal > 0)) synergyBonus += 7;
    if (hasSpellblade) synergyBonus += 5;
    if (hasDamageReduce || hasBloodRage) synergyBonus += 5;
    if (totalPhysPierce >= 150 || totalMagicPierce >= 150) synergyBonus += 5;
  }
  if (cappedCdr >= 30) synergyBonus += 4;
  synergyBonus = Math.min(30, synergyBonus);

  // C. 攻防维度健康分 (0 ~ 15分)
  let balanceScore = 10;
  if (isPhysicalHero) {
    if (heroRole.includes('战士')) {
      if (totalBonusHp >= 1500 && totalAd >= 180) balanceScore = 15;
      else if (totalBonusHp >= 1000 || totalAd >= 150) balanceScore = 12;
    } else if (heroRole.includes('刺客') || heroRole.includes('射手')) {
      if (totalAd >= 250 || totalCrit >= 40) balanceScore = 15;
      else if (totalAd >= 150) balanceScore = 12;
    }
  } else if (isMagicHero) {
    if (totalAp >= 500) balanceScore = 15;
    else if (totalAp >= 300) balanceScore = 12;
  } else if (isTankOrSupport) {
    if (totalBonusHp >= 3000 && (totalPdef >= 400 || totalMdef >= 200)) balanceScore = 15;
    else if (totalBonusHp >= 1800) balanceScore = 12;
  }

  // D. 严厉实战惩罚扣分机制
  let penalty = 0;
  let penaltyReasons = [];

  if (wastedApCount > 0) {
    penalty += wastedApCount * 15;
    penaltyReasons.push(`物法属性错位：物理英雄装备了 ${wastedApCount} 件法术属性装 (-${wastedApCount * 15}分)`);
  }
  if (wastedAdCount > 0) {
    penalty += wastedAdCount * 15;
    penaltyReasons.push(`物法属性错位：法术英雄装备了 ${wastedAdCount} 件高物攻/暴击装 (-${wastedAdCount * 15}分)`);
  }
  if (bootsCount > 1) {
    penalty += (bootsCount - 1) * 15;
    penaltyReasons.push(`鞋类重复出装：装备了 ${bootsCount} 双鞋子，唯一移速被动浪费 (-${(bootsCount - 1) * 15}分)`);
  }
  if (duplicateItemCount > 0) {
    penalty += duplicateItemCount * 12;
    penaltyReasons.push(`重复大件购买：存在 ${duplicateItemCount} 件同名重复装备，同名唯一被动无法叠加 (-${duplicateItemCount * 12}分)`);
  }
  if (spellbladeConflict) {
    penalty += 8;
    penaltyReasons.push(`强击唯一被动重叠冲突：同时装备多件强击装，仅生效优先级最高者 (-8分)`);
  }
  if (effItems.length >= 5 && tier1Count >= 3) {
    penalty += 10;
    penaltyReasons.push(`散件过多拖累经济：后期装备栏保留过多初级散件，属性成型严重落后 (-10分)`);
  }

  // 最终总分计算
  let score = Math.round(buildBaseScore + synergyBonus + balanceScore + 10 - penalty);
  score = Math.max(15, Math.min(100, score));

  // 评级与诊断徽章
  let rankBadge = 'S+ 巅峰神装契合';
  let rankColor = '#34c759';
  let rankSub = '攻防一体，被动联动极佳，完全激活英雄机制潜力';

  if (score >= 90) {
    rankBadge = 'S+ 巅峰神装契合';
    rankColor = '#34c759';
    rankSub = '攻防一体，被动联动极佳，完全激活英雄机制潜力';
  } else if (score >= 80) {
    rankBadge = 'A 优质战术出装';
    rankColor = '#0071e3';
    rankSub = '基础战力扎实，攻防维度完好，个别装备仍有针对性优化空间';
  } else if (score >= 70) {
    rankBadge = 'B 常规级可用配装';
    rankColor = '#ff9500';
    rankSub = penaltyReasons[0] || '具备基本作战能力，但被动联动较单薄，攻防分布略显失衡';
  } else if (score >= 60) {
    rankBadge = 'C 偏离主轴 / 散件较多';
    rankColor = '#ff5e00';
    rankSub = penaltyReasons[0] || '初级散件偏多或缺少核心质变大件，实战无法充分激发英雄潜力';
  } else {
    rankBadge = 'D 严重冲突 / 属性倒挂';
    rankColor = '#ff3b30';
    rankSub = penaltyReasons.join(' ； ') || '存在严重属性浪费或装备冲突，实战作战效能极低';
  }

  // 五维雷达能力评估计算
  const physBurst = Math.min(100, Math.round((totalAd / 350) * 50 + (totalCrit / 50) * 30 + (totalPhysPierce / 200) * 20));
  const sustainSurvive = Math.min(100, Math.round((totalBonusHp / 4000) * 45 + (totalPdef / 600) * 30 + (totalMdef / 350) * 25));
  const cdLoop = Math.min(100, Math.round((cappedCdr / 40) * 70 + (hasSpellblade ? 20 : 0) + (hasSkillHeal ? 10 : 0)));
  const roamSpeed = Math.min(100, Math.round((bootsCount > 0 ? 50 : 20) + (totalPercentSpeed / 15) * 30 + (hasBaoLie ? 20 : 0)));
  const hasHardCc = skills.some(s => (s.tags || []).includes('硬控'));
  const controlScore = Math.min(100, Math.round((hasHardCc ? 50 : 20) + (effNames.includes('冰霜冲击') ? 25 : 0) + (hasSpellblade ? 20 : 0) + (effNames.includes('极寒风暴') ? 15 : 0)));

  return {
    score,
    rankBadge,
    rankColor,
    rankSub,
    penaltyReasons,
    synergyContext: {
      hasYellowShield,
      hasPhoenix,
      hasBaoLie,
      hasSpellblade,
      hasBloodRage,
      hasDamageReduce
    },
    radarStats: [physBurst, sustainSurvive, cdLoop, roamSpeed, controlScore]
  };
}
