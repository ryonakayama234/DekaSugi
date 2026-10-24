# EXP-0002B — 事前登録v2への改訂記録

id: EXP-0002B-PREREG-V2
status: methodological revision, no implementation or FINAL run
updated: 2026-10-24
tags: research, experiments, protocol-revision, leakage, preregistration, no-results

## 変更の背景と根拠
- [PR #10](https://github.com/ryonakayama234/DekaSugi/pull/10)の独立レビューで、split seed `260201..260203`と`+j`の合成によってTRAIN/DEV/FINALの例に同じ乱数seedが再使用されるP1問題が発見された。文書が人間向けには英語だったことも指摘された。
- 実装前のモデル非依存な列挙数を検査すると、固定familyの16正規化問題で節約できる候補数は最大16件程度であり、候補総数`1536`に対する改善は`1.04%`程度が上限。旧v1のOFF比5%削減ゲートは実現不能に近い。これらは**新しいFINALの結果を閲覧した事後調整ではなく、実装前のレビューと構造的解析**による。
- 事前登録済みの旧[plan.md](plan.md)は追記/改変せず保存する。v2は独立した[plan-v2.md](plan-v2.md)として固定する。PR #10のレビュー記録も削除しない。

## 変更した範囲
| 項目 | v1 | v2 |
|---|---|---|
| split seed | 260201/260202/260203 | 10000000/20000000/30000000（非重複領域） |
| OFFに対する候補改善ゲート | 5%以上 | 合計8候補以上、同時に32 primitive calls以上 |
| ONに対する改善ゲート | 呼出数と候補数とも5%以上 | 変更なし |
| human-readable plan | 英語主体 | 日本語 |
| TaskFeatures / 5-NN / abstention | 固定 | 変更なし |
| 既知6family + OOD 1family、TRAIN/DEV/FINALの件数 | 144 / 48 / 112 | 変更なし |
| 監査例・型安全・正確性・尾部・OODのゲート | 固定 | 変更なし |

## 科学的限界
- v2も各familyの文字列例生成規則は固定であり、未知の関数の発見・真の広域転移の証拠にはならない。
- 旧v1のデータと比較して改善したとは主張しない。旧FINALは生成されていないため、旧評価結果との比較はそもそも存在しない。
- 研究の採否は新しいv2のFINALが未使用であることを検査してから実施する。失敗のログも保存する。
- 各ファイルのMermaid図と情報契約を更新し、参照先はv2を示す。旧v1は研究史として読める状態を維持する。

## 現在の状態
- protocol v2: **本文と採用ゲートを先行して固定**、レビュー待ち。
- 新しい生成器・TaskFeatures・Kernel・PolicySnapshot: **未実装**。
- 結果：**存在しない**。PR #6/9の安全レビューと依存関係の統合も未完了。

[プロトコルv2](plan-v2.md) / [合意したビジョン](../../docs/vision/mission.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7)。
