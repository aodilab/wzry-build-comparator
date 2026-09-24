// ==============================================================================
// 王者出装箱 ｜ 英雄实战连招与技能总伤害/回复推演引擎 (synergy_combos.js)
// 依据王者官方连招教学与英雄技能数值公式，推演自选方案与王者推荐方案的实战连招输出与回复量
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 350 行以内
// ==============================================================================

// === 1. 英雄经典连招与打法策略描述生成 ===
function generateComboSteps(currentHero, skills, synergyContext) {
  currentHero = currentHero || {};
  skills = skills || [];
  synergyContext = synergyContext || {};
  const { hasYellowShield, hasPhoenix, hasSpellblade } = synergyContext;
  let comboSteps = [];
  const hasDash = skills.some(s => (s.tags || []).includes('位移突进'));
  const hasCc = skills.some(s => (s.tags || []).includes('硬控'));

  if (currentHero.cname === '赵云') {
    comboSteps = [
      '3技能天翔之龙大招跃空击飞，施加感电标记与额外伤害',
      '2技能破云之龙多段龙枪穿刺打满感电伤害，同时获得高额回血与护盾',
      '1技能惊雷之龙突刺穿行追击，重置普攻冷却',
      hasSpellblade ? '穿插强化普攻打出【宗师/冰痕强击】高额减速与真实斩杀' : '接平A补足斩杀伤害',
      '在低血线时触发【飞龙在天】极限免伤绝地反打收割'
    ];
  } else if (currentHero.cname === '杨戬') {
    if (hasYellowShield && hasPhoenix) {
      comboSteps = [
        '1技能哮天犬远程预判标记目标 (施加已损生命 16% 斩杀印记)',
        '1技能二段飞狗突进直达目标身旁',
        '2技能虚妄破灭横扫控制，对生命百分比更高目标造成 0.75s 眩晕并附带真伤普攻',
        '连续平A触发【黄盾·重击】最大生命额外物理与真实混伤并回复生命',
        '血线偏低时开启 3技能大招激光扫射，触发【不死鸟之眼】治疗翻倍拉满血条',
        '二段 1技能对残血目标造成致命斩杀收割刷新技能'
      ];
    } else {
      comboSteps = [
        '1技能哮天犬远程预判标记目标施加斩杀印记',
        '1技能二段突进贴脸接近敌人',
        '2技能近身真实伤害横扫造成范围减速或眩晕',
        hasSpellblade ? '立刻接普攻打出【强击】爆发与真实伤害' : '立刻接平A打出附魔真伤',
        '3技能大招三道激光扫射打满伤害并回复高额血量',
        '二段 1技能完成残血百分比斩杀收割'
      ];
    }
  } else if (currentHero.cname === '安琪拉') {
    comboSteps = [
      '2技能混沌火种精准预判眩晕目标并施加灼烧减速',
      '3技能炽热光辉开启霸体护盾，超远距离激光灼烧融化敌方血条',
      '激光结束或手动取消后，接 1技能五颗火球术收尾斩杀残血'
    ];
  } else if (currentHero.cname === '孙尚香') {
    comboSteps = [
      '1技能翻滚突袭存枪拉开身位并强化下一次普通攻击',
      '2技能红莲爆弹减速目标并标记削弱 25% 物理护甲',
      '打出 1技能超远射程重炮强化普攻',
      hasSpellblade ? '触发【宗师之力·强击】加速拉扯并补一记普攻' : '接平A持续走A输出',
      '3技能究极弩炮超远距离轰击收割残血逃生目标'
    ];
  } else if (currentHero.cname === '吕布') {
    comboSteps = [
      '3技能魔神降世大招跳入敌阵中心击飞敌人并直接附魔方天画戟',
      '1技能方天画斩划出半月弧光打出高额范围真实伤害',
      '2技能贪婪之握吸取敌方灵魂转化为高额护盾并回复血量',
      '开启纯净苍穹主动免伤，贴脸持续打出 100% 暴击真实伤害普攻'
    ];
  } else if (currentHero.cname === '鲁班七号') {
    comboSteps = [
      '3技能空中支援照亮视野并逼迫走位，触发第一次【火力压制】扫射',
      '1技能河豚手雷投掷减速眩晕目标，触发第二次百分比穿透扫射',
      '2技能无敌鲨嘴炮击退贴脸刺客并斩杀残血，触发第三次高额扫射'
    ];
  } else if (currentHero.cname === '李白') {
    comboSteps = [
      '1技能将进酒两段突进位移穿梭并眩晕目标',
      '2技能神来之笔释放剑阵不可选中，边缘破除敌方高额物理防御',
      '平A叠满四道剑气解锁大招',
      '3技能青莲剑歌不可选中释放五道极速剑气融化敌方后排',
      '激活 1技能三段瞬移回到初始残影安全位置'
    ];
  } else {
    comboSteps = [
      hasDash ? '1技能或位移突进技能接近目标起手' : '远程技能探草与消耗压低血线',
      hasCc ? '释放核心控制技能控制敌人限制走位' : '释放输出技能打出第一波消耗',
      hasYellowShield ? '穿插普攻打出【黄盾】最大生命百分比伤害' : (hasSpellblade ? '技能间隙穿插普通攻击，无缝触发【强击】被动' : '技能间隙穿插普通攻击补足伤害'),
      '释放大招锁定敌方核心进行集火或收割'
    ];
  }

  return comboSteps;
}

// === 2. 英雄连招总伤害与技能回复推演算法 ===
function calculateHeroCombo(hero, userItems, userArcana, officialItems, officialArcana) {
  hero = hero || {};
  const cname = hero.cname || '赵云';
  const role = hero.role || '战士';

  function evalPresetCombat(items, arcanaMap) {
    items = items || [];
    arcanaMap = arcanaMap || {};

    const getStatVal = (val, def) => {
      if (Array.isArray(val)) return val[1] || val[0] || def;
      return typeof val === 'number' ? val : def;
    };
    const bStats = hero.base_stats || {};
    let ad = getStatVal(bStats.atk, 350);
    let ap = 0;
    let extraHp = 0;
    let pdef = getStatVal(bStats.pdef, 350);
    let critRate = 0;
    let armPenFlat = 0;
    let armPenPct = 0;
    let magPenFlat = 0;
    let magPenPct = 0;
    let lifesteal = 0;
    let spellbladeMult = 0;
    let hasCangqiong = false;
    let hasHuiyue = false;
    let hasPhoenix = false;
    let hasEcho = false;
    let hasBojuezhe = false;
    let hasPojun = false;

    // 1. 装备属性汇总
    items.forEach(it => {
      const st = it.stats || {};
      const name = it.item_name || '';
      ad += st.atk || 0;
      ap += st.ap || 0;
      extraHp += st.hp || 0;
      pdef += st.pdef || 0;
      critRate += st.crit || 0;

      if (name.includes('纯净苍穹') || name.includes('天穹')) hasCangqiong = true;
      if (name.includes('辉月')) hasHuiyue = true;
      if (name.includes('不死鸟之眼')) hasPhoenix = true;
      if (name.includes('破军') || name.includes('强者破军')) hasPojun = true;
      if (name.includes('博学者之怒')) hasBojuezhe = true;
      if (name.includes('回响之杖')) hasEcho = true;

      if (name.includes('暗影战斧')) armPenFlat += 170;
      if (name.includes('破晓') || name.includes('仁者破晓')) armPenPct += 0.40;
      if (name.includes('碎星锤')) armPenPct += 0.40;
      if (name.includes('虚无法杖')) magPenPct += 0.45;
      if (name.includes('日暮之流')) magPenFlat += 240;
      if (name.includes('秘法之靴')) magPenFlat += 120;
      if (name.includes('泣血之刃')) lifesteal += 0.25;
      if (name.includes('末世')) lifesteal += 0.10;
      if (name.includes('宗师之力')) spellbladeMult = Math.max(spellbladeMult, 0.80);
      if (name.includes('冰痕之握')) spellbladeMult = Math.max(spellbladeMult, 0.40);
      if (name.includes('巫术法杖')) spellbladeMult = Math.max(spellbladeMult, 0.70);
    });

    // 博学者之怒 25% 法强增幅
    if (hasBojuezhe) ap = Math.round(ap * 1.25);

    // 2. 铭文加成计算
    const arcList = [];
    ['red', 'green', 'blue'].forEach(k => {
      const m = arcanaMap[k] || {};
      Object.entries(m).forEach(([aname, cnt]) => {
        if (typeof ARCANA_DATA !== 'undefined' && ARCANA_DATA[aname]) {
          const ast = ARCANA_DATA[aname].stats || {};
          ad += (ast.atk || 0) * cnt;
          ap += (ast.ap || 0) * cnt;
          extraHp += (ast.hp || 0) * cnt;
          critRate += (ast.crit || 0) * cnt;
          armPenFlat += (ast.armor_pen || 0) * cnt;
          magPenFlat += (ast.magic_pen || 0) * cnt;
          lifesteal += (ast.lifesteal || 0) * cnt;
        }
      });
    });

    // 对标假人防御基准 (标准脆皮英雄满级基准：物防 360，法防 180)
    const targetArmor = 360;
    const targetMDef = 180;
    const effArmor = Math.max(0, (targetArmor - armPenFlat) * (1 - armPenPct));
    const effMDef = Math.max(0, (targetMDef - magPenFlat) * (1 - magPenPct));
    const pDmgFactor = 602 / (602 + effArmor);
    const mDmgFactor = 602 / (602 + effMDef);

    // 英雄技能连招模型推演
    let comboName = '常规全套爆发连招';
    let steps = [];
    let totalDmg = 0;
    let totalHeal = 0;

    if (cname === '赵云') {
      comboName = '3-2-1-A 龙魂绝杀连招';
      // 3技能 天翔之龙: 700 + 1.3额外AD，附带感电 65 + 0.33额外AD
      const s3Raw = Math.round(750 + 1.30 * (ad - 350) + 120);
      const s3Dmg = Math.round(s3Raw * pDmgFactor);

      // 2技能 破云之龙: 4段 x (160 + 0.45AD) + 回复 4段 x (70 + 0.15AD + 0.03额外HP)
      const s2Raw = Math.round(4 * (165 + 0.45 * ad));
      const s2Dmg = Math.round(s2Raw * pDmgFactor * 1.15); // 感电加深
      let s2Heal = Math.round(4 * (75 + 0.18 * ad + 0.03 * extraHp));
      if (hasPhoenix) s2Heal = Math.round(s2Heal * 1.35);

      // 1技能 惊雷之龙: 350 + 0.85AD
      const s1Raw = Math.round(360 + 0.85 * ad);
      const s1Dmg = Math.round(s1Raw * pDmgFactor);

      // 强化普攻 + 宗师/冰痕强击: base AD + 65 + 0.35AD + spellblade
      const enhancedAtkRaw = Math.round(ad + 120 + 0.35 * ad + spellbladeMult * ad);
      const critMultiplier = 1 + (critRate / 100) * 0.7; // 期望暴击收益
      const enhancedAtkDmg = Math.round(enhancedAtkRaw * pDmgFactor * critMultiplier);
      const aaHeal = Math.round(enhancedAtkDmg * (lifesteal / 100));

      totalDmg = s3Dmg + s2Dmg + s1Dmg + enhancedAtkDmg;
      totalHeal = s2Heal + aaHeal;

      if (hasPojun) totalDmg = Math.round(totalDmg * 1.12); // 斩杀期望增幅

      steps = [
        { name: '3技能 天翔之龙', desc: '雷霆击飞破防并施加感电标记', dmg: s3Dmg, heal: 0 },
        { name: '2技能 破云之龙', desc: '四段极速穿刺打满感电，高额回血与护盾', dmg: s2Dmg, heal: s2Heal },
        { name: '1技能 惊雷之龙', desc: '位移穿行突刺追击', dmg: s1Dmg, heal: 0 },
        { name: '强化普攻 (附强击)', desc: '感电真伤暴击重砸斩杀', dmg: enhancedAtkDmg, heal: aaHeal }
      ];
    } else if (cname === '杨戬') {
      comboName = '1-2-A-3 哮天斩灭连招';
      const s1Raw = Math.round(300 + 0.60 * ad);
      const s1Dmg = Math.round(s1Raw * pDmgFactor);

      const s2Raw = Math.round(550 + 1.0 * ad);
      const s2Dmg = Math.round(s2Raw * pDmgFactor);

      const aaRaw = Math.round(ad * (1 + spellbladeMult) + 180); // 附带真伤
      const aaDmg = Math.round(aaRaw * pDmgFactor + 250); // 真伤不削减
      let aaHeal = Math.round(150 + 0.02 * extraHp);

      const s3Raw = Math.round(3 * (450 + 0.85 * ad));
      const s3Dmg = Math.round(s3Raw * pDmgFactor);
      let s3Heal = Math.round(s3Dmg * 0.50);
      if (hasPhoenix) s3Heal = Math.round(s3Heal * 1.45);

      const s1ExecRaw = Math.round(s1Dmg * 1.8); // 斩杀加深
      totalDmg = s1Dmg + s2Dmg + aaDmg + s3Dmg + s1ExecRaw;
      totalHeal = aaHeal + s3Heal;

      steps = [
        { name: '1技能 哮天飞狗', desc: '预判哮天犬标记并二段突进', dmg: s1Dmg, heal: 0 },
        { name: '2技能 虚妄横扫', desc: '近身横扫眩晕控场并附魔真伤', dmg: s2Dmg, heal: 0 },
        { name: '真伤强化普攻', desc: '真实伤害连击与生命续航', dmg: aaDmg, heal: aaHeal },
        { name: '3技能 根源之目', desc: '三道激光爆轰群伤，巨额血条吸满', dmg: s3Dmg, heal: s3Heal },
        { name: '二段 哮天斩杀', desc: '已损生命百分比致命收割', dmg: s1ExecRaw, heal: 0 }
      ];
    } else if (cname === '安琪拉') {
      comboName = '2-3-1 炽热瞬秒连招';
      const s2Raw = Math.round(500 + 0.50 * ap + (hasEcho ? 100 + 0.4 * ap : 0));
      const s2Dmg = Math.round(s2Raw * mDmgFactor);

      const s3Raw = Math.round(8 * (170 + 0.23 * ap)); // 8段激光
      const s3Dmg = Math.round(s3Raw * mDmgFactor * 1.20); // 炽热印记叠伤
      const s3Shield = Math.round(850 + 0.80 * ap);

      const s1Raw = Math.round(5 * (350 + 0.30 * ap)); // 5颗火球
      const s1Dmg = Math.round(s1Raw * mDmgFactor);

      totalDmg = s2Dmg + s3Dmg + s1Dmg;
      totalHeal = s3Shield;

      steps = [
        { name: '2技能 混沌火种', desc: '眩晕控场并施加灼烧印记', dmg: s2Dmg, heal: 0 },
        { name: '3技能 炽热光辉', desc: '八段霸体熔岩极速激光，生成法术护盾', dmg: s3Dmg, heal: s3Shield },
        { name: '1技能 火球术收尾', desc: '五颗炽热火球密集连发收割', dmg: s1Dmg, heal: 0 }
      ];
    } else if (cname === '孙尚香') {
      comboName = '1-A-2-3 重炮爆发连招';
      const rollRaw = Math.round(ad + 380 + 1.0 * ad + spellbladeMult * ad);
      const critMul = 1 + (critRate / 100) * 1.1; // 暴击翻倍
      const rollDmg = Math.round(rollRaw * pDmgFactor * critMul);

      const s2Raw = Math.round(400 + 0.50 * ad);
      const s2Dmg = Math.round(s2Raw * pDmgFactor); // 附带破甲25%

      const s3Raw = Math.round(900 + 1.85 * ad);
      const s3Dmg = Math.round(s3Raw * pDmgFactor);

      const aaRaw = Math.round(ad * pDmgFactor * critMul);
      const lifestealHeal = Math.round((rollDmg + aaRaw) * (lifesteal / 100));

      totalDmg = rollDmg + s2Dmg + s3Dmg + aaRaw;
      totalHeal = lifestealHeal;

      steps = [
        { name: '1技能 翻滚突袭', desc: '超远距离强化重炮普攻，触发宗师强击', dmg: rollDmg, heal: lifestealHeal },
        { name: '2技能 红莲爆弹', desc: '标记目标削弱 25% 物理护甲并减速', dmg: s2Dmg, heal: 0 },
        { name: '跟进普通攻击', desc: '穿透破甲连击走A', dmg: aaRaw, heal: 0 },
        { name: '3技能 究极弩炮', desc: '超远距离爆破飞弹轰击残血', dmg: s3Dmg, heal: 0 }
      ];
    } else {
      // 通用高仿真技能伤害模型
      comboName = '全套核心技能连招';
      const isMage = role.includes('法师') || ap > ad;
      const primaryStat = isMage ? ap : ad;
      const factor = isMage ? mDmgFactor : pDmgFactor;

      const s1Dmg = Math.round((450 + 0.75 * primaryStat) * factor);
      const s2Dmg = Math.round((550 + 0.90 * primaryStat) * factor);
      const s3Dmg = Math.round((1100 + 1.45 * primaryStat) * factor);
      const aaDmg = Math.round((ad * (1 + spellbladeMult)) * pDmgFactor);
      const healAmt = Math.round((lifesteal / 100) * aaDmg + (hasPhoenix ? 350 : 0));

      totalDmg = s1Dmg + s2Dmg + s3Dmg + aaDmg;
      totalHeal = healAmt;

      steps = [
        { name: '1技能 起手突进/消耗', desc: '首轮核心技能消耗与起手试探', dmg: s1Dmg, heal: 0 },
        { name: '2技能 核心机制控制', desc: '范围控场减速削弱防御', dmg: s2Dmg, heal: 0 },
        { name: '技能间隙穿插平A', desc: '触发装备强击与普攻附伤', dmg: aaDmg, heal: healAmt },
        { name: '3技能 必杀大招终结', desc: '大招锁定斩杀打满全额伤害', dmg: s3Dmg, heal: 0 }
      ];
    }

    return {
      comboName,
      steps,
      totalDmg,
      totalHeal,
      hasCangqiong,
      hasHuiyue
    };
  }

  const userCombat = evalPresetCombat(userItems, userArcana);
  const officialCombat = evalPresetCombat(officialItems, officialArcana);

  const dmgDiff = userCombat.totalDmg - officialCombat.totalDmg;
  const healDiff = userCombat.totalHeal - officialCombat.totalHeal;

  return {
    comboName: userCombat.comboName,
    userCombat,
    officialCombat,
    dmgDiff,
    healDiff,
    steps: userCombat.steps
  };
}
