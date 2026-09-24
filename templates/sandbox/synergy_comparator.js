// ==============================================================================
// 王者出装箱 ｜ 官方出装全维横向对比与机制差异推演引擎 (synergy_comparator.js)
// 依据王者官方 3 套经典对标方案（热门标配/极限高爆/半肉容错），
// 进行全维属性差值 (Diff) 与核心机制技能 (苍穹免伤/破晓穿透/泣血续航等) 对比剖析
// ==============================================================================

// === 1. 官方基准出装生成器 (100% 遵照官方原始命名与方案数量) ===
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

  // 1. 优先读取官方真实出装数据库 (SSOT)
  if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
    const rawList = OFFICIAL_HERO_BUILDS[cname];
    return rawList.map((p, idx) => ({
      id: p.id || `official_${idx + 1}`,
      title: p.name || `推荐出装${idx + 1}`, // 100% 官方原始名字
      tag: `官方方案${idx + 1}`,
      desc: p.desc || '王者官方推荐经典对局思路。',
      itemNames: p.item_names || [],
      items: resolveItems(p.item_names || [])
    }));
  }

  // 2. 兜底 fallback (遵循官方命名规范：推荐出装一、推荐出装二)
  const role = hero.role || '';
  const lane = hero.lane || '';
  const r = role + lane;

  let p1Names = [], p2Names = [];
  let p1Desc = '官方综合胜率最高的经典主流配装思路。';
  let p2Desc = '强化实战特定维度的官方备选方案。';

  if (r.includes('射手') || r.includes('发育路')) {
    p1Names = ['急速战靴', '影刃', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];
    p2Names = ['急速战靴', '末世', '无尽战刃', '破晓', '纯净苍穹', '魔女斗篷'];
    p1Desc = '利用无尽破晓的高额暴击与穿透打出持续高爆发输出。';
    p2Desc = '末世苍穹强化残血对拼与防刺客强切自保容错。';
  } else if (r.includes('法师') || r.includes('中路')) {
    p1Names = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
    p2Names = ['秘法之靴', '回响之杖', '博学者之怒', '日暮之流', '贤者之书', '虚无法杖'];
    p1Desc = '博学者之怒与法穿配合辉月金身，兼顾极致法强与保命。';
    p2Desc = '极限高法强法穿，远距离消耗瞬秒敌方后排脆皮。';
  } else if (r.includes('刺客') || (r.includes('打野') && !r.includes('坦克'))) {
    p1Names = ['贪婪之噬', '急速战靴', '泣血之刃', '暗影战斧', '宗师之力', '破军'];
    p2Names = ['贪婪之噬', '抵抗之靴', '暗影战斧', '纯净苍穹', '名刀·司命', '破军'];
    p1Desc = '黑切破军物穿拉满，专注野区经济滚雪球瞬秒后排。';
    p2Desc = '苍穹名刀双重保命，提升进场开团与残血收割容错率。';
  } else if (r.includes('坦克') || (r.includes('肉') && r.includes('游走'))) {
    p1Names = ['极影·救赎', '抵抗之靴', '红莲斗篷', '霸者重装', '魔女斗篷', '不祥征兆'];
    p2Names = ['抵抗之靴', '红莲斗篷', '暴烈之甲', '暗影战斧', '不祥征兆', '永夜守护'];
    p1Desc = '高额血量双抗构筑前排钢铁壁垒，吃满敌方集火。';
    p2Desc = '半肉战坦兼备一定物穿输出与灼烧消耗。';
  } else {
    p1Names = ['抵抗之靴', '暗影战斧', '暴烈之甲', '宗师之力', '纯净苍穹', '永夜守护'];
    p2Names = ['抵抗之靴', '暗影战斧', '红莲斗篷', '极寒风暴', '纯净苍穹', '不死鸟之眼'];
    p1Desc = '黑切苍穹半肉双抗攻守兼顾，切入后排威胁极大。';
    p2Desc = '强化对线抗压与技能冷却回转，多轮拉扯反打。';
  }

  return [
    { id: 'official_1', title: '推荐出装一', tag: '官方方案1', desc: p1Desc, itemNames: p1Names, items: resolveItems(p1Names) },
    { id: 'official_2', title: '推荐出装二', tag: '官方方案2', desc: p2Desc, itemNames: p2Names, items: resolveItems(p2Names) }
  ];
}

// === 2. 装备数值聚合汇总计算 ===
function aggregateBuildStats(items) {
  let ad = 0, ap = 0, hp = 0, pdef = 0, mdef = 0, cdr = 0, crit = 0, ms = 0, gold = 0;
  (items || []).forEach(it => {
    const st = it.stats || {};
    ad += st.atk || 0;
    ap += st.ap || 0;
    hp += st.hp || 0;
    pdef += st.pdef || 0;
    mdef += st.mdef || 0;
    cdr += st.cdr || 0;
    crit += st.crit || 0;
    ms += st.percent_speed || 0;
    gold += it.total_price || 0;
  });
  return { ad, ap, hp, pdef, mdef, cdr: Math.min(40, cdr), crit, ms, gold, count: items.length };
}

// === 3. 用户出装 vs 官方基准全维对比核心引擎 ===
function compareUserBuildWithOfficial(userItems, baselinePreset, hero) {
  userItems = userItems || [];
  baselinePreset = baselinePreset || { items: [] };
  const baseItems = baselinePreset.items || [];

  const uStat = aggregateBuildStats(userItems);
  const bStat = aggregateBuildStats(baseItems);

  // 数值维度的横向 Diff
  const numDiff = {
    ad: { label: '物理攻击', user: uStat.ad, base: bStat.ad, diff: uStat.ad - bStat.ad },
    ap: { label: '法术攻击', user: uStat.ap, base: bStat.ap, diff: uStat.ap - bStat.ap },
    hp: { label: '额外生命', user: uStat.hp, base: bStat.hp, diff: uStat.hp - bStat.hp },
    pdef: { label: '物理防御', user: uStat.pdef, base: bStat.pdef, diff: uStat.pdef - bStat.pdef },
    mdef: { label: '法术防御', user: uStat.mdef, base: bStat.mdef, diff: uStat.mdef - bStat.mdef },
    cdr: { label: '冷却缩减', user: uStat.cdr + '%', base: bStat.cdr + '%', diffVal: uStat.cdr - bStat.cdr, diff: (uStat.cdr - bStat.cdr >= 0 ? '+' : '') + (uStat.cdr - bStat.cdr) + '%' },
    crit: { label: '暴击率', user: uStat.crit + '%', base: bStat.crit + '%', diffVal: uStat.crit - bStat.crit, diff: (uStat.crit - bStat.crit >= 0 ? '+' : '') + (uStat.crit - bStat.crit) + '%' },
    gold: { label: '总金币造价', user: uStat.gold + 'g', base: bStat.gold + 'g', diffVal: uStat.gold - bStat.gold, diff: (uStat.gold - bStat.gold >= 0 ? '+' : '') + (uStat.gold - bStat.gold) + 'g' }
  };

  // 装备与机制提取
  const uNames = userItems.map(i => i.item_name);
  const bNames = baseItems.map(i => i.item_name);

  // 核心机制判定字典
  const MECHANIC_RULES = [
    {
      id: 'cangqiong',
      name: '纯净苍穹/天穹 (35%主动免伤)',
      check: names => names.includes('纯净苍穹') || names.includes('天穹'),
      proDesc: '装配【纯净苍穹】提供 35% 进场免伤且受控可用。相比选中的官方方案，进场开团与肉搏对拼时防暴毙容错大幅提升！',
      conDesc: '缺少【纯净苍穹】的高额免伤。选中的官方方案具备苍穹防被秒能力，当前配装若切入吃控容错显著低于官方方案。'
    },
    {
      id: 'huiyue',
      name: '辉月 (1.5秒保命金身)',
      check: names => names.includes('辉月'),
      proDesc: '装配【辉月】具备 1.5 秒无敌保命金身。相比官方方案，面对刺客强切或致命指向大招具备绝对的反制规避手段。',
      conDesc: '缺少【辉月】金身保命。选中的官方方案有金身规避爆发，当前配装身板脆弱，被强切时极难规避刺客致命一套。'
    },
    {
      id: 'poxiao',
      name: '破晓 (40%百分比物理穿透)',
      check: names => names.includes('破晓') || names.includes('仁者破晓'),
      proDesc: '装备【破晓】提供 40% 高额物理穿透。相比官方方案，中后期撕裂敌方 1000+ 双抗的前排坦克伤害大幅领先！',
      conDesc: '缺失【破晓】百分比穿甲。选中的官方方案具备破晓打肉能力，当前配装中后期打敌方万血高抗坦克犹如刮痧。'
    },
    {
      id: 'fachuan',
      name: '虚无法杖/日暮之流 (百分比法穿)',
      check: names => names.includes('虚无法杖') || names.includes('日暮之流'),
      proDesc: '装配核心法穿大件，面对敌方前排魔女斗篷与永夜守护时，法术伤害穿透力远高于官方方案。',
      conDesc: '缺失百分比法穿大件。选中的官方方案具备核心法穿，当前配装面对敌方出魔抗的前排时伤害衰减超 50%。'
    },
    {
      id: 'lifesteal',
      name: '泣血之刃/末世/吸血书 (吸血续航)',
      check: names => names.includes('泣血之刃') || names.includes('末世') || names.includes('噬神之书'),
      proDesc: '装配吸血续航大件。相比官方方案，残血可快速通过兵线野怪回满，无需频繁回城补给，对线参团节奏拉满。',
      conDesc: '缺少吸血与血量续航大件。选中的官方方案具备兵线吸血能力，当前配装残血只能频繁回城，易漏线丢节奏。'
    },
    {
      id: 'buxiang',
      name: '不祥征兆 (40%削弱攻速移速)',
      check: names => names.includes('不祥征兆'),
      proDesc: '装配【不祥征兆】受击削弱敌方 40% 攻速移速。相比官方方案，极大瓦解敌方射手走A输出节奏。',
      conDesc: '缺少【不祥征兆】的减速减攻速光环。选中的官方方案对普攻英雄压制力更强，当前配装抗射手持续走A偏弱。'
    },
    {
      id: 'mowu',
      name: '魔女斗篷/永夜守护 (高额法防与护盾)',
      check: names => names.includes('魔女斗篷') || names.includes('永夜守护'),
      proDesc: '装配核心魔抗大件与吸收法伤护盾。相比官方方案，团战面对敌方法核远程消耗与爆发 AOE 抗伤极为扎实。',
      conDesc: '缺少高额魔抗防御与法术护盾。选中的官方方案具备魔女防秒能力，当前配装极易吃法核一套技能暴毙。'
    },
    {
      id: 'honglian',
      name: '红莲斗篷 (贴脸灼烧附带重伤)',
      check: names => names.includes('红莲斗篷'),
      proDesc: '装配【红莲斗篷】贴脸持续灼烧最大生命法伤并附带重伤，肉搏吃伤害的同时强力限制敌方回复。',
      conDesc: '缺少【红莲斗篷】的灼烧与重伤压制。选中的官方方案清线更快且带重伤，当前配装近战肉搏消耗稍逊。'
    }
  ];

  const pros = [];
  const cons = [];

  MECHANIC_RULES.forEach(rule => {
    const userHas = rule.check(uNames);
    const baseHas = rule.check(bNames);
    if (userHas && !baseHas) {
      pros.push({ title: '🌟 领先机制：' + rule.name, desc: rule.proDesc });
    } else if (!userHas && baseHas) {
      cons.push({ title: '⚠️ 缺失机制：' + rule.name, desc: rule.conDesc });
    }
  });

  // 数值质变优势与短板补充
  if (uStat.cdr - bStat.cdr >= 15) {
    pros.push({ title: '🌟 冷却回转大幅领先 +' + (uStat.cdr - bStat.cdr) + '%', desc: '技能真空期显著短于选中的官方方案，多轮位移与技能拉扯频率具备绝对主动权。' });
  } else if (bStat.cdr - uStat.cdr >= 15) {
    cons.push({ title: '⚠️ 技能真空期显著偏长 -' + (bStat.cdr - uStat.cdr) + '%', desc: '相较选中的官方方案，当前配装技能冷却回转较慢，一轮技能交出后拉扯空窗期较长。' });
  }

  if (uStat.hp - bStat.hp >= 1500 || (uStat.pdef + uStat.mdef) - (bStat.pdef + bStat.mdef) >= 350) {
    pros.push({ title: '🌟 身板坦度明显高出官方方案', desc: `额外生命多 +${uStat.hp - bStat.hp}，物法抗性高出 +${(uStat.pdef + uStat.mdef) - (bStat.pdef + bStat.mdef)}，前排承伤防突刺容错更优。` });
  } else if (bStat.hp - uStat.hp >= 1500 || (bStat.pdef + bStat.mdef) - (uStat.pdef + uStat.mdef) >= 350) {
    cons.push({ title: '⚠️ 身板坦度明显低于官方方案', desc: `相较官方方案生命少 -${bStat.hp - uStat.hp}，双抗落后 -${(bStat.pdef + bStat.mdef) - (uStat.pdef + uStat.mdef)}，对拼与进场容错率较低。` });
  }

  if (uStat.ad - bStat.ad >= 80 || uStat.ap - bStat.ap >= 150 || uStat.crit - bStat.crit >= 20) {
    pros.push({ title: '🌟 输出伤害爆发力显著领先', desc: '攻击面板与核心爆发属性明显高出选中的官方方案，对敌方后排脆皮具备更强的瞬秒杀伤力。' });
  } else if (bStat.ad - uStat.ad >= 80 || bStat.ap - uStat.ap >= 150 || bStat.crit - uStat.crit >= 20) {
    cons.push({ title: '⚠️ 输出爆发力低于官方方案', desc: '相较选中的官方方案攻击面板与爆发不足，一套连招对残血的收割致死率稍有欠缺。' });
  }

  if (uStat.gold - bStat.gold >= 600) {
    cons.push({ title: '⚠️ 六神装总价偏高成型偏慢', desc: `配装总价高出官方方案 +${uStat.gold - bStat.gold} 金币，装备过渡较吃经济，逆风时成型真空期被拉长。` });
  } else if (bStat.gold - uStat.gold >= 600) {
    pros.push({ title: '🌟 经济造价便宜成型极快', desc: `总造价比官方方案便宜 -${bStat.gold - uStat.gold} 金币，相同经济下能更早做出关键大件，抢占对局中前期强势期。` });
  }

  return {
    numDiff,
    pros: pros.slice(0, 3),
    cons: cons.slice(0, 3),
    uStat,
    bStat
  };
}
