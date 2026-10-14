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

window.CalcEngine = {
  calcBuildStats,
  calcComboOutcome,
  calcSkillCooldowns,
  calcStatDiffs
};

