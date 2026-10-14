// =========================================================
// Apple 高保真比较控制器 App (严格对齐 wzry.aodilab.com 业务逻辑)
// =========================================================
const App = {
  hallRole: '全部',
  hallKw: '',
  hero: null,
  currentLane: '',
  schemes: [],
  combos: [],
  activeComboIdx: 0,
  
  // 方案 A 与 方案 B 状态 (对齐 wzry.aodilab.com)
  leftItems: [null, null, null, null, null, null],
  leftArc: { red: {}, green: {}, blue: {} },
  leftSchemeType: 'official', // 'official' | 'custom'
  leftOfficialIdx: 0,
  
  rightItems: [null, null, null, null, null, null],
  rightArc: { red: {}, green: {}, blue: {} },
  rightSchemeType: 'custom', // 'unselected' | 'custom' | 'official'
  rightOfficialIdx: 1,

  targetSchemeSide: 'left',
  targetSide: 'left',
  targetSlotIdx: 0,
  shopCat: '全部',
  shopKw: '',
  arcColor: 'red',
  filterStatsDiffOnly: true,

  init() {
    this.renderHallSeg();
    this.renderHallHeroes();
    this.initSheetDragGestures();
    document.addEventListener('click', (e) => {
      const wrap = document.getElementById('dComboWrap');
      if (wrap && wrap.classList.contains('active') && !wrap.contains(e.target)) {
        wrap.classList.remove('active');
      }
    });
  },

  goToHall() {
    document.getElementById('pageHall').classList.add('active');
    document.getElementById('pageDetail').classList.remove('active');
    document.getElementById('navBackBtn').style.display = 'none';
    document.getElementById('navPageTitle').textContent = '王者出装推演';
  },

  goToDetail(hero, lane) {
    this.hero = hero;
    this.currentLane = lane;
    document.getElementById('pageHall').classList.remove('active');
    document.getElementById('pageDetail').classList.add('active');
    document.getElementById('navBackBtn').style.display = 'flex';
    document.getElementById('navPageTitle').textContent = `${hero.cname} · ${this.currentLane}`;

    this.initHeroStudio();
  },

  renderHallSeg() {
    const roles = ['全部', '坦克', '战士', '刺客', '法师', '射手', '辅助'];
    const el = document.getElementById('hallRoleSeg');
    el.innerHTML = roles.map(r => `
      <div class="apple-seg-item ${r === this.hallRole ? 'active' : ''}" onclick="App.setHallRole('${r}')">${r}</div>
    `).join('');
  },

  setHallRole(r) {
    this.hallRole = r;
    this.renderHallSeg();
    this.renderHallHeroes();
  },

  onHallSearch(kw) {
    this.hallKw = (kw || '').trim().toLowerCase();
    this.renderHallHeroes();
  },

  renderHallHeroes() {
    let list = window.DATASET.HEROES_DATA || [];
    if (this.hallRole !== '全部') list = list.filter(h => h.role && h.role.includes(this.hallRole));
    if (this.hallKw) list = list.filter(h => h.cname.toLowerCase().includes(this.hallKw) || (h.title && h.title.toLowerCase().includes(this.hallKw)));

    const grid = document.getElementById('hallHeroGrid');
    grid.innerHTML = list.map(h => `
      <div class="hall-hero-tile" onclick="App.onHeroCardClick('${h.cname}')">
        <img class="hall-hero-avatar" referrerpolicy="no-referrer" src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg" alt="${h.cname}">
        <div class="hall-hero-name">${h.cname}</div>
      </div>
    `).join('');
  },

  onHeroCardClick(cname) {
    const h = window.DATASET.HEROES_DATA.find(x => x.cname === cname);
    if (!h) return;
    const lanes = h.supported_lanes || [h.lane || '对抗路'];
    if (lanes.length === 1) {
      this.goToDetail(h, lanes[0]);
    } else {
      this.openLaneModal(h, lanes);
    }
  },

  openLaneModal(h, lanes) {
    this.pendingHero = h;
    document.getElementById('laneModalAvatar').src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg`;
    document.getElementById('laneModalName').textContent = h.cname;
    document.getElementById('laneModalRole').innerHTML = (h.role || '').split('/').map(r => `<span class="hero-role-pill">${r}</span>`).join('');
    document.getElementById('laneModalTitle').textContent = h.title || '国服英雄';

    const grid = document.getElementById('laneOptionsGrid');
    grid.innerHTML = lanes.map(lane => `
      <button class="lane-choice-btn" onclick="App.confirmLaneAndEnter(null, '${lane}')">${lane}</button>
    `).join('');

    document.getElementById('laneSelectModal').classList.add('active');
  },

  closeLaneModal(e) {
    if (e && e.target && e.target.classList.contains('lane-modal-card')) return;
    document.getElementById('laneSelectModal').classList.remove('active');
  },

  confirmLaneAndEnter(e, lane) {
    const h = this.pendingHero;
    document.getElementById('laneSelectModal').classList.remove('active');
    this.goToDetail(h, lane);
  },

  switchStudioLane(l) {
    this.currentLane = l;
    document.getElementById('navPageTitle').textContent = `${this.hero.cname} · ${l}`;
    this.initHeroStudio();
  },

  initHeroStudio() {
    const h = this.hero;
    document.getElementById('dHeroAvatar').src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg`;
    document.getElementById('dHeroName').textContent = h.cname;
    document.getElementById('dHeroRole').textContent = h.role;
    document.getElementById('dHeroTitle').textContent = `${h.title || '国服英雄'} · 15级满级神装对决`;

    // 动态分路切换 (苹果分段器)
    const pBox = document.getElementById('dLanePills');
    const lanes = (h.supported_lanes && h.supported_lanes.length > 0) ? h.supported_lanes : [this.currentLane];
    pBox.innerHTML = lanes.map(l => {
      const isCur = (l === this.currentLane);
      return `<div class="lane-choice-pill ${isCur ? 'active' : ''}" onclick="App.switchStudioLane('${l}')">${l}</div>`;
    }).join('');

    // 加载官方推荐流派
    const allBuilds = window.DATASET.OFFICIAL_HERO_BUILDS[h.cname] || {};
    let laneBuilds = [];
    if (allBuilds.lanes && allBuilds.lanes[this.currentLane]) {
      laneBuilds = allBuilds.lanes[this.currentLane];
    } else if (allBuilds.lanes) {
      const firstLane = Object.keys(allBuilds.lanes)[0];
      if (firstLane) laneBuilds = allBuilds.lanes[firstLane];
    }
    this.schemes = (laneBuilds && laneBuilds.length > 0) ? laneBuilds.map((b, idx) => ({
      title: b.title || b.genre || `方案${idx + 1}`,
      items: b.items || b.item_names || [],
      arcana: b.arcana || { red: {'异变':10}, green: {'鹰眼':10}, blue: {'隐匿':10} }
    })) : [{
      title: '系统推荐',
      items: h.recommended_equips || ["暗影战斧", "抵抗之靴", "冰痕之握", "反伤刺甲", "魔女斗篷", "破军"],
      arcana: { red: {'异变':10}, green: {'鹰眼':10}, blue: {'隐匿':10} }
    }];

    // 连招数据
    this.combos = window.DATASET.HERO_COMBOS[h.cname] || [{
      name: '常规实战连招',
      title: '13A2A',
      desc: '核心爆发输出'
    }];
    this.activeComboIdx = 0;
    this.renderComboSelector();

    // === 逻辑 100% 对齐 index.html 与 wzry.aodilab.com ===
    // 默认刚进来没有出装，提示用户选择对照出装
    this.isLeftCustomMode = false;
    this.officialSchemeIdx = -1;

    const titleEl = document.getElementById("leftBuildTitle");
    if (titleEl) {
      titleEl.textContent = "请选择您对照的出装";
      titleEl.classList.add("is-prompt");
    }

    const rTitleEl = document.getElementById("rightBuildTitle");
    if (rTitleEl) {
      rTitleEl.textContent = "请搭配您的实战出装";
      rTitleEl.classList.add("is-prompt");
    }

    // 方案 A 初始为 6 个空白槽位
    this.leftItems = [null, null, null, null, null, null];
    this.leftArc = { red: {}, blue: {}, green: {} };

    // 渲染方案 A 标签栏 (此时所有流派 Tab 均为待选状态)
    this.renderSchemeTabs();

    // 方案 B 默认同样为空白对比方案
    this.rightItems = [null, null, null, null, null, null];
    this.rightArc = { red: {}, blue: {}, green: {} };

    this.recalculateAll();
  },

};
window.App = App;
