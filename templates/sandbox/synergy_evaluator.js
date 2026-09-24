// ==============================================================================
// 局内六神装配装战术协同评分引擎 (Synergy Evaluator Engine)
// 包含全职业核心被动机制联动、物法冲突惩罚、真实五维战力折算与协同评级
// ==============================================================================

function calculateSynergyScore(currentHero, effItems, currentSlots, skills, cappedCdr) {
  currentHero = currentHero || {};
  effItems = effItems || [];
  currentSlots = currentSlots || [];
  skills = skills || [];
  cappedCdr = cappedCdr || 0;

  const heroRole = currentHero.role || '';
  const heroName = currentHero.cname || '';
  const isPhysicalHero = ['战士', '刺客', '射手'].some(r => heroRole.includes(r)) && !['司空震', '芈月'].includes(heroName);
  const isMagicHero = heroRole.includes('法师') && !['司空震', '嬴政'].includes(heroName);
  const isTankOrSupport = heroRole.includes('坦克') || heroRole.includes('辅助') || currentHero.lane === '对抗路' || currentHero.lane === '游走';

  let totalAd = 0, totalAp = 0, totalBonusHp = 0, totalPdef = 0, totalMdef = 0;
  let totalCrit = 0, totalPercentSpeed = 0;
  let tier3Count = 0, tier2Count = 0, tier1Count = 0;
  let bootsCount = 0;

  effItems.forEach(it => {
    const st = it.stats || {};
    totalAd += st.atk || 0;
    totalAp += st.ap || 0;
    totalBonusHp += st.hp || 0;
    totalPdef += st.pdef || 0;
    totalMdef += st.mdef || 0;
    totalCrit += st.crit || 0;
    totalPercentSpeed += st.percent_speed || 0;
    if (typeof BOOTS_MAP !== 'undefined' && BOOTS_MAP[it.item_name]) bootsCount++;

    const price = it.total_price || 0;
    if (price >= 1800) tier3Count++;
    else if (price >= 700) tier2Count++;
    else tier1Count++;
  });

  // 1. 核心装备机制全面识别 (Insights)
  const slotNames = effItems.map(s => s.item_name);
  const insights = [];

  const hasHuangdun = slotNames.includes('怒龙剑盾') || slotNames.includes('龙鳞利剑');
  const hasPhoenix = slotNames.includes('不死鸟之眼');
  const hasCangqiong = slotNames.includes('纯净苍穹') || slotNames.includes('天穹');
  const hasAnyang = slotNames.includes('暗影战斧');
  const hasBaoLie = slotNames.includes('暴烈之甲');
  const hasZongshi = slotNames.includes('宗师之力');
  const hasBinghen = slotNames.includes('冰痕之握');
  const hasWujin = slotNames.includes('无尽战刃');
  const hasPoxiao = slotNames.includes('破晓') || slotNames.includes('仁者破晓') || slotNames.includes('仁者·破晓');
  const hasHonglian = slotNames.includes('红莲斗篷');
  const hasBuxiang = slotNames.includes('不祥征兆');
  const hasMowu = slotNames.includes('魔女斗篷');
  const hasBazhe = slotNames.includes('霸者重装');
  const hasSupport = slotNames.some(n => n.includes('极影') || n.includes('近卫') || n.includes('形昭') || n.includes('救赎'));
  const hasDikang = slotNames.includes('抵抗之靴');
  const hasYinren = slotNames.includes('影忍之足');
  const hasFanshang = slotNames.includes('反伤刺甲');
  const hasJihan = slotNames.includes('极寒风暴');
  const hasMaozi = slotNames.includes('博学者之怒');
  const hasHuixiang = slotNames.includes('回响之杖');
  const hasFaChuan = slotNames.includes('虚无法杖') || slotNames.includes('日暮之流');
  const hasShushen = slotNames.includes('噬神之书');
  const hasHuiyue = slotNames.includes('辉月');
  const hasMianju = slotNames.includes('痛苦面具');
  const hasXianshu = slotNames.includes('贤者之书') || slotNames.includes('贤者天书');

  if (hasHuangdun && hasPhoenix) {
    insights.push({ tag: '不死混伤', item: '怒龙剑盾 + 不死鸟', desc: '真伤与最大生命物理重击双重加持，残血受治疗倍增！' });
  } else if (hasHuangdun) {
    insights.push({ tag: '重击发育', item: '怒龙剑盾', desc: '普攻附带最大生命物理重击与持续回复，发育对拼质变。' });
  } else if (hasPhoenix) {
    insights.push({ tag: '血统护体', item: '不死鸟之眼', desc: '血量越低受治疗增幅越高，技能回血与残血反杀利器。' });
  }

  if (hasHonglian) {
    insights.push({ tag: '业炎灼烧', item: '红莲斗篷', desc: '近战每秒对敌造成高额最大生命法术灼烧并附带重伤减疗。' });
  }
  if (hasBuxiang) {
    insights.push({ tag: '寒铁削速', item: '不祥征兆', desc: '受到攻击大幅减少攻击者攻速与移速，强力限制射手突进。' });
  }
  if (hasBazhe) {
    insights.push({ tag: '天元极愈', item: '霸者重装', desc: '巨幅拉升最大生命与双抗，脱战极速回复生命值无需回城。' });
  }
  if (hasMowu) {
    insights.push({ tag: '迷雾法盾', item: '魔女斗篷', desc: '脱战提供高额法术吸收护盾，有效抵御法师秒杀与远程消耗。' });
  }
  if (hasSupport) {
    insights.push({ tag: '军团守护', item: '辅助团队神装', desc: '赋予周围队友双抗/攻速光环增益，关键时刻提供团队保命护盾。' });
  }
  if (hasCangqiong) {
    insights.push({ tag: '驱散免伤', item: '纯净苍穹', desc: '开启获得35%高额免伤并在受控时可用，进场抗集火核心神器。' });
  }
  if (hasAnyang) {
    insights.push({ tag: '切割减CD', item: '暗影战斧', desc: '提供高额物理穿透与15%冷却缩减，大幅缩减技能真空期。' });
  }
  if (hasZongshi || hasBinghen) {
    insights.push({ tag: '强击留人', item: hasZongshi ? '宗师之力' : '冰痕之握', desc: `技能后普攻附带额外爆发与${hasBinghen ? '强力减速' : '移速拉扯'}。` });
  }
  if (hasWujin) {
    insights.push({ tag: '暴击质变', item: '无尽战刃', desc: '提供高额暴击率与暴击效果增益，物理瞬秒爆发核心基石。' });
  }
  if (hasPoxiao) {
    insights.push({ tag: '穿甲破障', item: '破晓', desc: '提供40%物理穿透与攻速暴击，远程射手瓦解重装铁壁。' });
  }
  if (hasBaoLie) {
    insights.push({ tag: '受击增伤', item: '暴烈之甲', desc: '受击叠加最高10%全增伤与10%移速，抗压对拼越战越勇。' });
  }
  if (hasFanshang || hasJihan) {
    insights.push({ tag: '防御反制', item: hasFanshang ? '反伤刺甲' : '极寒风暴', desc: hasFanshang ? '高额物抗反弹法术伤害，克制物理刺客' : '提供20%超高冷缩与冰甲受击范围冲击减速。' });
  }
  if (hasMaozi) {
    insights.push({ tag: '法强跃迁', item: '博学者之怒', desc: '总法术攻击提升30%，技能法伤呈现指数级爆发飞跃。' });
  }
  if (hasHuixiang) {
    insights.push({ tag: '法术引爆', item: '回响之杖', desc: '技能命中触发范围法术爆炸，探草消耗与瞬时爆发兼备。' });
  }
  if (hasFaChuan) {
    insights.push({ tag: '法穿破壁', item: slotNames.includes('虚无法杖') ? '虚无法杖' : '日暮之流', desc: '提供高额百分比或叠层法穿，轻松穿透敌方法防屏障。' });
  }
  if (hasShushen) {
    insights.push({ tag: '法术吸血', item: '噬神之书', desc: '赋予25%法术吸血与10%CD，对拼持续回复赖线不回城。' });
  }
  if (hasHuiyue) {
    insights.push({ tag: '金身规避', item: '辉月', desc: '1.5秒金身无敌与免控，关键时刻规避刺客致命突进秒杀。' });
  }
  if (hasMianju) {
    insights.push({ tag: '生命灼烧', item: '痛苦面具', desc: '技能附带多段目标当前生命百分比伤害，持续消耗前排。' });
  }
  if (hasXianshu) {
    insights.push({ tag: '终极增伤', item: '贤者之书', desc: '按法强最高提升12%全技能增伤，后期法球爆发质变。' });
  }
  if (hasDikang) {
    insights.push({ tag: '韧性防控', item: '抵抗之靴', desc: '提供35%韧性缩短受控时间，大幅提升团战进场容错。' });
  } else if (hasYinren) {
    insights.push({ tag: '普攻减伤', item: '影忍之足', desc: '减少8%受到的普攻物理伤害，显著提升对拼承伤上限。' });
  }

  // 2. 冲突与惩罚检查
  let penalty = 0;
  let penaltyReasons = [];

  let wastedApCount = isPhysicalHero ? effItems.filter(it => (it.category === '法术') || (it.stats && it.stats.ap >= 80)).length : 0;
  let wastedAdCount = isMagicHero ? effItems.filter(it => (it.category === '攻击') && ((it.stats && it.stats.atk >= 80) || (it.stats && it.stats.crit >= 15))).length : 0;

  if (wastedApCount > 0) {
    penalty += wastedApCount * 15;
    penaltyReasons.push(`物法错位：物理英雄出了 ${wastedApCount} 件法术属性装 (-${wastedApCount * 15}分)`);
  }
  if (wastedAdCount > 0) {
    penalty += wastedAdCount * 15;
    penaltyReasons.push(`物法错位：法术英雄出了 ${wastedAdCount} 件物攻/暴击装 (-${wastedAdCount * 15}分)`);
  }
  if (bootsCount > 1) {
    penalty += (bootsCount - 1) * 15;
    penaltyReasons.push(`双鞋互斥：装备了 ${bootsCount} 双鞋子，移速被动浪费 (-${(bootsCount - 1) * 15}分)`);
  }

  const nameCounts = {};
  slotNames.forEach(n => nameCounts[n] = (nameCounts[n] || 0) + 1);
  let duplicateCount = 0;
  for (let n in nameCounts) { if (nameCounts[n] > 1) duplicateCount += (nameCounts[n] - 1); }
  if (duplicateCount > 0) {
    penalty += duplicateCount * 12;
    penaltyReasons.push(`重复购买：存在 ${duplicateCount} 件同名重复装备，被动无法叠加 (-${duplicateCount * 12}分)`);
  }

  // 3. 最终得分与评级
  let baseScore = 65 + effItems.length * 5; // 6件成装 = 95
  if (insights.length >= 4) baseScore += 5;
  else if (insights.length >= 2) baseScore += 3;

  let score = Math.max(15, Math.min(99, Math.round(baseScore - penalty)));
  let rankBadge = 'S+ 巅峰神装契合', rankColor = '#34c759', rankSub = `激活 ${insights.length} 项核心被动机制，与【${heroName}】技能特质高度共鸣。`;

  if (score >= 90) {
    rankBadge = 'S+ 巅峰神装契合'; rankColor = '#34c759';
  } else if (score >= 80) {
    rankBadge = 'A 优质战术出装'; rankColor = '#0071e3';
    rankSub = penaltyReasons[0] || `核心装备成型，激活 ${insights.length} 项战术机制，攻防分布扎实。`;
  } else if (score >= 70) {
    rankBadge = 'B 常规级可用配装'; rankColor = '#ff9500';
    rankSub = penaltyReasons[0] || '具备基本作战能力，但被动联动较单薄，可进一步补强核心质变装。';
  } else {
    rankBadge = 'C 存在属性冲突或散件'; rankColor = '#ff3b30';
    rankSub = penaltyReasons.join(' ； ') || '存在严重属性浪费或装备冲突，实战作战效能受限。';
  }

  // 4. 真实五维雷达战力折算 (0~100 百分比)
  const burstVal = Math.min(100, Math.max(20, Math.round((totalAd / 550) * 55 + (totalAp / 650) * 45 + (totalCrit / 50) * 20)));
  const tankVal = Math.min(100, Math.max(20, Math.round((totalBonusHp / 5000) * 50 + (totalPdef / 700) * 30 + (totalMdef / 400) * 20)));
  const cdrVal = Math.min(100, Math.max(20, Math.round((cappedCdr / 40) * 75 + (hasCangqiong ? 15 : 0) + (hasAnyang ? 10 : 0))));
  const speedVal = Math.min(100, Math.max(20, Math.round((bootsCount > 0 ? 55 : 20) + (totalPercentSpeed / 15) * 30 + (hasBaoLie ? 15 : 0))));
  const hasHardCc = skills.some(s => (s.tags || []).includes('硬控'));
  const ccVal = Math.min(100, Math.max(20, Math.round((hasHardCc ? 55 : 25) + (hasBuxiang ? 20 : 0) + (hasBinghen || hasCangqiong ? 20 : 0) + (hasHonglian ? 10 : 0))));

  const radarStats = {
    burst: burstVal,
    survive: tankVal,
    control: cdrVal,
    mobility: speedVal,
    sustain: ccVal,
    list: [burstVal, tankVal, cdrVal, speedVal, ccVal]
  };
  radarStats[0] = burstVal;
  radarStats[1] = tankVal;
  radarStats[2] = cdrVal;
  radarStats[3] = speedVal;
  radarStats[4] = ccVal;
  radarStats.length = 5;

  return {
    score,
    rankBadge,
    rankColor,
    rankSub,
    penaltyReasons,
    insights,
    synergyContext: {
      hasYellowShield: hasHuangdun,
      hasPhoenix,
      hasBaoLie,
      hasSpellblade: (hasZongshi || hasBinghen),
      hasDamageReduce: hasCangqiong
    },
    radarStats
  };
}
