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

  // 1. 优先读取官方提取的真实分路出装与强绑定铭文 (SSOT 单一事实来源)
  if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
    const hData = OFFICIAL_HERO_BUILDS[cname];
    let presets = [];
    if (hData.lanes && hData.lanes[lane]) {
      presets = hData.lanes[lane];
    } else if (Array.isArray(hData)) {
      presets = hData.filter(p => !p.lane || p.lane === lane);
    }
    if (presets && presets.length > 0) {
      return presets.map((p, idx) => {
        const items = resolveItems(p.item_names || p.items);
        const tag = p.tag || '推荐';
        const genre = p.genre || p.name || `推荐方案${idx + 1}`;
        const title = p.title || `【${tag}】${genre}`;
        return {
          id: p.id || `preset_${idx + 1}`,
          tag: tag,
          genre: genre,
          title: title,
          desc: p.desc || '王者官方推荐出装与专属铭文。',
          itemNames: p.item_names || p.items || [],
          items: items,
          arcana: p.arcana || null,
          arcana_desc: p.arcana_desc || ''
        };
      });
    }
  }

  // 2. 若分路为【打野】：必须包含打野刀体系！
  if (lane === '打野') {
    if (typeof OFFICIAL_HERO_BUILDS !== 'undefined' && OFFICIAL_HERO_BUILDS[cname]) {
      const jungleOfficial = Array.isArray(OFFICIAL_HERO_BUILDS[cname]) 
        ? OFFICIAL_HERO_BUILDS[cname].filter(p => p.lane === '打野' || hasJungleBlade(p.item_names))
        : [];
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

