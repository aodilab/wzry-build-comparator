// 技能拆解弹窗 · 定制英雄与全职业通用技能卡片生成
function formatSkillBadge(base, mechTag = '') {
  const bStr = typeof base === 'number' ? base.toFixed(1).replace(/\.0$/, '') : String(base).replace(/\.0$/, '');
  return mechTag ? `${mechTag} · 初CD ${bStr}s` : `初始CD ${bStr}s`;
}

function buildCustomHeroCards(h, sA, sB, multA, multB, drSqPA, drSqPB, drTkPA, drTkPB, normSqA, normSqB, normTkA, normTkB, sheenA, sheenB, effectA, effectB, attackIconUrl, skUrl, addCard) {
  if (h.cname === '孙尚香') {
    const hpsA = 1 + sA.aspeed / 100, hpsB = 1 + sB.aspeed / 100;
    const cmA = 1 + (sA.critRate / 100) * ((sA.critEff - 100) / 100), cmB = 1 + (sB.critRate / 100) * ((sB.critEff - 100) / 100);
    const cSqA = Math.round(normSqA * cmA), cSqB = Math.round(normSqB * cmB);
    const cTkA = Math.round(normTkA * cmA), cTkB = Math.round(normTkB * cmB);
    const vampA = Math.round(normSqA * (sA.pLifesteal / 100)), vampB = Math.round(normSqB * (sB.pLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 普攻秒伤与暴击期望', '持续输出', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      add('暴击期望单发 (中射)', cSqA, cSqB);
      add('暴击期望单发 (坦克)', cTkA, cTkB);
      add('持续秒伤 DPS (中射)', Math.round(cSqA * hpsA), Math.round(cSqB * hpsB));
      add('持续秒伤 DPS (坦克)', Math.round(cTkA * hpsA), Math.round(cTkB * hpsB));
      add('普攻频次 (攻速折算)', `${hpsA.toFixed(2)} 次/s`, `${hpsB.toFixed(2)} 次/s`);
      if (vampA > 0 || vampB > 0) add('单发普攻吸血', vampA, vampB, ' 点');
    });
    const cd1A = +(5.0 * (1 - sA.cdr / 100)).toFixed(1), cd1B = +(5.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('10'), false, '1技能 · 翻滚突袭', formatSkillBadge(5.0, '翻滚强化'), (add) => {
      add('翻滚重炮强化 (中射)', Math.round((370 + sA.atk * 1.0 + sheenA) * multA * drSqPA), Math.round((370 + sB.atk * 1.0 + sheenB) * multB * drSqPB));
      add('翻滚重炮强化 (坦克)', Math.round((370 + sA.atk * 1.0 + sheenA) * multA * drTkPA), Math.round((370 + sB.atk * 1.0 + sheenB) * multB * drTkPB));
      add('核心机制特性', '80%移速 · 强化射程', '80%移速 · 强化射程');
      add('实战技能冷却', cd1A, cd1B, 's', true);
    });
    const cd2A = +(6.0 * (1 - sA.cdr / 100)).toFixed(1), cd2B = +(6.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('20'), false, '2技能 · 红莲爆弹', formatSkillBadge(6.0, '+25%破甲'), (add) => {
      add('爆弹范围伤害 (中射)', Math.round((250 + sA.atk * 1.0) * multA * drSqPA), Math.round((250 + sB.atk * 1.0) * multB * drSqPB));
      add('爆弹范围伤害 (坦克)', Math.round((250 + sA.atk * 1.0) * multA * drTkPA), Math.round((250 + sB.atk * 1.0) * multB * drTkPB));
      add('核心机制特性', '25%破甲 · 50%减速', '25%破甲 · 50%减速');
      add('实战技能冷却', cd2A, cd2B, 's', true);
    });
    const cd3A = +(15.0 * (1 - sA.cdr / 100)).toFixed(1), cd3B = +(15.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('30'), false, '3技能 · 究极弩炮', formatSkillBadge(15.0, '远程AOE'), (add) => {
      add('究极弩炮命中 (中射)', Math.round((1000 + sA.atk * 1.85) * multA * drSqPA), Math.round((1000 + sB.atk * 1.85) * multB * drSqPB));
      add('究极弩炮命中 (坦克)', Math.round((1000 + sA.atk * 1.85) * multA * drTkPA), Math.round((1000 + sB.atk * 1.85) * multB * drTkPB));
      add('核心机制特性', '超远冲击 · 范围溅射', '超远冲击 · 范围溅射');
      add('实战技能冷却', cd3A, cd3B, 's', true);
    });
  } else if (h.cname === '李白') {
    const hpsA = 1 + sA.aspeed / 100, hpsB = 1 + sB.aspeed / 100;
    const vampA = Math.round(normSqA * (sA.pLifesteal / 100)), vampB = Math.round(normSqB * (sB.pLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 普通攻击与剑气解锁', '4A解封大招', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      add('普攻频次 (攻速折算)', `${hpsA.toFixed(2)} 次/s`, `${hpsB.toFixed(2)} 次/s`);
      if (vampA > 0 || vampB > 0) add('单发普攻吸血', vampA, vampB, ' 点');
      if (effectA !== '常规平A' || effectB !== '常规平A') add('强击与特效机制', effectA, effectB);
    });
    const cd1A = +(8.0 * (1 - sA.cdr / 100)).toFixed(1), cd1B = +(8.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('10'), false, '1技能 · 将进酒', formatSkillBadge(8.0, '两段眩晕'), (add) => {
      add('两段突进满伤 (中射)', Math.round(2 * (575 + sA.atk * 1.1) * multA * drSqPA), Math.round(2 * (575 + sB.atk * 1.1) * multB * drSqPB));
      add('两段突进满伤 (坦克)', Math.round(2 * (575 + sA.atk * 1.1) * multA * drTkPA), Math.round(2 * (575 + sB.atk * 1.1) * multB * drTkPB));
      add('核心机制特性', '两段眩晕 · 残影折返', '两段眩晕 · 残影折返');
      add('实战技能冷却', cd1A, cd1B, 's', true);
    });
    const cd2A = +(10.0 * (1 - sA.cdr / 100)).toFixed(1), cd2B = +(10.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('20'), false, '2技能 · 神来之笔', formatSkillBadge(10.0, '破甲·免控'), (add) => {
      add('神来之笔剑圈 (中射)', Math.round((680 + sA.atk * 1.6) * multA * drSqPA), Math.round((680 + sB.atk * 1.6) * multB * drSqPB));
      add('神来之笔剑圈 (坦克)', Math.round((680 + sA.atk * 1.6) * multA * drTkPA), Math.round((680 + sB.atk * 1.6) * multB * drTkPB));
      add('核心机制特性', '不可选中 · 剑圈破甲', '不可选中 · 剑圈破甲');
      add('实战技能冷却', cd2A, cd2B, 's', true);
    });
    const cd3A = +(12.0 * (1 - sA.cdr / 100)).toFixed(1), cd3B = +(12.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('30'), false, '3技能 · 青莲剑歌', formatSkillBadge(12.0, '不可选中'), (add) => {
      add('5段剑气斩击 (中射)', Math.round(5 * (320 + sA.atk * 0.5) * multA * drSqPA), Math.round(5 * (320 + sB.atk * 0.5) * multB * drSqPB));
      add('5段剑气斩击 (坦克)', Math.round(5 * (320 + sA.atk * 0.5) * multA * drTkPA), Math.round(5 * (320 + sB.atk * 0.5) * multB * drTkPB));
      add('核心机制特性', '全程不可选中 · 5段斩', '全程不可选中 · 5段斩');
      add('实战技能冷却', cd3A, cd3B, 's', true);
    });
  } else if (h.cname === '吕布') {
    const tA = Math.round(sA.atk * multA), tB = Math.round(sB.atk * multB);
    const hpsA = 1 + sA.aspeed / 100, hpsB = 1 + sB.aspeed / 100;
    const vampA = Math.round(sA.atk * (sA.pLifesteal / 100)), vampB = Math.round(sB.atk * (sB.pLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 附魔真实伤害与吸血', '附魔真伤', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      add('附魔真伤普攻 (中射)', tA, tB);
      add('附魔真伤普攻 (坦克)', tA, tB);
      add('普攻频次 (攻速折算)', `${hpsA.toFixed(2)} 次/s`, `${hpsB.toFixed(2)} 次/s`);
      if (vampA > 0 || vampB > 0) add('单发普攻吸血', vampA, vampB, ' 点');
    });
    const cd1A = +(5.0 * (1 - sA.cdr / 100)).toFixed(1), cd1B = +(5.0 * (1 - sB.cdr / 100)).toFixed(1);
    const s1A = Math.round((1200 + sA.atk * 1.9) * multA), s1B = Math.round((1200 + sB.atk * 1.9) * multB);
    addCard(skUrl('10'), false, '1技能 · 方天画斩', formatSkillBadge(5.0, '附魔真伤'), (add) => {
      add('方天画斩 (真实伤害)', s1A, s1B);
      add('核心机制特性', '命中附魔 · 真伤转化', '命中附魔 · 真伤转化');
      add('实战技能冷却', cd1A, cd1B, 's', true);
    });
    const cd2A = +(8.0 * (1 - sA.cdr / 100)).toFixed(1), cd2B = +(8.0 * (1 - sB.cdr / 100)).toFixed(1);
    const shA = Math.round(1050 + sA.atk * 0.6), shB = Math.round(1050 + sB.atk * 0.6);
    const hlA = Math.round(shA * 0.5), hlB = Math.round(shB * 0.5);
    addCard(skUrl('20'), false, '2技能 · 贪婪之握', formatSkillBadge(8.0, '护盾转血'), (add) => {
      add('抽取护盾吸收上限', shA, shB, ' 点');
      add('护盾转化生命回复', hlA, hlB, ' 点');
      if (sA.hasPhoenixEye || sB.hasPhoenixEye) {
        add('绝境急救(≤30%血)', sA.hasPhoenixEye ? Math.round(hlA * 1.42) : hlA, sB.hasPhoenixEye ? Math.round(hlB * 1.42) : hlB, ' 点');
      }
      add('实战技能冷却', cd2A, cd2B, 's', true);
    });
    const cd3A = +(50.0 * (1 - sA.cdr / 100)).toFixed(1), cd3B = +(50.0 * (1 - sB.cdr / 100)).toFixed(1);
    addCard(skUrl('30'), false, '3技能 · 魔神降世', formatSkillBadge(50.0, '击飞·双抗'), (add) => {
      add('天降挥斩 (真实伤害)', Math.round((800 + sA.atk * 1.2) * multA), Math.round((800 + sB.atk * 1.2) * multB));
      add('核心机制特性', '1.0s击飞 · 结界双抗', '1.0s击飞 · 结界双抗');
      add('实战技能冷却', cd3A, cd3B, 's', true);
    });
  }
}

function buildGeneralHeroCards(h, isMarksman, isMage, isSupport, sA, sB, multA, multB, drSqPA, drSqPB, drTkPA, drTkPB, drSqMA, drSqMB, drTkMA, drTkMB, normSqA, normSqB, normTkA, normTkB, effectA, effectB, heroSkills, attackIconUrl, skUrl, addCard) {
  if (isMarksman) {
    const hpsA = 1 + sA.aspeed / 100, hpsB = 1 + sB.aspeed / 100;
    const cmA = 1 + (sA.critRate / 100) * ((sA.critEff - 100) / 100), cmB = 1 + (sB.critRate / 100) * ((sB.critEff - 100) / 100);
    const cSqA = Math.round(normSqA * cmA), cSqB = Math.round(normSqB * cmB);
    const cTkA = Math.round(normTkA * cmA), cTkB = Math.round(normTkB * cmB);
    const vampA = Math.round(normSqA * (sA.pLifesteal / 100)), vampB = Math.round(normSqB * (sB.pLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 普攻秒伤与暴击期望', '持续输出', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      add('暴击期望单发 (中射)', cSqA, cSqB);
      add('暴击期望单发 (坦克)', cTkA, cTkB);
      add('持续秒伤 DPS (中射)', Math.round(cSqA * hpsA), Math.round(cSqB * hpsB));
      add('持续秒伤 DPS (坦克)', Math.round(cTkA * hpsA), Math.round(cTkB * hpsB));
      add('普攻频次 (攻速折算)', `${hpsA.toFixed(2)} 次/s`, `${hpsB.toFixed(2)} 次/s`);
      if (vampA > 0 || vampB > 0) add('单发普攻吸血', vampA, vampB, ' 点');
    });
  } else if (isMage) {
    const vMageA = Math.round(sA.ap * 0.4 * (sA.mLifesteal / 100));
    const vMageB = Math.round(sB.ap * 0.4 * (sB.mLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 基础普攻与法术衔接', '普攻·法术', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      if (vMageA > 0 || vMageB > 0) add('单发技能法术吸血', vMageA, vMageB, ' 点');
      add('强击与法术特效', effectA, effectB);
    });
  } else if (isSupport) {
    const fmtAct = (n) => (!n || n.includes('无主动')) ? '无主动' : (n.includes('救赎') ? '救赎护盾' : (n.includes('奔狼') ? '奔狼冲锋' : (n.includes('形昭') ? '形昭探草' : (n.includes('星泉') ? '星泉续航' : n.split('(')[0].trim()))));
    const fmtAu = (d) => (!d || d.includes('无团队') || d.includes('无光环')) ? '无光环' : (d.includes('近卫') ? '近卫双抗' : (d.includes('极影') ? '极影攻速' : d.split('(')[0].trim()));
    addCard(attackIconUrl, true, '普攻 · 普通攻击与辅助协同', '游走协同', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      add('辅助装主动技能', fmtAct(sA.supportActiveName), fmtAct(sB.supportActiveName));
      add('团队常驻防御光环', fmtAu(sA.supportAuraDesc), fmtAu(sB.supportAuraDesc));
      add('移动速度 (转线支援)', sA.moveSpeed, sB.moveSpeed, ' 点');
    });
  } else {
    const vampA = Math.round(sA.atk * (sA.pLifesteal / 100));
    const vampB = Math.round(sB.atk * (sB.pLifesteal / 100));
    addCard(attackIconUrl, true, '普攻 · 普通攻击与强击特效', '普通攻击', (add) => {
      add('常规平A (中射)', normSqA, normSqB);
      add('常规平A (坦克)', normTkA, normTkB);
      if (vampA > 0 || vampB > 0) add('单发普攻吸血', vampA, vampB, ' 点');
      add('强击与特效机制', effectA, effectB);
    });
  }

  const activeSkills = (heroSkills || []).slice(1);
  const skillList = activeSkills.length > 0 ? activeSkills : [
    { type: '1技能', name: '战术技能', desc: '物理爆发突进', cd_sec: 6.0, tags: ['物理输出'] },
    { type: '2技能', name: '核心技能', desc: '机制控制技能', cd_sec: 8.0, tags: ['控制'] },
    { type: '3技能', name: '终极奥义', desc: '决胜团战大招', cd_sec: 30.0, tags: ['爆发'] }
  ];

  skillList.forEach((sk, idx) => {
    const cleanSkName = (sk.name || '').split('(')[0].split('（')[0].trim() || sk.name;
    const baseCd = sk.cd_sec || (idx === 2 ? (isSupport ? 40.0 : 30.0) : (idx === 1 ? (isSupport ? 10.0 : 8.0) : (isSupport ? 8.0 : 6.0)));
    const cdA = +(baseCd * (1 - sA.cdr / 100)).toFixed(1), cdB = +(baseCd * (1 - sB.cdr / 100)).toFixed(1);
    const desc = sk.desc || '', tags = sk.tags || [], tagsStr = tags.join(' ');
    const hasShield = tagsStr.includes('护盾') || desc.includes('护盾') || desc.includes('吸收');
    const hasHeal = tagsStr.includes('回血') || tagsStr.includes('回复') || desc.includes('回复') || desc.includes('治疗') || desc.includes('回血');
    const skType = sk.type || '';
    const isUlt = skType.includes('3') || skType.includes('4') || idx >= 2;

    let ccText = isSupport ? '团队协同' : (tags.length > 0 ? tags[0] : '战术机制');
    const kwList = isSupport
      ? [['压制','绝对压制'],['复活','濒死复活'],['刷新','大招刷新'],['击飞','范围击飞'],['眩晕','眩晕打断'],['晕眩','眩晕打断'],['击退','击退控场'],['嘲讽','范围嘲讽'],['沉默','沉默限制'],['隐身','团队隐身'],['回城','空间法阵'],['减速','减速牵制']]
      : [['真实伤害','真实伤害'],['击飞','范围击飞'],['眩晕','眩晕硬控'],['晕眩','眩晕硬控'],['沉默','沉默限制'],['减速','减速牵制'],['不可选中','不可选中'],['霸体','霸体免控']];
    for (const [kw, lb] of kwList) {
      if (desc.includes(kw)) { ccText = lb; break; }
    }
    const t0 = (tags && tags[0] && tags[0] !== ccText) ? tags[0] : (isSupport ? '团队增益' : '战术核心');
    const mechSummary = `${ccText} · ${t0}`;

    addCard(skUrl((idx + 1) * 10), false, `${sk.type || `技能 ${idx + 1}`} · ${cleanSkName}`, formatSkillBadge(baseCd, ccText), (add) => {
      if (isSupport) {
        let rowCount = 0;
        const hasDmgKw = ['物理伤害', '法术伤害', '真实伤害', '对敌人造成', '范围内的敌人', '敌方造成'].some(k => desc.includes(k));
        const isPureProt = (hasShield || hasHeal || desc.includes('回城') || desc.includes('刷新') || desc.includes('复活') || desc.includes('附身')) &&
          ['为己方', '为友方', '为友军', '自身获得', '为自身', '队友', '附身', '传送', '刷新'].some(p => desc.includes(p)) &&
          !['横劈', '砸地', '冲锋', '飞斧', '机械爪'].some(a => desc.includes(a));
        const hasRealDamage = hasDmgKw && !isPureProt;
        if (hasRealDamage) {
          const isMagic = isMage || desc.includes('法术伤害') || tags.includes('法术伤害') || sA.ap > sA.atk;
          const bV = isUlt ? 600 : (idx === 0 ? 350 : 450);
          if (isMagic) {
            add(`${cleanSkName}伤害 (中射)`, Math.round((bV + sA.ap * 0.6 + sA.hp * 0.03) * multA * drSqMA), Math.round((bV + sB.ap * 0.6 + sB.hp * 0.03) * multB * drSqMB));
            add(`${cleanSkName}伤害 (坦克)`, Math.round((bV + sA.ap * 0.6 + sA.hp * 0.03) * multA * drTkMA), Math.round((bV + sB.ap * 0.6 + sB.hp * 0.03) * multB * drTkMB));
          } else {
            add(`${cleanSkName}伤害 (中射)`, Math.round((bV + sA.atk * 0.8 + sA.hp * 0.02) * multA * drSqPA), Math.round((bV + sB.atk * 0.8 + sB.hp * 0.02) * multB * drSqPB));
            add(`${cleanSkName}伤害 (坦克)`, Math.round((bV + sA.atk * 0.8 + sA.hp * 0.02) * multA * drTkPA), Math.round((bV + sB.atk * 0.8 + sB.hp * 0.02) * multB * drTkPB));
          }
          rowCount++;
        }
        if (hasShield) {
          const shA = (isUlt && desc.includes('最大生命')) ? Math.round(sA.hp * 0.40) : ((sA.ap > sA.atk || isMage) ? Math.round(1000 + sA.ap * 0.45 + sA.hp * 0.08) : Math.round(900 + sA.hp * 0.08 + sA.atk * 0.4));
          const shB = (isUlt && desc.includes('最大生命')) ? Math.round(sB.hp * 0.40) : ((sB.ap > sB.atk || isMage) ? Math.round(1000 + sB.ap * 0.45 + sB.hp * 0.08) : Math.round(900 + sB.hp * 0.08 + sB.atk * 0.4));
          add(isUlt ? '终极真血护盾吸收量' : `${cleanSkName}护盾庇护吸收量`, shA, shB, ' 点');
          rowCount++;
        }
        if (hasHeal) {
          const hlA = (sA.ap > sA.atk || isMage) ? Math.round(700 + sA.ap * 0.40 + sA.hp * 0.03) : Math.round(500 + sA.hp * 0.06);
          const hlB = (sB.ap > sB.atk || isMage) ? Math.round(700 + sB.ap * 0.40 + sB.hp * 0.03) : Math.round(500 + sB.hp * 0.06);
          add(`${cleanSkName}生命回复总量`, hlA, hlB, ' 点');
          rowCount++;
          if (sA.hasPhoenixEye || sB.hasPhoenixEye) {
            add('绝境急救(≤30%血)', sA.hasPhoenixEye ? Math.round(hlA * 1.42) : hlA, sB.hasPhoenixEye ? Math.round(hlB * 1.42) : hlB, ' 点');
            rowCount++;
          }
        }
        if (isUlt || (!hasRealDamage && !hasShield && !hasHeal)) {
          add('自身承伤极限 (物理EHP)', Math.round(sA.hp * (1 + sA.pdef / 602)), Math.round(sB.hp * (1 + sB.pdef / 602)), ' 点');
          add('自身承伤极限 (法术EHP)', Math.round(sA.hp * (1 + sA.mdef / 602)), Math.round(sB.hp * (1 + sB.mdef / 602)), ' 点');
          rowCount++;
        }
        if (rowCount < 2) {
          add('核心机制特性', mechSummary, mechSummary);
        }
        add('实战技能冷却', cdA, cdB, 's', true);
      } else {
        let rowCount = 1;
        const isTrue = desc.includes('真实伤害') || tags.includes('真实伤害');
        const isMag = isMage || desc.includes('法术伤害') || tags.includes('法术伤害');
        const isMulti = desc.includes('段') || desc.includes('次') || desc.includes('持续');
        const bR = idx === 2 ? 1.5 : (idx === 1 ? 1.0 : 0.8), bV = idx === 2 ? 750 : (idx === 1 ? 480 : 350);
        if (isTrue) {
          const dA = Math.round((bV + sA.atk * bR) * multA), dB = Math.round((bV + sB.atk * bR) * multB);
          add(`${cleanSkName} (真实伤害)`, dA, dB);
        } else {
          const rawA = isMag ? Math.round(bV + sA.ap * (bR * 0.7)) : Math.round(bV + sA.atk * bR);
          const rawB = isMag ? Math.round(bV + sB.ap * (bR * 0.7)) : Math.round(bV + sB.atk * bR);
          const sqA = Math.round(rawA * multA * (isMag ? drSqMA : drSqPA)), sqB = Math.round(rawB * multB * (isMag ? drSqMB : drSqPB));
          const tkA = Math.round(rawA * multA * (isMag ? drTkMA : drTkPA)), tkB = Math.round(rawB * multB * (isMag ? drTkMB : drTkPB));
          add(isMulti ? `${cleanSkName}多段满额 (中射)` : `${cleanSkName}单发净伤 (中射)`, sqA, sqB);
          add(isMulti ? `${cleanSkName}多段满额 (坦克)` : `${cleanSkName}单发净伤 (坦克)`, tkA, tkB);
        }
        if (hasHeal) {
          const hlA = Math.round(sA.hp * 0.05 + sA.atk * 0.2 + sA.ap * 0.25), hlB = Math.round(sB.hp * 0.05 + sB.atk * 0.2 + sB.ap * 0.25);
          add(`${cleanSkName}生命回复总量`, hlA, hlB, ' 点');
          rowCount++;
          if (sA.hasPhoenixEye || sB.hasPhoenixEye) {
            add('绝境急救(≤30%血)', sA.hasPhoenixEye ? Math.round(hlA * 1.42) : hlA, sB.hasPhoenixEye ? Math.round(hlB * 1.42) : hlB, ' 点');
            rowCount++;
          }
        }
        if (hasShield) {
          add(`${cleanSkName}护盾庇护吸收量`, Math.round(500 + sA.hp * 0.08 + sA.ap * 0.3 + sA.atk * 0.2), Math.round(500 + sB.hp * 0.08 + sB.ap * 0.3 + sB.atk * 0.2), ' 点');
          rowCount++;
        }
        if (rowCount < 2) {
          add('核心机制特性', mechSummary, mechSummary);
        }
        add('实战技能冷却', cdA, cdB, 's', true);
      }
    });
  });
}

module.exports = { buildCustomHeroCards, buildGeneralHeroCards };
