# METRO-0001 CAL-01 — 独立校正の工学的採用判断

id: METRO-0001-CAL01-DECISION-20261027
status: accepted_engineering_calibration; scoped_to_synthetic_fixtures
updated: 2026-10-27
tags: metrology, evidence, calibration, review, decision

## 決定
**CAL-01計測器を、事前登録済みの人工fixtureに対してのみ工学的に校正済みとして採用する。** この決定は知能能力の向上・転移、測定の領域横断妥当性、産業実運用データの認証を意味しない。後から元の実験runやplanの結果・閾値を変更しない。

## 独立した監査証拠
- [前段設計PR #39](https://github.com/ryonakayama234/DekaSugi/pull/39) merged `c26287405959999f6814b34841e52126168d64e9`。観測・推定・主張の分離、MetricSpec、EvidenceEnvelope、CAL-01 v1を工学実行前に固定。
- [計測器PR #41](https://github.com/ryonakayama234/DekaSugi/pull/41) merged `462a8e5df57b3d1433b83eaf71aaa2397dc2566c`。PR exact head `1d80ac922a46ae4ca938373d582104fa242c74ed` の [CI #40460725917](https://github.com/ryonakayama234/DekaSugi/actions/runs/40460725917) completed success、Codexレビューcompletedかつ未解決指摘0。過去レビューのP2四件は修正と再検証を経て全件解決。
- merge後のmain [CI #40460951680](https://github.com/ryonakayama234/DekaSugi/actions/runs/40460951680) completed success。
- [合成fixtureと原本SHAの独立検証](../runs/20261027-cal01-provenance-verified.md): [CI #40458100322](https://github.com/ryonakayama234/DekaSugi/actions/runs/40458100322)、86 unittest PASS、F01–F08 8/8一致、ZIP/元JSON/fixture個別レコードのhash再照合、CPU 7,065,012ns / wall 7,063,327ns (特定CI runの観測のみ)。
- [初期run記録](../runs/20261027-cal01-synthetic.md)と[改良後run記録](../runs/20261027-cal01-provenance-verified.md)はいずれも変更せず保管。

## 計測器の成立を認める範囲
| Quality hypothesis | Evidence | Interpretation |
|---|---|---|
| M1 deterministic metric | F01と順序変更F02のcanonical summary SHA完全一致 | 指定fixtureで再現性PASS |
| M2 provenance and integrity | duplicate/missing audit/tamper/partition leak/negative-value拒否、raw input hashes照合 | 指定fixtureの失敗ケースでPASS。SHAは真正性の署名ではない |
| M3 non-interference | synthetic public TaskSpecでcanonical meter ON/OFFのstatus/AST/candidates/traceが一致 | テスト対象の既存探索経路に限定してPASS |
| M4 comparability | 個々に合法だが異単位・異予算のarmをnon_comparableとして識別、paired差を返さない | 指定fixtureと追加回帰でPASS |

## 適用範囲と不採用の主張
- `packages/metrology` は **人工 CAL-01専用** のread-only validator/reducer。既存EXPの本物の証拠は受け入れず、非公開監査やFINALを触る権限も持たない。
- EXP-0003Aのplan-v1・freeze-v1・固定source全14ファイル・TRAIN/DREAM snapshotsは不変更。DEV64/FINAL128の評価は起動しない。
- `primitive_invocations`は原始演算数であって総CPUでも一般的な知能値でもない。新しい科学的仮説の独立holdout評価は行っていない。
- 元Artifactは保存期限のある外部証拠。GitHub run URLと観測した元bytesのhashを永続文書に記録して再照合可能にしたが、永久保持や悪意ある同一ホストからの保護を保証しない。

## 次段階の判断
METRO-0001当初の実装ゴールは明確に達成。次段階が必要なら **新しいIssue・事前登録・新規PR** として区別する。優先候補は、アクセス境界を維持したまま実際のTRAIN-only証拠へAdapterを接続し、欠測率・観測来歴・既存MetricSpecとの互換性を測定すること。既存FINALやEXP-0003A DEVを研究計画なしに評価しない。

Related: [CAL-01 plan-v1](../plan.md) / [run index](../runs/README.md) / [METRO evidence contract](../../../docs/metrology/evidence-model.md) / [METRO validity](../../../docs/metrology/validity.md).
