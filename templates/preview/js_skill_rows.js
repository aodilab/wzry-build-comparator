Object.assign(App, {
  formatSkillDiffPill(valA, valB, unit = "", lowerIsBetter = false) {
    if (typeof valA === "number" && typeof valB === "number") {
      const diff = valB - valA;
      if (Math.abs(diff) < 0.01) {
        return `<span class="diff-dash">—</span>`;
      }
      const isBetterB = lowerIsBetter ? (diff < 0) : (diff > 0);
      const diffAbs = Math.abs(diff).toFixed(diff % 1 === 0 ? 0 : 1);
      if (isBetterB) {
        const prefix = lowerIsBetter ? "-" : "+";
        return `<span class="apple-diff-pill pill-b-better">${prefix}${diffAbs}${unit}</span>`;
      } else {
        const prefix = lowerIsBetter ? "-" : "+";
        return `<span class="apple-diff-pill pill-a-better">${prefix}${diffAbs}${unit}</span>`;
      }
    }
    if (valA === valB) {
      return `<span class="diff-dash">—</span>`;
    }
    return `<span class="apple-diff-pill pill-diff">机制差异</span>`;
  },

  openSkillDetailModal() {
    const h = this.hero;
    if (!h) return;
    this.renderSkillDetailModal();
    const modal = document.getElementById('skillDetailModal');
    if (!modal) return;
    const sheet = modal.querySelector('.sheet-box');
    if (sheet) {
      sheet.style.transform = 'translateY(100%)';
      sheet.style.transition = 'none';
    }
    modal.classList.add('active');
    if (sheet) {
      void sheet.offsetHeight;
      requestAnimationFrame(() => {
        sheet.style.transition = 'transform 0.36s cubic-bezier(0.32, 0.72, 0, 1)';
        sheet.style.transform = 'translateY(0)';
      });
    }
  },

  closeSkillDetailModal() {
    const modal = document.getElementById('skillDetailModal');
    if (!modal) return;
    const sheet = modal.querySelector('.sheet-box');
    if (sheet) {
      sheet.style.transition = 'transform 0.28s cubic-bezier(0.32, 0.72, 0, 1)';
      sheet.style.transform = 'translateY(100%)';
    }
    modal.style.transition = 'opacity 0.28s cubic-bezier(0.32, 0.72, 0, 1)';
    modal.style.opacity = '0';
    setTimeout(() => {
      modal.classList.remove('active');
      modal.style.opacity = '';
      modal.style.transition = '';
      if (sheet) {
        sheet.style.transform = '';
        sheet.style.transition = '';
      }
    }, 280);
  },

  createSkillRowHelpers() {
    const formatSkillBadge = (base, mechTag = "") => {
      const bStr = typeof base === 'number' ? base.toFixed(1).replace(/\.0$/, '') : String(base).replace(/\.0$/, '');
      const txt = mechTag ? `${mechTag} · 初CD ${bStr}s` : `初始CD ${bStr}s`;
      return `<span class="skill-cd-badge">${txt}</span>`;
    };

    const formatEffectLabel = (s) => {
      if (s.hasDragon) {
        if (s.hasMaster) return "宗师 + 怒龙";
        if (s.hasIce) return "冰痕 + 怒龙";
        if (s.hasWushu) return "巫术 + 怒龙";
        return "平A + 怒龙";
      }
      if (s.hasMaster) return "宗师强击";
      if (s.hasIce) return "冰痕强击";
      if (s.hasWushu) return "巫术强击";
      return "常规平A";
    };

    let pendingRow = null;

    const renderDiffBadge = (valA, valB, unit = "", lowerIsBetter = false) => {
      if (typeof valA === "number" && typeof valB === "number") {
        const diff = valB - valA;
        if (Math.abs(diff) < 0.01) return { aWins: false, bWins: false, badgeA: "", badgeB: "" };
        const isBetterB = lowerIsBetter ? (diff < 0) : (diff > 0);
        const diffAbs = Math.abs(diff).toFixed(diff % 1 === 0 ? 0 : 1);
        if (isBetterB) {
          const prefix = lowerIsBetter ? "-" : "+";
          return {
            aWins: false,
            bWins: true,
            badgeA: "",
            badgeB: `<span class="win-diff-pill win-b">${prefix}${diffAbs}${unit}</span>`
          };
        } else {
          const prefix = lowerIsBetter ? "-" : "+";
          return {
            aWins: true,
            bWins: false,
            badgeA: `<span class="win-diff-pill win-a">${prefix}${diffAbs}${unit}</span>`,
            badgeB: ""
          };
        }
      }
      return { aWins: false, bWins: false, badgeA: "", badgeB: "" };
    };

    const fmtVal = (v, unit = "") => {
      if (typeof v === 'number') {
        const numStr = (v % 1 === 0) ? String(Math.round(v)) : v.toFixed(1);
        return (unit === 's' ? v.toFixed(1) : numStr) + unit;
      }
      return v;
    };

    const renderDualDmgRow = (title, squishyA, squishyB, tankA, tankB, unit = "") => {
      const resSq = renderDiffBadge(squishyA, squishyB, unit, false);
      return `
        <div class="skill-metric-row dual-dmg-row">
          <div class="m-name-col">
            <div class="m-metric-title">${title}</div>
            <div class="m-metric-sub">中射 / 坦克</div>
          </div>
          <div class="m-val-col left">
            <div class="val-primary ${resSq.aWins ? 'win-a' : ''}">
              ${fmtVal(squishyA, unit)}
              ${resSq.badgeA}
            </div>
            <div class="val-secondary">
              ${fmtVal(tankA, unit)}
            </div>
          </div>
          <div class="m-val-col right">
            <div class="val-primary ${resSq.bWins ? 'win-b' : ''}">
              ${fmtVal(squishyB, unit)}
              ${resSq.badgeB}
            </div>
            <div class="val-secondary">
              ${fmtVal(tankB, unit)}
            </div>
          </div>
        </div>
      `;
    };

    const renderSingleRow = (name, valA, valB, unit = "", lowerIsBetter = false) => {
      let mainTitle = name;
      let subTitle = "";

      if (mainTitle.includes("(真实伤害)")) {
        mainTitle = mainTitle.replace("(真实伤害)", "").trim();
        subTitle = "真实伤害 · 穿透护甲";
      } else if (mainTitle.includes("(无视坦克护甲)")) {
        mainTitle = mainTitle.replace("(无视坦克护甲)", "").trim();
        subTitle = "对坦克 · 真实伤害";
      } else if (mainTitle.includes("物理承伤上限")) {
        mainTitle = "极限物理承伤";
        subTitle = "物理EHP (防具折算)";
      } else if (mainTitle.includes("法术承伤上限")) {
        mainTitle = "极限法术承伤";
        subTitle = "法术EHP (防具折算)";
      } else if (mainTitle.includes("终极真血护盾吸收量")) {
        mainTitle = "终极大招护盾";
        subTitle = "40%最大生命值吸收";
      } else if (mainTitle.includes("护盾庇护吸收量")) {
        const prefix = mainTitle.replace("护盾庇护吸收量", "").trim();
        mainTitle = prefix ? `${prefix}护盾` : "护盾庇护量";
        subTitle = "实战吸收总量";
      } else if (mainTitle.includes("生命回复总量")) {
        const prefix = mainTitle.replace("生命回复总量", "").trim();
        mainTitle = prefix ? `${prefix}回复` : "生命回复量";
        subTitle = "实战治疗总量";
      } else if (mainTitle.includes("绝境急救")) {
        mainTitle = "绝境急救回复";
        subTitle = "血量≤30% · 不死鸟增幅";
      } else if (mainTitle.includes("最大生命值上限")) {
        mainTitle = "最大生命上限";
        subTitle = "基础体质+装备铭文";
      } else if (mainTitle.includes("辅助装主动技能")) {
        mainTitle = "辅助装主动";
        subTitle = "局内主动技能";
      } else if (mainTitle.includes("团队常驻防御光环")) {
        mainTitle = "团队防御光环";
        subTitle = "全队常驻增益";
      } else if (mainTitle.includes("移动速度")) {
        mainTitle = "实战移动速度";
        subTitle = "转线支援跑图";
      } else if (mainTitle.includes("普攻频次")) {
        mainTitle = "实际普攻频次";
        subTitle = "攻速档位折算";
      } else if (mainTitle.includes("强击与法术特效") || mainTitle.includes("强化与法术特效")) {
        mainTitle = "强击法术特效";
        subTitle = "被动机制协同";
      } else if (mainTitle.includes("强击与特效机制")) {
        mainTitle = "强击被动特效";
        subTitle = "装备机制协同";
      } else if (mainTitle.includes("单发普攻吸血") || mainTitle.includes("单次普攻吸血")) {
        mainTitle = "普攻物理吸血";
        subTitle = "单发吸血回复";
      } else if (mainTitle.includes("单发技能法术吸血")) {
        mainTitle = "技能法术吸血";
        subTitle = "单发吸血回复";
      } else if (mainTitle.includes("附带减速软控")) {
        mainTitle = "减速留人软控";
        subTitle = "技能+冰痕被动";
      } else if (mainTitle.includes("抽取护盾")) {
        mainTitle = "抽取护盾上限";
        subTitle = "最大护盾吸收量";
      } else if (mainTitle.includes("护盾转化")) {
        mainTitle = "护盾转化回复";
        subTitle = "护盾转生命值";
      } else if (mainTitle.includes("(中射)")) {
        mainTitle = mainTitle.replace("(中射)", "").trim();
        subTitle = "对中射 · 350物防";
      } else if (mainTitle.includes("(坦克)")) {
        mainTitle = mainTitle.replace("(坦克)", "").trim();
        subTitle = "对坦克 · 1000物防";
      }

      const res = renderDiffBadge(valA, valB, unit, lowerIsBetter);

      return `
        <div class="skill-metric-row single-row">
          <div class="m-name-col">
            <div class="m-metric-title">${mainTitle}</div>
            ${subTitle ? `<div class="m-metric-sub">${subTitle}</div>` : ''}
          </div>
          <div class="m-val-col left">
            <div class="val-single ${res.aWins ? 'win-a' : ''}">
              ${fmtVal(valA, unit)}
              ${res.badgeA}
            </div>
          </div>
          <div class="m-val-col right">
            <div class="val-single ${res.bWins ? 'win-b' : ''}">
              ${fmtVal(valB, unit)}
              ${res.badgeB}
            </div>
          </div>
        </div>
      `;
    };

    return {
      formatSkillBadge,
      formatEffectLabel,
      renderDiffBadge,
      fmtVal,
      renderDualDmgRow,
      renderSingleRow
    };
  }
});
