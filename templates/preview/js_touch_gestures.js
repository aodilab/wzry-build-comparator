Object.assign(App, {
  initSheetDragGestures() {
    const modalConfigs = [
      { id: 'arcanaModal', onClose: () => this.recalculateAll() },
      { id: 'itemInspectorModal', onClose: null },
      { id: 'shopModal', onClose: null },
      { id: 'skillDetailModal', onClose: null },
    ];

    modalConfigs.forEach(cfg => {
      const modal = document.getElementById(cfg.id);
      if (!modal) return;
      const sheet = modal.querySelector('.sheet-box');
      if (!sheet) return;

      let isDragging = false;
      let startY = 0;
      let currentY = 0;
      let lastMoveY = 0;
      let lastMoveTime = 0;
      let velocityY = 0;
      let targetScrollEl = null;

      const findScrollableParent = (el) => {
        let cur = el;
        while (cur && cur !== sheet) {
          const style = window.getComputedStyle(cur);
          const ovY = style.overflowY;
          if ((ovY === 'auto' || ovY === 'scroll') && cur.scrollHeight > cur.clientHeight) {
            return cur;
          }
          cur = cur.parentElement;
        }
        return null;
      };

      const onPointerDown = (e) => {
        if (!modal.classList.contains('active')) return;
        if (e.button !== undefined && e.button !== 0) return;

        const target = e.target;
        const isCloseBtn = target.closest('.sheet-close-btn, .detail-modal-close-btn');
        if (isCloseBtn) return;

        const isInteractive = target.closest('button, input, .arc-cnt-btn, .apple-seg-item, .shop-grid-card, .btn-inspector-replace, .btn-inspector-unequip, a');
        const isGrabber = target.closest('.sheet-grabber, .sheet-title-bar, .detail-modal-header');

        if (isInteractive && !isGrabber) {
          return;
        }

        targetScrollEl = findScrollableParent(target);
        startY = e.clientY;
        currentY = e.clientY;
        lastMoveY = e.clientY;
        lastMoveTime = Date.now();
        velocityY = 0;
        isDragging = false;

        if (isGrabber) {
          isDragging = true;
          sheet.style.transition = 'none';
        }

        window.addEventListener('pointermove', onPointerMove, { passive: false });
        window.addEventListener('pointerup', onPointerUp);
        window.addEventListener('pointercancel', onPointerUp);
      };

      const onPointerMove = (e) => {
        const dy = e.clientY - startY;
        const now = Date.now();
        const dt = now - lastMoveTime;
        if (dt > 0) {
          velocityY = (e.clientY - lastMoveY) / dt;
        }
        lastMoveY = e.clientY;
        lastMoveTime = now;
        currentY = e.clientY;

        if (!isDragging) {
          if (targetScrollEl && targetScrollEl.scrollTop > 0) {
            return;
          }
          if (dy > 8 || (dy < -8 && !targetScrollEl)) {
            isDragging = true;
            sheet.style.transition = 'none';
          } else {
            return;
          }
        }

        if (e.cancelable) e.preventDefault();

        let translateY = 0;
        if (dy > 0) {
          translateY = dy;
        } else {
          translateY = dy * 0.22;
        }

        sheet.style.transform = 'translateY(' + translateY + 'px)';

        const sheetH = sheet.offsetHeight || 500;
        if (dy > 0) {
          const fade = Math.max(0.12, 1 - (dy / (sheetH * 0.85)));
          modal.style.opacity = fade.toFixed(3);
          const sheetFade = Math.max(0.70, 1 - (dy / (sheetH * 1.1)) * 0.35);
          sheet.style.opacity = sheetFade.toFixed(3);
        } else {
          modal.style.opacity = '1';
          sheet.style.opacity = '1';
        }
      };

      const onPointerUp = (e) => {
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('pointerup', onPointerUp);
        window.removeEventListener('pointercancel', onPointerUp);

        if (!isDragging) return;
        isDragging = false;

        const dy = currentY - startY;
        const sheetH = sheet.offsetHeight || 500;
        const dismissThreshold = Math.min(100, sheetH * 0.22);
        const isFlickDown = velocityY > 0.55 && dy > 45;
        const shouldDismiss = dy > dismissThreshold || isFlickDown;

        if (shouldDismiss) {
          sheet.style.transition = 'transform 0.26s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.26s ease';
          sheet.style.transform = 'translateY(100%)';
          sheet.style.opacity = '0';
          modal.style.transition = 'opacity 0.26s cubic-bezier(0.32, 0.72, 0, 1)';
          modal.style.opacity = '0';
          setTimeout(() => {
            modal.classList.remove('active');
            modal.style.opacity = '';
            modal.style.transition = '';
            sheet.style.transform = '';
            sheet.style.opacity = '';
            sheet.style.transition = '';
            if (cfg.onClose) cfg.onClose();
          }, 260);
        } else {
          sheet.style.transition = 'transform 0.36s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.36s ease';
          sheet.style.transform = 'translateY(0)';
          sheet.style.opacity = '1';
          modal.style.transition = 'opacity 0.36s ease';
          modal.style.opacity = '1';
          setTimeout(() => {
            sheet.style.transform = '';
            sheet.style.opacity = '';
            sheet.style.transition = '';
            modal.style.opacity = '';
            modal.style.transition = '';
          }, 360);
        }
      };

      sheet.addEventListener('pointerdown', onPointerDown);
    });
  }
});

window.App = App;
window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
