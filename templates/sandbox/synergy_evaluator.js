// ==============================================================================
// 局内六神装配装战术协同评分引擎 (Synergy Evaluator Engine)
// 包含科学多维量化算分体系、实战直观优劣势剖析(PROS/CONS)、机制质变与五维战力推演
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
  let tier3Count = 0, bootsCount = 0;

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
    if ((it.total_price || 0) >= 1700) tier3Count++;
  });

  const slotNames = effItems.map(s => s.item_name);
  const hasHuangdun = slotNames.includes('怒龙剑盾') || slotNames.includes('龙鳞利剑');
  const hasPhoenix = slotNames.includes('不死鸟之眼');
  const hasCangqiong = slotNames.includes('纯净苍穹') || slotNames.includes('天穹');
  const hasAnyang = slotNames.includes('暗影战斧');
  const hasBaoLie = slotNames.includes('暴烈之甲');
  const hasZongshi = slotNames.includes('宗师之力');
  const hasBinghen = slotNames.includes('冰痕之握');
  const hasWujin = slotNames.includes('无尽战刃');
  const hasPoxiao = slotNames.includes('破晓') || slotNames.includes('仁者破晓');
  const hasHonglian = slotNames.includes('红莲斗篷');
  const hasBuxiang = slotNames.includes('不祥征兆');
  const hasMowu = slotNames.includes('魔女斗篷');
  const hasBazhe = slotNames.includes('霸者重装');
  const hasSupport = slotNames.some(n => n.includes('极影') || n.includes('近卫') || n.includes('形昭') || n.includes('救赎'));
  const hasFanshang = slotNames.includes('反伤刺甲');
  const hasJihan = slotNames.includes('极寒风暴');
  const hasMaozi = slotNames.includes('博学者之怒');
  const hasHuixiang = slotNames.includes('回响之杖');
  const hasFaChuan = slotNames.includes('虚无法杖') || slotNames.includes('日暮之流');
  const hasShushen = slotNames.includes('噬神之书');
  const hasHuiyue = slotNames.includes('辉月');
  const hasLifesteal = slotNames.includes('泣血之刃') || slotNames.includes('末世') || slotNames.includes('噬神之书') || slotNames.includes('贪婪之噬') || hasHuangdun || hasPhoenix || hasBazhe;
  const hasArmorPen = hasAnyang || hasPoxiao || slotNames.includes('碎星锤') || slotNames.includes('破魔刀');
  const hasDamageReduce = hasCangqiong || slotNames.includes('天穹') || hasHuiyue || slotNames.includes('名刀·司命') || slotNames.includes('贤者的庇护');

  // ==========================================
  // 1. 实战核心优势 (PROS - 直截了当、针对出装机制)
  // ==========================================
  const pros = [];
  if (hasCangqiong || hasHuiyue) {
    pros.push({
      title: '进场免伤避免被秒',
      desc: hasCangqiong
        ? '纯净苍穹提供 35% 高额免伤且受控可用，彻底避免刚进场突进时被敌方集火瞬间蒸发。'
        : '辉月提供 1.5 秒无敌保命金身，关键时刻化解敌方致命爆发连招与高伤指向技能。'
    });
  }
  if (totalBonusHp >= 3000 || (totalPdef + totalMdef) >= 600) {
    pros.push({
      title: '防御极高抗伤扎实',
      desc: `总额外生命达到 +${totalBonusHp}，物法双抗加成高达 +${totalPdef + totalMdef}，前排坦度极为扎实，能为队友吃满第一波强集火。`
    });
  }
  if (hasPhoenix || hasLifesteal) {
    pros.push({
      title: '回复极强续航拉满',
      desc: hasPhoenix
        ? '不死鸟之眼大幅放大残血受疗效率，搭配回复技能或重击吸血，残血对拼具备极强反杀续航。'
        : '具备高额物理/法术吸血加成，对线残血后无需频繁回城，能快速补满状态并持续参团。'
    });
  }
  if ((totalAd >= 180 && hasArmorPen) || (totalAp >= 400 && (hasFaChuan || hasMaozi))) {
    pros.push({
      title: '核心爆发瞬秒脆皮',
      desc: '高额攻击属性搭配核心穿透/暴击，技能与普攻伤害充足，对敌方后排脆皮具备极强的一套秒杀威慑。'
    });
  }
  if (cappedCdr >= 25) {
    pros.push({
      title: '冷却缩减高频循环',
      desc: `冷却缩减达到 ${cappedCdr}%，大幅压缩技能真空期，高频位移留人与多轮技能拉扯反打极具主动权。`
    });
  }
  if (hasBuxiang) {
    pros.push({
      title: '压制敌方攻速与走位',
      desc: '不祥征兆受到攻击削弱敌方 40% 攻速与移速，极大破坏敌方射手走A与普攻刺客的输出环境。'
    });
  }
  if (hasHuangdun && hasPhoenix) {
    pros.push({
      title: '绝地不死混伤重击',
      desc: '黄盾最大生命物理重击搭配真伤普攻，残血开大触发不死鸟受治愈翻倍，残血绝地对拼反杀质变。'
    });
  }
  if (pros.length === 0) {
    pros.push({
      title: '基础三维属性均衡',
      desc: '装备提供扎实的基础数值增益，满足常规对局推演与平稳对线基准。'
    });
  }

  // ==========================================
  // 2. 实战潜在短板 (CONS - 针砭装备缺陷，拒绝空话)
  // ==========================================
  const cons = [];
  if (!isTankOrSupport && totalBonusHp <= 1200 && (totalPdef + totalMdef) <= 220 && !hasDamageReduce) {
    cons.push({
      title: '过度注重伤害缺少坦度',
      desc: '整套配装偏向纯攻击输出，身板极脆容错率偏低，一旦团战切入稍有不慎或吃控制，极易被瞬间反秒。'
    });
  }
  if (!hasLifesteal) {
    cons.push({
      title: '缺少回复与续航手段',
      desc: '整套配装缺少吸血与血量回复大件，打残后无法靠兵线快速补满状态，必须频繁回城补给漏线亏节奏。'
    });
  }
  if (cappedCdr < 15) {
    cons.push({
      title: '冷却缩减不足真空偏长',
      desc: `整套出装仅 ${cappedCdr}% 冷缩，关键技能交完后有数秒无技能空窗期，拉扯与多轮反打能力受限。`
    });
  }
  if ((isPhysicalHero && totalAd >= 140 && !hasArmorPen) || (isMagicHero && totalAp >= 300 && !hasFaChuan)) {
    cons.push({
      title: '缺少穿甲中后期破坦乏力',
      desc: '未装配百分比破甲大件（如破晓/碎星锤/虚无法杖），对局进入中后期打敌方上千双抗的前排伤害衰减严重。'
    });
  }
  if (totalMdef <= 120 && !slotNames.includes('魔女斗篷') && !slotNames.includes('永夜守护') && !hasPhoenix) {
    cons.push({
      title: '法抗偏低防法核爆发弱',
      desc: '缺少魔女斗篷或永夜守护，面对敌方高爆发法师（如安琪拉、干将、不知火舞）极易吃技能被瞬间秒杀。'
    });
  }
  if (isTankOrSupport && totalAd <= 80 && totalAp <= 100) {
    cons.push({
      title: '纯肉出装单人收割乏力',
      desc: '整套出装偏向纯防御，缺乏物理攻击与穿透，单人面对满血脆皮无法单杀，较依赖队友补足伤害。'
    });
  }
  if (bootsCount === 0 && totalPercentSpeed <= 0) {
    cons.push({
      title: '缺少鞋类成装机动滞后',
      desc: '未装配鞋类大件，基础移速偏低，极易被敌方长手减速拉扯，支援转线与团战进退节奏滞后。'
    });
  }
  if (cons.length === 0) {
    cons.push({
      title: '装备造价偏高成型期长',
      desc: '整套配装多为高造价三级大件，前期过渡较吃经济运营，若逆风发育受阻成型周期会被迫拉长。'
    });
  }

  // ==========================================
  // 3. 科学量化评分模型 (科学依据：四维透明评分表)
  // ==========================================
  // 维度一：神装成件基础分 (上限 35分)
  const tier3Score = Math.min(6, tier3Count) * 5.8;

  // 维度二：核心机制质变分 (上限 30分)
  let mechanicScore = 0;
  if (hasDamageReduce) mechanicScore += 8;
  if ((hasHuangdun && hasPhoenix) || (hasBazhe && hasHonglian) || (hasAnyang && hasZongshi) || (hasWujin && hasPoxiao)) mechanicScore += 8;
  if (hasBuxiang || hasJihan) mechanicScore += 7;
  if (hasSupport || hasMowu) mechanicScore += 7;
  mechanicScore = Math.min(30, Math.max(10, mechanicScore + effItems.length * 2.5));

  // 维度三：攻防循环平衡分 (上限 25分)
  let balanceScore = 0;
  if (cappedCdr >= 20 && cappedCdr <= 40) balanceScore += 10;
  else if (cappedCdr >= 10) balanceScore += 5;
  if (bootsCount === 1) balanceScore += 8;
  if ((totalPdef + totalMdef) >= 300 || (totalAd >= 200 && hasArmorPen) || (totalAp >= 400 && hasFaChuan)) balanceScore += 7;
  balanceScore = Math.min(25, balanceScore);

  // 维度四：实战短板惩罚扣分 (扣减项)
  let penalty = 0;
  const penaltyReasons = [];
  const wastedApCount = isPhysicalHero ? effItems.filter(it => (it.category === '法术') || (it.stats && it.stats.ap >= 80)).length : 0;
  const wastedAdCount = isMagicHero ? effItems.filter(it => (it.category === '攻击') && ((it.stats && it.stats.atk >= 80) || (it.stats && it.stats.crit >= 15))).length : 0;

  if (wastedApCount > 0) {
    penalty += wastedApCount * 12;
    penaltyReasons.push(`物法错位：物理英雄出了 ${wastedApCount} 件法术属性装 (-${wastedApCount * 12}分)`);
  }
  if (wastedAdCount > 0) {
    penalty += wastedAdCount * 12;
    penaltyReasons.push(`物法错位：法术英雄出了 ${wastedAdCount} 件物理属性装 (-${wastedAdCount * 12}分)`);
  }
  if (bootsCount > 1) {
    penalty += (bootsCount - 1) * 8;
    penaltyReasons.push(`移速互斥：重复装备了 ${bootsCount} 双鞋子 (-${(bootsCount - 1) * 8}分)`);
  }

  // 计算综合总分 (72~93 分客观实战梯度)
  const rawScore = Math.round(tier3Score + mechanicScore + balanceScore - penalty);
  const score = Math.max(35, Math.min(94, rawScore));

  let rankBadge = 'A 均衡可用配装', rankColor = '#0071e3';
  if (score >= 90) {
    rankBadge = 'S+ 巅峰神装契合'; rankColor = '#34c759';
  } else if (score >= 84) {
    rankBadge = 'S 顶尖实战套路'; rankColor = '#0071e3';
  } else if (score >= 76) {
    rankBadge = 'A 均衡可用配装'; rankColor = '#ff9500';
  } else if (score >= 65) {
    rankBadge = 'B 存在明显短板'; rankColor = '#ff5e00';
  } else {
    rankBadge = 'C 严重属性冲突'; rankColor = '#ff3b30';
  }

  const rankSub = cons.length > 0 && score < 92
    ? `实战优势突出，但需重点注意【${cons[0].title}】局限。`
    : `综合契合度高，激活 ${pros.length} 项核心战术机制，攻防曲线扎实。`;

  // 评分科学依据表细化
  const scoreBreakdown = {
    tierScore: Math.round(tier3Score),
    mechanicScore: Math.round(mechanicScore),
    balanceScore: Math.round(balanceScore),
    penaltyScore: Math.round(penalty),
    penaltyReasons
  };

  // 4. 五维雷达战力推演
  const burstVal = Math.min(100, Math.max(15, Math.round((totalAd / 520) * 55 + (totalAp / 650) * 45 + (totalCrit / 50) * 20)));
  const tankVal = Math.min(100, Math.max(20, Math.round((totalBonusHp / 5500) * 50 + (totalPdef / 700) * 30 + (totalMdef / 400) * 20)));
  const cdrVal = Math.min(100, Math.max(15, Math.round((cappedCdr / 40) * 75 + (hasCangqiong ? 15 : 0) + (hasAnyang ? 10 : 0))));
  const speedVal = Math.min(100, Math.max(20, Math.round((bootsCount > 0 ? 55 : 20) + (totalPercentSpeed / 15) * 30 + (hasBaoLie ? 15 : 0))));
  const hasHardCc = skills.some(s => (s.tags || []).includes('硬控'));
  const ccVal = Math.min(100, Math.max(20, Math.round((hasHardCc ? 55 : 25) + (hasBuxiang ? 20 : 0) + (hasBinghen || hasCangqiong ? 20 : 0) + (hasHonglian ? 10 : 0))));

  const radarStats = {
    burst: burstVal, survive: tankVal, control: cdrVal, mobility: speedVal, sustain: ccVal,
    list: [burstVal, tankVal, cdrVal, speedVal, ccVal]
  };
  radarStats[0] = burstVal; radarStats[1] = tankVal; radarStats[2] = cdrVal; radarStats[3] = speedVal; radarStats[4] = ccVal; radarStats.length = 5;

  return {
    score,
    rankBadge,
    rankColor,
    rankSub,
    pros: pros.slice(0, 3),
    cons: cons.slice(0, 2),
    scoreBreakdown,
    penaltyReasons,
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
