Object.assign(App, {
  renderGeneralHeroSkills(ctx) {
    const {
      h, sA, sB, isSupport, isMarksman, isMage, heroSkills,
      multA, multB, drSquishyPhysA, drSquishyPhysB, drTankPhysA, drTankPhysB,
      drSquishyMagicA, drSquishyMagicB, drTankMagicA, drTankMagicB,
      normSquishyA, normSquishyB, normTankA, normTankB, effectA, effectB,
      renderCard, buildRow, getSkillImg, getAttackBadge, formatSkillBadge
    } = ctx;
    if (h.cname === "吕布") {
      const tA = Math.round(sA.atk * multA), tB = Math.round(sB.atk * multB);
      const hpsA = 1 + sA.aspeed / 100, hpsB = 1 + sB.aspeed / 100;
      const vampA = Math.round(sA.atk * (sA.pLifesteal / 100)), vampB = Math.round(sB.atk * (sB.pLifesteal / 100));
      renderCard(getAttackBadge(), "普攻 · 附魔真实伤害与吸血", '<span class="skill-spec-tag">附魔真伤</span>', () => [
        buildRow("常规平A (中射)", normSquishyA, normSquishyB),
        buildRow("常规平A (坦克)", normTankA, normTankB),
        buildRow("附魔真伤普攻 (中射)", tA, tB),
        buildRow("附魔真伤普攻 (坦克)", tA, tB),
        buildRow("普攻频次 (攻速折算)", `${hpsA.toFixed(2)} 次/s`, `${hpsB.toFixed(2)} 次/s`),
        (vampA > 0 || vampB > 0) ? buildRow("单发普攻吸血", vampA, vampB, " 点") : ""
      ].join(""));

      const cd1A = +(5.0 * (1 - sA.cdr / 100)).toFixed(1), cd1B = +(5.0 * (1 - sB.cdr / 100)).toFixed(1);
      const s1A = Math.round((1200 + sA.atk * 1.9) * multA), s1B = Math.round((1200 + sB.atk * 1.9) * multB);
      renderCard(getSkillImg('10'), "1技能 · 方天画斩", formatSkillBadge(5.0, "附魔真伤"), () => [
        buildRow("方天画斩 (真实伤害)", s1A, s1B),
        buildRow("实战技能冷却", cd1A, cd1B, "s", true)
      ].join(""));

      const cd2A = +(8.0 * (1 - sA.cdr / 100)).toFixed(1), cd2B = +(8.0 * (1 - sB.cdr / 100)).toFixed(1);
      const shA = Math.round(1050 + sA.atk * 0.6), shB = Math.round(1050 + sB.atk * 0.6);
      const hlA = Math.round(shA * 0.5), hlB = Math.round(shB * 0.5);
      renderCard(getSkillImg('20'), "2技能 · 贪婪之握", formatSkillBadge(8.0, "护盾转血"), () => [
        buildRow("抽取护盾吸收上限", shA, shB, " 点"),
        buildRow("护盾转化生命回复", hlA, hlB, " 点"),
        (sA.hasPhoenixEye || sB.hasPhoenixEye) ? buildRow("绝境急救(≤30%血)", sA.hasPhoenixEye ? Math.round(hlA * 1.42) : hlA, sB.hasPhoenixEye ? Math.round(hlB * 1.42) : hlB, " 点") : "",
        buildRow("实战技能冷却", cd2A, cd2B, "s", true)
      ].join(""));

      const cd3A = +(50.0 * (1 - sA.cdr / 100)).toFixed(1), cd3B = +(50.0 * (1 - sB.cdr / 100)).toFixed(1);
      renderCard(getSkillImg('30'), "3技能 · 魔神降世", formatSkillBadge(50.0, "击飞·双抗"), () => [
        buildRow("天降挥斩 (真实伤害)", Math.round((800 + sA.atk * 1.2) * multA), Math.round((800 + sB.atk * 1.2) * multB)),
        buildRow("实战技能冷却", cd3A, cd3B, "s", true)
      ].join(""));
    } else {
      if (isMarksman) {
        const hpsA = 1 + sA.aspeed / 100, hpsB = 1 + sB.aspeed / 100;
        const cmA = 1 + (sA.critRate / 100) * ((sA.critEff - 100) / 100), cmB = 1 + (sB.critRate / 100) * ((sB.critEff - 100) / 100);
        const cSqA = Math.round(normSquishyA * cmA), cSqB = Math.round(normSquishyB * cmB);
        const cTkA = Math.round(normTankA * cmA), cTkB = Math.round(normTankB * cmB);
        const vampA = Math.round(normSquishyA * (sA.pLifesteal / 100)), vampB = Math.round(normSquishyB * (sB.pLifesteal / 100));
        renderCard(getAttackBadge(), "普攻 · 普攻秒伤与暴击期望", '<span class="skill-spec-tag">持续输出</span>', () => [
          buildRow("常规平A (中射)", normSquishyA, normSquishyB),
          buildRow("常规平A (坦克)", normTankA, normTankB),
          buildRow("暴击期望单发 (中射)", cSqA, cSqB),
          buildRow("暴击期望单发 (坦克)", cTkA, cTkB),
          buildRow("持续秒伤 DPS (中射)", Math.round(cSqA * hpsA), Math.round(cSqB * hpsB)),
          buildRow("持续秒伤 DPS (坦克)", Math.round(cTkA * hpsA), Math.round(cTkB * hpsB)),
          buildRow("普攻频次 (攻速折算)", `${hpsA.toFixed(2)} 次/s`, `${hpsB.toFixed(2)} 次/s`),
          (vampA > 0 || vampB > 0) ? buildRow("单发普攻吸血", vampA, vampB, " 点") : ""
        ].join(""));
      } else if (isMage) {
        const vMageA = Math.round(sA.ap * 0.4 * (sA.mLifesteal / 100)), vMageB = Math.round(sB.ap * 0.4 * (sB.mLifesteal / 100));
        renderCard(getAttackBadge(), "普攻 · 基础普攻与法术衔接", '<span class="skill-spec-tag">普攻·法术</span>', () => [
          buildRow("常规平A (中射)", normSquishyA, normSquishyB),
          buildRow("常规平A (坦克)", normTankA, normTankB),
          (vMageA > 0 || vMageB > 0) ? buildRow("单发技能法术吸血", vMageA, vMageB, " 点") : "",
          buildRow("强击与法术特效", effectA, effectB)
        ].join(""));
      } else if (isSupport) {
        const fmtAct = (n) => (!n || n.includes("无主动")) ? "无主动" : (n.includes("救赎") ? "救赎护盾" : (n.includes("奔狼") ? "奔狼冲锋" : (n.includes("形昭") ? "形昭探草" : (n.includes("星泉") ? "星泉续航" : n.split('(')[0].trim()))));
        const fmtAu = (d) => (!d || d.includes("无团队") || d.includes("无光环")) ? "无光环" : (d.includes("近卫") ? "近卫双抗" : (d.includes("极影") ? "极影攻速" : d.split('(')[0].trim()));
        renderCard(getAttackBadge(), "普攻 · 普通攻击与辅助协同", '<span class="skill-spec-tag">游走协同</span>', () => [
          buildRow("常规平A (中射)", normSquishyA, normSquishyB),
          buildRow("常规平A (坦克)", normTankA, normTankB),
          buildRow("辅助装主动技能", fmtAct(sA.supportActiveName), fmtAct(sB.supportActiveName)),
          buildRow("团队常驻防御光环", fmtAu(sA.supportAuraDesc), fmtAu(sB.supportAuraDesc)),
          buildRow("移动速度 (转线支援)", sA.moveSpeed, sB.moveSpeed, " 点")
        ].join(""));
      } else {
        const vampA = Math.round(sA.atk * (sA.pLifesteal / 100)), vampB = Math.round(sB.atk * (sB.pLifesteal / 100));
        renderCard(getAttackBadge(), "普攻 · 普通攻击与强击特效", '<span class="skill-spec-tag">普通攻击</span>', () => [
          buildRow("常规平A (中射)", normSquishyA, normSquishyB),
          buildRow("常规平A (坦克)", normTankA, normTankB),
          (vampA > 0 || vampB > 0) ? buildRow("单发普攻吸血", vampA, vampB, " 点") : "",
          buildRow("强击与特效机制", effectA, effectB)
        ].join(""));
      }

      const activeSkills = (heroSkills || []).slice(1);
      const skillList = activeSkills.length > 0 ? activeSkills : [
        { type: "1技能", name: "战术技能", desc: "物理爆发突进", cd_sec: 6.0, tags: ["物理输出"] },
        { type: "2技能", name: "核心技能", desc: "机制控制技能", cd_sec: 8.0, tags: ["控制"] },
        { type: "3技能", name: "终极奥义", desc: "决胜团战大招", cd_sec: 30.0, tags: ["爆发"] }
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

        let ccText = isSupport ? "团队协同" : (tags.length > 0 ? tags[0] : "战术机制");
        const kwList = isSupport
          ? [['压制','绝对压制'],['复活','濒死复活'],['刷新','大招刷新'],['击飞','范围击飞'],['眩晕','眩晕打断'],['晕眩','眩晕打断'],['击退','击退控场'],['嘲讽','范围嘲讽'],['沉默','沉默限制'],['隐身','团队隐身'],['回城','空间法阵'],['减速','减速牵制']]
          : [['真实伤害','真实伤害'],['击飞','范围击飞'],['眩晕','眩晕硬控'],['晕眩','眩晕硬控'],['沉默','沉默限制'],['减速','减速牵制'],['不可选中','不可选中'],['霸体','霸体免控']];
        for (const [kw, lb] of kwList) {
          if (desc.includes(kw)) { ccText = lb; break; }
        }

        renderCard(getSkillImg((idx + 1) * 10), `${sk.type || `技能 ${idx + 1}`} · ${cleanSkName}`, formatSkillBadge(baseCd, ccText), () => {
          const out = [];
          if (isSupport) {
            const hasDmgKw = ['物理伤害', '法术伤害', '真实伤害', '对敌人造成', '范围内的敌人', '敌方造成'].some(k => desc.includes(k));
            const isPureProt = (hasShield || hasHeal || desc.includes('回城') || desc.includes('刷新') || desc.includes('复活') || desc.includes('附身')) &&
              ['为己方', '为友方', '为友军', '自身获得', '为自身', '队友', '附身', '传送', '刷新'].some(p => desc.includes(p)) &&
              !['横劈', '砸地', '冲锋', '飞斧', '机械爪'].some(a => desc.includes(a));
            const hasRealDamage = hasDmgKw && !isPureProt;
            if (hasRealDamage) {
              const isMagic = isMage || desc.includes('法术伤害') || tags.includes('法术伤害') || sA.ap > sA.atk;
              const bV = isUlt ? 600 : (idx === 0 ? 350 : 450);
              if (isMagic) {
                out.push(buildRow(`${cleanSkName}伤害 (中射)`, Math.round((bV + sA.ap * 0.6 + sA.hp * 0.03) * multA * drSquishyMagicA), Math.round((bV + sB.ap * 0.6 + sB.hp * 0.03) * multB * drSquishyMagicB)));
                out.push(buildRow(`${cleanSkName}伤害 (坦克)`, Math.round((bV + sA.ap * 0.6 + sA.hp * 0.03) * multA * drTankMagicA), Math.round((bV + sB.ap * 0.6 + sB.hp * 0.03) * multB * drTankMagicB)));
              } else {
                out.push(buildRow(`${cleanSkName}伤害 (中射)`, Math.round((bV + sA.atk * 0.8 + sA.hp * 0.02) * multA * drSquishyPhysA), Math.round((bV + sB.atk * 0.8 + sB.hp * 0.02) * multB * drSquishyPhysB)));
                out.push(buildRow(`${cleanSkName}伤害 (坦克)`, Math.round((bV + sA.atk * 0.8 + sA.hp * 0.02) * multA * drTankPhysA), Math.round((bV + sB.atk * 0.8 + sB.hp * 0.02) * multB * drTankPhysB)));
              }
            }
            if (hasShield) {
              const shA = (isUlt && desc.includes('最大生命')) ? Math.round(sA.hp * 0.40) : ((sA.ap > sA.atk || isMage) ? Math.round(1000 + sA.ap * 0.45 + sA.hp * 0.08) : Math.round(900 + sA.hp * 0.08 + sA.atk * 0.4));
              const shB = (isUlt && desc.includes('最大生命')) ? Math.round(sB.hp * 0.40) : ((sB.ap > sB.atk || isMage) ? Math.round(1000 + sB.ap * 0.45 + sB.hp * 0.08) : Math.round(900 + sB.hp * 0.08 + sB.atk * 0.4));
              out.push(buildRow(isUlt ? "终极真血护盾吸收量" : `${cleanSkName}护盾庇护吸收量`, shA, shB, " 点"));
            }
            if (hasHeal) {
              const hlA = (sA.ap > sA.atk || isMage) ? Math.round(700 + sA.ap * 0.40 + sA.hp * 0.03) : Math.round(500 + sA.hp * 0.06);
              const hlB = (sB.ap > sB.atk || isMage) ? Math.round(700 + sB.ap * 0.40 + sB.hp * 0.03) : Math.round(500 + sB.hp * 0.06);
              out.push(buildRow(`${cleanSkName}生命回复总量`, hlA, hlB, " 点"));
              if (sA.hasPhoenixEye || sB.hasPhoenixEye) {
                out.push(buildRow("绝境急救(≤30%血)", sA.hasPhoenixEye ? Math.round(hlA * 1.42) : hlA, sB.hasPhoenixEye ? Math.round(hlB * 1.42) : hlB, " 点"));
              }
            }
            if (isUlt || (!hasRealDamage && !hasShield && !hasHeal)) {
              out.push(buildRow("自身物理承伤上限 (物理EHP)", Math.round(sA.hp * (1 + sA.pdef / 602)), Math.round(sB.hp * (1 + sB.pdef / 602)), " 点"));
              out.push(buildRow("自身法术承伤上限 (法术EHP)", Math.round(sA.hp * (1 + sA.mdef / 602)), Math.round(sB.hp * (1 + sB.mdef / 602)), " 点"));
              if (isUlt) out.push(buildRow("最大生命值上限", sA.hp, sB.hp, " 点"));
            }
            out.push(buildRow("实战技能冷却", cdA, cdB, "s", true));
          } else {
            const isTrue = desc.includes('真实伤害') || tags.includes('真实伤害');
            const isMag = isMage || desc.includes('法术伤害') || tags.includes('法术伤害');
            const isMulti = desc.includes('段') || desc.includes('次') || desc.includes('持续');
            const bR = idx === 2 ? 1.5 : (idx === 1 ? 1.0 : 0.8), bV = idx === 2 ? 750 : (idx === 1 ? 480 : 350);
            if (isTrue) {
              const dA = Math.round((bV + sA.atk * bR) * multA), dB = Math.round((bV + sB.atk * bR) * multB);
              out.push(buildRow(`${cleanSkName} (真实伤害)`, dA, dB));
            } else {
              const rawA = isMag ? Math.round(bV + sA.ap * (bR * 0.7)) : Math.round(bV + sA.atk * bR);
              const rawB = isMag ? Math.round(bV + sB.ap * (bR * 0.7)) : Math.round(bV + sB.atk * bR);
              const sqA = Math.round(rawA * multA * (isMag ? drSquishyMagicA : drSquishyPhysA)), sqB = Math.round(rawB * multB * (isMag ? drSquishyMagicB : drSquishyPhysB));
              const tkA = Math.round(rawA * multA * (isMag ? drTankMagicA : drTankPhysA)), tkB = Math.round(rawB * multB * (isMag ? drTankMagicB : drTankPhysB));
              out.push(buildRow(isMulti ? `${cleanSkName}多段满额 (中射)` : `${cleanSkName}单发净伤 (中射)`, sqA, sqB));
              out.push(buildRow(isMulti ? `${cleanSkName}多段满额 (坦克)` : `${cleanSkName}单发净伤 (坦克)`, tkA, tkB));
            }
            if (hasHeal) {
              const hlA = Math.round(sA.hp * 0.05 + sA.atk * 0.2 + sA.ap * 0.25), hlB = Math.round(sB.hp * 0.05 + sB.atk * 0.2 + sB.ap * 0.25);
              out.push(buildRow(`${cleanSkName}生命回复`, hlA, hlB, " 点"));
              if (sA.hasPhoenixEye || sB.hasPhoenixEye) {
                out.push(buildRow("绝境急救(≤30%血)", sA.hasPhoenixEye ? Math.round(hlA * 1.42) : hlA, sB.hasPhoenixEye ? Math.round(hlB * 1.42) : hlB, " 点"));
              }
            }
            if (hasShield) {
              out.push(buildRow(`${cleanSkName}护盾吸收`, Math.round(500 + sA.hp * 0.08 + sA.ap * 0.3 + sA.atk * 0.2), Math.round(500 + sB.hp * 0.08 + sB.ap * 0.3 + sB.atk * 0.2), " 点"));
            }
            out.push(buildRow("实战技能冷却", cdA, cdB, "s", true));
          }
          return out.join("");
        });
      });

    }
  }
});
