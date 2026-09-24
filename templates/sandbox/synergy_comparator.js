// ==============================================================================
// 王者出装箱 ｜ 自选方案 VS 王者推荐方案 全维对比与机制推演引擎 (synergy_comparator.js)
// 依据王者官方出装推荐、英雄多分路出装、全维数值Diff、核心机制差异与实战连招总伤害
// 遵循 AGENTS.md 规范：模块单一职责，行数控制在 350 行以内
// ==============================================================================

// === 1. 智能推断方案实战流派名称 ===
function inferPresetTypeName(items, hero, desc, idx) {
  desc = desc || '';
  const role = (hero && hero.role) || '';
  let ad = 0, ap = 0, hp = 0;
  const names = (items || []).map(i => i.item_name || '');

  (items || []).forEach(it => {
    const st = it.stats || {};
    ad += st.atk || 0;
    ap += st.ap || 0;
    hp += st.hp || 0;
  });

  if (names.some(n => ['贪婪之噬', '追击刀锋', '巨人之握', '巡守利斧', '符文大剑', '游击弯刀', '怒龙剑盾'].includes(n))) return '打野节奏流';
  if (names.some(n => n.includes('极影') || n.includes('救赎') || n.includes('近卫') || n.includes('形昭'))) return '游走辅核流';
  if (desc.includes('名刀') || names.includes('名刀·司命')) return '名刀极限流';
  if (desc.includes('贤者') || names.includes('贤者的庇护')) return '复活容错流';
  if (desc.includes('全输出') || desc.includes('直接击破') || desc.includes('秒杀') || desc.includes('爆发')) return '高爆秒人流';
  if (desc.includes('全肉') || desc.includes('提高生存') || desc.includes('控制敌人')) return '全肉抗伤流';
  if (desc.includes('半肉') || desc.includes('容错') || desc.includes('坦度')) return '半肉容错流';
  if (desc.includes('穿透') || desc.includes('暴击')) return '暴击破甲流';
  if (desc.includes('冷却') || desc.includes('频繁的使用') || desc.includes('消耗')) return '技能消耗流';

  if (role.includes('射手')) return idx === 0 ? '暴击破甲流' : '法球攻速流';
  if (role.includes('法师')) return idx === 0 ? '法核爆发流' : '技能消耗流';
  if (role.includes('坦克') || role.includes('辅助')) return idx === 0 ? '全肉坦伤流' : '半肉对抗流';
  if (role.includes('刺客')) return idx === 0 ? '瞬杀收割流' : '半肉容错流';

  if (hp >= 2000 && ad >= 140) return '半肉战阵流';
  if (hp >= 3500) return '重装坦伤流';
  return idx === 0 ? '半肉稳健流' : '极速切入流';
}

// === 2. 获取英雄在特定分路下的王者推荐方案列表 (核心：同一英雄不同分路出装不同) ===
const JUNGLE_ITEMS_NAMES = ['贪婪之噬', '追击刀锋', '狩猎宽刃', '巨人之握', '巡守利斧', '符文大剑', '游击弯刀', '怒龙剑盾', '龙鳞利剑'];
const ROAM_ITEMS_NAMES = ['极影·救赎', '极影·形昭', '极影·星泉', '极影·空明', '近卫·救赎', '近卫·形昭', '近卫·星泉', '极影', '近卫', '学识宝石'];

function hasJungleBlade(names) {
  return (names || []).some(n => JUNGLE_ITEMS_NAMES.includes(n));
}

function hasRoamItem(names) {
  return (names || []).some(n => ROAM_ITEMS_NAMES.some(r => n.includes(r)));
}

function getHeroOfficialPresets(hero, lane) {
  if (!hero) return [];
  lane = lane || (typeof currentHeroActiveLane !== 'undefined' ? currentHeroActiveLane : (hero.lane || '对抗路'));
  const cname = hero.cname || '';
  const role = hero.role || '';
  const aliasMap = { '强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴' };

  function resolveItems(names) {
    const list = [];
    (names || []).forEach(name => {
      const it = (typeof ITEMS_DATA !== 'undefined' ? ITEMS_DATA : []).find(i => i.item_name === name || i.item_name === aliasMap[name]);
      if (it && list.length < 6) list.push(it);
    });
    return list;
  }

  // 1. 若分路为【打野】：必须包含打野刀体系！
  if (lane === '打野') {
    // 检查官方预设中是否有真正携带打野刀的方案 (如韩信、李白、澜、镜等原生刺客打野，以及杨戬局内打野方案)
    if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
      const jungleOfficial = OFFICIAL_HERO_BUILDS[cname].filter(p => p.lane === '打野' || hasJungleBlade(p.item_names));
      if (jungleOfficial.length > 0) {
        return jungleOfficial.map((p, idx) => {
          const items = resolveItems(p.item_names);
          const typeName = inferPresetTypeName(items, hero, p.desc, idx);
          return {
            id: p.id || `official_jungle_${idx + 1}`,
            title: `王者推荐·${typeName}`,
            genre: typeName,
            desc: p.desc || '王者官方推荐打野经典出装。',
            itemNames: p.item_names,
            items
          };
        });
      }
    }

    // 若官方原始接口未录入打野刀方案（如亚瑟、铠、夏侯惇、司空震、诸葛亮等），提供专属国服实战打野双体系
    let p1Names, p2Names;
    let p1Title = '王者推荐·野区高爆流', p1Desc = '红野刀贪婪之噬配合黑切穿透，野区清野控龙与抓人爆发极快。';
    let p2Title = '王者推荐·肉野容错流', p2Desc = '肉野刀巨人之握配合高额双抗，进场坦度惊人兼具持续肉搏伤害。';

    if (cname === '司空震') {
      p1Title = '王者推荐·符文极速流';
      p1Desc = '符文大剑配合金色圣剑与法穿，远近普攻雷霆连击爆发极高。';
      p1Names = ['符文大剑', '秘法之靴', '金色圣剑', '噬神之书', '博学者之怒', '虚无法杖'];
      p2Title = '王者推荐·半肉法刺流';
      p2Desc = '时之预言提升双抗容错，开大进场雷霆狂轰不易猝死。';
      p2Names = ['符文大剑', '抵抗之靴', '金色圣剑', '时之预言', '日暮之流', '博学者之怒'];
    } else if (cname === '诸葛亮') {
      p1Title = '王者推荐·蓝野法核流';
      p1Desc = '符文大剑配合回响法强，野区刷被动极快，大招元气弹连环收割。';
      p1Names = ['符文大剑', '秘法之靴', '回响之杖', '噬神之书', '博学者之怒', '虚无法杖'];
      p2Title = '王者推荐·金身容错流';
      p2Desc = '辉月提供极限保命与被动等待，团战容错率更高。';
      p2Names = ['符文大剑', '抵抗之靴', '回响之杖', '博学者之怒', '辉月', '虚无法杖'];
    } else if (role.includes('坦克')) {
      p1Names = ['巨人之握', '影忍之足', '红莲斗篷', '暴烈之甲', '不祥征兆', '永夜守护'];
      p2Names = ['巨人之握', '抵抗之靴', '暗影战斧', '暴烈之甲', '不祥征兆', '霸者重装'];
    } else if (role.includes('法师') || cname === '露娜' || cname === '芈月') {
      p1Names = ['符文大剑', '秘法之靴', '金色圣剑', '噬神之书', '博学者之怒', '虚无法杖'];
      p2Names = ['符文大剑', '抵抗之靴', '时之预言', '噬神之书', '日暮之流', '博学者之怒'];
    } else if (role.includes('射手')) {
      p1Names = ['贪婪之噬', '急速战靴', '影刃', '无尽战刃', '破晓', '泣血之刃'];
      p2Names = ['贪婪之噬', '急速战靴', '末世', '无尽战刃', '破晓', '纯净苍穹'];
    } else {
      // 战刺通用打野（如铠、亚瑟、夏侯惇、孙策、赵云、典韦等）
      p1Names = ['贪婪之噬', '抵抗之靴', '暗影战斧', '纯净苍穹', '宗师之力', '破军'];
      p2Names = ['巨人之握', '抵抗之靴', '暗影战斧', '暴烈之甲', '纯净苍穹', '永夜守护'];
    }

    const p1Items = resolveItems(p1Names);
    const p2Items = resolveItems(p2Names);
    return [
      { id: 'jungle_1', title: p1Title, genre: p1Title.replace('王者推荐·', ''), desc: p1Desc, itemNames: p1Names, items: p1Items },
      { id: 'jungle_2', title: p2Title, genre: p2Title.replace('王者推荐·', ''), desc: p2Desc, itemNames: p2Names, items: p2Items }
    ];
  }

  // 2. 若分路为【游走】：必须包含辅助装备体系！
  if (lane === '游走') {
    let p1Names, p2Names;
    if (role.includes('法师') || cname === '孙膑' || cname === '蔡文姬' || cname === '大乔' || cname === '瑶' || cname === '朵莉亚' || cname === '桑启') {
      p1Names = ['极影·形昭', '冷静之靴', '凝冰之息', '梦魇之牙', '圣杯', '霸者重装'];
      p2Names = ['极影·救赎', '冷静之靴', '时之预言', '博学者之怒', '虚无法杖', '辉月'];
    } else {
      // 战坦硬辅游走（如廉颇、亚瑟、张飞、牛魔、钟馗等）
      p1Names = ['极影·救赎', '影忍之足', '红莲斗篷', '霸者重装', '魔女斗篷', '不祥征兆'];
      p2Names = ['极影·形昭', '抵抗之靴', '暗影战斧', '暴烈之甲', '霸者重装', '永夜守护'];
    }
    const p1Items = resolveItems(p1Names);
    const p2Items = resolveItems(p2Names);
    return [
      { id: 'roam_1', title: '王者推荐·重装保人流', genre: '重装保人流', desc: '救赎护盾配合高额抗性，团战承伤吃满并保护核心C位。', itemNames: p1Names, items: p1Items },
      { id: 'roam_2', title: '王者推荐·开团突进流', genre: '开团突进流', desc: '形昭范围减速显形配合暗影战斧，拥有极强先手开团能力。', itemNames: p2Names, items: p2Items }
    ];
  }

  // 3. 若分路为【中路】：法术输出体系
  if (lane === '中路') {
    let p1Names = ['冷静之靴', '回响之杖', '博学者之怒', '虚无法杖', '辉月', '贤者之书'];
    let p2Names = ['秘法之靴', '痛苦面具', '凝冰之息', '日暮之流', '博学者之怒', '噬神之书'];
    if (!role.includes('法师')) {
      p1Names = ['抵抗之靴', '暗影战斧', '纯净苍穹', '破军', '暴烈之甲', '魔女斗篷'];
      p2Names = ['冷静之靴', '暗影战斧', '宗师之力', '无尽战刃', '碎星锤', '名刀·司命'];
    }
    const p1Items = resolveItems(p1Names);
    const p2Items = resolveItems(p2Names);
    return [
      { id: 'mid_1', title: '王者推荐·法核爆发流', genre: '法核爆发流', desc: '高额法强与穿透，远距离技能一套瞬秒敌方脆皮。', itemNames: p1Names, items: p1Items },
      { id: 'mid_2', title: '王者推荐·消耗拉扯流', genre: '消耗拉扯流', desc: '短CD消耗与减速拉扯，团战持续打出高额AOE伤害。', itemNames: p2Names, items: p2Items }
    ];
  }

  // 4. 若分路为【发育路】：射手/持续输出体系
  if (lane === '发育路') {
    let p1Names = ['急速战靴', '影刃', '无尽战刃', '泣血之刃', '破晓', '暴烈之甲'];
    let p2Names = ['急速战靴', '末世', '影刃', '破晓', '纯净苍穹', '暴烈之甲'];
    const p1Items = resolveItems(p1Names);
    const p2Items = resolveItems(p2Names);
    return [
      { id: 'farm_1', title: '王者推荐·暴击穿透流', genre: '暴击穿透流', desc: '无尽破晓高暴击高穿透，后期普攻持续爆发极强。', itemNames: p1Names, items: p1Items },
      { id: 'farm_2', title: '王者推荐·法球容错流', genre: '法球容错流', desc: '末世苍穹兼具百分比打肉伤害与进场减伤自保。', itemNames: p2Names, items: p2Items }
    ];
  }

  // 5. 对抗路及其他：战士/战坦体系（官方真实出装优先，排除打野刀和辅助装）
  if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
    const rawList = OFFICIAL_HERO_BUILDS[cname].filter(p => p.lane === '对抗路' || (!p.lane && !hasJungleBlade(p.item_names) && !hasRoamItem(p.item_names)));
    if (rawList.length > 0) {
      return rawList.map((p, idx) => {
        const items = resolveItems(p.item_names || []);
        const typeTitle = inferPresetTypeName(items, hero, p.desc, idx);
        return {
          id: p.id || `official_${idx + 1}`,
          title: `王者推荐·${typeTitle}`,
          genre: typeTitle,
          desc: p.desc || '王者官方推荐对抗路实战配装。',
          itemNames: p.item_names || [],
          items
        };
      });
    }
  }

  // 对抗路通用 fallback
  let p1Names = ['抵抗之靴', '暗影战斧', '暴烈之甲', '纯净苍穹', '宗师之力', '永夜守护'];
  let p2Names = ['影忍之足', '红莲斗篷', '暗影战斧', '极寒风暴', '霸者重装', '魔女斗篷'];
  if (role.includes('坦克')) {
    p1Names = ['影忍之足', '红莲斗篷', '暗影战斧', '暴烈之甲', '霸者重装', '魔女斗篷'];
    p2Names = ['极寒风暴', '影忍之足', '红莲斗篷', '不祥征兆', '魔女斗篷', '霸者重装'];
  }
  const p1Items = resolveItems(p1Names);
  const p2Items = resolveItems(p2Names);
  return [
    { id: 'clash_1', title: '王者推荐·半肉战阵流', genre: '半肉战阵流', desc: '攻守兼备，切入后排威慑力强，肉搏对拼容错率高。', itemNames: p1Names, items: p1Items },
    { id: 'clash_2', title: '王者推荐·重装坦伤流', genre: '重装坦伤流', desc: '高额血量双抗壁垒，先手开团吸收全套爆发。', itemNames: p2Names, items: p2Items }
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
