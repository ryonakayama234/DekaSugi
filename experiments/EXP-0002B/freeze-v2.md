# EXP-0002B — 評価前の学習方策凍結記録

id: EXP-0002B-FREEZE-V2
status: TRAIN-only evidence frozen; DEV/FINAL not evaluated
updated: 2026-10-25
tags: experiment, freeze, policy-snapshot, provenance, pre-final, exp0002b

## 不変の研究境界
**この凍結はDEV/FINALの探索結果を取得する前に確定した。** 現行方法の唯一の正本は[plan-v2](plan-v2.md)。先行するv1の研究史は変更しない。評価結果を見てからしきい値・特徴・方法を調整しない。

## 固定対象
- **コード:** [main commit `2cd159a`](https://github.com/ryonakayama234/DekaSugi/commit/2cd159af1815690d46105bc785c7d31cd88919fd) 。原始演算の実行境界はSEC-004、計測はMEASURE-0001。
- **生成器source SHA-256:** `734598f4f9db91096fa4aff78cc9f3d423184ddc05dcf8309c7e8663409ee7ab`
- **TRAIN/DEV/FINAL全データの内容SHA-256:** `ce6f4bec90479295b1e465ab8eb9e2fbd6124f254bad37166ffbd5886a2d944a`。split 144/48/112問、seed合計912件一意。
- **TRAIN観測SHA-256:** `48d322d923500b7b73be6d08cc738bf1e680f049d0d090ccafb91068fd80747b`
- **学習方策PolicySnapshot SHA-256:** `1e85d06958bf65abc11eb14f4fc2f98645a9480d14618f6e7f477fee5b1affe7`
- **技能のbody SHA-256:** `8fe1361cb5014f8503e4a57392e45f4fc7607e788fdd598f66668fbc11338eff`
- **機械用の固定識別情報:** [freeze-v2.json](freeze-v2.json)。後続評価はcode/source/data/policy/hashを照合し、不一致ならfail closedとする。

## 観測の来歴
- [PR #22](https://github.com/ryonakayama234/DekaSugi/pull/22)の最終HEAD `ab402e83a498d10ea4b238feafe2ea01c9737c14`：GitHub Actions [#40154074074](https://github.com/ryonakayama234/DekaSugi/actions/runs/40154074074)とCodexコードレビュー成功。
- main統合 `2cd159af1815690d46105bc785c7d31cd88919fd`：GitHub Actions [#40154262757](https://github.com/ryonakayama234/DekaSugi/actions/runs/40154262757)成功。artifact `EXP-0002B-train-only`にはTRAIN144問のOFF/ON status/AST/trace/実際の原始演算回数と独立audit判定を保存。
- 2回の再実行で**PolicySnapshot SHA・dataset SHA・generator SHA・training observations SHAが一致**。elapsed_msを含むtrial-evidence hashは計測ノイズにより一致しないため、方策の決定性ハッシュとして使わない。

## TRAIN限定の観測
- 正規化24問はON選好、その他の120問はOFF選好。TRAINの両arm合計primitive呼出数は11,904。これは方策の**未知課題への改善の証明ではない**。
- TEST/DEV/FINAL結果や手動探索はこの記録に含めていない。方法v2の性能ゲートを達成したとの主張はしない。
- 実際の総CPU/wallはprimitive呼出数に代替できない。学習費用償却や汎化主張は後続評価で別計上する。

## 次のゲート
1. [Issue #23](https://github.com/ryonakayama234/DekaSugi/issues/23)の独立レビュー、CIとmain統合。
2. 凍結済みsnapshotが一致することを確認した**DEV48問のengineering smoke**。DEV結果で方法を変更する場合はv3+新FINAL。
3. 別PRでFINAL112問の実行パス・統計報告をレビューし、信頼境界/ハッシュを再確認した**後**でのみ最終結果を開く。
4. いずれの採用ゲートにも達しなければ`not_demonstrated`を明記し、失敗を含めて結果を保存。

[研究Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7) / [TRAIN-only監査](reviews/20261025-train-only-kernel.md) / [run索引](runs/README.md)。

## 実行ソースの追加保全（DEV/FINAL開始前）
実行時コード`runtime`・`verification`・`evaluation`・`learning`・`kernel`・`protocol`・`synthesis`・`library`等の9ソースについて、最初の学習済み方策を作ったmain commit `2cd159af1815690d46105bc785c7d31cd88919fd`のGit blob SHA-1を[freeze-v2.json](freeze-v2.json)に追記した。後続評価では生成器・方策hashに加えて**これらのファイルの中身の一致**を検査し、変更がある場合はDEV/FINALを開く前に拒否する。科学的方法とTRAIN方策hashは変更しない。評価器自体は独立のコードレビュー対象。
