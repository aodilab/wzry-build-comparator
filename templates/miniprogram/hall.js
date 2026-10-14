// 王者出装推演 ｜ 页面一：挑选英雄大厅 (1:1 复刻 preview_miniprogram.html)
const { HEROES_DATA } = require('../../data/dataset.js');

Page({
  data: {
    roles: ['全部', '坦克', '战士', '刺客', '法师', '射手', '辅助'],
    hallRole: '全部',
    hallKw: '',
    filteredHeroes: [],
    showLaneModal: false,
    pendingHero: null,
    pendingHeroRoles: [],
    pendingLanes: []
  },

  onLoad() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
    this.renderHallHeroes();
  },

  onShareAppMessage() {
    return {
      title: '王者出装箱 ｜ 双轨实战出装推演实验室',
      path: '/pages/index/index',
      imageUrl: '/assets/app_icon.png'
    };
  },

  onShareTimeline() {
    return {
      title: '王者出装箱 ｜ 133位英雄神装双轨实战推演',
      query: '',
      imageUrl: '/assets/app_icon.png'
    };
  },

  setHallRole(e) {
    const r = e.currentTarget.dataset.role;
    if (!r || r === this.data.hallRole) return;
    this.setData({ hallRole: r }, () => {
      this.renderHallHeroes();
    });
  },

  onHallSearch(e) {
    const kw = (e.detail.value || '').trim().toLowerCase();
    this.setData({ hallKw: kw }, () => {
      this.renderHallHeroes();
    });
  },

  renderHallHeroes() {
    const { hallRole, hallKw } = this.data;
    let list = HEROES_DATA || [];
    if (hallRole !== '全部') {
      list = list.filter(h => h.role && h.role.includes(hallRole));
    }
    if (hallKw) {
      list = list.filter(h =>
        (h.cname && h.cname.toLowerCase().includes(hallKw)) ||
        (h.title && h.title.toLowerCase().includes(hallKw))
      );
    }
    this.setData({ filteredHeroes: list });
  },

  onHeroCardClick(e) {
    const cname = e.currentTarget.dataset.cname;
    const h = (HEROES_DATA || []).find(x => x.cname === cname);
    if (!h) return;
    const lanes = (h.supported_lanes && h.supported_lanes.length > 0)
      ? h.supported_lanes
      : [h.lane || '对抗路'];
    if (lanes.length === 1) {
      this.goToDetail(h, lanes[0]);
    } else {
      this.openLaneModal(h, lanes);
    }
  },

  openLaneModal(h, lanes) {
    const roles = (h.role || '').split('/').filter(Boolean);
    this.setData({
      pendingHero: h,
      pendingHeroRoles: roles,
      pendingLanes: lanes,
      showLaneModal: true
    });
  },

  closeLaneModal() {
    this.setData({ showLaneModal: false });
  },

  confirmLaneAndEnter(e) {
    const lane = e.currentTarget.dataset.lane;
    const h = this.data.pendingHero;
    this.setData({ showLaneModal: false });
    if (h && lane) {
      this.goToDetail(h, lane);
    }
  },

  goToDetail(hero, lane) {
    const paramHero = encodeURIComponent(hero.cname || '');
    const paramLane = encodeURIComponent(lane || '');
    wx.navigateTo({
      url: `/pages/duel/duel?heroName=${paramHero}&lane=${paramLane}`
    });
  },

  stopProp() {}
});
