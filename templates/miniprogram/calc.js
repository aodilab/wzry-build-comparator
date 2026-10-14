// 王者出装箱 ｜ 微信小程序原生双轨物理演算引擎 (对齐 index.html 权威单一数据源)
// 包含属性计算、连招实战对决、PVE野区清理控龙耗时、生存续航与全维Diff

function calcBuildStats(hero, items, arcana, arcanaDict) {
  const base = (hero && hero.base_stats) || {};
  let hp = (base.hp && base.hp[1]) || 6700;
  let atk = (base.atk && base.atk[1]) || 380;
  let pdef = (base.pdef && base.pdef[1]) || 380;
  let mdef = (base.mdef && base.mdef[1]) || 169;
  let ap = 0;
  let cdr = 0;
  let aspeed = parseFloat(base.aspeed || "0") * 14;
  let flatPen = 0;
  let percentPen = 0;
  let mFlatPen = 0;
  let mPercentPen = 0;
  let moveSpeed = base.speed || 380;
  let pLifesteal = 0;
  let mLifesteal = 0;
  let critRate = 0;
  let critEff = 200;

  let hasMaster = false, hasIce = false, hasDragon = false;
  let hasFenghuang = false, hasDoomsdayArmor = false, hasPhoenixEye = false;
  let hasBazhe = false, hasMoShi = false;
  let knifeTier = 0, knifeType = 'none';
  let supportActiveName = "无主动辅助装", supportAuraDesc = "无团队光环";

  // 1. 铭文累加 (严格对齐 app_stats.js 官方字段键名)
  const arc = arcana || {};
  let arcAtk = 0, arcAp = 0, arcPdef = 0, arcMdef = 0, arcHp = 0;
  let arcFlatPen = 0, arcMFlatPen = 0, arcAspeed = 0, arcCdr = 0;
  let arcPLifesteal = 0, arcMLifesteal = 0, arcCritRate = 0, arcCritEff = 0;
  let arcMoveSpeedPct = 0;

  ['red', 'blue', 'green'].forEach(col => {
    const colorMap = arc[col] || {};
    Object.keys(colorMap).forEach(arcName => {
      const count = colorMap[arcName] || 0;
      if (count <= 0) return;
      const def = arcanaDict && arcanaDict[arcName];
      if (def && (def.stats_1 || def.stats_10)) {
        const s1 = def.stats_1 || {}, s10 = def.stats_10 || {};
        const getVal = (k1, k10) => {
          if (s1[k1] !== undefined) return s1[k1] * count;
          if (s10[k10 || k1] !== undefined) return (s10[k10 || k1] / 10) * count;
          return 0;
        };
        arcAtk += getVal('phys_atk');
        arcAp += getVal('magic_atk');
        arcPdef += getVal('phys_def');
        arcMdef += getVal('magic_def');
        arcHp += getVal('max_hp');
        arcFlatPen += getVal('phys_pierce', 'phys_pen');
        arcMFlatPen += getVal('magic_pierce', 'magic_pen');
        arcAspeed += getVal('atk_speed_pct', 'attack_speed');
        arcCdr += getVal('cd_reduction_pct', 'cdr');
        arcPLifesteal += getVal('phys_vamp_pct', 'phys_vamp');
        arcMLifesteal += getVal('magic_vamp_pct', 'magic_vamp');
        arcCritRate += getVal('crit_rate_pct', 'crit_rate');
        arcCritEff += getVal('crit_effect_pct', 'crit_effect');
        arcMoveSpeedPct += getVal('move_speed_pct', 'move_speed');
      }
    });
  });

  atk += arcAtk;
  ap += arcAp;
  pdef += arcPdef;
  mdef += arcMdef;
  hp += arcHp;
  flatPen += arcFlatPen;
  mFlatPen += arcMFlatPen;
  aspeed += arcAspeed;
  cdr += arcCdr;
  pLifesteal += arcPLifesteal;
  mLifesteal += arcMLifesteal;
  critRate += arcCritRate;
  critEff += arcCritEff;

  // 2. 装备累加与唯一被动检测 (严格对齐 app_stats.js)
  let flatMoveBonus = 0, pctMoveBonus = arcMoveSpeedPct;
  let hasHat = false, hasProphecy = false, hasPomo = false;
  let hasInfinity = false, hasBloodBook = false, hasTwilight = false;
  let hasWushu = false, hasEcho = false, hasMask = false;
  let hasLightning = false, hasGoldenBlade = false, hasDaybreak = false;
  let bootsCounted = false;

  (items || []).forEach(it => {
    if (!it) return;
    const s = it.stats || {};
    hp += (s.hp !== undefined ? s.hp : (s.max_hp || 0));
    atk += (s.atk !== undefined ? s.atk : (s.phys_atk || 0));
    ap += (s.ap !== undefined ? s.ap : (s.magic_atk || 0));
    pdef += (s.pdef !== undefined ? s.pdef : (s.phys_def || 0));
    mdef += (s.mdef !== undefined ? s.mdef : (s.magic_def || 0));
    cdr += (s.cdr || 0);
    aspeed += (s.aspeed !== undefined ? s.aspeed : (s.attack_speed || 0));
    pLifesteal += (s.p_lifesteal !== undefined ? s.p_lifesteal : (s.phys_vamp || 0));
    mLifesteal += (s.m_lifesteal !== undefined ? s.m_lifesteal : (s.magic_vamp || 0));
    critRate += (s.crit_rate || s.crit || 0);
    critEff += (s.crit_eff || s.crit_effect || 0);
    if (s.m_pierce_flat) mFlatPen += s.m_pierce_flat;
    if (s.m_pierce_percent) mPercentPen = Math.max(mPercentPen, s.m_pierce_percent > 1 ? s.m_pierce_percent / 100 : s.m_pierce_percent);
    const fSpd = (s.flat_speed || 0) + (s.move_speed || 0);
    if (fSpd > 0 && !bootsCounted) {
      flatMoveBonus += fSpd;
      bootsCounted = true;
    }
    if (s.percent_speed) pctMoveBonus += s.percent_speed;
    if (s.p_pierce_flat) flatPen += s.p_pierce_flat;
    if (s.p_pierce_percent) percentPen = Math.max(percentPen, s.p_pierce_percent > 1 ? s.p_pierce_percent / 100 : s.p_pierce_percent);

    const n = it.item_name || "";
    if (n.includes("博学者之怒")) hasHat = true;
    if (n.includes("时之预言")) hasProphecy = true;
    if (n.includes("破魔刀")) hasPomo = true;
    if (n.includes("无尽战刃")) hasInfinity = true;
    if (n.includes("噬神之书")) hasBloodBook = true;
    if (n.includes("日暮之流")) hasTwilight = true;
    if (n.includes("巫术法杖")) hasWushu = true;
    if (n.includes("回响之杖")) hasEcho = true;
    if (n.includes("痛苦面具")) hasMask = true;
    if (n.includes("闪电匕首")) hasLightning = true;
    if (n.includes("金色圣剑")) hasGoldenBlade = true;
    if (n.includes("破晓")) hasDaybreak = true;
    if (n.includes("宗师之力")) hasMaster = true;
    if (n.includes("冰痕之握")) hasIce = true;
    if (n.includes("怒龙剑盾") || n.includes("红莲斗篷")) hasDragon = true;
    if (n.includes("破军")) hasFenghuang = true;
    if (n.includes("暴烈之甲")) hasDoomsdayArmor = true;
    if (n.includes("不死鸟之眼")) hasPhoenixEye = true;
    if (n.includes("霸者重装")) hasBazhe = true;
    if (n.includes("末世")) hasMoShi = true;
    if (n.includes("碎星锤") || n.includes("破晓")) percentPen = Math.max(percentPen, 0.35);
    if (n.includes("虚无法杖")) mPercentPen = Math.max(mPercentPen, 0.45);

    // 辅助装备识别 (近卫光环为自身及友军提供 +120 双抗)
    if (n.includes("近卫")) {
      pdef += 120;
      mdef += 120;
      supportAuraDesc = "近卫守护光环 (周围友军 +120双抗 / 回血)";
    } else if (n.includes("极影")) {
      supportAuraDesc = "极影迅捷光环 (周围友军 +20%攻速 / +15%冷却 / 回蓝)";
    }
    if (n.includes("救赎")) supportActiveName = "救赎 (为周围友军施加 2800 点生命护盾)";
    else if (n.includes("奔狼")) supportActiveName = "奔狼 (全队瞬间爆发移速冲锋)";
    else if (n.includes("形昭")) supportActiveName = "形昭 (照亮草丛探隐并减速50%)";
    else if (n.includes("星泉")) supportActiveName = "星泉 (储备充能为友方单体回复血蓝)";

    // 打野刀识别与满层奖赏属性 (S45 正式服标准：3级刀25层，2级刀15层)
    if (n.includes("贪婪之噬")) { knifeTier = 3; knifeType = 'atk'; atk += 75; cdr += 5; flatPen += 60; }
    else if (n.includes("巨人之握")) { knifeTier = 3; knifeType = 'meat'; hp += 750; cdr += 5; }
    else if (n.includes("符文大剑")) { knifeTier = 3; knifeType = 'ap'; ap += 150; cdr += 5; }
    else if (n.includes("追击刀锋")) { knifeTier = 2; knifeType = 'atk'; atk += 45; }
    else if (n.includes("巡守利斧")) { knifeTier = 2; knifeType = 'meat'; hp += 450; }
    else if (n.includes("游击弯刀")) { knifeTier = 2; knifeType = 'ap'; ap += 90; }
    else if (n.includes("狩猎宽刃") || n.includes("弃鳞短刃")) { knifeTier = 1; knifeType = 'basic'; }
  });

  // 3. 核心机制转化计算 (严格对齐 S45 正式服与 app_stats.js)
  // 无尽战刃：获得20%暴击效果，每2%暴击增加1%暴击效果，最多不超过50%
  if (hasInfinity) {
    critEff += Math.min(50, 20 + Math.floor(critRate / 2));
  }
  // 噬神之书：每2%法术吸血额外提供1%冷却缩减
  if (hasBloodBook) {
    cdr += Math.floor(mLifesteal / 2);
  }
  // 日暮之流：满层6层净魔提供 240 点法术穿透
  if (hasTwilight) {
    mFlatPen += 240;
  }
  // 金色圣剑：叠满2层额外提供 20% 攻速
  if (hasGoldenBlade) {
    aspeed += 20;
  }
  // 博学者之怒：总法强放大 30%
  if (hasHat) {
    ap = Math.floor(ap * 1.30);
  }
  // 时之预言：法强的 10% 转化为双抗 (上限 250)
  if (hasProphecy) {
    const propVal = Math.min(Math.floor(ap * 0.10), 250);
    pdef += propVal;
    mdef += propVal;
  }
  // 破魔刀：总物理攻击力的 50% 转化为法术防御 (上限 250)
  if (hasPomo) {
    const pomoVal = Math.min(Math.floor(atk * 0.50), 250);
    mdef += pomoVal;
  }

  moveSpeed = Math.round((moveSpeed + flatMoveBonus) * (1 + pctMoveBonus / 100));
  cdr = Math.min(40, Math.round(cdr * 10) / 10);

  return {
    hp: Math.round(hp), atk: Math.round(atk), ap: Math.round(ap),
    pdef: Math.round(pdef), mdef: Math.round(mdef), cdr,
    aspeed: Math.round(aspeed), flatPen: Math.round(flatPen), percentPen,
    mFlatPen: Math.round(mFlatPen), mPercentPen,
    critRate: Math.min(100, Math.round(critRate)), critEff: Math.min(250, Math.round(critEff)),
    supportActiveName: supportActiveName || "无主动辅助装",
    supportAuraDesc: supportAuraDesc || "无团队光环",
    moveSpeed: Math.round(moveSpeed), pLifesteal: Math.round(pLifesteal), mLifesteal: Math.round(mLifesteal),
    hasMaster, hasIce, hasWushu, hasEcho, hasMask, hasLightning, hasGoldenBlade, hasDaybreak,
    hasDragon, hasFenghuang, hasDoomsdayArmor, hasPhoenixEye, hasBazhe, hasMoShi,
    knifeTier, knifeType
  };
}


const { calcComboOutcome } = require('./calc_combat.js');

// 技能实际冷却推演 (自动读取当前英雄真实 1/2/3 技能 CD)
function calcSkillCooldowns(heroOrSkills, statsOrCdr) {
  let cdr = typeof statsOrCdr === 'number' ? statsOrCdr : (statsOrCdr && statsOrCdr.cdr || 0);
  let baseCds = [5.0, 6.0, 12.0];
  let names = ['1 技能 实际冷却', '2 技能 实际冷却', '3 技能 (大招) 冷却'];

  let skillsList = null;
  if (Array.isArray(heroOrSkills)) {
    skillsList = heroOrSkills;
  } else if (heroOrSkills && heroOrSkills.cname && typeof window !== 'undefined' && window.DATASET && window.DATASET.HERO_SKILLS) {
    skillsList = window.DATASET.HERO_SKILLS[heroOrSkills.cname];
  }
  if (Array.isArray(skillsList) && skillsList.length >= 4) {
    const active = skillsList.slice(1, 4);
    baseCds = active.map((sk, i) => sk.cd_sec || [5.0, 6.0, 12.0][i]);
    names = active.map((sk, i) => `${i + 1}技能·${sk.name}`);
  }

  const cdrFactor = 1 - (cdr || 0) / 100;

  return baseCds.map((base, idx) => ({
    title: names[idx],
    baseCd: base.toFixed(1) + 's',
    actualCd: Math.max(0.1, base * cdrFactor).toFixed(1) + 's'
  }));
}

// 面板核心属性全维度差额对比表
function calcStatDiffs(statsA, statsB, onlyDiffs) {
  const rows = [
    { label: '物理攻击', valA: statsA.atk, valB: statsB.atk, unit: '点' },
    { label: '法术攻击', valA: statsA.ap, valB: statsB.ap, unit: '点' },
    { label: '最大生命', valA: statsA.hp, valB: statsB.hp, unit: '点' },
    { label: '物理防御', valA: statsA.pdef, valB: statsB.pdef, unit: '点' },
    { label: '法术防御', valA: statsA.mdef, valB: statsB.mdef, unit: '点' },
    { label: '冷却缩减', valA: statsA.cdr, valB: statsB.cdr, unit: '%' },
    { label: '物理穿透', valA: statsA.flatPen, valB: statsB.flatPen, unit: '点' },
    { label: '法术穿透', valA: statsA.mFlatPen, valB: statsB.mFlatPen, unit: '点' },
    { label: '暴击率', valA: statsA.critRate, valB: statsB.critRate, unit: '%' },
    { label: '攻击速度', valA: statsA.aspeed, valB: statsB.aspeed, unit: '%' },
    { label: '移动速度', valA: statsA.moveSpeed, valB: statsB.moveSpeed, unit: '点' },
    { label: '物理吸血', valA: statsA.pLifesteal, valB: statsB.pLifesteal, unit: '%' },
    { label: '法术吸血', valA: statsA.mLifesteal, valB: statsB.mLifesteal, unit: '%' }
  ];

  return rows.map(r => {
    const diff = r.valB - r.valA;
    return {
      label: r.label,
      valA: r.valA + (r.unit === '%' ? '%' : ''),
      valB: r.valB + (r.unit === '%' ? '%' : ''),
      diff,
      diffText: diff === 0 ? '持平' : (diff > 0 ? `+${diff}${r.unit}` : `${diff}${r.unit}`),
      diffClass: diff === 0 ? 'diff-even' : (diff > 0 ? 'diff-plus' : 'diff-minus'),
      isDiff: diff !== 0
    };
  }).filter(r => (!onlyDiffs || r.isDiff));
}

module.exports = {
  calcBuildStats,
  calcComboOutcome,
  calcSkillCooldowns,
  calcStatDiffs
};
