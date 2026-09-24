// ==============================================================================
// 王者出装箱 ｜ 自选方案 VS 王者推荐方案 全维对比与机制推演引擎 (synergy_comparator.js)
// 依据王者官方出装推荐、全维数值Diff(自选/推荐/差异)、核心机制差异(PROS/CONS)与实战连招总伤害
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 350 行以内
// ==============================================================================

// === 1. 智能推断王者推荐方案实战流派名称 ===
function inferPresetTypeName(items, hero, desc, idx) {
  desc = desc || '';
  const role = (hero && hero.role) || '';
  let ad = 0, ap = 0, hp = 0, crit = 0;
  const names = (items || []).map(i => i.item_name || '');

  (items || []).forEach(it => {
    const st = it.stats || {};
    ad += st.atk || 0;
    ap += st.ap || 0;
    hp += st.hp || 0;
    crit += st.crit || 0;
  });

  // 1. 优先提取官方 Tips 中的明确意图关键词
  if (desc.includes('全输出') || desc.includes('直接击破') || desc.includes('秒杀') || desc.includes('爆发')) return '高爆秒人流';
  if (desc.includes('全肉') || desc.includes('提高生存') || desc.includes('控制敌人')) return '全肉抗伤流';
  if (desc.includes('半肉') || desc.includes('容错') || desc.includes('坦度')) return '半肉容错流';
  if (desc.includes('穿透') || desc.includes('暴击')) return '暴击破甲流';
  if (desc.includes('冷却') || desc.includes('频繁的使用') || desc.includes('消耗')) return '技能消耗流';
  if (names.some(n => n.includes('贪婪之噬') || n.includes('追击刀锋') || n.includes('利斧') || n.includes('打野'))) return '打野节奏流';
  if (names.some(n => n.includes('极影') || n.includes('救赎') || n.includes('近卫') || n.includes('形昭'))) return '游走辅核流';

  // 2. 根据装备属性智能定性
  if (role.includes('射手')) {
    if (crit >= 30 || names.includes('破军')) return '暴击穿透流';
    if (hp >= 1200 || names.includes('纯净苍穹')) return '半肉自保流';
    return idx === 0 ? '暴击破甲流' : '法球攻速流';
  }
  if (role.includes('法师')) {
    if (ap >= 500 || names.includes('博学者之怒')) return '法核爆发流';
    return idx === 0 ? '法核爆发流' : '技能消耗流';
  }
  if (role.includes('坦克') || role.includes('辅助')) {
    if (ad <= 80 && hp >= 3500) return '重装坦伤流';
    return idx === 0 ? '全肉坦伤流' : '半肉对抗流';
  }
  if (role.includes('刺客')) {
    if (ad >= 220) return '瞬杀高爆流';
    return idx === 0 ? '爆发收割流' : '半肉容错流';
  }

  // 战士/对抗路
  if (hp >= 2000 && ad >= 140) return '半肉战阵流';
  if (hp >= 3500) return '重装坦伤流';
  if (ad >= 250) return '极限输出流';
  return idx === 0 ? '半肉稳健流' : '极速切入流';
}

// === 2. 获取当前英雄王者推荐方案列表 ===
function getHeroOfficialPresets(hero) {
  if (!hero) return [];
  const cname = hero.cname || '';
  const aliasMap = { '强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴' };

  function resolveItems(names) {
    const list = [];
    (names || []).forEach(name => {
      const it = (typeof ITEMS_DATA !== 'undefined' ? ITEMS_DATA : []).find(i => i.item_name === name || i.item_name === aliasMap[name]);
      if (it && list.length < 6) list.push(it);
    });
    return list;
  }

  // 1. 优先读取官方真实出装数据库
  if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
    const rawList = OFFICIAL_HERO_BUILDS[cname];
    return rawList.map((p, idx) => {
      const items = resolveItems(p.item_names || []);
      const typeTitle = inferPresetTypeName(items, hero, p.desc, idx);
      return {
        id: p.id || `official_${idx + 1}`,
        title: `王者推荐·${typeTitle}`,
        genre: typeTitle,
        desc: p.desc || '王者官方推荐经典实战配装。',
        itemNames: p.item_names || [],
        items
      };
    });
  }

  // 2. 兜底方案
  const r = (hero.role || '') + (hero.lane || '');
  let p1Names = [], p2Names = [];
  let p1Desc = '官方综合胜率最高的经典高爆配装。';
  let p2Desc = '强化实战对拼与防御容错的稳健配装。';

  if (r.includes('射手') || r.includes('发育路')) {
    p1Names = ['急速战靴', '影刃', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];
    p2Names = ['急速战靴', '末世', '无尽战刃', '破晓', '纯净苍穹', '魔女斗篷'];
  } else if (r.includes('法师') || r.includes('中路')) {
    p1Names = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
    p2Names = ['秘法之靴', '回响之杖', '博学者之怒', '日暮之流', '贤者之书', '虚无法杖'];
  } else if (r.includes('刺客') || (r.includes('打野') && !r.includes('坦克'))) {
    p1Names = ['贪婪之噬', '急速战靴', '泣血之刃', '暗影战斧', '宗师之力', '破军'];
    p2Names = ['贪婪之噬', '抵抗之靴', '暗影战斧', '纯净苍穹', '名刀·司命', '破军'];
  } else if (r.includes('坦克') || (r.includes('肉') && r.includes('游走'))) {
    p1Names = ['极影·救赎', '抵抗之靴', '红莲斗篷', '霸者重装', '魔女斗篷', '不祥征兆'];
    p2Names = ['抵抗之靴', '红莲斗篷', '暴烈之甲', '暗影战斧', '不祥征兆', '永夜守护'];
  } else {
    p1Names = ['抵抗之靴', '暗影战斧', '暴烈之甲', '宗师之力', '纯净苍穹', '永夜守护'];
    p2Names = ['抵抗之靴', '暗影战斧', '红莲斗篷', '极寒风暴', '纯净苍穹', '不死鸟之眼'];
  }

  const p1Items = resolveItems(p1Names);
  const p2Items = resolveItems(p2Names);

  return [
    { id: 'official_1', title: `王者推荐·${inferPresetTypeName(p1Items, hero, p1Desc, 0)}`, genre: inferPresetTypeName(p1Items, hero, p1Desc, 0), desc: p1Desc, itemNames: p1Names, items: p1Items },
    { id: 'official_2', title: `王者推荐·${inferPresetTypeName(p2Items, hero, p2Desc, 1)}`, genre: inferPresetTypeName(p2Items, hero, p2Desc, 1), desc: p2Desc, itemNames: p2Names, items: p2Items }
  ];
}

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

// === 4. 汇总装备与铭文综合实战数值 ===
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

  // 累加铭文属性
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

  // 1. 判断铭文是否一致
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
    const uArcStats = aggregateBuildStats([], userArcana);
    const bArcStats = aggregateBuildStats([], officialArcana);
    const diffTokens = [];
    if (uArcStats.ad !== bArcStats.ad) diffTokens.push(`物理攻击 ${uArcStats.ad - bArcStats.ad > 0 ? '+' : ''}${uArcStats.ad - bArcStats.ad}`);
    if (uArcStats.ap !== bArcStats.ap) diffTokens.push(`法术攻击 ${uArcStats.ap - bArcStats.ap > 0 ? '+' : ''}${uArcStats.ap - bArcStats.ap}`);
    if (uArcStats.hp !== bArcStats.hp) diffTokens.push(`生命值 ${uArcStats.hp - bArcStats.hp > 0 ? '+' : ''}${uArcStats.hp - bArcStats.hp}`);
    if (uArcStats.crit !== bArcStats.crit) diffTokens.push(`暴击率 ${uArcStats.crit - bArcStats.crit > 0 ? '+' : ''}${uArcStats.crit - bArcStats.crit}%`);
    if (uArcStats.cdr !== bArcStats.cdr) diffTokens.push(`冷却缩减 ${uArcStats.cdr - bArcStats.cdr > 0 ? '+' : ''}${uArcStats.cdr - bArcStats.cdr}%`);
    arcanaDiffNotice = diffTokens.length > 0 ? `自选铭文与王者推荐差异：${diffTokens.join('、')}（已计入整体对比）` : '';
  }

  // 2. 综合数值对比 (装备 + 铭文 + 满级基准)
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

  // 3. 核心机制效果差异判定
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

  // 4. 计算连招实战伤害与回复
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
