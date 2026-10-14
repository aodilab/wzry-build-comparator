// 王者出装推演 · 连招实战伤害与打野耗时引擎
// 严谨实战连招与伤害推演 (支持物理/法术/射手暴击/坦克真伤全职业自适应)
function calcComboOutcome(comboOrHero, stats, comboKeysOrHero) {
  let totPhysDmg = 0, totMagicDmg = 0, totTrueDmg = 0, ccDuration = 0;
  let hasEnhancedBasic = false, isElectrified = false, electroHitsLeft = 0;
  let triggerStrongAttack = false;
  let skillHitsCount = 0;

  let rawComboKeys = "13A2A", hero = null;
  if (typeof comboOrHero === 'object' && comboOrHero && (comboOrHero.keys || comboOrHero.title)) {
    rawComboKeys = comboOrHero.keys || comboOrHero.title;
    hero = comboKeysOrHero;
  } else if (comboOrHero && comboOrHero.cname) {
    hero = comboOrHero;
    rawComboKeys = typeof comboKeysOrHero === 'string' ? comboKeysOrHero : (comboKeysOrHero && (comboKeysOrHero.keys || comboKeysOrHero.title) ? (comboKeysOrHero.keys || comboKeysOrHero.title) : "13A2A");
  }
  const validKeyMatch = String(rawComboKeys || "13A2A").toUpperCase().match(/[123A]/g);
  const comboKeys = (validKeyMatch && validKeyMatch.length > 0) ? validKeyMatch.join('') : "13A2A";

  const cname = (hero && hero.cname) || "";
  const role = (hero && hero.role) || "";
  const isZhaoYun = (cname === "赵云");
  const isYangJian = (cname === "杨戬");
  const isLvBu = (cname === "吕布");
  const isMarksman = role.includes("射手");
  const isMage = !isMarksman && (role.includes("法师") || stats.ap > stats.atk * 0.8);

  // 暴击期望系数与攻速帧率加成
  const critMult = 1 + (stats.critRate / 100) * ((stats.critEff - 100) / 100);
  const aspeedBonusFactor = isMarksman ? (1 + stats.aspeed / 260) : (1 + stats.aspeed / 400);

  for (let ch of comboKeys) {
    if (ch === '1') {
      skillHitsCount++;
      if (isLvBu) {
        totTrueDmg += (1200 + stats.atk * 1.9);
      } else if (isMage) {
        totMagicDmg += (560 + stats.ap * 0.85);
      } else {
        const d = isYangJian ? (300 + stats.atk * 0.9) : (isZhaoYun ? (315 + stats.atk * 1.0) : (350 + stats.atk * 0.85));
        totPhysDmg += d;
      }
      hasEnhancedBasic = true;
      triggerStrongAttack = true;
      if (isElectrified && electroHitsLeft > 0) {
        totMagicDmg += (75 + stats.atk * 0.13);
        electroHitsLeft--;
      }
    } else if (ch === '2') {
      skillHitsCount++;
      if (isMage) {
        totMagicDmg += (480 + stats.ap * 0.72);
        ccDuration += 0.75;
      } else if (isYangJian) {
        totPhysDmg += (400 + stats.atk * 1.0);
        totTrueDmg += (120 + stats.atk * 0.35) * 2;
        ccDuration += 0.5;
      } else {
        const hits = isZhaoYun ? 4 : 1;
        const dPerHit = isZhaoYun ? (195 + stats.atk * 0.48) : (280 + stats.atk * 0.65);
        for (let h = 0; h < hits; h++) {
          totPhysDmg += dPerHit;
          if (isElectrified && electroHitsLeft > 0) {
            totMagicDmg += (75 + stats.atk * 0.13);
            electroHitsLeft--;
          }
        }
      }
      triggerStrongAttack = true;
    } else if (ch === '3') {
      skillHitsCount++;
      if (isLvBu) {
        totTrueDmg += (800 + stats.atk * 1.2);
        ccDuration += 1.0;
      } else if (isMage) {
        totMagicDmg += (1150 + stats.ap * 1.35);
      } else {
        const d = isYangJian ? (350 + stats.atk * 0.8) * 3 : (isZhaoYun ? (550 + stats.atk * 1.30) : (800 + stats.atk * 1.40));
        totPhysDmg += d;
        ccDuration += 1.0;
        if (isZhaoYun) {
          isElectrified = true;
          electroHitsLeft = 6;
        }
      }
      triggerStrongAttack = true;
    } else if (ch === 'A') {
      let basicDmg = hasEnhancedBasic ? (isZhaoYun ? (110 + stats.atk * 1.35) : (stats.atk * 1.35)) : (stats.atk * 1.0);
      hasEnhancedBasic = false;

      if (isLvBu) {
        totTrueDmg += basicDmg * critMult * aspeedBonusFactor;
      } else {
        basicDmg = basicDmg * critMult * aspeedBonusFactor;
        if (stats.hasDaybreak) basicDmg += (isMarksman ? 50 : 25) * critMult * aspeedBonusFactor;
        if (stats.hasMoShi) basicDmg += 220 * aspeedBonusFactor;
        if (triggerStrongAttack) {
          if (stats.hasMaster) basicDmg += (stats.atk * 0.80) * critMult;
          else if (stats.hasIce) basicDmg += 440;
          else if (stats.hasWushu) totMagicDmg += (360 + stats.ap * 0.40);
          triggerStrongAttack = false;
        }
        if (stats.hasDragon) basicDmg += (50 + stats.hp * 0.04);
        totPhysDmg += basicDmg;
      }

      if (stats.hasLightning) totMagicDmg += 140 * aspeedBonusFactor;
      if (stats.hasGoldenBlade) totMagicDmg += (60 + stats.ap * 0.30) * aspeedBonusFactor;
      if (isElectrified && electroHitsLeft > 0) {
        totMagicDmg += (75 + stats.atk * 0.13);
        electroHitsLeft--;
      }
    }
  }

  // 法术装备技能命中特效 (回响之杖 / 痛苦面具)
  let maskSquishyMagic = 0, maskTankMagic = 0;
  if (skillHitsCount > 0) {
    if (stats.hasEcho) {
      totMagicDmg += (280 + stats.ap * 0.28);
    }
    if (stats.hasMask) {
      maskSquishyMagic = 620;
      maskTankMagic = 1180;
    }
  }

  let dmgMult = 1.0;
  if (stats.hasDoomsdayArmor) dmgMult *= 1.10;
  if (stats.hasFenghuang) dmgMult *= 1.15;

  // 靶子一：【中射】(350 物防 / 180 法防)
  const effPdefSquishy = Math.max(0, (350 - stats.flatPen) * (1 - stats.percentPen));
  const drPhysSquishy = 602 / (602 + effPdefSquishy);
  const effMdefSquishy = Math.max(0, (180 - (stats.mFlatPen || 0)) * (1 - (stats.mPercentPen || 0)));
  const drMagicSquishy = 602 / (602 + effMdefSquishy);
  const dmgSquishy = Math.round((totPhysDmg * drPhysSquishy + (totMagicDmg + maskSquishyMagic) * drMagicSquishy + totTrueDmg) * dmgMult);

  // 靶子二：【坦克】(1000 物防 / 500 法防)
  const effPdefTank = Math.max(0, (1000 - stats.flatPen) * (1 - stats.percentPen));
  const drPhysTank = 602 / (602 + effPdefTank);
  const effMdefTank = Math.max(0, (500 - (stats.mFlatPen || 0)) * (1 - (stats.mPercentPen || 0)));
  const drMagicTank = 602 / (602 + effMdefTank);
  const dmgTank = Math.round((totPhysDmg * drPhysTank + (totMagicDmg + maskTankMagic) * drMagicTank + totTrueDmg) * dmgMult);

  // 生存与续航计算 (兼容物理吸血与法师法术吸血)
  const physVampHit = Math.round(stats.atk * critMult * (stats.pLifesteal / 100));
  const magicVampHit = Math.round((300 + stats.ap * 0.65) * (stats.mLifesteal / 100));
  const aHitVamp = isMage ? Math.max(physVampHit, magicVampHit) : physVampHit;

  let healDef = "核心技能回复";
  let regularHeal = 0;
  if (isZhaoYun) {
    healDef = "【2技能·破云之龙】回血";
    regularHeal = Math.round((120 + stats.atk * 0.15 + stats.hp * 0.02) * 4);
  } else if (isYangJian) {
    healDef = "【大招·根源之目】回血";
    regularHeal = Math.round(300 + stats.atk * 0.5 + stats.hp * 0.03) * 3;
  } else if (isMage) {
    regularHeal = Math.round(stats.hp * 0.08 + stats.ap * 0.35 + 180);
  } else {
    regularHeal = Math.round(stats.hp * 0.10 + stats.atk * 0.25 + 200);
  }
  let clutchHeal = stats.hasPhoenixEye ? Math.round(regularHeal * 1.42) : regularHeal;

  // 脱战每秒常态生命回复 (霸者重装 4%HP, 不死鸟 20点/s)
  let outOfCombatRegen = Math.round(25 + stats.hp * 0.005);
  if (stats.hasBazhe) outOfCombatRegen += Math.round(stats.hp * 0.04);
  if (stats.hasPhoenixEye) outOfCombatRegen += 20;

  // 有效物理/法术承伤上限 (EHP)
  const ehpPhys = Math.round(stats.hp * (1 + stats.pdef / 602));
  const ehpMagic = Math.round(stats.hp * (1 + stats.mdef / 602));
  let supportUtility = 0;
  if (cname === "张飞") supportUtility = Math.round(1500 + stats.hp * 0.08);
  else if (cname === "蔡文姬") supportUtility = Math.round(stats.ap * 2.5 + 4500);
  else supportUtility = Math.round(stats.hp * 0.08 + stats.ap * 0.40);

  // PVE 野区清理与控龙测算 (对齐 index.html，支持物理/法术/肉刀/末世/强击被动)
  const effBuffDef = Math.max(0, (200 - stats.flatPen) * (1 - stats.percentPen));
  const drBuff = 602 / (602 + effBuffDef);
  const effDragonDef = Math.max(0, (350 - stats.flatPen) * (1 - stats.percentPen));
  const drDragon = 602 / (602 + effDragonDef);

  const effBuffMdef = Math.max(0, (150 - (stats.mFlatPen || 0)) * (1 - (stats.mPercentPen || 0)));
  const drBuffMagic = 602 / (602 + effBuffMdef);
  const effDragonMdef = Math.max(0, (250 - (stats.mFlatPen || 0)) * (1 - (stats.mPercentPen || 0)));
  const drDragonMagic = 602 / (602 + effDragonMdef);

  const knifeMult = stats.knifeTier >= 2 ? 1.60 : (stats.knifeTier === 1 ? 1.25 : 1.0);
  const punishDmg = stats.knifeTier >= 3 ? 2800 : (stats.knifeTier === 2 ? 2400 : (stats.knifeTier === 1 ? 1600 : 0));
  const burstActionTime = 2.2;
  const pveBurstRatio = Math.min(1.0, 4.0 / Math.max(1, comboKeys.length)) * 0.72;
  const burstBuffDmg = Math.round((totPhysDmg * drBuff + totMagicDmg * drBuffMagic + totTrueDmg) * pveBurstRatio * knifeMult);
  const burstDragonDmg = Math.round((totPhysDmg * drDragon + totMagicDmg * drDragonMagic + totTrueDmg) * pveBurstRatio * knifeMult);

  const cycleCd = Math.max(3.5, 6.0 * (1 - stats.cdr / 100));
  const atkSpeedFactor = 0.70 + stats.aspeed / 100;
  const sustainedSkillBuff = ((totPhysDmg * drBuff + totMagicDmg * drBuffMagic + totTrueDmg) * pveBurstRatio * 0.55 * knifeMult) / cycleCd;
  const sustainedSkillDragon = ((totPhysDmg * drDragon + totMagicDmg * drDragonMagic + totTrueDmg) * pveBurstRatio * 0.55 * knifeMult) / cycleCd;
  const basicDpsBuff = stats.atk * critMult * atkSpeedFactor * drBuff * knifeMult;
  const basicDpsDragon = stats.atk * critMult * atkSpeedFactor * drDragon * knifeMult;

  // 装备特效持续秒伤 (强击周期、肉刀/蓝刀灼烧、怒龙剑盾、末世、电刀、圣剑)
  let extraBuff = 0;
  let extraDragon = 0;
  if (stats.hasMaster) {
    extraBuff += (stats.atk * 0.80 * drBuff * knifeMult) / 2.5;
    extraDragon += (stats.atk * 0.80 * drDragon * knifeMult) / 2.5;
  } else if (stats.hasIce) {
    extraBuff += (440 * drBuff * knifeMult) / 2.0;
    extraDragon += (440 * drDragon * knifeMult) / 2.0;
  } else if (stats.hasWushu) {
    extraBuff += ((360 + stats.ap * 0.40) * drBuffMagic * knifeMult) / 2.5;
    extraDragon += ((360 + stats.ap * 0.40) * drDragonMagic * knifeMult) / 2.5;
  }
  if (stats.knifeType === 'meat' || stats.knifeType === 'ap') {
    extraBuff += 300;
    extraDragon += 300;
  }
  if (stats.hasDragon) {
    extraBuff += ((50 + stats.hp * 0.03) * drBuff * knifeMult) / 2.0;
    extraDragon += ((50 + stats.hp * 0.03) * drDragon * knifeMult) / 2.0;
  }
  if (stats.hasMoShi) {
    extraBuff += 100 * atkSpeedFactor * drBuff * knifeMult;
    extraDragon += 100 * atkSpeedFactor * drDragon * knifeMult;
  }
  if (stats.hasGoldenBlade) {
    extraBuff += (60 + stats.ap * 0.30) * atkSpeedFactor * drBuffMagic * knifeMult;
    extraDragon += (60 + stats.ap * 0.30) * atkSpeedFactor * drDragonMagic * knifeMult;
  }

  const sustainedDpsBuff = Math.max(350, (sustainedSkillBuff + basicDpsBuff + extraBuff) * dmgMult);
  const sustainedDpsDragon = Math.max(350, (sustainedSkillDragon + basicDpsDragon + extraDragon) * dmgMult);

  const totBurstBuff = burstBuffDmg + punishDmg;
  let buffTime = 0;
  if (totBurstBuff >= 12000) {
    buffTime = +(Math.max(0.8, burstActionTime * (12000 / totBurstBuff))).toFixed(1);
  } else {
    buffTime = +(burstActionTime + ((12000 - totBurstBuff) / sustainedDpsBuff)).toFixed(1);
  }
  const totBurstDragon = burstDragonDmg + punishDmg;
  const remainDragonHp = Math.max(0, 35000 - totBurstDragon);
  const dragonTime = +(burstActionTime + (remainDragonHp / sustainedDpsDragon)).toFixed(1);

  return {
    totPhysDmg, totMagicDmg, totTrueDmg, ccDuration,
    dmgSquishy, dmgTank,
    healDef, regularHeal, clutchHeal, aHitVamp, outOfCombatRegen,
    buffTime, dragonTime, ehpPhys, ehpMagic, supportUtility
  };
}


module.exports = { calcComboOutcome };
