// 王者出装推演 ｜ 页面二：双轨实战推演室控制器 (1:1 复刻 preview_miniprogram.html)
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


Page({
  data: {
    hero: {},
    heroAvatar: '',
    currentLane: '打野',
    supportedLanes: [],
    schemes: [],
    officialSchemeIdx: -1,
    isLeftCustomMode: false,
    leftBuildTitle: '请选择您对照的出装',
    leftTitleIsPrompt: true,
    rightBuildTitle: '请搭配您的实战出装',
    rightTitleIsPrompt: true,
    leftItems: [null, null, null, null, null, null],
    rightItems: [null, null, null, null, null, null],
    hasLeftItems: false,
    hasRightItems: false,
    leftArc: { red: {}, blue: {}, green: {} },
    rightArc: { red: {}, blue: {}, green: {} },
    leftArcSummary: { hasAny: false, groups: [] },
    rightArcSummary: { hasAny: false, groups: [] },

    // 连招与实战伤害对决
    comboOptions: [],
    activeComboIdx: 0,
    activeCombo: { name: '常规实战连招', key: '13A2A', desc: '核心爆发输出' },
    showComboMenu: false,
    isSupport: false,
    isJungle: false,
    combatSectionTitle: '实战伤害对决',
    combatSectionDesc: '双抗折算实战净掉血',
    skillEntryDesc: '伤害 / 控制 / 回复物理拆解',
    targetSlotLabel: '方案 A 第 1 格',

    // 指标数值与对比胶囊
    dmgSquishyA: '0',
    dmgSquishyB: '0',
    dmgTankA: '0',
    dmgTankB: '0',
    ehpPhysA: '0',
    ehpPhysB: '0',
    ehpMagicA: '0',
    ehpMagicB: '0',
    supportUtilA: '0',
    supportUtilB: '0',
    vampTitle: '普攻单次吸血',
    vampSub: '物理吸血率单次普攻实算',
    statsA: {},
    statsB: {},
    outA: {},
    outB: {},
    pills: {},
    cdRows: [],
    mechanicDiff: { isEmpty: true, contrasts: [], exclusiveA: [], exclusiveB: [] },
    filterStatsDiffOnly: true,
    displaySpecRows: [],
    combatSectionTitle: '实战伤害对决',
    combatSectionDesc: '双抗折算实战净掉血',
    skillEntryDesc: '伤害 / 控制 / 回复物理拆解',

    // 4 大底部抽屉 (Apple Sheets)
    showItemInspector: false,
    inspectorSide: 'left',
    inspectorSlotIdx: 0,
    inspectorItem: null,

    showShopSheet: false,
    targetSide: 'left',
    targetSlotIdx: 0,
    targetSlotLabel: '方案 A 第 1 格',
    canUnequipCurrentSlot: false,
    shopCats: ['全部', '攻击', '法术', '防御', '移动', '打野', '游走'],
    shopCat: '全部',
    shopKw: '',
    filteredShopItems: [],
    previewingItemName: '',
    shopInspector: null,

    showArcanaSheet: false,
    arcColor: 'red',
    arcColorTotalCount: 0,
    filteredArcanaList: [],

    showSkillDetailModal: false,
    skillDetailData: { benchmarkHint: '', cards: [] },

    // 下滑关闭手势样式与防滚动穿透标记
    isAnyModalOpen: false,
    sheetBoxStyle: { inspector: '', shop: '', arcana: '', skill: '' },
    sheetMaskStyle: { inspector: '', shop: '', arcana: '', skill: '' }
  },

  onLoad(options) {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
    const heroName = decodeURIComponent(options.heroName || options.hero || options.cname || '赵云');
    const lane = decodeURIComponent(options.lane || '');
    const heroObj = (DATASET.HEROES_DATA || []).find(h => h.cname === heroName) || (DATASET.HEROES_DATA || [])[0];
    if (!heroObj) return;

    const lanes = (heroObj.supported_lanes && heroObj.supported_lanes.length > 0)
      ? heroObj.supported_lanes
      : [heroObj.lane || '打野'];
    const currentLane = (lane && lanes.includes(lane)) ? lane : lanes[0];

    this.heroObj = heroObj;
    this.leftArcState = { red: {}, blue: {}, green: {} };
    this.rightArcState = { red: {}, blue: {}, green: {} };
    this.initHeroStudio(heroObj, currentLane);
  },

  onPageScroll(e) {
    if (!this.data.isAnyModalOpen && e && typeof e.scrollTop === 'number') {
      this.savedScrollTop = e.scrollTop;
    }
  },

  initHeroStudio(heroObj, currentLane) {
    const h = heroObj || this.heroObj;
    const lanes = (h.supported_lanes && h.supported_lanes.length > 0) ? h.supported_lanes : [currentLane];
    wx.setNavigationBarTitle({ title: `${h.cname} · ${currentLane}` });

    const allBuilds = (DATASET.OFFICIAL_HERO_BUILDS || {})[h.cname] || {};
    let laneBuilds = [];
    if (allBuilds.lanes && allBuilds.lanes[currentLane]) {
      laneBuilds = allBuilds.lanes[currentLane];
    } else if (allBuilds.lanes) {
      const firstLane = Object.keys(allBuilds.lanes)[0];
      if (firstLane) laneBuilds = allBuilds.lanes[firstLane];
    }
    const schemes = (laneBuilds && laneBuilds.length > 0) ? laneBuilds.map((b, idx) => ({
      title: b.title || b.genre || `方案${idx + 1}`,
      items: b.items || b.item_names || [],
      arcana: b.arcana || { red: { '异变': 10 }, green: { '鹰眼': 10 }, blue: { '隐匿': 10 } },
      isActive: false
    })) : [{
      title: '系统推荐',
      items: h.recommended_equips || ['暗影战斧', '抵抗之靴', '冰痕之握', '反伤刺甲', '魔女斗篷', '破军'],
      arcana: { red: { '异变': 10 }, green: { '鹰眼': 10 }, blue: { '隐匿': 10 } },
      isActive: false
    }];

    const rawCombos = (DATASET.HERO_COMBOS || {})[h.cname] || [{
      name: '常规实战连招',
      title: '13A2A',
      desc: '核心爆发输出'
    }];
    const comboOptions = rawCombos.map(c => ({
      name: c.name,
      key: c.title || c.keys || '',
      keys: c.keys || c.title || '13A2A',
      desc: c.desc || '',
      cleanDesc: (c.desc || '').replace(/.*?(实战连招|爆发|技巧|说明)[：:]\s*/, '').trim()
    }));

    this.schemesList = schemes;
    this.combosList = comboOptions;
    this.leftItemsList = [null, null, null, null, null, null];
    this.rightItemsList = [null, null, null, null, null, null];
    this.leftArcState = { red: {}, blue: {}, green: {} };
    this.rightArcState = { red: {}, blue: {}, green: {} };

    this.setData({
      hero: h,
      heroAvatar: `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg`,
      currentLane,
      supportedLanes: lanes,
      schemes,
      officialSchemeIdx: -1,
      isLeftCustomMode: false,
      leftBuildTitle: '请选择您对照的出装',
      leftTitleIsPrompt: true,
      rightBuildTitle: '请搭配您的实战出装',
      rightTitleIsPrompt: true,
      comboOptions,
      activeComboIdx: 0,
      activeCombo: comboOptions[0],
      showComboMenu: false
    });

    this.recalculateAll();
  },

  goBackToHall() {
    const pages = getCurrentPages();
    if (pages.length > 1) {
      wx.navigateBack({ delta: 1 });
    } else {
      wx.redirectTo({ url: '/pages/index/index' });
    }
  },

  switchStudioLane(e) {
    const lane = e.currentTarget.dataset.lane;
    if (!lane || lane === this.data.currentLane) return;
    this.initHeroStudio(this.heroObj, lane);
  },

  getItemsFromNames(names) {
    const all = DATASET.ITEMS_DATA || [];
    const res = (names || []).slice(0, 6).map(n => all.find(it => it.item_name === n) || null);
    while (res.length < 6) res.push(null);
    return res;
  },

  switchOfficialScheme(e) {
    const idx = Number(e.currentTarget.dataset.index);
    const schemes = (this.schemesList || []).map((s, i) => ({
      ...s,
      isActive: i === idx
    }));
    const activeOfficial = schemes[idx] || schemes[0] || { items: [] };
    this.leftItemsList = this.getItemsFromNames(activeOfficial.items || []);

    if (activeOfficial.arcana && Object.keys(activeOfficial.arcana).length > 0) {
      this.leftArcState = JSON.parse(JSON.stringify(activeOfficial.arcana));
    } else {
      const rec = this.heroObj.recommended_arcana || { red: '异变', blue: '隐匿', green: '鹰眼' };
      this.leftArcState = {
        red: { [rec.red || '异变']: 10 },
        blue: { [rec.blue || '隐匿']: 10 },
        green: { [rec.green || '鹰眼']: 10 }
      };
    }

    this.setData({
      schemes,
      officialSchemeIdx: idx,
      isLeftCustomMode: false,
      leftBuildTitle: '王者官方推荐',
      leftTitleIsPrompt: false
    });
    this.recalculateAll();
  },

  enableLeftCustomMode() {
    this.leftItemsList = [null, null, null, null, null, null];
    this.leftArcState = { red: {}, blue: {}, green: {} };
    const schemes = (this.schemesList || []).map(s => ({ ...s, isActive: false }));
    this.setData({
      schemes,
      isLeftCustomMode: true,
      officialSchemeIdx: -1,
      leftBuildTitle: '我的实战方案',
      leftTitleIsPrompt: false
    });
    this.recalculateAll();
  },

  resetOfficial() {
    this.leftItemsList = [null, null, null, null, null, null];
    this.leftArcState = { red: {}, blue: {}, green: {} };
    const schemes = (this.schemesList || []).map(s => ({ ...s, isActive: false }));
    this.setData({
      schemes,
      isLeftCustomMode: false,
      officialSchemeIdx: -1,
      leftBuildTitle: '请选择您对照的出装',
      leftTitleIsPrompt: true
    });
    this.recalculateAll();
  },

  applyCopyAToB() {
    this.rightItemsList = JSON.parse(JSON.stringify(this.leftItemsList));
    this.rightArcState = JSON.parse(JSON.stringify(this.leftArcState));
    this.setData({
      rightBuildTitle: '我的实战方案',
      rightTitleIsPrompt: false
    });
    this.recalculateAll();
  },

  clearRightScheme() {
    this.rightItemsList = [null, null, null, null, null, null];
    this.rightArcState = { red: {}, blue: {}, green: {} };
    this.setData({
      rightBuildTitle: '请搭配您的实战出装',
      rightTitleIsPrompt: true
    });
    this.recalculateAll();
  },

  onShareAppMessage() {
    const heroName = (this.heroObj && this.heroObj.cname) || '英雄';
    const lane = this.data.currentLane || '实战';
    return {
      title: `【王者出装推演】${heroName} · ${lane}神装实战方案对决`,
      path: `/pages/duel/duel?heroName=${encodeURIComponent(heroName)}&lane=${encodeURIComponent(lane)}`,
      imageUrl: this.data.heroAvatar || '/assets/app_icon.png'
    };
  },

  onShareTimeline() {
    const heroName = (this.heroObj && this.heroObj.cname) || '英雄';
    const lane = this.data.currentLane || '实战';
    return {
      title: `【王者出装推演】${heroName} · ${lane}实战出装对决与伤害拆解`,
      query: `heroName=${encodeURIComponent(heroName)}&lane=${encodeURIComponent(lane)}`,
      imageUrl: this.data.heroAvatar || '/assets/app_icon.png'
    };
  },


  // === 装备商店与推演计算方法 ===
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

  // === 铭文与交互手势方法 ===
  confirmEquipItem(e) {
    const name = e.currentTarget.dataset.name;
    this.confirmEquipItemByName(name);
  },

  confirmEquipItemByName(itemName) {
    const it = (DATASET.ITEMS_DATA || []).find(x => x.item_name === itemName);
    if (!it) return;
    if (this.data.targetSide === 'left') {
      this.leftItemsList[this.data.targetSlotIdx] = it;
      this.setData({
        isLeftCustomMode: true,
        officialSchemeIdx: -1,
        leftBuildTitle: '我的实战方案',
        leftTitleIsPrompt: false
      });
    } else {
      this.rightItemsList[this.data.targetSlotIdx] = it;
      this.setData({
        rightBuildTitle: '我的实战方案',
        rightTitleIsPrompt: false
      });
    }
    this.closeShopSheet();
    this.recalculateAll();
  },

  recordCurrentScroll() {
    wx.createSelectorQuery().selectViewport().scrollOffset((res) => {
      if (res && typeof res.scrollTop === 'number' && res.scrollTop >= 0) {
        this.savedScrollTop = res.scrollTop;
      }
    }).exec();
  },

  restorePageScroll() {
    const top = this.savedScrollTop;
    if (typeof top === 'number' && top > 0) {
      wx.pageScrollTo({
        scrollTop: top,
        duration: 0
      });
    }
  },

  // 3. 铭文配置抽屉 (Arcana Sheet)
  openArcanaSheet(e) {
    this.recordCurrentScroll();
    const side = e.currentTarget.dataset.side || 'left';
    const color = e.currentTarget.dataset.color || 'red';
    this.setData({
      targetSide: side,
      arcColor: color,
      showArcanaSheet: true,
      isAnyModalOpen: true,
      'sheetBoxStyle.arcana': '',
      'sheetMaskStyle.arcana': ''
    });
    this.refreshArcanaList();
  },

  closeArcanaSheet() {
    this.setData({
      showArcanaSheet: false,
      isAnyModalOpen: this.checkAnyModalOpen('arcana')
    });
    this.restorePageScroll();
    this.recalculateAll();
  },

  setArcanaColor(e) {
    const color = e.currentTarget.dataset.color;
    this.setData({ arcColor: color });
    this.refreshArcanaList();
  },

  refreshArcanaList() {
    const allArc = DATASET.ARCANA_DATA || {};
    const color = this.data.arcColor;
    const curCfg = this.data.targetSide === 'left' ? this.leftArcState : this.rightArcState;
    const curMap = curCfg[color] || {};
    const totalCount = Object.values(curMap).reduce((a, b) => a + b, 0);

    const filtered = Object.keys(allArc)
      .filter(k => (allArc[k].color_type === color || allArc[k].color === color))
      .map(k => ({
        name: k,
        icon: allArc[k].icon,
        propsText: allArc[k].raw_des || allArc[k].des || '',
        count: curMap[k] || 0
      }));

    this.setData({
      arcColorTotalCount: totalCount,
      filteredArcanaList: filtered
    });
  },

  changeArcanaCount(e) {
    const name = e.currentTarget.dataset.name;
    const delta = Number(e.currentTarget.dataset.delta);
    const side = this.data.targetSide;
    const color = this.data.arcColor;
    const targetCfg = side === 'left' ? this.leftArcState : this.rightArcState;
    if (!targetCfg[color]) targetCfg[color] = {};
    const curMap = targetCfg[color];
    const curVal = curMap[name] || 0;
    const curTotal = Object.values(curMap).reduce((a, b) => a + b, 0);

    if (delta > 0 && curTotal >= 10) return;
    const newVal = Math.max(0, Math.min(10, curVal + delta));
    if (newVal === 0) delete curMap[name];
    else curMap[name] = newVal;

    if (side === 'left') {
      this.setData({
        isLeftCustomMode: true,
        officialSchemeIdx: -1,
        leftBuildTitle: '我的实战方案',
        leftTitleIsPrompt: false
      });
    } else {
      this.setData({
        rightBuildTitle: '我的实战方案',
        rightTitleIsPrompt: false
      });
    }
    this.refreshArcanaList();
    this.recalculateAll();
  },

  clearCurrentArcanaColor() {
    const side = this.data.targetSide;
    const color = this.data.arcColor;
    const targetCfg = side === 'left' ? this.leftArcState : this.rightArcState;
    targetCfg[color] = {};
    if (side === 'left') {
      this.setData({
        isLeftCustomMode: true,
        officialSchemeIdx: -1,
        leftBuildTitle: '我的实战方案',
        leftTitleIsPrompt: false
      });
    } else {
      this.setData({
        rightBuildTitle: '我的实战方案',
        rightTitleIsPrompt: false
      });
    }
    this.refreshArcanaList();
    this.recalculateAll();
  },

  checkAnyModalOpen(closingModal = '') {
    const d = this.data;
    const inspector = closingModal === 'inspector' ? false : d.showItemInspector;
    const shop = closingModal === 'shop' ? false : d.showShopSheet;
    const arcana = closingModal === 'arcana' ? false : d.showArcanaSheet;
    const skill = closingModal === 'skill' ? false : d.showSkillDetailModal;
    return Boolean(inspector || shop || arcana || skill);
  },

  // 4. 各技能详细物理拆解二级视窗 (Skill Detail Modal)
  openSkillDetailModal() {
    const h = this.heroObj;
    if (!h) return;
    this.recordCurrentScroll();
    const heroSkills = ((DATASET.HERO_SKILLS || {})[h.cname]) || [];
    const skillDetailData = buildSkillDetailData(
      h,
      this.data.currentLane,
      this.statsACache || this.data.statsA,
      this.statsBCache || this.data.statsB,
      heroSkills,
      DATASET.OFFICIAL_ATTACK_ICON || ''
    );
    this.setData({
      skillDetailData,
      showSkillDetailModal: true,
      isAnyModalOpen: true,
      'sheetBoxStyle.skill': '',
      'sheetMaskStyle.skill': ''
    });
  },

  closeSkillDetailModal() {
    this.setData({
      showSkillDetailModal: false,
      isAnyModalOpen: this.checkAnyModalOpen('skill')
    });
    this.restorePageScroll();
  },

  // 5. 抽屉下滑手势关闭 (WXS 120fps 视图层跟手 + 逻辑层收尾)
  closeSheetFromWxs(payload) {
    const key = payload && payload.key;
    if (!key) return;
    if (key === 'inspector') this.closeItemInspector();
    else if (key === 'shop') this.closeShopSheet();
    else if (key === 'arcana') this.closeArcanaSheet();
    else if (key === 'skill') this.closeSkillDetailModal();
    this.restorePageScroll();
  },

  onSheetTouchStart(e) {
    if (!e.touches || e.touches.length === 0) return;
    this.dragSheetKey = e.currentTarget.dataset.sheet;
    this.dragStartY = e.touches[0].clientY;
    this.dragCurrentY = this.dragStartY;
    this.dragStartTime = Date.now();
  },

  onSheetTouchMove(e) {
    if (!this.dragSheetKey || !e.touches || e.touches.length === 0) return;
    const y = e.touches[0].clientY;
    const dy = y - this.dragStartY;
    this.dragCurrentY = y;
    if (dy <= 6) return;
    const key = this.dragSheetKey;
    this.setData({
      [`sheetBoxStyle.${key}`]: `transform: translate3d(0, ${dy}px, 0); transition: none;`
    });
  },

  onSheetTouchEnd() {
    const key = this.dragSheetKey;
    if (!key) return;
    this.dragSheetKey = null;
    const dy = (this.dragCurrentY || 0) - (this.dragStartY || 0);
    const dt = Math.max(1, Date.now() - (this.dragStartTime || Date.now()));
    const velocity = dy / dt;
    if (dy > 55 || (velocity > 0.35 && dy > 25)) {
      this.closeSheetFromWxs({ key });
      setTimeout(() => {
        this.setData({
          [`sheetBoxStyle.${key}`]: '',
          [`sheetMaskStyle.${key}`]: ''
        });
      }, 240);
    } else if (dy > 6) {
      this.setData({
        [`sheetBoxStyle.${key}`]: '',
        [`sheetMaskStyle.${key}`]: ''
      });
    }
  }
});
