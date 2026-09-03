[English](reproducibility.md) | [简体中文](reproducibility.zh-CN.md)

# 复现指南

## 环境要求

- Python 3.9 或更高版本；
- 能安装 wheel 的包管理器；
- 足够运行 GeoPandas、Rasterio、scikit-image 和 Matplotlib 的内存。

仓库已包含小型公开输入。复现不依赖私有项目、地图集扫描、来源 PDF 或全球 GIS 数据集。

## 安装

在仓库根目录运行：

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
```

## 验证并运行审查后基线

```bash
.venv/bin/historical-geo validate cases/crusader_states/public

MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1130 --scenario reviewed-baseline

MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1187 --scenario reviewed-baseline
```

`run` 依次执行 `validate -> build-inputs -> reconstruct -> audit -> render`。每次运行会在已忽略的案例 `build/` 目录中写入有效求解器输入、边界假设 GeoJSON、运行清单、渲染 QA 和预览图。

## 重建情景集合

登记的情景为 `verified-only`、`reviewed-baseline`、`inclusive`、`flat-natural`、`projection-normal`、`projection-expansive`、`grid-5km` 和 `grid-20km`。单个情景的命令如下：

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1130 --scenario verified-only
```

对两个切片和上述每个名称重复运行。10 km 审查后基线提供共同分析格网；5 km 与 20 km 只检查格网敏感性，不改变历史证据。

## 重新生成图件与指标

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo figures \
  cases/crusader_states/public
```

该命令会重建两个切片的全部必要情景，并写出六幅图：

- `evidence-anchors.png`；
- `reconstruction-slices.png`；
- `natural-ablation.png` 及 JSON 指标；
- `boundary-attractor-diagnostics.png` 及 JSON 诊断；
- `reference-comparison.png` 及分类比较 JSON；
- `uncertainty-zones.png` 及情景一致性 JSON；
- 用于非空检查和哈希记录的 `figure-qa.json`。

外部比较没有数字化地图集边界。不确定性分类只描述已声明情景集合的一致程度，不表示概率。

## 运行测试

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=.cache/matplotlib \
  .venv/bin/pytest -p no:cacheprovider
```

当前预期结果：**68 passed**。

## 核验输出

每个切片、每个情景的审计都必须确认几何有效、预期实体全部保留、实体多边形互不重叠。审查后基线写入 `build/run-{slice}`；其他情景写入 `build/run-{slice}-{scenario}`。

`cases/crusader_states/public/fixture-manifest.json` 保存公开输入的字节数与 SHA-256。`natural-earth-source-check.json` 保存 Natural Earth 官方文件和几何比较结果。每次生成的运行清单还会对有效输入和结果表面计算哈希。

## 合成冒烟案例

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/fixtures/synthetic_smoke --slice 1130
```

该案例在不使用历史或第三方数据的条件下检查软件行为。已接受点种子和标为假设的 phase 进入分配；事件与路线观察不会进入求解器。

## 复现边界

- 生成的 `build/`、`.cache/`、字节码和 pytest 缓存都是本地文件，必须保持未跟踪。
- 二进制哈希只对已测试依赖栈作保证；跨版本主要检查几何有效性和语义 QA。
- 复现检验的是已记录的 Agent 决策链和模型实现，不构成历史真实性认证。
- 参考资料的访问状态可能变化。登记表保存本轮 URL、访问日期、权利判断以及实际录入的比较主张。
