const { buildCustomHeroCards, buildGeneralHeroCards } = require('./skill_breakdown_cards.js');
// 王者出装推演 ｜ 各技能全维物理拆解二级视窗引擎 (1:1 复刻 preview_miniprogram.html)

const SUBTITLE_MAP = [
  ['物理承伤上限', '极限物理承伤', '物理EHP (防具折算)'],
  ['法术承伤上限', '极限法术承伤', '法术EHP (防具折算)'],
  ['终极真血护盾吸收量', '终极大招护盾', '40%最大生命值吸收'],
  ['绝境急救', '绝境急救回复', '血量≤30% · 不死鸟增幅'],
  ['最大生命值上限', '最大生命上限', '基础体质+装备铭文'],
  ['辅助装主动技能', '辅助装主动', '局内主动技能'],
  ['团队常驻防御光环', '团队防御光环', '全队常驻增益'],
  ['移动速度', '实战移动速度', '转线支援跑图'],
  ['普攻频次', '实际普攻频次', '攻速档位折算'],
  ['强击与法术特效', '强击法术特效', '被动机制协同'],
  ['强化与法术特效', '强击法术特效', '被动机制协同'],
  ['强击与特效机制', '强击被动特效', '装备机制协同'],
  ['单发普攻吸血', '普攻物理吸血', '单发吸血回复'],
  ['单次普攻吸血', '普攻物理吸血', '单发吸血回复'],
  ['单发技能法术吸血', '技能法术吸血', '单发吸血回复'],
  ['附带减速软控', '减速留人软控', '技能+冰痕被动'],
  ['抽取护盾', '抽取护盾上限', '最大护盾吸收量'],
  ['护盾转化', '护盾转化回复', '护盾转生命值']
];

function fmtVal(v, unit = '') {
  if (typeof v === 'number') {
    const numStr = (v % 1 === 0) ? String(Math.round(v)) : v.toFixed(1);
    return (unit === 's' ? v.toFixed(1) : numStr) + unit;
  }
  return v;
}

function renderDiffBadge(valA, valB, unit = '', lowerIsBetter = false) {
  if (typeof valA === 'number' && typeof valB === 'number') {
    const diff = valB - valA;
    if (Math.abs(diff) < 0.01) return { aWins: false, bWins: false, badgeA: '', badgeB: '' };
    const isBetterB = lowerIsBetter ? (diff < 0) : (diff > 0);
    const diffAbs = Math.abs(diff).toFixed(diff % 1 === 0 ? 0 : 1);
    const prefix = lowerIsBetter ? '-' : '+';
    if (isBetterB) {
      return { aWins: false, bWins: true, badgeA: '', badgeB: `${prefix}${diffAbs}${unit}` };
    } else {
      return { aWins: true, bWins: false, badgeA: `${prefix}${diffAbs}${unit}`, badgeB: '' };
    }
  }
  return { aWins: false, bWins: false, badgeA: '', badgeB: '' };
}

function formatSkillBadge(base, mechTag = '') {
  const bStr = typeof base === 'number' ? base.toFixed(1).replace(/\.0$/, '') : String(base).replace(/\.0$/, '');
  return mechTag ? `${mechTag} · 初CD ${bStr}s` : `初始CD ${bStr}s`;
}

function formatEffectLabel(s) {
  if (s.hasDragon) {
    if (s.hasMaster) return '宗师 + 怒龙';
    if (s.hasIce) return '冰痕 + 怒龙';
    if (s.hasWushu) return '巫术 + 怒龙';
    return '平A + 怒龙';
  }
  if (s.hasMaster) return '宗师强击';
  if (s.hasIce) return '冰痕强击';
  if (s.hasWushu) return '巫术强击';
  return '常规平A';
}

function createRowBuilder() {
  let pendingRow = null;
  const rows = [];

  const pushDual = (title, sqA, sqB, tkA, tkB, unit = '') => {
    const resSq = renderDiffBadge(sqA, sqB, unit, false);
    const resTk = { aWins: false, bWins: false, badgeA: '', badgeB: '' };
    rows.push({
      isDual: true,
      title,
      sub: '中射 / 坦克',
      sqA: fmtVal(sqA, unit),
      sqB: fmtVal(sqB, unit),
      tkA: fmtVal(tkA, unit),
      tkB: fmtVal(tkB, unit),
      resSq,
      resTk
    });
  };

  const pushSingle = (name, valA, valB, unit = '', lowerIsBetter = false) => {
    let mainTitle = name;
    let subTitle = '';
    if (mainTitle.includes('(真实伤害)')) {
      mainTitle = mainTitle.replace('(真实伤害)', '').trim();
      subTitle = '真实伤害 · 穿透护甲';
    } else if (mainTitle.includes('(无视坦克护甲)')) {
      mainTitle = mainTitle.replace('(无视坦克护甲)', '').trim();
      subTitle = '对坦克 · 真实伤害';
    } else if (mainTitle.includes('护盾庇护吸收量') && !mainTitle.includes('终极真血')) {
      const p = mainTitle.replace('护盾庇护吸收量', '').trim();
      mainTitle = p ? `${p}护盾` : '护盾庇护量';
      subTitle = '实战吸收总量';
    } else if (mainTitle.includes('生命回复总量')) {
      const p = mainTitle.replace('生命回复总量', '').trim();
      mainTitle = p ? `${p}回复` : '生命回复量';
      subTitle = '实战治疗总量';
    } else if (mainTitle.includes('(中射)')) {
      mainTitle = mainTitle.replace('(中射)', '').trim();
      subTitle = '对中射 · 350物防';
    } else if (mainTitle.includes('(坦克)')) {
      mainTitle = mainTitle.replace('(坦克)', '').trim();
      subTitle = '对坦克 · 1000物防';
    } else {
      for (const [k, m, s] of SUBTITLE_MAP) {
        if (mainTitle.includes(k)) {
          mainTitle = m;
          subTitle = s;
          break;
        }
      }
    }
    const res = renderDiffBadge(valA, valB, unit, lowerIsBetter);
    rows.push({
      isDual: false,
      mainTitle,
      subTitle,
      valA: fmtVal(valA, unit),
      valB: fmtVal(valB, unit),
      res
    });
  };

  const flush = () => {
    if (pendingRow) {
      const r = pendingRow;
      pendingRow = null;
      pushSingle(r.name, r.valA, r.valB, r.unit, r.lowerIsBetter);
    }
  };

  const add = (name, valA, valB, unit = '', lowerIsBetter = false) => {
    const isSq = name.includes('(中射)') || name.includes('（中射）');
    const isTk = name.includes('(坦克)') || name.includes('（坦克）');
    if (isSq) {
      flush();
      pendingRow = { name, valA, valB, unit, lowerIsBetter };
      return;
    }
    if (isTk && pendingRow) {
      const baseName = name.replace(/[(（]坦克[)）]/g, '').trim();
      const prevBase = pendingRow.name.replace(/[(（]中射[)）]/g, '').trim();
      if (baseName === prevBase) {
        const prev = pendingRow;
        pendingRow = null;
        pushDual(baseName, prev.valA, prev.valB, valA, valB, unit);
        return;
      }
    }
    flush();
    pushSingle(name, valA, valB, unit, lowerIsBetter);
  };

  const finish = () => {
    flush();
    return rows;
  };

  return { add, finish };
}

function buildSkillDetailData(h, currentLane, sA, sB, heroSkills, attackIconUrl) {
  const isSupport = currentLane === '游走' || (h.role && h.role.includes('辅助'));
  const isMarksman = !isSupport && (currentLane === '发育路' || (h.role && h.role.includes('射手')));
  const isMage = !isSupport && !isMarksman && (currentLane === '中路' || (h.role && h.role.includes('法师')));

  const benchmarkHint = isMage
    ? '基准防御：后排 180 法抗 ｜ 前排 500 法抗'
    : (isSupport ? '基准对决：团队光环 ｜ 护盾治疗 ｜ 承伤极限' : '基准防御：后排 350 物防 ｜ 前排 1000 物防');

  const drSqPA = 602 / (602 + Math.max(0, (350 - sA.flatPen) * (1 - sA.percentPen)));
  const drSqPB = 602 / (602 + Math.max(0, (350 - sB.flatPen) * (1 - sB.percentPen)));
  const drTkPA = 602 / (602 + Math.max(0, (1000 - sA.flatPen) * (1 - sA.percentPen)));
  const drTkPB = 602 / (602 + Math.max(0, (1000 - sB.flatPen) * (1 - sB.percentPen)));

  const drSqMA = 602 / (602 + Math.max(0, (180 - sA.mFlatPen) * (1 - sA.mPercentPen)));
  const drSqMB = 602 / (602 + Math.max(0, (180 - sB.mFlatPen) * (1 - sB.mPercentPen)));
  const drTkMA = 602 / (602 + Math.max(0, (500 - sA.mFlatPen) * (1 - sA.mPercentPen)));
  const drTkMB = 602 / (602 + Math.max(0, (500 - sB.mFlatPen) * (1 - sB.mPercentPen)));

  let multA = 1.0;
  if (sA.hasDoomsdayArmor) multA *= 1.10;
  if (sA.hasFenghuang) multA *= 1.15;
  let multB = 1.0;
  if (sB.hasDoomsdayArmor) multB *= 1.10;
  if (sB.hasFenghuang) multB *= 1.15;

  const sheenA = sA.hasMaster ? (sA.atk * 0.8) : (sA.hasIce ? 440 : (sA.hasWushu ? sA.ap * 0.7 : 0));
  const dragonA = sA.hasDragon ? (50 + sA.hp * 0.04) : 0;
  const sheenB = sB.hasMaster ? (sB.atk * 0.8) : (sB.hasIce ? 440 : (sB.hasWushu ? sB.ap * 0.7 : 0));
  const dragonB = sB.hasDragon ? (50 + sB.hp * 0.04) : 0;

  const effectA = formatEffectLabel(sA);
  const effectB = formatEffectLabel(sB);

  const normSqA = Math.round(sA.atk * multA * drSqPA);
  const normSqB = Math.round(sB.atk * multB * drSqPB);
  const normTkA = Math.round(sA.atk * multA * drTkPA);
  const normTkB = Math.round(sB.atk * multB * drTkPB);

  const skUrl = (suffix) => `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}${suffix}.png`;
  const cards = [];

  const addCard = (icon, isAttack, title, badge, builderFn) => {
    const rb = createRowBuilder();
    builderFn(rb.add);
    cards.push({ icon, isAttack, title, badge, rows: rb.finish() });
  };

  if (h.cname === '赵云') {
    const rawSwA = 110 + sA.atk * 1.35 + sheenA + dragonA;
    const rawSwB = 110 + sB.atk * 1.35 + sheenB + dragonB;
    const vampA = Math.round(sA.atk * (sA.pLifesteal / 100));
    const vampB = Math.round(sB.atk * (sB.pLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 基础平A与横扫强化', '强击·横扫', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      add('强化横扫 (中射)', Math.round(rawSwA * multA * drSqPA), Math.round(rawSwB * multB * drSqPB));
      add('强化横扫 (坦克)', Math.round(rawSwA * multA * drTkPA), Math.round(rawSwB * multB * drTkPB));
      if (vampA > 0 || vampB > 0) add('单次普攻吸血', vampA, vampB, ' 点');
      add('强击与特效机制', effectA, effectB);
    });
    const cd1A = +(5.0 * (1 - sA.cdr / 100)).toFixed(1), cd1B = +(5.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('10'), false, '1技能 · 惊雷之龙', formatSkillBadge(5.0, '重置普攻'), (add) => {
      add('冲锋突进 (中射)', Math.round((315 + sA.atk * 1.0) * multA * drSqPA), Math.round((315 + sB.atk * 1.0) * multB * drSqPB));
      add('冲锋突进 (坦克)', Math.round((315 + sA.atk * 1.0) * multA * drTkPA), Math.round((315 + sB.atk * 1.0) * multB * drTkPB));
      if (sA.hasIce || sB.hasIce) {
        add('附带减速软控', sA.hasIce ? '50%减速 + 冰痕' : '50%减速', sB.hasIce ? '50%减速 + 冰痕' : '50%减速');
      }
      add('实战技能冷却', cd1A, cd1B, 's', true);
    });
    const cd2A = +(4.0 * (1 - sA.cdr / 100)).toFixed(1), cd2B = +(4.0 * (1 - sB.cdr / 100)).toFixed(1);
    const hNA = Math.round(4 * (120 + sA.atk * 0.15 + sA.hp * 0.02)), hNB = Math.round(4 * (120 + sB.atk * 0.15 + sB.hp * 0.02));
    addCard(skUrl('20'), false, '2技能 · 破云之龙', formatSkillBadge(4.0, '4段回血'), (add) => {
      add('4段刺击总伤 (中射)', Math.round(4 * (195 + sA.atk * 0.48) * multA * drSqPA), Math.round(4 * (195 + sB.atk * 0.48) * multB * drSqPB));
      add('4段刺击总伤 (坦克)', Math.round(4 * (195 + sA.atk * 0.48) * multA * drTkPA), Math.round(4 * (195 + sB.atk * 0.48) * multB * drTkPB));
      add('常态生命回复量', hNA, hNB, ' 点');
      if (sA.hasPhoenixEye || sB.hasPhoenixEye) {
        add('绝境急救(≤30%血)', sA.hasPhoenixEye ? Math.round(hNA * 1.42) : hNA, sB.hasPhoenixEye ? Math.round(hNB * 1.42) : hNB, ' 点');
      }
      add('实战技能冷却', cd2A, cd2B, 's', true);
    });
    const cd3A = +(12.0 * (1 - sA.cdr / 100)).toFixed(1), cd3B = +(12.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('30'), false, '3技能 · 天翔之龙', formatSkillBadge(12.0, '击飞1.0s'), (add) => {
      add('跃击砸地 (中射)', Math.round((550 + sA.atk * 1.30) * multA * drSqPA), Math.round((550 + sB.atk * 1.30) * multB * drSqPB));
      add('跃击砸地 (坦克)', Math.round((550 + sA.atk * 1.30) * multA * drTkPA), Math.round((550 + sB.atk * 1.30) * multB * drTkPB));
      add('感电6次法伤 (中射)', Math.round(6 * (75 + sA.atk * 0.13) * multA * drSqMA), Math.round(6 * (75 + sB.atk * 0.13) * multB * drSqMB));
      add('感电6次法伤 (坦克)', Math.round(6 * (75 + sA.atk * 0.13) * multA * drTkMA), Math.round(6 * (75 + sB.atk * 0.13) * multB * drTkMB));
      add('实战技能冷却', cd3A, cd3B, 's', true);
    });
  } else if (h.cname === '孙尚香' || h.cname === '李白' || h.cname === '吕布') {
    buildCustomHeroCards(h, sA, sB, multA, multB, drSqPA, drSqPB, drTkPA, drTkPB, normSqA, normSqB, normTkA, normTkB, sheenA, sheenB, effectA, effectB, attackIconUrl, skUrl, addCard);
  } else {
    buildGeneralHeroCards(h, isMarksman, isMage, isSupport, sA, sB, multA, multB, drSqPA, drSqPB, drTkPA, drTkPB, drSqMA, drSqMB, drTkMA, drTkMB, normSqA, normSqB, normTkA, normTkB, effectA, effectB, heroSkills, attackIconUrl, skUrl, addCard);
  }

  return { benchmarkHint, cards };
}

module.exports = {
  buildSkillDetailData
};
