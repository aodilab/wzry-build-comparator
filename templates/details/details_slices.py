# -*- coding: utf-8 -*-
"""
王者荣耀淘宝详情页 5 大核心切片卡片模板与文案
"""

SLICES = [
    # 01_详情页：旗舰面板与推演大典
    (
        "01_详情页_核心大典与版本.png",
        "2026 正式服全量清洗 · 收录 133 位英雄",
        "王者全英雄战术手册",
        '<span class="subtitle-badge">全套 6 册</span> <span>官方级全维度数据 ｜ 铭文出装大典</span>',
        """
        <div class="pro-card">
            <!-- 英雄抬头 -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f2f2f7; padding-bottom:16px;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="position:relative; width:64px; height:64px; border-radius:18px; padding:2px; background:linear-gradient(135deg, #f59e0b, #d97706); box-shadow:0 4px 14px rgba(245,158,11,0.25);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg" style="width:100%; height:100%; border-radius:16px; object-fit:cover; display:block;">
                        <div style="position:absolute; bottom:-4px; right:-4px; background:#1d1d1f; border:1px solid #f59e0b; color:#f59e0b; font-size:11px; font-weight:800; padding:1px 5px; border-radius:6px;">15</div>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:24px; font-weight:800; color:#1d1d1f;">廉颇</span>
                            <span style="background:#f2f2f7; color:#48484a; font-size:13px; font-weight:700; padding:3px 9px; border-radius:8px;">对抗路 / 坦克</span>
                        </div>
                        <div style="font-size:14px; color:#86868b; margin-top:3px;">正义爆轰 · 满级六神装与铭文最佳协同推演</div>
                    </div>
                </div>
                <div style="background:rgba(0,113,227,0.08); color:#0071e3; font-size:14px; font-weight:700; padding:6px 14px; border-radius:20px; border:1px solid rgba(0,113,227,0.2);">
                    • 实时算分引擎
                </div>
            </div>

            <!-- 六神装插槽 -->
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="font-size:13px; font-weight:700; color:#86868b; letter-spacing:0.02em;">六神装实战配置 (装备被动互斥与协同检测)</span>
                    <span style="color:#34c759; font-size:13px; font-weight:700;">✔ 装备被动无冲突</span>
                </div>
                <div style="display:flex; justify-content:space-between; gap:10px;">
                    <div style="flex:1; background:#fbfbfd; border:1px solid #ebebf0; border-radius:16px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1133.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #f59e0b; box-shadow:0 4px 10px rgba(0,0,0,0.06);">
                        <span style="font-size:12px; font-weight:700; color:#1d1d1f;">暗影战斧</span>
                    </div>
                    <div style="flex:1; background:#fbfbfd; border:1px solid #ebebf0; border-radius:16px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1332.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #f59e0b; box-shadow:0 4px 10px rgba(0,0,0,0.06);">
                        <span style="font-size:12px; font-weight:700; color:#1d1d1f;">不祥征兆</span>
                    </div>
                    <div style="flex:1; background:#fbfbfd; border:1px solid #ebebf0; border-radius:16px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1331.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #f59e0b; box-shadow:0 4px 10px rgba(0,0,0,0.06);">
                        <span style="font-size:12px; font-weight:700; color:#1d1d1f;">暴烈之甲</span>
                    </div>
                    <div style="flex:1; background:#fbfbfd; border:1px solid #ebebf0; border-radius:16px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1334.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #f59e0b; box-shadow:0 4px 10px rgba(0,0,0,0.06);">
                        <span style="font-size:12px; font-weight:700; color:#1d1d1f;">魔女斗篷</span>
                    </div>
                    <div style="flex:1; background:#fbfbfd; border:1px solid #ebebf0; border-radius:16px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1126.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #f59e0b; box-shadow:0 4px 10px rgba(0,0,0,0.06);">
                        <span style="font-size:12px; font-weight:700; color:#1d1d1f;">碎星锤</span>
                    </div>
                    <div style="flex:1; background:#fbfbfd; border:1px solid #ebebf0; border-radius:16px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1337.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #f59e0b; box-shadow:0 4px 10px rgba(0,0,0,0.06);">
                        <span style="font-size:12px; font-weight:700; color:#1d1d1f;">贤者庇护</span>
                    </div>
                </div>
            </div>

            <!-- 三大核心算分数据指标 -->
            <div style="background:#fbfbfd; border-radius:18px; padding:18px 20px; display:flex; justify-content:space-around; align-items:center; border:1px solid #f0f0f4;">
                <div style="text-align:center;">
                    <div style="font-size:13px; color:#86868b; margin-bottom:4px;">最终最大生命</div>
                    <div style="font-size:34px; font-weight:850; color:#1d1d1f; line-height:1;">11,280</div>
                    <div style="width:75px; height:4px; background:#e5e5ea; border-radius:2px; margin:6px auto 0 auto;"><div style="width:85%; height:100%; background:#0071e3; border-radius:2px;"></div></div>
                </div>
                <div style="width:1px; height:40px; background:#e5e5ea;"></div>
                <div style="text-align:center;">
                    <div style="font-size:13px; color:#86868b; margin-bottom:4px;">物理抗性免伤率</div>
                    <div style="font-size:34px; font-weight:850; color:#0071e3; line-height:1;">64.2%</div>
                    <div style="width:75px; height:4px; background:#e5e5ea; border-radius:2px; margin:6px auto 0 auto;"><div style="width:64.2%; height:100%; background:#0071e3; border-radius:2px;"></div></div>
                </div>
                <div style="width:1px; height:40px; background:#e5e5ea;"></div>
                <div style="text-align:center;">
                    <div style="font-size:13px; color:#86868b; margin-bottom:4px;">机制协同诊断</div>
                    <div style="font-size:34px; font-weight:850; color:#34c759; line-height:1;">100分</div>
                    <div style="width:75px; height:4px; background:#e5e5ea; border-radius:2px; margin:6px auto 0 auto;"><div style="width:100%; height:100%; background:#34c759; border-radius:2px;"></div></div>
                </div>
            </div>

            <!-- 卡片内置专属权益微注 -->
            <div class="card-footer-tip">
                <span>🎁 独家随包附赠 · <strong>在线配装推演沙盒</strong> (手机/电脑随时开)</span>
                <span style="color:#0071e3;">永久云端更新 ›</span>
            </div>
        </div>
        """
    ),

    # 02_详情页：克制案例全景
    (
        "02_详情页_阵容克制与搭档.png",
        "实战克制谱系 · BP针对破局",
        "133位英雄克制谱系",
        '<span class="subtitle-badge">对位破解</span> <span>对位克制解法 ｜ 最佳搭档阵容 ｜ 排位选人针对</span>',
        """
        <div class="pro-card">
            <!-- 克制组 1 -->
            <div style="background:#fbfbfd; border-radius:18px; padding:15px 18px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; border:2px solid #f59e0b; box-shadow:0 3px 10px rgba(245,158,11,0.25);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/141/141.jpg" style="width:100%; height:100%; object-fit:cover; display:block;">
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#1d1d1f;">貂蝉</div>
                        <div style="font-size:13px; color:#86868b;">中路 / 法刺核心</div>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
                    <span style="background:rgba(52,199,89,0.12); color:#248a3d; border:1px solid rgba(52,199,89,0.3); font-size:12px; font-weight:800; padding:2px 10px; border-radius:8px;">绝对压制 ➔</span>
                    <span style="font-size:11px; color:#86868b;">真伤风筝无解</span>
                </div>
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; border:2px solid #e5e5ea;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg" style="width:100%; height:100%; object-fit:cover; display:block;">
                    </div>
                    <div>
                        <div style="font-size:16px; font-weight:800; color:#1d1d1f;">笨重前排 (如廉颇/吕布)</div>
                        <div style="font-size:12px; color:#86868b;">坦度被真实伤害熔断</div>
                    </div>
                </div>
            </div>

            <!-- 克制组 2 -->
            <div style="background:#fbfbfd; border-radius:18px; padding:15px 18px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; border:2px solid #ff3b30; box-shadow:0 3px 10px rgba(255,59,48,0.25);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/187/187.jpg" style="width:100%; height:100%; object-fit:cover; display:block;">
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#1d1d1f;">东皇太一 / 张良</div>
                        <div style="font-size:13px; color:#86868b;">压制型绝对强控</div>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
                    <span style="background:rgba(255,59,48,0.12); color:#d70015; border:1px solid rgba(255,59,48,0.3); font-size:12px; font-weight:800; padding:2px 10px; border-radius:8px;">天克死穴 ➔</span>
                    <span style="font-size:11px; color:#86868b;">净化不可解除</span>
                </div>
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; border:2px solid #e5e5ea;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/146/146.jpg" style="width:100%; height:100%; object-fit:cover; display:block;">
                    </div>
                    <div>
                        <div style="font-size:16px; font-weight:800; color:#1d1d1f;">多位移秀儿 (露娜/公孙离)</div>
                        <div style="font-size:12px; color:#86868b;">大招定身即刻阵亡</div>
                    </div>
                </div>
            </div>

            <!-- 克制组 3 (搭档) -->
            <div style="background:#fbfbfd; border-radius:18px; padding:15px 18px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; border:2px solid #0071e3; box-shadow:0 3px 10px rgba(0,113,227,0.25);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/193/193.jpg" style="width:100%; height:100%; object-fit:cover; display:block;">
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#1d1d1f;">铠 / 典韦</div>
                        <div style="font-size:13px; color:#86868b;">重装近战战士</div>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
                    <span style="background:rgba(0,113,227,0.12); color:#0071e3; border:1px solid rgba(0,113,227,0.3); font-size:12px; font-weight:800; padding:2px 10px; border-radius:8px;">最佳搭档 ⚡</span>
                    <span style="font-size:11px; color:#0071e3;">群体增益/拉扯</span>
                </div>
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; border:2px solid #0071e3; box-shadow:0 3px 10px rgba(0,113,227,0.25);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/113/113.jpg" style="width:100%; height:100%; object-fit:cover; display:block;">
                    </div>
                    <div>
                        <div style="font-size:16px; font-weight:800; color:#1d1d1f;">庄周 / 孙膑</div>
                        <div style="font-size:12px; color:#86868b;">解控提速，团战无敌</div>
                    </div>
                </div>
            </div>

            <!-- 卡片内置微注 -->
            <div class="card-footer-tip">
                <span>📱 手机分屏/备用机秒开查对位 · <strong>BP选人瞬间看穿对手死穴</strong></span>
                <span style="color:#0071e3;">查克制快人一步 ›</span>
            </div>
        </div>
        """
    ),

    # 03_详情页：全套 6 册战术大典矩阵
    (
        "03_详情页_6本手册深度全景.png",
        "全量清洗 · 6 大核心战术维度全覆盖",
        "全套 6 本高清战术手册",
        '<span class="subtitle-badge">高清矢量 PDF</span> <span>从底层机制到实战出装 ｜ 官方级全量数据清洗</span>',
        """
        <div class="pro-card">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div style="background:#fbfbfd; border:1px solid #f0f0f4; border-radius:16px; padding:15px 16px;">
                    <div style="color:#0071e3; font-size:12px; font-weight:800;">01 · 数值全解</div>
                    <div style="font-size:17px; font-weight:800; color:#1d1d1f; margin:2px 0 4px 0;">技能与成长数值</div>
                    <div style="font-size:12px; color:#86868b; line-height:1.4;">133位英雄被动机制、等级成长梯度、全量加成系数</div>
                </div>
                <div style="background:#fbfbfd; border:1px solid #f0f0f4; border-radius:16px; padding:15px 16px;">
                    <div style="color:#0071e3; font-size:12px; font-weight:800;">02 · 阵容克制</div>
                    <div style="font-size:17px; font-weight:800; color:#1d1d1f; margin:2px 0 4px 0;">战术克制与搭档</div>
                    <div style="font-size:12px; color:#86868b; line-height:1.4;">对位压制破局策略、BP选人针对解法、最佳双排搭档</div>
                </div>
                <div style="background:#fbfbfd; border:1px solid #f0f0f4; border-radius:16px; padding:15px 16px;">
                    <div style="color:#0071e3; font-size:12px; font-weight:800;">03 · 分路神装</div>
                    <div style="font-size:17px; font-weight:800; color:#1d1d1f; margin:2px 0 4px 0;">五大分路实战出装</div>
                    <div style="font-size:12px; color:#86868b; line-height:1.4;">对抗/中/野/射/辅标准六神装、顺逆风备选与变异方案</div>
                </div>
                <div style="background:#fbfbfd; border:1px solid #f0f0f4; border-radius:16px; padding:15px 16px;">
                    <div style="color:#0071e3; font-size:12px; font-weight:800;">04 · 装备图谱</div>
                    <div style="font-size:17px; font-weight:800; color:#1d1d1f; margin:2px 0 4px 0;">装备属性与合成树</div>
                    <div style="font-size:12px; color:#86868b; line-height:1.4;">双向合成拓扑结构、被动冲突警示、合成曲线与性价比</div>
                </div>
                <div style="background:#fbfbfd; border:1px solid #f0f0f4; border-radius:16px; padding:15px 16px;">
                    <div style="color:#0071e3; font-size:12px; font-weight:800;">05 · 铭文搭配</div>
                    <div style="font-size:17px; font-weight:800; color:#1d1d1f; margin:2px 0 4px 0;">五级铭文流派全鉴</div>
                    <div style="font-size:12px; color:#86868b; line-height:1.4;">百穿/88法穿/暴击移速卡阈值配置、全流派英雄装配</div>
                </div>
                <div style="background:#fbfbfd; border:1px solid #f0f0f4; border-radius:16px; padding:15px 16px;">
                    <div style="color:#0071e3; font-size:12px; font-weight:800;">06 · 底层算分</div>
                    <div style="font-size:17px; font-weight:800; color:#1d1d1f; margin:2px 0 4px 0;">峡谷战场底层机制</div>
                    <div style="font-size:12px; color:#86868b; line-height:1.4;">双抗实际免伤公式、韧性穿透上限、野区经济经验刷新</div>
                </div>
            </div>

            <!-- 卡片内置微注 -->
            <div class="card-footer-tip">
                <span>📚 拍下整套 6 本一键打包提取 · <strong>手机电脑平板随时秒开</strong></span>
                <span style="color:#0071e3;">无水印高清单页 ›</span>
            </div>
        </div>
        """
    ),

    # 04_详情页：推演沙盒硬核三大功能
    (
        "04_详情页_独家在线推演沙盒.png",
        "网页端轻量化推演 · 免安装即开即用",
        "在线配装推演沙盒",
        '<span class="subtitle-badge">独家随赠</span> <span>全铭文自由混搭 ｜ 装备动态算分 ｜ 永久云端同步</span>',
        """
        <div class="pro-card">
            <div style="background:#fbfbfd; border-radius:18px; padding:16px 20px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:44px; height:44px; border-radius:12px; background:rgba(0,113,227,0.08); display:flex; align-items:center; justify-content:center; font-size:22px;">💎</div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#1d1d1f;">30 颗全量铭文自由混搭</div>
                        <div style="font-size:12.5px; color:#86868b; margin-top:2px;">支持 9异变+1纷争、7狩猎+3夺萃等极限卡攻速阈值方案</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/mingwen/1504.png" style="width:34px; height:34px; border-radius:8px; border:1px solid #f59e0b;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/mingwen/3514.png" style="width:34px; height:34px; border-radius:8px; border:1px solid #f59e0b;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/mingwen/2517.png" style="width:34px; height:34px; border-radius:8px; border:1px solid #f59e0b;">
                    <span style="background:rgba(0,113,227,0.1); color:#0071e3; font-size:13px; font-weight:800; padding:4px 10px; border-radius:12px;">百穿 +100</span>
                </div>
            </div>

            <div style="background:#fbfbfd; border-radius:18px; padding:16px 20px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:44px; height:44px; border-radius:12px; background:rgba(245,158,11,0.1); display:flex; align-items:center; justify-content:center; font-size:22px;">⚔️</div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#1d1d1f;">装备双向合成拓扑树</div>
                        <div style="font-size:12.5px; color:#86868b; margin-top:2px;">大件成装自动回溯前置小件，平滑过渡告别对局空档期</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1126.png" style="width:34px; height:34px; border-radius:8px; border:1px solid #f59e0b;">
                    <span style="color:#86868b; font-weight:800; font-size:12px;">+</span>
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1133.png" style="width:34px; height:34px; border-radius:8px; border:1px solid #f59e0b;">
                    <span style="background:rgba(0,113,227,0.1); color:#0071e3; font-size:13px; font-weight:800; padding:4px 10px; border-radius:12px;">平滑合成</span>
                </div>
            </div>

            <div style="background:#fbfbfd; border-radius:18px; padding:16px 20px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:44px; height:44px; border-radius:12px; background:rgba(52,199,89,0.1); display:flex; align-items:center; justify-content:center; font-size:22px;">🛡️</div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#1d1d1f;">双抗实际免伤率结算引擎</div>
                        <div style="font-size:12.5px; color:#86868b; margin-top:2px;">根据防御力衰减公式动态计算等效生命值，智能诊断被动冲突</div>
                    </div>
                </div>
                <span style="background:rgba(52,199,89,0.12); color:#248a3d; border:1px solid rgba(52,199,89,0.3); font-size:14px; font-weight:800; padding:5px 14px; border-radius:14px;">
                    协同 100 分
                </span>
            </div>

            <!-- 卡片内置微注 -->
            <div class="card-footer-tip">
                <span>🌐 浏览器点开即用无需安装 · <strong>平衡性调整云端自动同步</strong></span>
                <span style="color:#0071e3;">即买即开 ›</span>
            </div>
        </div>
        """
    ),

    # 05_详情页：发货流程与全平台畅读
    (
        "05_详情页_秒级发货全端畅读.png",
        "24 小时无人值守 · 拍下旺旺秒级自动发货",
        "秒级发货 · 全端畅读",
        '<span class="subtitle-badge" style="background:#34c759;">自动发卡</span> <span>手机平板随开随查 ｜ 极客专属 AI 知识库原生包</span>',
        """
        <div class="pro-card">
            <div style="background:#fbfbfd; border-radius:18px; padding:18px 20px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="width:48px; height:48px; border-radius:14px; background:rgba(0,113,227,0.08); display:flex; align-items:center; justify-content:center; font-size:24px;">📱</div>
                    <div>
                        <div style="font-size:19px; font-weight:800; color:#1d1d1f;">手机 / 平板端 · 高清战术手册</div>
                        <div style="font-size:13px; color:#86868b; margin-top:2px;">全彩矢量排版，对局排位随手翻阅，无广告不卡壳</div>
                    </div>
                </div>
                <span style="background:rgba(52,199,89,0.12); color:#248a3d; border:1px solid rgba(52,199,89,0.3); font-size:13px; font-weight:800; padding:6px 14px; border-radius:14px;">秒开即读</span>
            </div>

            <div style="background:#fbfbfd; border-radius:18px; padding:18px 20px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="width:48px; height:48px; border-radius:14px; background:rgba(0,113,227,0.08); display:flex; align-items:center; justify-content:center; font-size:24px;">💻</div>
                    <div>
                        <div style="font-size:19px; font-weight:800; color:#1d1d1f;">电脑宽屏端 · 在线推演沙盒</div>
                        <div style="font-size:13px; color:#86868b; margin-top:2px;">独家配装动态算分，铭文混搭模拟，阵容协同诊断</div>
                    </div>
                </div>
                <span style="background:rgba(0,113,227,0.1); color:#0071e3; border:1px solid rgba(0,113,227,0.25); font-size:13px; font-weight:800; padding:6px 14px; border-radius:14px;">送专属网址</span>
            </div>

            <div style="background:#fbfbfd; border-radius:18px; padding:18px 20px; border:1px solid #f0f0f4; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="width:48px; height:48px; border-radius:14px; background:rgba(175,82,222,0.1); display:flex; align-items:center; justify-content:center; font-size:24px;">🤖</div>
                    <div>
                        <div style="font-size:19px; font-weight:800; color:#1d1d1f;">AI 极客专享 · 原生数据包</div>
                        <div style="font-size:13px; color:#86868b; margin-top:2px;">纯净 Markdown 格式，一键投喂 NotebookLM / DeepSeek 打造私人教练</div>
                    </div>
                </div>
                <span style="background:rgba(175,82,222,0.12); color:#9933cc; border:1px solid rgba(175,82,222,0.3); font-size:13px; font-weight:800; padding:6px 14px; border-radius:14px;">随包附赠</span>
            </div>

            <!-- 卡片内置微注 -->
            <div class="card-footer-tip">
                <span>⚡ 拍下后旺旺聊天窗口 1 秒自动推送网盘链接 · <strong>永久享受更新</strong></span>
                <span style="color:#0071e3;">自动发货 ›</span>
            </div>
        </div>
        """
    ),
]
