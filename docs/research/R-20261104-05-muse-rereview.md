# GATE-R0 単一方法文書へのClaude再査読 — 合格（OwnerのR0-E判断待ち）

id: DIAG-R-20261104-05-MUSE-REREVIEW
status: rereview_passed / owner_r0e_pending / r1_not_authorized
updated: 2026-11-04
tags: gate-r0, rereview, claude-review, single-method, claim-certificate, owner-decision-pending

> 本書は外部監督者Claude（ごま）による独立再査読の記録である。再査読対象は [GATE-R0単一方法文書](GATE-R0-20261104-single-method.md)（commit `8b3a44172ea5fef5023f42bed9a37c26745dab86`）。本書はR0-Eの決定でも、R1-ENGの実装許可でも、PRのマージ承認でもない。最終判断はOwnerが行う。

## 1. 独立確認した提出状態

- PR headは報告どおり `8b3a441`。直前head `a47cfe6` からの変更は2ファイルのみ（方法文書の新規追加164行、`docs/INDEX.md` への登録1行）。新規の方法正本候補は1件だけで、競合する正本は増えていない。
- 監督者が自分の環境で `python scripts/check_docs.py` を再実行し、116 Markdown filesでPASSした。
- GitHub Actions run `41791919928` はhead `8b3a441` に対してSuccessであることを確認した（注記はNode.js等の非推奨警告のみで、文書検証の失敗ではない）。
- 方法文書・INDEXとも、新規実装・実験・採点・滞留物整理を主張していない。

## 2. 有限ケースの独立検算

監督者が真理値表を再計算し、方法文書の数値はすべて一致した。

- XORに対する初期6候補 `0,1,x,!x,z,!z` の誤りは全て `2/4`。ORに対する最小誤りは `1/4`。
- 公開3点 `P={(0,0)->0,(0,1)->1,(1,0)->1}` を全て満たす初期6候補は0件。追加照会 `(1,1)` がXOR（0）とOR（1）を識別する。
- body `OR(AND(x,NOT(z)),AND(NOT(x),z))` はXORと全域で一致する。
- Nケースでは、`x` と `x AND !z` は合法3点で同値、終端 `(1,1)` でのみ異なる。Sケースでは `Q(0,0)` が `x` と `!x` を識別する。Eケースでは列挙順の最初の5候補が公開2点と不整合で、6番目の `x` のみが整合する。

## 3. P0 / P1 チェック

| 条件 | 判定 | 方法文書での反映 |
|---|---|---|
| P0-1: Mの分割とClaim Certificate Matrix | 合格 | `M_use` と `M_gap` を分離し、無印Mを禁止。行列にH0_object、H0_effective(B)の内訳、OFF時の最良fallback、認定できる最大ラベル、禁止する推論を対象別に固定。Rの現時点の上限は `G_object>0` と公開識別可能性までで、M_gap・U・Tへ格上げしていない |
| P1-1: 有限全域での証拠上限 | 合格 | Rでは識別後に全4点が公開済みになること、公開検証は整合性チェック、fresh USEは永続化・dispatchの確認であり、未見汎化や独立family転移ではないことを明記 |
| P1-2: Sleep-liteの境界 | 合格 | 意味を変えないcanonical化、validator結果の記録、版管理・immutable保存までに限定。意味の異なる候補の選択はWake側の合成・検証へ帰属 |
| P1-3: R0-P/R0-Tの統合とR1許可行 | 合格 | 紙上エピソードは方法文書の1節へ統合。Owner決定欄に `R1-ENG authorization: granted / not granted — scope: ...` を未決定のまま保持し、この行がなければGOでも実装禁止と明記 |
| P1-4: episodic retrievalの算入 | 合格 | episodic retrievalとlookupをH0_effective(B)へ算入。4点lookupが合法なら `G_effective=0` になり得ること、R行列と紙上エピソードのOFF条件にも反映 |
| P1-5: 未評価とNULLの区別、N_rep | 合格 | 現時点のM_use / M_gap / N_rep / U / Tは全て `NOT_EVALUATED`。Nは外延ではなく表現上の新規性 `N_rep` として初期Libraryと照合する |
| P1-6: 長期仮説の扱い | 合格 | 方法文書へ展開せず、R0範囲外として因果アーキテクチャ案への参照だけを置く |

## 4. Owner指示の6項目チェック

| 必須内容 | 判定 |
|---|---|
| H0_effective(B)の定義・内訳・公平性規則 | 合格（初期primitive/macro、Kernel分岐、dispatch、rank/policy、memory、episodic/lookup、予算まで閉包し、等情報・等資源・最良fallback保持を規則化） |
| N / S / R / Eの紙上ケース・証明・証拠上限 | 合格（第2節の検算と一致） |
| source→public→learner→validator境界、合法行動・費用、漏洩時のINVALID | 合格（記録契約、費用台帳、INVALIDを分母から除外し再試行には別承認を要求） |
| Claim Certificate Matrix、M_use / M_gap / N_rep / U / T、段階別強対照、生涯総費用 | 合格（F00/F01/F10/F11、episodic、fixed macro、Oracle上限、償却式まで固定） |
| 紙上エピソード1件 | 合格（未実行の思考実験として明示し、新しい世界や結果を追加していない） |
| 主張単位のSTOP／転換条件とOwner決定欄 | 合格（弱いH0への差し戻し禁止、圧縮・Uへの転換は新主張としてOwner再承認を要求） |

**未解決のP0 / P1はない。**

## 5. R1開始前に固定すべき注記（方法文書の欠陥ではない）

方法文書の行列とF00では、STATIC-H+が「対照arm」であると同時に「最良fallback」とも読める箇所がある。将来R1の実装仕様を作る際は、次の区別を先に固定すること。

- M_useのbody OFFで残すfallbackは、**同じSnapshot内の非学習body経路**（H0_effectiveの候補、Kernel dispatch、episodic/lookup等）に限る。
- STATIC-H+とfixed macroは、同じSnapshot内のfallbackではなく、N_rep / Uを判定するための**別armの対照**として扱う。

この区別を曖昧にすると、外部の静的合成器が常にbodyを再合成できるためにM_useが定義上認定不能になったり、逆にfallbackを止めた自己成就的なOFF差を作ったりする。R0の方法判定を変える問題ではないが、R1仕様では必須の前提とする。

## 6. 監督者の勧告

1. **方法文書をR0の正本として受け入れることを推奨する。**
2. **R0-Eは `GO` を推奨する。** ここでのGOは「R0の診断が完了し、Dルートと方法が次のゲートへ進めるだけ具体化した」という意味に限る。科学的陽性、M_use / M_gapの成立、方法の恒久凍結を意味しない。
3. **R1-ENG許可はR0-Eとは別に、Ownerが決定文の行で明示すること。** 許可する場合の最大範囲として監督者が推奨するのは、方法文書の2bit N/S/R/Eを工学診断用fixtureとして実装し、M_useパイプライン（公開境界、公開証拠からの候補合成、独立validator、immutable保存、fresh dispatch、同一Snapshotでのbody OFF）を通すことまでである。正式な科学採点、M_gap / N_rep / U / Tの判定、封印済み評価、独立family、学習型Active Learning、本格Sleep、NN、滞留PRの整理は含めない。
4. R1を許可しない場合は、R0-EのGOをもってR0を閉じ、作業は停止したままにする。
5. PR #170のマージは、R0-EやR1許可とは別のOwner承認事項として残す。

## 7. 現在の状態

| 項目 | 状態 |
|---|---|
| D案の条件付き採用 | 決定済み |
| 単一R0方法文書 | 提出済み |
| Claude再査読 | **合格（未解決P0/P1なし）** |
| R0-E最終判定 | Owner未決定（監督者勧告: GO） |
| R1-ENG実装許可 | 未許可（範囲はOwnerが決定文で明示） |
| PRマージ | 未実施・未承認 |
