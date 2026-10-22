# ChainScope：Web 产品 URL 与操作说明

提交版更新日期：2026-10-22（北京时间）。本文件描述当前已部署状态。

## 访问入口

| 项目 | 地址 / 说明 |
| --- | --- |
| 可操作 Web 产品 | [打开 ChainScope](https://emberscrolls.top/ChainScope-0.3.22/dist/) |
| 公开源代码 | [GitHub / ChainScope](https://github.com/caiwenjie295-hash/ChainScope) |
| 研究流程 | [流程与证据](https://emberscrolls.top/ChainScope-0.3.22/dist/agent_architecture.html) |
| 运行成本与验证 | [成本核算](https://emberscrolls.top/ChainScope-0.3.22/dist/cost_performance.html) |
| 产品边界 | [产品说明](https://emberscrolls.top/ChainScope-0.3.22/dist/prod_loop.html) |
| 研究 JSON | [已发布快照](https://emberscrolls.top/ChainScope-0.3.22/dist/data/snapshot.json) |
| 登录与环境 | 无需登录、安装软件或填写 API Key；推荐桌面浏览器 |
| 版本 | 界面 0.3.22；研究 2026-10-22.p2.deep.b1h.p1.c；数据截至 2026-10-21 |

## 建议评审流程

1. 打开产品，勾选 **AI**，点击 **开始分析**。
2. 约 3 秒后显示产业结构；选择温控与液冷相关环节，再选择 **英维克**。
3. 先查看主营业务、财务指标及报告期；点击 **AI智能总结**，阅读已发布研究。
4. 查看产业链归属证据、A–E 概念可信度、中外可比与不可比边界、外部变化传导路径。
5. 打开来源链接，核对公开材料页码或定位；无公开链接的来源显示访问限制。
6. 可打开等级说明、切换公司、刷新或返回，并访问顶部研究流程、成本与验证页面。

[直接打开英维克研究示例](https://emberscrolls.top/ChainScope-0.3.22/dist/?concept=concept.ai&stage=structure&segment=segment.thermal&company=envicool&summary=1)。本地 60 秒成片见 [视频说明](../demo/视频说明.md)。

## 产品选择与核心口径

面向希望理解 AI 产业链的个人投资者，把产业结构、公司业务、财务指标、证据可信度、跨市场对照与事件传导整理在同一界面。当前快照 27 家公司，其中 17 家 reviewed、10 家 candidate；只有 AI 主主题可进入分析，其余入口为 Demo。reviewed 不表示每家公司已完成相同深度核验。

产业结构按技术功能分为主题、分支和环节；公司归属由业务证据支持或标为推断。数据商概念板层级与成分另存在 concepts 中，不能将板块命中等同主营归属或已实现 AI 收入。

## 已完成的部署与验证

主站根目录保持 `/www/wwwroot/emberscrolls.top`，产品文件放在 `/www/wwwroot/emberscrolls.top/ChainScope-0.3.22/dist`。使用相对路径加载脚本、样式、数据与导航；主域名原首页保留。网页地址以上面的 HTTPS 链接为准，服务器文件路径不能直接交给评审访问。

已通过外网浏览器查看公司研究与总结、跳转研究流程；JSON、脚本及页面与发布构建核对。记录见 [公网部署验证](验证记录/公网部署验证.json)、[公网截图](验证记录/公网部署验证.png)、[子目录构建校验](验证记录/子目录构建校验.json)。公网连通性是验证时点结果，不是可用性或负载承诺。

## 演示与研究边界

- 两处约 3 秒进度展示已有研究快照，不会启动新的 AI 研究或实时金融请求。
- 各项指标按自身报告期与币种呈现；“数据截至”不表示全部项目实时更新。
- AI 专项收入未核实则显示未知，集团及母类别收入不能替代专项收入；A–E 是概念证据等级，不是信用评级或收益承诺。
- 中外比较须保留期间、会计准则和业务结构差异；事件区分事实、推断与情景，不把供应合同或收入未证实的部分当成已发生结果。
- 完整研究原件、部分受限来源及全套研究测试仍有限制，见 [测试说明](04_测试说明.md)、[溯源索引](06_关键数字与结论溯源索引.md)。

## 本地复现

下载公开源码后，在 frontend/ 内运行 `npm ci`、`npm run dev`；生产构建用 `npm run build`。研究模型或金融数据凭证不是浏览前端的前提。完整启动方式、环境变量、AI 角色与未做事项见 [README](02_源代码与README.md)。
