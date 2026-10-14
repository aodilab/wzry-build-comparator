// 双轨推演室：连招切换、全量重算与装备商店面板方法
const DATASET = require('../../data/dataset.js');
const { calcBuildStats, calcComboOutcome } = require('./calc.js');
const {
  formatAppleWinnerPill,
  computeMechanicDifferences,
  computeSpecsTable,
  formatInspectorItem,
  formatShopInspectorItem,
  formatArcanaSummary
} = require('./mechanic_engine.js');
const { buildSkillDetailData } = require('./skill_breakdown.js');

module.exports = {
  toggleComboMenu() {
    this.setData({ showComboMenu: !this.data.showComboMenu });
  },

  closeComboMenu() {
    if (this.data.showComboMenu) {
      this.setData({ showComboMenu: false });
    }
  },

  stopProp() {},
  noop() {},

  selectCombo(e) {
    const idx = Number(e.currentTarget.dataset.index);
    const combos = this.combosList || [];
    const active = combos[idx] || combos[0];
    this.setData({
      activeComboIdx: idx,
      activeCombo: active,
      showComboMenu: false
    });
    this.recalculateAll();
  },

  setStatsFilter(e) {
    const diffOnly = Boolean(e.currentTarget.dataset.diff);
    this.setData({ filterStatsDiffOnly: diffOnly });
    this.recalculateAll();
  },

  recalculateAll() {
    const hero = this.heroObj;
    if (!hero) return;
    const arcDict = DATASET.ARCANA_DATA || {};
    const leftItems = this.leftItemsList;
    const rightItems = this.rightItemsList;
    const leftArc = this.leftArcState;
    const rightArc = this.rightArcState;

    const statsA = calcBuildStats(hero, leftItems, leftArc, arcDict);
    const statsB = calcBuildStats(hero, rightItems, rightArc, arcDict);
    const combo = (this.combosList && this.combosList[this.data.activeComboIdx]) || { keys: '1A2A', name: '常规爆发' };
    const outA = calcComboOutcome(combo, statsA, hero);
    const outB = calcComboOutcome(combo, statsB, hero);

    const currentLane = this.data.currentLane;
    const isSupport = (hero.role && hero.role.includes('辅助')) || currentLane === '游走';
    const isJungle = currentLane === '打野';
    const isMageHero = Boolean(hero.role && hero.role.includes('法师'));

    const pills = {
      dmgSquishy: formatAppleWinnerPill(outA.dmgSquishy || 0, outB.dmgSquishy || 0, '点'),
      dmgTank: formatAppleWinnerPill(outA.dmgTank || 0, outB.dmgTank || 0, '点'),
      ehpPhys: formatAppleWinnerPill(outA.ehpPhys || 0, outB.ehpPhys || 0, '点'),
      ehpMagic: formatAppleWinnerPill(outA.ehpMagic || 0, outB.ehpMagic || 0, '点'),
      supportUtil: formatAppleWinnerPill(outA.supportUtility || 0, outB.supportUtility || 0, '点'),
      buffTime: formatAppleWinnerPill(outA.buffTime || 0, outB.buffTime || 0, 's', true),
      dragonTime: formatAppleWinnerPill(outA.dragonTime || 0, outB.dragonTime || 0, 's', true),
      vamp: formatAppleWinnerPill(outA.aHitVamp || 0, outB.aHitVamp || 0, '点'),
      regen: formatAppleWinnerPill(outA.outOfCombatRegen || 0, outB.outOfCombatRegen || 0, '点/s'),
      healReg: formatAppleWinnerPill(outA.regularHeal || 0, outB.regularHeal || 0, '点'),
      clutchHeal: formatAppleWinnerPill(outA.clutchHeal || 0, outB.clutchHeal || 0, '点')
    };

    const heroSkillsRaw = ((DATASET.HERO_SKILLS || {})[hero.cname]) || [];
    const activeSkills = heroSkillsRaw.length >= 4 ? heroSkillsRaw.slice(1, 4) : [];
    const baseCds = activeSkills.length === 3
      ? activeSkills.map((sk, i) => sk.cd_sec || [5.0, 6.0, 12.0][i])
      : [5.0, 6.0, 12.0];
    const skillTitles = activeSkills.length === 3
      ? activeSkills.map((sk, i) => `${i + 1}技能 · ${(sk.name || '').split('(')[0].split('（')[0].trim()}`)
      : ['1技能实际真空期', '2技能实际真空期', '3技能 (大招) 实际真空期'];
    const skillSubs = [
      `主力起手/主要消耗技能实战冷却 (基准 ${baseCds[0].toFixed(1)}s)`,
      `核心位移/保命控制技能实战冷却 (基准 ${baseCds[1].toFixed(1)}s)`,
      `团战决定性大招实战冷却 (基准 ${baseCds[2].toFixed(1)}s)`
    ];
    const cdRows = skillTitles.map((title, idx) => {
      const cA = +(baseCds[idx] * (1 - statsA.cdr / 100)).toFixed(1);
      const cB = +(baseCds[idx] * (1 - statsB.cdr / 100)).toFixed(1);
      return {
        title,
        sub: skillSubs[idx],
        cdA: cA,
        cdB: cB,
        pill: formatAppleWinnerPill(cA, cB, 's', true)
      };
    });

    const mechanicDiff = computeMechanicDifferences(leftItems, rightItems);
    const displaySpecRows = computeSpecsTable(hero, statsA, statsB, this.data.filterStatsDiffOnly);

    this.statsACache = statsA;
    this.statsBCache = statsB;

    this.setData({
      combatSectionTitle: isSupport ? '辅助团队价值与承伤对决' : '实战伤害对决',
      combatSectionDesc: isSupport ? '测算依据：全队护盾/治疗量 + 极限有效物理与法术承伤上限 (EHP) + 开团控制冷却' : '双抗折算实战净掉血',
      skillEntryDesc: isSupport ? '团队光环 / 护盾治疗 / 承伤极限' : '伤害 / 控制 / 回复物理拆解',
      leftItems,
      rightItems,
      hasLeftItems: leftItems.some(Boolean),
      hasRightItems: rightItems.some(Boolean),
      leftArcSummary: formatArcanaSummary(leftArc),
      rightArcSummary: formatArcanaSummary(rightArc),
      isSupport,
      isJungle,
      dmgSquishyA: (outA.dmgSquishy || 0).toLocaleString(),
      dmgSquishyB: (outB.dmgSquishy || 0).toLocaleString(),
      dmgTankA: (outA.dmgTank || 0).toLocaleString(),
      dmgTankB: (outB.dmgTank || 0).toLocaleString(),
      ehpPhysA: (outA.ehpPhys || 0).toLocaleString(),
      ehpPhysB: (outB.ehpPhys || 0).toLocaleString(),
      ehpMagicA: (outA.ehpMagic || 0).toLocaleString(),
      ehpMagicB: (outB.ehpMagic || 0).toLocaleString(),
      supportUtilA: (outA.supportUtility || 0).toLocaleString(),
      supportUtilB: (outB.supportUtility || 0).toLocaleString(),
      vampTitle: isMageHero ? '单次技能/普攻吸血' : '普攻单次吸血',
      vampSub: isMageHero ? '法术吸血/物理吸血单次实算' : '物理吸血率单次普攻实算',
      statsA,
      statsB,
      outA,
      outB,
      pills,
      cdRows,
      mechanicDiff,
      displaySpecRows
    });
  },

  // 1. 装备检视弹窗 (Item Inspector)
  openItemInspector(e) {
    const side = e.currentTarget.dataset.side;
    const idx = Number(e.currentTarget.dataset.index);
    const items = side === 'left' ? this.leftItemsList : this.rightItemsList;
    const it = items[idx];
    if (!it) return;
    this.recordCurrentScroll();

    this.setData({
      inspectorSide: side,
      inspectorSlotIdx: idx,
      inspectorItem: formatInspectorItem(it),
      showItemInspector: true,
      isAnyModalOpen: true,
      'sheetBoxStyle.inspector': '',
      'sheetMaskStyle.inspector': ''
    });
  },

  closeItemInspector() {
    this.setData({
      showItemInspector: false,
      isAnyModalOpen: this.checkAnyModalOpen('inspector')
    });
    this.restorePageScroll();
  },

  openShopFromInspector() {
    const side = this.data.inspectorSide;
    const idx = this.data.inspectorSlotIdx;
    this.closeItemInspector();
    this.openShopSheetInternal(side, idx);
  },

  unequipFromInspector() {
    const side = this.data.inspectorSide;
    const idx = this.data.inspectorSlotIdx;
    this.closeItemInspector();
    this.unequipSlotAt(side, idx);
  },

  unequipSlotAt(side, idx) {
    if (side === 'left') {
      this.leftItemsList[idx] = null;
      this.setData({
        isLeftCustomMode: true,
        officialSchemeIdx: -1,
        leftBuildTitle: '我的实战方案',
        leftTitleIsPrompt: false
      });
    } else {
      this.rightItemsList[idx] = null;
      const countB = this.rightItemsList.filter(Boolean).length;
      this.setData({
        rightBuildTitle: countB === 0 ? '请搭配您的实战出装' : '我的实战方案',
        rightTitleIsPrompt: countB === 0
      });
    }
    this.recalculateAll();
  },

  // 2. 装备商店抽屉 (Shop Sheet)
  openShopSheet(e) {
    const side = e.currentTarget.dataset.side;
    const idx = Number(e.currentTarget.dataset.index);
    this.openShopSheetInternal(side, idx);
  },

  openShopSheetInternal(side, idx) {
    const curItem = side === 'left' ? this.leftItemsList[idx] : this.rightItemsList[idx];
    const targetSlotLabel = (side === 'left' ? '方案 A' : '方案 B') + ' 第 ' + (idx + 1) + ' 格';
    this.recordCurrentScroll();
    this.setData({
      targetSide: side,
      targetSlotIdx: idx,
      targetSlotLabel,
      canUnequipCurrentSlot: Boolean(curItem),
      shopKw: '',
      previewingItemName: curItem ? curItem.item_name : '',
      showShopSheet: true,
      isAnyModalOpen: true,
      'sheetBoxStyle.shop': '',
      'sheetMaskStyle.shop': ''
    });
    this.refreshShopList();
  },

  closeShopSheet() {
    this.setData({
      showShopSheet: false,
      isAnyModalOpen: this.checkAnyModalOpen('shop')
    });
    this.restorePageScroll();
  },

  unequipCurrentSlot() {
    this.closeShopSheet();
    this.unequipSlotAt(this.data.targetSide, this.data.targetSlotIdx);
  },

  setShopCat(e) {
    const cat = e.currentTarget.dataset.cat;
    this.setData({ shopCat: cat });
    this.refreshShopList();
  },

  onShopSearch(e) {
    const kw = (e.detail.value || '').trim().toLowerCase();
    this.setData({ shopKw: kw });
    this.refreshShopList();
  },

  refreshShopList() {
    let list = DATASET.ITEMS_DATA || [];
    const cat = this.data.shopCat;
    const kw = this.data.shopKw;
    if (cat !== '全部') list = list.filter(it => it.category === cat);
    if (kw) {
      list = list.filter(it =>
        (it.item_name && it.item_name.toLowerCase().includes(kw)) ||
        (it.des1 && it.des1.toLowerCase().includes(kw)) ||
        (it.des2 && it.des2.toLowerCase().includes(kw))
      );
    }
    let previewName = this.data.previewingItemName;
    if (list.length > 0 && (!previewName || !list.some(it => it.item_name === previewName))) {
      previewName = list[0].item_name;
    }
    const previewItem = (DATASET.ITEMS_DATA || []).find(x => x.item_name === previewName) || null;
    this.setData({
      filteredShopItems: list,
      previewingItemName: previewName,
      shopInspector: formatShopInspectorItem(previewItem)
    });
  },

  previewShopItem(e) {
    const name = e.currentTarget.dataset.name;
    const now = Date.now();
    if (this.lastTappedShopItem === name && (now - (this.lastTappedShopTime || 0)) < 320) {
      this.confirmEquipItemByName(name);
      return;
    }
    this.lastTappedShopItem = name;
    this.lastTappedShopTime = now;
    const previewItem = (DATASET.ITEMS_DATA || []).find(x => x.item_name === name) || null;
    this.setData({
      previewingItemName: name,
      shopInspector: formatShopInspectorItem(previewItem)
    });
  },

};
