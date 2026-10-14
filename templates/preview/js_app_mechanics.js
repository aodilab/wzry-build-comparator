Object.assign(App, {
  // 严格对齐沙盒实战：装备差集驱动的核心机制精准比对引擎 (100% 杜绝漏判)
  renderMechanicDifferences(itemsA, itemsB) {
    const box = document.getElementById('dMechanicDeck');
    const validItemsA = (itemsA || []).filter(Boolean);
    const validItemsB = (itemsB || []).filter(Boolean);
    const namesA = validItemsA.map(i => i.item_name);
    const namesB = validItemsB.map(i => i.item_name);

    // 1. 峡谷神装核心机制字典 (精炼描述，并具备官方 passives 自动 fallback)
    const ITEM_MECHANIC_MAP = {
      // 攻击核心
      '暗影战斧': { cat: '破甲穿透', label: '等级物穿', desc: '增加 90~180 点等级成长物理穿透，普攻几率减速' },
      '碎星锤': { cat: '破甲穿透', label: '35%物穿', desc: '提供 35% 百分比物理穿透，近战撕裂万血前排坦克' },
      '破晓': { cat: '破甲穿透', label: '35%物穿', desc: '提供 35% 百分比物理穿透(远程翻倍)与普攻伤害提升，打肉质变核心' },
      '仁者破晓': { cat: '破甲穿透', label: '35%物穿', desc: '提供 35% 百分比物理穿透与普攻伤害增幅' },
      '宗师之力': { cat: '强击机制', label: '强击·爆发加速', desc: '技能后普攻附带 0.8AD 物理伤害，并获 12% 移速爆发 (3s CD)' },
      '冰痕之握': { cat: '强击机制', label: '强击·范围减速', desc: '技能后普攻附带 140~420 物伤并造成 30% 范围减速 (1.2s CD)' },
      '末世': { cat: '普攻特效', label: '8%生命物伤', desc: '普攻附带敌方 8% 当前生命物伤，兼具 10% 吸血与攻速' },
      '泣血之刃': { cat: '吸血续航', label: '25%吸血残血盾', desc: '提供 25% 物理吸血，生命低于 30% 时触发残血护盾' },
      '制裁之刃': { cat: '重伤减疗', label: '重伤挂毒', desc: '普攻或技能降低敌方 35% 生命回复与吸血持续 3 秒' },
      '破军': { cat: '特殊增伤', label: '残血斩杀30%', desc: '目标生命低于 50% 时，对其造成的所有伤害额外提升 30%' },
      '无尽战刃': { cat: '暴击特效', label: '暴伤质变', desc: '获得 20%~50% 额外暴击效果，大幅提升暴击伤害倍率' },
      '闪电匕首': { cat: '普攻特效', label: '电弧群伤', desc: '普攻周期性触发连锁电弧法伤，加快清线与消耗' },
      '影刃': { cat: '暴击特效', label: '暴击加速', desc: '暴击后增加 20% 攻速与 10% 移速，走A手感核心质变' },
      '纯净苍穹': { cat: '保命免伤', label: '35%主动免伤', desc: '主动开启获得 35% 全免伤持续 3 秒，受控状态亦可释放 (90s CD)' },
      '天穹': { cat: '保命免伤', label: '穿墙解控免伤', desc: '解除减速并获 35% 免伤，无视地形阻挡持续 3.5 秒 (90s CD)' },
      '名刀·司命': { cat: '保命免伤', label: '免疫致命伤', desc: '受到致命伤害时免疫死亡持续 0.5~1 秒并获 20% 移速 (90s CD)' },
      '幽影袖箭': { cat: '保命免伤', label: '主动隐身加速', desc: '主动进入隐身状态获 30% 移速并持续回血，普攻或技能退出 (75s CD)' },
      '逐日之弓': { cat: '射程特性', label: '+150射程', desc: '主动提升 150 普攻射程与 40% 移速持续 5 秒 (60s CD)' },
      '日落进击': { cat: '射程特性', label: '进阶射程', desc: '进阶神装，开启大幅提升射程与爆发走位' },
      '铸梦·逐风': { cat: '普攻特效', label: '技能后攻速', desc: '技能命中后下 3 次普攻获得高额攻速加成' },

      // 防御核心
      '怒龙剑盾': { cat: '输出强化', label: '神力·生命物伤', desc: '普攻与技能造成最大生命百分比额外物伤，大幅加速清野清线' },
      '红莲斗篷': { cat: '重伤减疗', label: '业火·贴脸重伤', desc: '近战贴脸每秒灼烧最大生命法伤，受击与灼烧均触发 35% 重伤' },
      '暴烈之甲': { cat: '特殊增伤', label: '受击叠增伤移速', desc: '受到伤害叠加层数，最高获得 10% 全伤害提升与 10% 移速' },
      '反伤刺甲': { cat: '防御反弹', label: '物理反弹', desc: '受到物理伤害反弹部分法术伤害，近战克制物理爆发' },
      '不祥征兆': { cat: '双速削弱', label: '减40%攻速', desc: '受到伤害削弱攻击者 40% 攻速与 10% 移速持续 3 秒' },
      '极寒风暴': { cat: '双速削弱', label: '受损冲击控场', desc: '单次受损超 10% 生命冲击周围，降低 30% 攻速与移速' },
      '不死鸟之眼': { cat: '吸血续航', label: '血统强化', desc: '每损失 10% 最大生命提升 6% 受治疗效果，残血回复质变' },
      '魔女斗篷': { cat: '防御护盾', label: '法伤护盾', desc: '脱战后获得吸收高额法伤的护盾，抵抗法核远程消耗' },
      '永夜守护': { cat: '防御护盾', label: '爆发回血', desc: '受到高额爆发伤害时 3 秒内持续回复 360+8% 最大生命' },
      '霸者重装': { cat: '回复强化', label: '脱战回血增体', desc: '每秒回复百分比生命，脱战回血翻倍，按额外生命提升坦度' },
      '血魔之怒': { cat: '保命免伤', label: '低血厚盾', desc: '主动扣除 30% 当前生命转化为相当于 40% 最大生命护盾 (75s CD)' },
      '怒魂': { cat: '保命免伤', label: '真伤冲击盾', desc: '扣血换取高额护盾并持续对周围释放真实伤害冲击 (75s CD)' },
      '冰霜冲击': { cat: '控场打断', label: '0.5s眩晕打断', desc: '主动释放眩晕周围目标 0.5 秒打断蓄力与位移 (90s CD)' },
      '凛冬': { cat: '控场打断', label: '冲锋冰冻', desc: '朝敌人冲锋并冰冻周围目标，强化突进控制 (90s CD)' },
      '贤者的庇护': { cat: '保命免伤', label: '原地复活', desc: '阵亡后 2 秒原地复活并回复 2000+ 生命 (每局限2次，150s CD)' },
      '旭日初光': { cat: '防御护盾', label: '对决双护盾', desc: '普攻或技能命中敌方为自身和血量最低队友套取护盾' },

      // 法术核心
      '博学者之怒': { cat: '法强放大', label: '总法强+30%', desc: '使英雄当前法术攻击力总和额外提升 30% 核心质变' },
      '虚无法杖': { cat: '法术穿透', label: '45%法穿', desc: '提供 45% 百分比法术穿透，击穿高魔抗装备' },
      '日暮之流': { cat: '法术穿透', label: '叠层240法穿', desc: '技能命中叠加层数，最高获得 240 点固定法术穿透' },
      '回响之杖': { cat: '技能特效', label: '技能爆炸', desc: '技能命中触发小范围法术爆炸伤害，提升消耗' },
      '痛苦面具': { cat: '技能特效', label: '多段生命法伤', desc: '技能命中触发 4 段相当于目标当前生命百分比的法伤' },
      '巫术法杖': { cat: '强击机制', label: '强击·法伤爆发', desc: '技能后普攻附带高额法强加成法伤与 8% 移速 (2.5s CD)' },
      '金色圣剑': { cat: '普攻特效', label: '圣剑法伤普攻', desc: '普攻叠满后额外提升 20% 攻速并附带 0.3AP 法术伤害' },
      '噬神之书': { cat: '吸血续航', label: '24%法吸转冷缩', desc: '提供 24% 法术吸血，每 2% 法吸额外转化 1% 冷却缩减' },
      '梦魇之牙': { cat: '重伤减疗', label: '重伤挂毒', desc: '法术伤害命中降低目标 35% 生命回复与吸血持续 3 秒' },
      '辉月': { cat: '保命免伤', label: '1.5s绝对金身', desc: '主动进入 1.5 秒无敌与不可选中状态，规避爆发 (90s CD)' },
      '炽热支配': { cat: '保命免伤', label: '残血解控护盾', desc: '生命低于 30% 解除控制并获得吸收法伤护盾与 30% 加速' },
      '炽热支配者': { cat: '保命免伤', label: '残血解控护盾', desc: '生命低于 30% 解除控制并获得吸收法伤护盾与 30% 加速' },
      '时之预言': { cat: '双抗强化', label: '法强转双抗', desc: '按法强比例额外转化为高额物理防御与法术防御' },
      '破茧之衣': { cat: '减伤穿透', label: '法强转穿透减伤', desc: '按法强比例增加法穿与获得进场免伤' },
      '凝冰之息': { cat: '控场打断', label: '技能减速20%', desc: '技能命中造成持续 20% 移速削弱持续 2 秒' },
      '圣杯': { cat: '回复强化', label: '回蓝转回血', desc: '持续回复法力值，满蓝转化为持续生命回复' },

      // 鞋子与野刀
      '抵抗之靴': { cat: '韧性移动', label: '35%韧性', desc: '减少 35% 受控时间，减少被连环控死风险' },
      '影忍之足': { cat: '防御移动', label: '减10%普攻伤', desc: '减少 10% 受到的物理普攻伤害，近战克制普攻流' },
      '冷静之靴': { cat: '冷缩移动', label: '15%冷却缩减', desc: '提供高额技能冷却缩减，加快技能周转' },
      '秘法之靴': { cat: '穿透移动', label: '法穿回蓝', desc: '提供固定法术穿透与低法力时法力回复' },
      '疾步之靴': { cat: '游走移动', label: '脱战超高速', desc: '脱战后大幅提升移动速度，游走支援神装' },
      '急速战靴': { cat: '攻速移动', label: '25%攻速', desc: '提供攻击速度加成与普攻回血' },
      '贪婪之噬': { cat: '打野特权', label: '红野刀·物攻穿透', desc: '惩击升级为狂怒惩击，击败野怪叠加物理攻击、穿透与冷却' },
      '巨人之握': { cat: '打野特权', label: '肉野刀·生命叠层', desc: '惩击升级，击败野怪叠加最大生命与范围灼烧' },
      '符文大剑': { cat: '打野特权', label: '蓝野刀·法强溅射', desc: '击败野怪叠加法强与冷却，普攻/技能附带野怪灼烧' },

      // 游走与辅助核心装
      '极影·救赎': { cat: '辅助协同', label: '极影光环+救赎护盾', desc: '全队攻速冷却光环 + 主动为周围队友提供高额护盾 (60s CD)' },
      '极影·奔狼': { cat: '辅助协同', label: '极影光环+奔狼冲锋', desc: '全队攻速冷却光环 + 主动全队大幅提速冲锋开团 (120s CD)' },
      '极影·形昭': { cat: '辅助协同', label: '极影光环+形昭探草', desc: '全队攻速冷却光环 + 主动探照视野并对周围敌方减速 (60s CD)' },
      '极影·星泉': { cat: '辅助协同', label: '极影光环+星泉续航', desc: '全队攻速冷却光环 + 主动链接队友分摊伤害并补血回蓝 (60s CD)' },
      '近卫·救赎': { cat: '辅助协同', label: '近卫光环+救赎护盾', desc: '全队双抗常驻光环 + 主动为周围队友提供高额护盾 (60s CD)' },
      '近卫·奔狼': { cat: '辅助协同', label: '近卫光环+奔狼冲锋', desc: '全队双抗常驻光环 + 主动全队大幅提速冲锋开团 (120s CD)' },
      '近卫·形昭': { cat: '辅助协同', label: '近卫光环+形昭探草', desc: '全队双抗常驻光环 + 主动探照视野并对周围敌方减速 (60s CD)' },
      '近卫·星泉': { cat: '辅助协同', label: '近卫光环+星泉续航', desc: '全队双抗常驻光环 + 主动链接队友分摊伤害并补血回蓝 (60s CD)' },
      '极影': { cat: '辅助协同', label: '初级攻速光环', desc: '提供基础生命移速与全队攻速冷却光环' },
      '近卫': { cat: '辅助协同', label: '初级双抗光环', desc: '提供基础生命移速与全队双抗常驻光环' }
    };

    // 2. 双方相同装备对冲 (抵消双方完全相同的装备)
    const countB = {};
    namesB.forEach(n => countB[n] = (countB[n] || 0) + 1);

    const diffItemsA = [];
    validItemsA.forEach(it => {
      if ((countB[it.item_name] || 0) > 0) {
        countB[it.item_name]--;
      } else {
        diffItemsA.push(it);
      }
    });

    const countA = {};
    namesA.forEach(n => countA[n] = (countA[n] || 0) + 1);

    const diffItemsB = [];
    validItemsB.forEach(it => {
      if ((countA[it.item_name] || 0) > 0) {
        countA[it.item_name]--;
      } else {
        diffItemsB.push(it);
      }
    });

    if (diffItemsA.length === 0 && diffItemsB.length === 0) {
      box.innerHTML = `
        <div class="mechanic-empty-box">
          <div style="font-weight:600; color:var(--apple-text-primary); margin-bottom:4px; font-size:13px;">双方装备配置完全一致</div>
          <div style="font-size:11.5px; color:var(--apple-text-secondary);">两套方案装备完全相同，胜负重点取决于铭文配置与局内等级。</div>
        </div>
      `;
      return;
    }

    // 辅助函数：提取一件装备的机制定义 (有字典用字典，无字典用 passives 自动 fallback)
    const getItemMechanic = (it) => {
      const name = it.item_name;
      if (ITEM_MECHANIC_MAP[name]) {
        return {
          name,
          cat: ITEM_MECHANIC_MAP[name].cat,
          label: ITEM_MECHANIC_MAP[name].label,
          desc: ITEM_MECHANIC_MAP[name].desc
        };
      }
      if (it.passives && it.passives.length > 0) {
        const p = it.passives[0];
        return {
          name,
          cat: '专属被动',
          label: p.name || '核心机制',
          desc: p.desc || (it.des1 || '提供面板属性与实战增益')
        };
      }
      return {
        name,
        cat: '基础装备',
        label: '基础属性',
        desc: it.des1 ? it.des1.replace(/\s+/g, ' · ') : '提供基础面板数值加成'
      };
    };

    const mechsA = diffItemsA.map(getItemMechanic);
    const mechsB = diffItemsB.map(getItemMechanic);

    // 3. 智能寻找同类被动取向对撞 (例如同属强击机制、保命机制、重伤减疗等)
    const contrasts = [];
    const usedIdxA = new Set();
    const usedIdxB = new Set();

    mechsA.forEach((mA, idxA) => {
      mechsB.forEach((mB, idxB) => {
        if (!usedIdxA.has(idxA) && !usedIdxB.has(idxB) && mA.cat === mB.cat && mA.cat !== '基础装备') {
          contrasts.push({
            category: mA.cat,
            itemA: mA,
            itemB: mB
          });
          usedIdxA.add(idxA);
          usedIdxB.add(idxB);
        }
      });
    });

    const exclusiveA = mechsA.filter((_, idx) => !usedIdxA.has(idx));
    const exclusiveB = mechsB.filter((_, idx) => !usedIdxB.has(idx));

    let html = '';

    // 1. 机制取向差异 (同类被动选择不同)
    if (contrasts.length > 0) {
      html += `
        <div class="mechanic-section-group">
          <div class="mechanic-group-header">
            <span class="mechanic-group-tag tag-contrast">机制取向差异</span>
            <span class="mechanic-group-sub">同类被动选择不同</span>
          </div>
          <div class="mechanic-exclusive-list">
            ${contrasts.map(c => `
              <div class="mechanic-contrast-row">
                <div class="mechanic-contrast-side">
                  <span class="scheme-name-tag">方案 A</span>
                  <div class="m-contrast-title">${c.itemA.name} <span class="m-badge-pill">${c.itemA.label}</span></div>
                  <div class="m-item-desc">${c.itemA.desc}</div>
                </div>
                <div class="mechanic-contrast-vs">vs</div>
                <div class="mechanic-contrast-side">
                  <span class="scheme-name-tag">方案 B</span>
                  <div class="m-contrast-title">${c.itemB.name} <span class="m-badge-pill" style="color:#248a3d; background:rgba(52,199,89,0.1);">${c.itemB.label}</span></div>
                  <div class="m-item-desc">${c.itemB.desc}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // 2. 方案 A 独有机制
    if (exclusiveA.length > 0) {
      html += `
        <div class="mechanic-section-group">
          <div class="mechanic-group-header">
            <span class="mechanic-group-tag tag-a">方案 A 专属机制 (${exclusiveA.length} 项)</span>
          </div>
          <div class="mechanic-exclusive-list">
            ${exclusiveA.map(it => `
              <div class="mechanic-exclusive-item">
                <div class="m-item-head">
                  <span class="m-equip-name">${it.name}</span>
                  <span class="m-badge-pill">${it.label}</span>
                </div>
                <div class="m-item-desc">${it.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // 3. 方案 B 独有机制
    if (exclusiveB.length > 0) {
      html += `
        <div class="mechanic-section-group">
          <div class="mechanic-group-header">
            <span class="mechanic-group-tag tag-b">方案 B 专属机制 (${exclusiveB.length} 项)</span>
          </div>
          <div class="mechanic-exclusive-list">
            ${exclusiveB.map(it => `
              <div class="mechanic-exclusive-item">
                <div class="m-item-head">
                  <span class="m-equip-name">${it.name}</span>
                  <span class="m-badge-pill" style="color:#248a3d; background:rgba(52,199,89,0.1);">${it.label}</span>
                </div>
                <div class="m-item-desc">${it.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    box.innerHTML = html;
  },

});
