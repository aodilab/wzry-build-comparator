// ==============================================================================
// 局内六神装配装战术协同评分引擎 (Synergy Evaluator Engine)
// 包含真实梯队算分、实战优劣势剖析(PROS/CONS)、机制联动与五维战力推演
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
  const hasMianju = slotNames.includes('痛苦面具');
  const hasXianshu = slotNames.includes('贤者之书') || slotNames.includes('贤者天书');

  // 1. 实战核心优势 (PROS) 智能归纳
  const pros = [];
  if (hasHuangdun && hasPhoenix) {
    pros.push({ title: '绝地不死混伤', desc: '真伤普攻附带黄盾最大生命物理重击，残血开大触发不死鸟受治疗翻倍，残血对拼反杀质变。' });
  } else if (hasHuangdun) {
    pros.push({ title: '清野与重击增益', desc: '普攻附带最大生命物理重击与回复，大幅提升前期兵线与野怪清剿效率。' });
  } else if (hasPhoenix) {
    pros.push({ title: '血统残血极愈', desc: '血量越低受治疗增幅越高，显著放大技能与吸血回复效率。' });
  }

  if (hasHonglian && (hasBazhe || totalBonusHp >= 3000)) {
    pros.push({ title: '重装灼烧战阵', desc: `红莲业炎灼烧基于 ${totalBonusHp} 额外生命值造成持续范围法伤并附带重伤，肉搏清线输出兼备。` });
  }
  if (hasBuxiang) {
    pros.push({ title: '强力克制突进与攻速', desc: '受到攻击降低攻击者 40% 攻速与移速，极大限制敌方射手走位与普攻输出环境。' });
  }
  if (hasBazhe && (totalPdef >= 300 || totalMdef >= 200)) {
    pros.push({ title: '超高坦度与脱战极愈', desc: '双抗强化与天元高额生命加持，脱战极速回满血量，减少频繁回城节奏损失。' });
  }
  if (hasMowu) {
    pros.push({ title: '高额法术吸收护盾', desc: '脱战生成专属法伤护盾，有效规避敌方法核的高爆发消耗与远距离秒杀。' });
  }
  if (hasCangqiong) {
    pros.push({ title: '进场驱散免伤', desc: '受控可用并提供 35% 减伤，确保切后排或前排接团时不会被瞬时连控集火蒸发。' });
  }
  if (hasAnyang) {
    pros.push({ title: '穿透切割与技能循环', desc: '提供高额物理穿透与 15% 冷缩，显著压缩技能冷却真空期，压制脆皮输出。' });
  }
  if (hasZongshi || hasBinghen) {
    pros.push({ title: '技能强击与拉扯留人', desc: `技能后普攻附带强力额外伤害与${hasBinghen ? '范围减速留人' : '瞬间移速加成'}，连招无缝衔接。` });
  }
  if (hasWujin || hasPoxiao) {
    pros.push({ title: '终极物理爆发', desc: '超高暴击率与穿甲加持，在中后期无论是点杀脆皮还是瓦解前排均具备毁灭级伤害。' });
  }
  if (hasMaozi || hasFaChuan) {
    pros.push({ title: '法强爆发与穿透贯通', desc: '法强提升 30% 配合百分比法穿，技能法球能瞬时撕裂敌方前排魔抗防线。' });
  }
  if (hasSupport) {
    pros.push({ title: '全队光环与绝境救援', desc: '提供团队双抗或攻速增益，主动救援护盾能化解敌方关键第一波爆发。' });
  }
  if (pros.length === 0) {
    pros.push({ title: '基础三维属性稳固', desc: '装备提供扎实的基础数值增益，满足常规对局推演基准。' });
  }

  // 2. 实战潜在劣势 / 短板 (CONS) 智能诊断
  const cons = [];
  if (isTankOrSupport && totalAd <= 80 && totalAp <= 100) {
    cons.push({ title: '单人爆发与收割乏力', desc: '整套出装缺少纯攻击或穿透质变大件，对敌方满血脆皮难以单人瞬秒，较依赖队友伤害跟进。' });
  }
  if (isPhysicalHero && !isTankOrSupport && totalBonusHp <= 1500 && !hasCangqiong) {
    cons.push({ title: '身板脆弱容错率偏低', desc: '缺少防御成装与免伤主动，进场遭硬控或被刺客埋伏时极易被瞬秒，对团战切入时机要求极高。' });
  }
  if (totalAd >= 150 && !hasAnyang && !hasPoxiao && !slotNames.includes('碎星锤')) {
    cons.push({ title: '缺少穿甲大件面对重坦乏力', desc: '未装配暗影战斧/碎星锤/破晓等穿透装备，对局进入中后期打敌方上千物抗的前排坦度衰减严重。' });
  }
  if (cappedCdr < 15) {
    cons.push({ title: '冷却缩减不足技能真空偏长', desc: '当前装配未激活高冷缩区间，技能释放后真空期较长，拉扯或多次反打能力受限。' });
  }
  if (totalMdef <= 120 && !hasMowu) {
    cons.push({ title: '法术防御偏低防法核秒杀弱', desc: '缺少魔女斗篷或永夜守护，若敌方法师经济良好，极易被远距离技能消耗成残血。' });
  }
  if (cons.length === 0) {
    cons.push({ title: '打法走位需防长手拉扯', desc: '面对孙尚香、马可波罗等长手灵活射手拉扯时，需注意卡视野进场避免被提前消耗。' });
  }

  // 3. 客观评分系统 (拒绝千篇一律 99 分，打造 72~92 分真实梯度)
  let baseScore = 60 + Math.min(6, tier3Count) * 3.5; // 满6件 = 81分
  // 机制加成 (最多 +10分)
  if (pros.length >= 3) baseScore += 7;
  else if (pros.length >= 2) baseScore += 5;
  else baseScore += 2;

  // 攻防与CD合理性加减分
  if (cappedCdr >= 20 && cappedCdr <= 40) baseScore += 3;
  if (totalMdef >= 200 && (totalPdef >= 350 || totalAd >= 250)) baseScore += 2;

  // 短板扣分
  let penalty = 0;
  let penaltyReasons = [];
  let wastedApCount = isPhysicalHero ? effItems.filter(it => (it.category === '法术') || (it.stats && it.stats.ap >= 80)).length : 0;
  let wastedAdCount = isMagicHero ? effItems.filter(it => (it.category === '攻击') && ((it.stats && it.stats.atk >= 80) || (it.stats && it.stats.crit >= 15))).length : 0;

  if (wastedApCount > 0) {
    penalty += wastedApCount * 12;
    penaltyReasons.push(`物法属性错位：物理英雄装备了 ${wastedApCount} 件法术属性装`);
  }
  if (wastedAdCount > 0) {
    penalty += wastedAdCount * 12;
    penaltyReasons.push(`物法属性错位：法术英雄装备了 ${wastedAdCount} 件高物攻/暴击装`);
  }
  if (bootsCount > 1) {
    penalty += (bootsCount - 1) * 10;
    penaltyReasons.push(`双鞋互斥：装备了 ${bootsCount} 双鞋子`);
  }

  // 真实打分结算 (优质出装在 83~92 分，有明显短板在 75~82 分，极品契合在 91~94 分)
  let rawScore = Math.round(baseScore - penalty);
  let score = Math.max(35, Math.min(94, rawScore));

  let rankBadge = 'A 优质主流配装', rankColor = '#0071e3';
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

  let rankSub = `综合契合度高，激活 ${pros.length} 项核心战术优势，攻防曲线扎实。`;
  if (cons.length > 0 && score < 90) {
    rankSub = `实战优势明显，但需注意【${cons[0].title}】对局影响。`;
  }

  // 4. 真实五维雷达战力折算 (0~100 百分比)
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
