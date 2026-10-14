// ==============================================================================
// 局内六神装配装战术协同评估引擎 (Synergy Evaluator Engine)
// 依据英雄职业定位与技能伤害乘区，智能识别出装战术流派，输出实战优劣势剖析(PROS/CONS)
// ==============================================================================

function calculateSynergyScore(currentHero, effItems, currentSlots, skills, cappedCdr) {
  currentHero = currentHero || {};
  effItems = effItems || [];
  currentSlots = currentSlots || [];
  skills = skills || [];
  cappedCdr = cappedCdr || 0;

  const heroRole = currentHero.role || '';
  const heroName = currentHero.cname || '';
  const heroLane = currentHero.lane || '';
  const isPhysicalHero = ['战士', '刺客', '射手'].some(r => heroRole.includes(r)) && !['司空震', '芈月'].includes(heroName);
  const isMagicHero = heroRole.includes('法师') && !['司空震', '嬴政'].includes(heroName);
  const isTankOrSupport = heroRole.includes('坦克') || heroRole.includes('辅助') || heroLane === '对抗路' || heroLane === '游走';

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
  const hasFaChuan = slotNames.includes('虚无法杖') || slotNames.includes('日暮之流');
  const hasMaozi = slotNames.includes('博学者之怒');
  const hasHuiyue = slotNames.includes('辉月');
  const hasLifesteal = slotNames.includes('泣血之刃') || slotNames.includes('末世') || slotNames.includes('噬神之书') || slotNames.includes('贪婪之噬') || hasHuangdun || hasPhoenix || hasBazhe;
  const hasArmorPen = hasAnyang || hasPoxiao || slotNames.includes('碎星锤') || slotNames.includes('破魔刀');
  const hasDamageReduce = hasCangqiong || slotNames.includes('天穹') || hasHuiyue || slotNames.includes('名刀·司命') || slotNames.includes('贤者的庇护');

  // ==========================================
  // 1. 战术流派智能定性 (按职业定位与核心出装分类)
  // ==========================================
  let tacticGenre = '常规平衡流派';
  let genreDesc = '装备攻守兼顾，具备基础战术周转能力。';
  let genreColor = '#0071e3';

  if (heroRole.includes('射手') || heroLane === '发育路') {
    if (totalCrit >= 35) {
      tacticGenre = '暴击穿透流';
      genreDesc = '核心依靠普攻暴击与破晓高额穿甲打出致命物理爆发，点杀后排与撕裂前排兼备。';
      genreColor = '#ff9500';
    } else if (slotNames.includes('末世') || slotNames.includes('影刃')) {
      tacticGenre = '高频法球攻速流';
      genreDesc = '依靠高攻速持续附带百分比生命物理伤害，对线拉扯与持续压制前排能力极强。';
      genreColor = '#af52de';
    } else {
      tacticGenre = '破甲持续输出流';
      genreDesc = '以破甲与基础攻速为主，注重稳定走A消耗与安全距离输出。';
      genreColor = '#0071e3';
    }
  } else if (heroRole.includes('法师') || heroLane === '中路') {
    if (totalAp >= 600 || hasMaozi) {
      tacticGenre = '法核高爆发流';
      genreDesc = '超高法强搭配百分比法穿，技能法球爆发极为夸张，具备远距离一套瞬秒脆皮能力。';
      genreColor = '#af52de';
    } else if (slotNames.includes('痛苦面具') || slotNames.includes('凝冰之息') || slotNames.includes('日暮之流')) {
      tacticGenre = '面具冰杖拉扯消耗流';
      genreDesc = '依靠多段技能触发持续灼烧法伤与范围减速，团战拉扯控场与消耗折磨极强。';
      genreColor = '#0071e3';
    } else {
      tacticGenre = '功能工具人流';
      genreDesc = '偏向技能冷却与团队控制，利用高频技能为队友打出控制链与开视野。';
      genreColor = '#34c759';
    }
  } else if (heroRole.includes('坦克') || (heroRole.includes('辅助') && totalBonusHp >= 3500)) {
    if (hasHonglian && totalBonusHp >= 4500) {
      tacticGenre = '重装灼烧肉坦流';
      genreDesc = '超高双抗与高额血量构筑钢铁防线，贴脸持续灼烧附带重伤，肉搏吃满集火。';
      genreColor = '#34c759';
    } else {
      tacticGenre = '前排钢铁壁垒流';
      genreDesc = '全套双抗与血量拉满，充当团队第一承伤支柱，为后排创造安全输出环境。';
      genreColor = '#34c759';
    }
  } else if (heroRole.includes('刺客') || (heroLane === '打野' && totalAd >= 240)) {
    tacticGenre = '野区收割突刺流';
    genreDesc = '纯攻击与破甲拉满，专注野区经济滚雪球与团战侧翼切入瞬秒敌方核心输出。';
    genreColor = '#ff3b30';
  } else {
    // 战士/对抗路
    if (totalBonusHp >= 2000 && totalAd >= 130) {
      tacticGenre = '半肉战阵突进流';
      genreDesc = '攻守平衡兼具抗伤与后排突进威胁，团战进可强切C位退可抗伤保护阵型。';
      genreColor = '#0071e3';
    } else if (totalBonusHp >= 4000) {
      tacticGenre = '重装战坦抗伤流';
      genreDesc = '偏向防守反击与前排抗压，利用英雄自身被动与高坦度打残血反杀。';
      genreColor = '#34c759';
    } else if (totalAd >= 250) {
      tacticGenre = '极限全输出刺客流';
      genreDesc = '极致物理爆发但身板较脆，高度依赖切入时机与连招瞬秒敌方后排。';
      genreColor = '#ff9500';
    }
  }

  // ==========================================
  // 2. 实战核心优势 (PROS - 按各职业核心关注维度直球输出)
  // ==========================================
  const pros = [];
  if (heroRole.includes('射手') || heroLane === '发育路') {
    if (totalCrit >= 35 && hasPoxiao) pros.push({ title: '暴击破晓穿透爆发', desc: '无尽搭配破晓形成物理输出质变，普攻撕裂前排，点杀后排爆发极高。' });
    if (slotNames.includes('泣血之刃') || slotNames.includes('末世')) pros.push({ title: '极强吸血续航拉满', desc: '装配核心吸血大件，残血能通过兵线瞬间补满，团战走A站撸持续提供高额输出。' });
    if (hasCangqiong || slotNames.includes('逐日之弓')) pros.push({ title: '自保拉扯容错极高', desc: hasCangqiong ? '纯净苍穹主动 35% 免伤，防刺客突脸瞬秒。' : '逐日之弓扩大普攻射程，安全距离走A消耗。' });
  } else if (heroRole.includes('法师') || heroLane === '中路') {
    if (totalAp >= 500 && (hasFaChuan || hasMaozi)) pros.push({ title: '法核超高爆发瞬秒', desc: '博学者之怒搭配法穿，技能法术伤害达到峰值，具备远距离一套瞬秒敌方脆皮的恐怖威慑。' });
    if (slotNames.includes('痛苦面具') || slotNames.includes('凝冰之息')) pros.push({ title: '面具冰杖减速折磨', desc: '多段技能持续触发当前生命百分比法伤与群体减速，团战大范围拉扯消耗与分割战场极强。' });
    if (hasHuiyue) pros.push({ title: '金身规避致命集火', desc: '辉月提供 1.5 秒无敌保命金身，关键时刻规避刺客强切与致命爆发技能。' });
  } else if (heroRole.includes('刺客') || (heroLane === '打野' && totalAd >= 200)) {
    if (hasArmorPen && totalAd >= 220) pros.push({ title: '物理穿透瞬秒脆皮', desc: '高额攻击叠加固定物穿，技能连招瞬间灌满伤害，后排露头即被秒杀。' });
    if (slotNames.includes('名刀·司命') || hasCangqiong) pros.push({ title: '进场保命脱身容错', desc: '装配名刀/苍穹免伤，进场强切 C 位时即便吃满反打也能规避暴毙，从容收割撤退。' });
    if (cappedCdr >= 20) pros.push({ title: '技能高频游走转线', desc: `冷却缩减达 ${cappedCdr}%，压缩位移与爆发技能冷却，野区控龙抓人节奏拉满。` });
  } else if (heroRole.includes('坦克') || heroRole.includes('辅助')) {
    if (totalBonusHp >= 3000 && (totalPdef + totalMdef) >= 550) pros.push({ title: '钢铁身板抗伤扎实', desc: `额外生命 +${totalBonusHp}，物法双抗加成 +${totalPdef + totalMdef}，前排抗击打能力极强。` });
    if (hasBuxiang) pros.push({ title: '减攻速移速克制射手', desc: '不祥征兆受到攻击大幅削弱敌方 40% 攻速与移速，极大破坏敌方后排输出节奏。' });
    if (hasHonglian) pros.push({ title: '近身肉搏灼烧重伤', desc: '红莲斗篷贴脸持续造成最大生命百分比法伤并附带重伤，强力限制敌方回复。' });
  } else {
    if (hasCangqiong) pros.push({ title: '进场免伤避免被秒', desc: '纯净苍穹提供 35% 高额免伤且受控可用，彻底避免进场突进切后排时被瞬间蒸发。' });
    if (totalBonusHp >= 2000 && (totalPdef + totalMdef) >= 350) pros.push({ title: '半肉双抗攻守兼备', desc: `血量提升 +${totalBonusHp}，双抗均衡，团战既能切入后排打满威胁，又能顶住阵型抗伤。` });
    if (hasPhoenix || hasHuangdun) pros.push({ title: '残血受愈绝地反打', desc: '不死鸟之眼大幅放大残血回复与护盾效益，对拼进入残血期具备极强的绝地反杀能力。' });
  }
  if (pros.length === 0) {
    if (cappedCdr >= 20) pros.push({ title: '冷却缩减高频循环', desc: `技能冷却缩减达 ${cappedCdr}%，大幅缩短技能真空期，多轮拉扯与技能反打极具主动权。` });
    else pros.push({ title: '基础三维属性均衡', desc: '装备提供扎实的基础面板增益，满足常规对局推演与平稳对线基准。' });
  }

  // ==========================================
  // 3. 实战潜在短板 (CONS - 按各职业最忌讳的硬伤直击痛点)
  // ==========================================
  const cons = [];
  if (heroRole.includes('射手') || heroLane === '发育路') {
    if (!hasPoxiao && !slotNames.includes('碎星锤')) cons.push({ title: '缺少破晓后期打不动前排', desc: '未装配破晓或百分比破甲大件，对局进入中后期打敌方上千护甲的前排犹如刮痧。' });
    if (!slotNames.includes('泣血之刃') && !slotNames.includes('末世')) cons.push({ title: '缺少吸血频繁回城断节奏', desc: '无续航吸血装备，被消耗残血后无法快速回血，被迫频繁回城容易漏线丢防御塔。' });
    if (totalBonusHp <= 800 && !hasCangqiong && !slotNames.includes('名刀·司命')) cons.push({ title: '全身无自保装容错极低', desc: '整套偏全输出身板极脆，一旦被敌方刺客或战刺突脸近身容易瞬间蒸发。' });
  } else if (heroRole.includes('法师') || heroLane === '中路') {
    if (!hasFaChuan && totalAp >= 350) cons.push({ title: '缺少法穿中后期被魔抗克制', desc: '未出虚无法杖或日暮之流，一旦敌方前排合成魔女斗篷或永夜守护，技能伤害衰减严重。' });
    if (!hasHuiyue && totalBonusHp <= 1000) cons.push({ title: '缺少金身防刺客强切弱', desc: '无辉月保命无敌金身且身板脆弱，被敌方刺客或战刺绕后切入时缺少反制规避手段。' });
    if (cappedCdr < 15) cons.push({ title: '冷却缩减不足消耗真空长', desc: `当前出装仅 ${cappedCdr}% 冷缩，关键控制与消耗技能真空期过长，团战打完一套后存在输出断档。` });
  } else if (heroRole.includes('刺客') || (heroLane === '打野' && totalAd >= 200)) {
    if (!slotNames.includes('名刀·司命') && !hasCangqiong && !slotNames.includes('贤者的庇护')) cons.push({ title: '缺少保命大件切入容错低', desc: '未做名刀或保命大件，团战切入如果吃到了反手控制或第一波AOE，极易被反秒。' });
    if (cappedCdr < 15) cons.push({ title: '冷却回转偏慢节奏真空长', desc: `仅 ${cappedCdr}% 冷缩，位移与大招冷却偏长，若一套未能成功击杀极难二次拉扯。` });
    if (totalMdef <= 120 && !hasPhoenix) cons.push({ title: '法抗偏低易吃AOE暴毙', desc: '无魔抗防御装，切入敌方法师范围伤害时极易被大范围法伤融化。' });
  } else if (heroRole.includes('坦克') || heroRole.includes('辅助')) {
    if (totalAd <= 90 && totalAp <= 100 && !hasHonglian) cons.push({ title: '纯肉无伤害单人收割乏力', desc: '整套偏纯肉防御，缺乏灼烧或输出数值，单人清兵线极慢且对残血脆皮毫无单杀威胁。' });
    if (totalPdef >= 600 && totalMdef <= 120) cons.push({ title: '魔抗严重偏低惧怕法核', desc: '物抗极高但未装配魔女斗篷或永夜守护，面对敌方法核法师输出时抗伤能力大打折扣。' });
    else if (totalMdef >= 400 && totalPdef <= 180) cons.push({ title: '物抗严重偏低惧怕物理切入', desc: '魔抗充裕但缺乏物抗大件，面对敌方射手或刺客的物理普攻撕裂时身板较脆弱。' });
  } else {
    if (totalBonusHp <= 1200 && (totalPdef + totalMdef) <= 220 && !hasCangqiong) cons.push({ title: '过度注重伤害缺少坦度', desc: '整套配装偏向纯攻击输出，身板极脆容错率偏低，切入稍有不慎或吃控制极易被秒。' });
    if (!hasLifesteal) cons.push({ title: '缺少回复续航对线吃亏', desc: '缺少吸血与续航装备，换血被打残后无法快速回血，被迫频繁回城补给漏线亏兵。' });
    if (cappedCdr < 15) cons.push({ title: '冷却缩减不足连招真空长', desc: `整套出装仅 ${cappedCdr}% 冷缩，关键技能交完后有数秒无技能空窗期，拉扯与反打能力受限。` });
  }
  if (bootsCount === 0 && totalPercentSpeed <= 0) cons.push({ title: '缺少鞋类成装机动滞后', desc: '未装配鞋类大件，基础移速偏低，极易被敌方长手减速拉扯，支援转线滞后。' });
  if (cons.length === 0) cons.push({ title: '装备造价偏高成型期长', desc: '整套配装多为高造价三级大件，前期过渡较吃经济运营，若逆风成型周期会被迫拉长。' });

  // 4. 五维能力雷达战力推演 (基于当前职业面板真实百分比)
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
    tacticGenre,
    genreDesc,
    genreColor,
    pros: pros.slice(0, 3),
    cons: cons.slice(0, 2),
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
