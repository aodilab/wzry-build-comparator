// 双轨推演室：铭文搭配、技能弹窗与原生丝滑下拉手势
const DATASET = require('../../data/dataset.js');
const { formatArcanaSummary } = require('./mechanic_engine.js');
const { calcBuildStats } = require('./calc.js');
const { buildSkillDetailData } = require('./skill_breakdown.js');

module.exports = {
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
};
