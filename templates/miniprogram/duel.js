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

const duelShopMethods = require('./duel_shop.js');
const duelArcanaTouchMethods = require('./duel_arcana_touch.js');

Page(Object.assign({
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

}, duelShopMethods, duelArcanaTouchMethods));
