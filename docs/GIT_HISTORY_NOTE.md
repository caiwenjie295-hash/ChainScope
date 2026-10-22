> 本文件描述原始本地仓库的历史。本次公开仓库以发布快照建立，未导入原始本地提交；原历史保留于本地及原源码 ZIP。

# Git 历史说明

本仓库 **保留了开发初期的真实本地 git 历史**（来自用户首份源码包 `01M5FA510ATEXAH7…zip`），并在其上接了交付冻结树。

## 原始历史（作者 Cai Wenjie）

| Commit | 说明 | 标签 |
| --- | --- | --- |
| `07e0244` | round-two verified research baseline | `v0.1.0-research.20261021` |
| `36a9137` | export reviewed frontend snapshot | |
| `bdd5665` | graph-first prototype checkpoint | `checkpoint-ui-graph-20261021` |
| `76cd895` | mvp.2 scoped investor metrics | |

## 交付叠加（ChainScope Delivery）

| Commit / Tag | 说明 |
| --- | --- |
| `v0.3.21` | `chainscope-dev-0.3.21.zip` 树（包内 VERSION 曾为 0.3.12） |
| `v0.3.22` | 最终冻结：前端 0.3.22 + snapshot `b1h.p1.c` |

中间 0.2.x→0.3.x 的逐版本完整工作树未在首份包中归档；CHANGELOG 有文字记录，但本仓 **不伪造** 那些中间 commit 的文件树。
