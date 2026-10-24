# RSRCH-001 — Program synthesis and library learning

id: RSRCH-001
status: notes
updated: 2026-10-24
tags: dreamcoder, wake-sleep, abstraction, library-learning

## 検討対象の文献
- **DreamCoder** — Ellis et al., 2021, *Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning*; https://arxiv.org/abs/2006.08381
- **LILO** — *Learning Interpretable Libraries by Compressing and Documenting Code*; https://arxiv.org/abs/2310.19791
- **Voyager** — *An Open-Ended Embodied Agent with Large Language Models*; https://arxiv.org/abs/2305.16291

## このプロジェクトで取り出したい研究問い
- 型付きのプログラム空間を小さく限定すると、CPUだけでも興味深い抽象獲得を観察できるか。
- 部分式をライブラリに取り込むと探索の深さが減っても、分岐が増える副作用はないか。
- Wakeで得た解法からSleepで抽象化し、Dreamで生成した課題を使う際、自己生成データへの過適合をどう避けるか。
- 外部のLLMを必要とする先行例から、LLMなしでも成立する部分をどこまで切り離せるか。

## 研究から実装へ
EXP-0001は学習前の探索器を用意する。以後、EXP-0002で技能圧縮と探索効率、EXP-0003で生成課題と探索方針学習を検証する。

## 注意
ここに記載した研究リンクは参考文献候補。網羅的調査や論文の実装再現を完了したわけではない。先行研究の結果とDekaSugiの実測は混同しない。
