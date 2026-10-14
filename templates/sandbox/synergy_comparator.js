// === 3. 获取官方默认推荐铭文 ===
function getHeroOfficialArcana(hero) {
  if (hero && hero.recommended_arcana) {
    const rec = hero.recommended_arcana;
    return {
      red: { [rec.red]: 10 },
      green: { [rec.green]: 10 },
      blue: { [rec.blue]: 10 }
    };
  }
  const r = (hero.role || '') + (hero.lane || '');
  if (r.includes('法师') || r.includes('中路')) {
    return { red: { '梦魇': 10 }, green: { '心眼': 10 }, blue: { '狩猎': 10 } };
  } else if (r.includes('坦克') || r.includes('游走')) {
    return { red: { '宿命': 10 }, green: { '虚空': 10 }, blue: { '调和': 10 } };
  }
  return { red: { '异变': 10 }, green: { '鹰眼': 10 }, blue: { '狩猎': 10 } };
}

// === 4. 汇总装备、铭文与英雄满级基准数值 ===
function aggregateBuildStats(items, arcanaMap, hero) {
  items = items || [];
  arcanaMap = arcanaMap || {};

  const getStatVal = (val, def) => {
    if (Array.isArray(val)) return val[1] || val[0] || def;
    return typeof val === 'number' ? val : def;
  };
  const bStats = (hero && hero.base_stats) || {};
  let ad = getStatVal(bStats.atk, 0);
  let ap = 0;
  let hp = getStatVal(bStats.hp, 0);
  let pdef = getStatVal(bStats.pdef, 0);
  let mdef = getStatVal(bStats.mdef, 0);
  let cdr = 0, crit = 0, gold = 0;

  items.forEach(it => {
    const st = it.stats || {};
    ad += st.atk || 0;
    ap += st.ap || 0;
    hp += st.hp || 0;
    pdef += st.pdef || 0;
    mdef += st.mdef || 0;
    cdr += st.cdr || 0;
    crit += st.crit || 0;
    gold += it.total_price || 0;
  });

  ['red', 'green', 'blue'].forEach(k => {
    const m = arcanaMap[k] || {};
    Object.entries(m).forEach(([aname, cnt]) => {
      if (typeof ARCANA_DATA !== 'undefined' && ARCANA_DATA[aname]) {
        const ast = ARCANA_DATA[aname].stats || {};
        ad += (ast.atk || 0) * cnt;
        ap += (ast.ap || 0) * cnt;
        hp += (ast.hp || 0) * cnt;
        pdef += (ast.pdef || 0) * cnt;
        mdef += (ast.mdef || 0) * cnt;
        cdr += (ast.cdr || 0) * cnt;
        crit += (ast.crit || 0) * cnt;
      }
    });
  });

  return {
    ad: Math.round(ad),
    ap: Math.round(ap),
    hp: Math.round(hp),
    pdef: Math.round(pdef),
    mdef: Math.round(mdef),
    cdr: Math.min(40, Math.round(cdr)),
    crit: Math.round(crit),
    gold: Math.round(gold),
    count: items.length
  };
}

// === 5. 自选方案 VS 王者推荐方案 综合对比核心引擎 ===
function compareUserBuildWithOfficial(userItems, baselinePreset, hero, userArcana) {
  userItems = userItems || [];
  baselinePreset = baselinePreset || { items: [] };
  const baseItems = baselinePreset.items || [];
  hero = hero || {};

  userArcana = userArcana || (typeof currentArcana !== 'undefined' ? currentArcana : {});
  const officialArcana = getHeroOfficialArcana(hero);

  function isArcanaEqual(a1, a2) {
    for (const color of ['red', 'green', 'blue']) {
      const m1 = a1[color] || {};
      const m2 = a2[color] || {};
      const k1 = Object.keys(m1).sort();
      const k2 = Object.keys(m2).sort();
      if (k1.length !== k2.length) return false;
      for (let i = 0; i < k1.length; i++) {
        if (k1[i] !== k2[i] || m1[k1[i]] !== m2[k2[i]]) return false;
      }
    }
    return true;
  }

  const isArcanaSame = isArcanaEqual(userArcana, officialArcana);
  let arcanaDiffNotice = '';
  if (!isArcanaSame) {
    const uArcStats = aggregateBuildStats([], userArcana, {});
    const bArcStats = aggregateBuildStats([], officialArcana, {});
    const diffTokens = [];
    if (uArcStats.ad !== bArcStats.ad) diffTokens.push(`物理攻击 ${uArcStats.ad - bArcStats.ad > 0 ? '+' : ''}${uArcStats.ad - bArcStats.ad}`);
    if (uArcStats.ap !== bArcStats.ap) diffTokens.push(`法术攻击 ${uArcStats.ap - bArcStats.ap > 0 ? '+' : ''}${uArcStats.ap - bArcStats.ap}`);
    if (uArcStats.hp !== bArcStats.hp) diffTokens.push(`生命值 ${uArcStats.hp - bArcStats.hp > 0 ? '+' : ''}${uArcStats.hp - bArcStats.hp}`);
    if (uArcStats.crit !== bArcStats.crit) diffTokens.push(`暴击率 ${uArcStats.crit - bArcStats.crit > 0 ? '+' : ''}${uArcStats.crit - bArcStats.crit}%`);
    if (uArcStats.cdr !== bArcStats.cdr) diffTokens.push(`冷却缩减 ${uArcStats.cdr - bArcStats.cdr > 0 ? '+' : ''}${uArcStats.cdr - bArcStats.cdr}%`);
    arcanaDiffNotice = diffTokens.length > 0 ? `自选铭文与王者推荐差异：${diffTokens.join('、')}（已计入整体对比）` : '';
  }

  // 综合数值对比 (装备 + 铭文 + 满级基准)
  const uStat = aggregateBuildStats(userItems, userArcana, hero);
  const bStat = aggregateBuildStats(baseItems, officialArcana, hero);

  function create3ColRow(label, userVal, baseVal, unit) {
    unit = unit || '';
    const diff = userVal - baseVal;
    let diffStr = '持平';
    let status = 'equal';
    if (diff > 0) {
      diffStr = `+${diff}${unit} (领先)`;
      status = 'plus';
    } else if (diff < 0) {
      diffStr = `${diff}${unit} (落后)`;
      status = 'minus';
    }
    return {
      label,
      userDisplay: `${userVal}${unit}`,
      baseDisplay: `${baseVal}${unit}`,
      diffVal: diff,
      diffStr,
      status
    };
  }

  const tableRows = [
    create3ColRow('物理攻击', uStat.ad, bStat.ad),
    create3ColRow('法术攻击', uStat.ap, bStat.ap),
    create3ColRow('最大生命', uStat.hp, bStat.hp),
    create3ColRow('物理防御', uStat.pdef, bStat.pdef),
    create3ColRow('法术防御', uStat.mdef, bStat.mdef),
    create3ColRow('冷却缩减', uStat.cdr, bStat.cdr, '%'),
    create3ColRow('暴击率', uStat.crit, bStat.crit, '%'),
    {
      label: '六神总价',
      userDisplay: `${uStat.gold}g`,
      baseDisplay: `${bStat.gold}g`,
      diffVal: uStat.gold - bStat.gold,
      diffStr: uStat.gold === bStat.gold ? '持平' : (uStat.gold < bStat.gold ? `-${bStat.gold - uStat.gold}g (更便宜)` : `+${uStat.gold - bStat.gold}g (稍贵)`),
      status: uStat.gold < bStat.gold ? 'plus' : (uStat.gold > bStat.gold ? 'minus' : 'equal')
    }
  ];

  // 核心机制判定
  const uNames = userItems.map(i => i.item_name || '');
  const bNames = baseItems.map(i => i.item_name || '');

  const MECHANIC_RULES = [
    {
      name: '纯净苍穹/天穹 (35%主动免伤)',
      check: names => names.includes('纯净苍穹') || names.includes('天穹'),
      pro: '装配【纯净苍穹】，提供 35% 进场主动减伤且受控可用，开团对拼防暴毙容错大幅提升。',
      con: '缺少【纯净苍穹】的高额免伤。选中的王者推荐具备苍穹自保能力，当前配装切入吃控易被秒。'
    },
    {
      name: '辉月 (1.5秒金身规避爆发)',
      check: names => names.includes('辉月'),
      pro: '装配【辉月】具备 1.5 秒无敌保命金身，面对刺客强切或致命大招具备绝对规避反制手段。',
      con: '缺少【辉月】金身保命。选中的王者推荐方案有金身规避爆发，当前身板脆弱易被瞬秒。'
    },
    {
      name: '破晓 (40%百分比物理穿透)',
      check: names => names.includes('破晓') || names.includes('仁者破晓'),
      pro: '装配【破晓】提供 40% 高额物理穿甲，中后期撕裂敌方高抗万血前排坦克伤害大幅领先。',
      con: '缺少【破晓】百分比穿甲。选中的王者推荐方案具备打肉能力，当前配装打前排稍显刮痧。'
    },
    {
      name: '虚无法杖/日暮之流 (百分比法穿)',
      check: names => names.includes('虚无法杖') || names.includes('日暮之流'),
      pro: '装配核心法穿大件，面对敌方前排魔女斗篷与永夜守护时法术伤害穿透力远高于推荐方案。',
      con: '缺少百分比法穿大件。选中的王者推荐方案具备核心法穿，当前配装面对出魔抗的前排伤害衰减较大。'
    },
    {
      name: '泣血之刃/末世/吸血书 (吸血续航)',
      check: names => names.includes('泣血之刃') || names.includes('末世') || names.includes('噬神之书'),
      pro: '装配高额吸血大件，残血可快速通过小兵野怪回满，无需频繁回城补给，对线参团节奏拉满。',
      con: '缺少吸血续航大件。选中的王者推荐方案具备兵线吸血能力，当前配装残血只能频繁回城，易漏线丢节奏。'
    },
    {
      name: '不祥征兆 (40%削弱攻速移速)',
      check: names => names.includes('不祥征兆'),
      pro: '装配【不祥征兆】受击削弱敌方 40% 攻速与 10% 移速，极大限制敌方射手走A输出节奏。',
      con: '缺少【不祥征兆】的减速减攻速光环，对普攻型英雄压制力较王者推荐方案偏弱。'
    },
    {
      name: '魔女斗篷/永夜守护 (法术护盾与魔抗)',
      check: names => names.includes('魔女斗篷') || names.includes('永夜守护'),
      pro: '装配核心魔抗与吸收法伤护盾，团战面对敌方法核远程消耗与爆发 AOE 抗伤极为扎实。',
      con: '缺少核心魔抗防御与法术护盾，面对敌方法核一套技能极易血条融化。'
    },
    {
      name: '红莲斗篷 (贴脸灼烧附带重伤)',
      check: names => names.includes('红莲斗篷'),
      pro: '装配【红莲斗篷】贴脸持续灼烧最大生命法伤并附带重伤，近战肉搏的同时强力限制敌方回复。',
      con: '缺少【红莲斗篷】的灼烧与重伤压制，选中的王者推荐方案清线更快且带重伤限制敌方吸血。'
    }
  ];

  const pros = [];
  const cons = [];

  MECHANIC_RULES.forEach(r => {
    const userHas = r.check(uNames);
    const baseHas = r.check(bNames);
    if (userHas && !baseHas) {
      pros.push({ title: r.name, desc: r.pro });
    } else if (!userHas && baseHas) {
      cons.push({ title: r.name, desc: r.con });
    }
  });

  const comboResult = (typeof calculateHeroCombo === 'function')
    ? calculateHeroCombo(hero, userItems, userArcana, baseItems, officialArcana)
    : null;

  return {
    tableRows,
    pros: pros.slice(0, 3),
    cons: cons.slice(0, 3),
    uStat,
    bStat,
    isArcanaSame,
    arcanaDiffNotice,
    comboResult
  };
}
