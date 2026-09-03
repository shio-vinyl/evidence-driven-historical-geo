[English](README.md) | [简体中文](README.zh-CN.md)

# 证据驱动的历史地理重建

**可审计空间研究 Agent 原型 · Python 3.9+ · 后端中立研究契约 · 两个可复现历史切片**

这个项目检验研究型 Agent 能否在不读取现成历史疆域地图的条件下，从分散、异质且相互冲突的证据中构造可接受的历史地理假说。系统显式保存 Agent 的认知状态，把合格决策编译为后端中立的空间请求，诊断假说在哪些区域敏感，再把真正影响空间结果的证据缺口转成下一轮搜索议程。

![1130 年与 1187 年末的边界假说](cases/crusader_states/public/figures/reconstruction-slices.png)

## Agent 负责什么

每个案例都经过同一条研究链：

```text
检索并取得来源
  -> 记录带定位与权利状态的观察
  -> 处理冲突，或明确保留冲突
  -> 按空间含义分类主张
  -> 作出经审查的模型决策
  -> 编译后端中立的空间假说
  -> 比较受控的证据情景与模型情景
  -> 诊断有后果的不确定性
  -> 排定下一轮证据搜索
```

仓库提供闭环所需的契约、可执行检查、案例结构和失败规则。资料检索可以由任何具备相应能力的研究 Agent 完成；无法化约的历史判断继续留给人工接受。

## 为什么必须分层

史料可能证明某城市易手、某统治者使用政治头衔，或某支军队沿路线行动。这些观察都不能直接证明连续领土边界。谱系把来源、观察、主张、模型决策、求解器输入和输出要素分开，防止 Agent 静默提升证据的空间含义。

v0.2 契约把 `Source → Observation → Claim → Model Decision → Evidence Gap` 定义为 Agent 的认知状态。编译器只暴露控制点、空间约束、通行约束等通用角色；XTENT 位于这条边界之后，是可以替换的空间推断后端。

## 核心案例：十字军诸国

案例覆盖 **1130 年**和 **1187 年末**。第二轮来源审查后，1130 基线保留 5 个实体；Fatimid Egypt 只通过有争议的 Ascalon 锚点出现在 inclusive 情景。1187 基线保留 4 个实体，并移除有争议的 Cairo 与 Jaffa 点。

7 组承重缺口已经全部决策：2 组 KEEP、3 组 DOWNGRADE、2 组 DISPUTED。决策写入 `historical-claim-decisions.json`，不只停留在说明文字中。

![有证据支持的地点锚点](cases/crusader_states/public/figures/evidence-anchors.png)

## 外部比较

项目登记了三套出版物中的四幅地图。公有领域的 Shepherd 与 Johnston 地图用于分类比较；Buck 的精确 1130 地图因合法预览未开放正文，被记录为访问和权利受阻。仓库没有提交扫描页或沿地图集描绘的边界。

比较维度包括具名城市控制、实体存在、邻接与海岸地点顺序。约 1140 年代理图有 17 项可比断言，其中 12 项一致；Shepherd 约 1190 年图的 4 项实体断言全部一致；Johnston 1187—1190 战役图有 14 项城市与实体断言，其中 13 项一致。这些计数表示一致程度，不是历史准确率。

![分类式外部地图比较](cases/crusader_states/public/figures/reference-comparison.png)

## 不确定性驱动研究

8 个情景分别测试证据资格、自然成本、允许的 projection 等级和 5/10/20 km 格网。统一分析格网把结果分为 stable core、model-sensitive、evidence-sensitive 与 unresolved zone。

![情景一致性区域](cases/crusader_states/public/figures/uncertainty-zones.png)

当前结果中模型敏感区占比很大，说明有界 projection 选择对面状结果的影响高于新增争议地点。v0.2 诊断还会测量证据情景改变了哪些格网单元，并把这些变化追溯到尚未关闭的证据缺口。仓库保存的首轮研究结果据此生成具体搜索任务，包含目标资料类型、成功标准和停止条件。

十字军案例属于回顾性 testbed：外部地图从未进入重建输入或参数调优，但开发期间已经被检查。严格预注册的 held-out evaluation 需要留给未来的新案例。

## 已实现组件

| 组件 | 作用 |
|---|---|
| 可审计认知状态 | 分离来源、观察、主张、决策和证据缺口。 |
| 后端中立编译器 | 选择经审查的决策并生成通用重建请求。 |
| XTENT 后端 | 把通用空间角色翻译为确定性的 XTENT 输入。 |
| 成本距离重建 | 在投影格网上生成有效、无重叠的领土表面。 |
| 不确定性诊断 | 在格网单元层面区分证据效应与模型敏感性。 |
| 搜索目标生成器 | 只对已观察到空间后果的开放缺口排序。 |
| 外部比较 | 在不把参考图当成 ground truth 或调参目标的前提下做分类比较。 |

## 快速运行

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'

.venv/bin/historical-geo validate-research cases/crusader_states/public
.venv/bin/historical-geo compile-request cases/crusader_states/public \
  --slice 1130 --scenario reviewed-baseline
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo research-loop \
  cases/crusader_states/public --slice 1130
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo figures \
  cases/crusader_states/public
.venv/bin/pytest
```

运行中间结果保存在已忽略的 `build/` 目录。审查后的图件与机器可读指标位于 `cases/crusader_states/public/figures/`。

## 已核验状态

- 101 项测试通过。
- v0.1 旧基线在迁移前已经完成哈希冻结。
- v0.2 bundle、诊断与搜索目标文档通过结构和引用校验。
- 后端边界测试证明，v0.2 编译后的案例输入保持了已审查的 v0.1 XTENT 行为。
- 公开谱系验证为零错误。
- 两个切片的必要情景均可重建。
- 每个运行都保留该情景预期实体，几何有效且无重叠。
- 6 张图全部通过非空 QA。
- Fixture 字节数与 SHA-256 一致。
- 中英文配对标题结构和 Markdown 相对链接通过检查。
- 公开树中没有缓存、绝对机器路径、来源 PDF、地图集扫描、受限地图衍生物或意外大文件。

这些核验说明流程可复现、可审计；历史学接受仍需合格读者作出判断。

## 文档

- [方法论与 Agent 研究协议](docs/architecture/methodology.zh-CN.md)
- [十字军诸国案例研究](docs/research/crusader-states-case-study.zh-CN.md)
- [历史来源审查](docs/research/source-review.zh-CN.md)
- [外部地图比较](docs/research/comparative-evaluation.zh-CN.md)
- [不确定性分析](docs/research/uncertainty-analysis.zh-CN.md)
- [复现指南](docs/operations/reproducibility.zh-CN.md)
- [案例数据归属与权利说明（英文）](cases/crusader_states/public/ATTRIBUTION.md)
