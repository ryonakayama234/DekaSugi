# WORLD-PREREG-RQ7-20261111-07 — Muse に提出する二点限定の最小閉鎖条項

id: WORLD-PREREG-RQ7-20261111-07
status: research_lead_minimal_protocol_contract_clarifications / MUSE_AND_OWNER_DECISION_PENDING / PROPOSAL_ONLY / NOT_FROZEN / NO_CAL_APPROVAL / NO_CAL_GO / NO_IMPLEMENTATION / NO_EXPERIMENT
updated: 2026-11-11
tags: world-expansion, preregistration, research-lead, muse-review, final-closure, docs-only, no-execution
author_role: Research Lead (ChatGPT)
parent_review: [WORLD-PREREG-R7-20261111-07](WORLD-PREREG-R7-20261111-07-lead-v5-exact-head-final-review.md)
review_target: [PR #194 v5 exact head 3d98c13818ebb9078c123b8117b7248470e8a10b](https://github.com/ryonakayama234/DekaSugi/pull/194)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **提案であって正本の改変・権限発行ではない**。第5版に反映済みの RQ6 PATCH1〜5＋E1〜E3 は支持する。下記 S1/S2 の**最小限の明示文だけ**を Muse に判断してもらう。数値は候補、CAL の値は未観測、いかなる simulation も実行しない。Owner の明示採用がなければ本提案は有効な仕様にはならない。

## S1（B4）: 10 gate の joint-power simulation に必要な joint outcome 入力の型を確定する

### 見落としてはいけない区別

v5 §5 は `θ*=(Δ*,G1*,G2*,Contrast*)` を指定するが、これは主に**周辺効果/達成率の値**であって、7対照＋G1/G2＋10pp の10イベント間の依存構造や、law ごとのペア差、分散、max-T のリサンプリング分布を定めない。同じ周辺成功率でも依存により joint success は異なる。v5 §6 の `BLIND_DESIGN_CALCULATOR` は E3 に従って読み取り集合を列挙で閉じているため、前の [RQ6 PATCH4](https://github.com/ryonakayama234/DekaSugi/blob/docs/world-prereg-r6-v4-final-acceptance-20261110/docs/research/WORLD-PREREG-RQ6-20261110-06-final-closure-proposal-to-muse.md) で明記した CAL 公開可能な分散要約を、暗黙に「等」として read させてはならない。

### 推奨 PATCH S1-A（閉じた ACL を変更せず、`解析規則`を厳密化する）

**v5 §5 検出力段落への追加規範文案**:

> `θ*` は4つの周辺閾値超過量だけでなく、10判定成分の全**joint synthetic outcome generator** `G_θ` に対する事前登録されたシナリオ識別子を含む。`G_θ` は law/parent cluster ごとのペア差・G1/G2 成否・最強対照差・依存構造・分散/共分散・予算 checkpoint 間の関係を合成でき、固定した q/π/Sampford 設計の下で10イベントと max-T を評価できる**全確率モデル**とする。シナリオ候補集合、`θ*` から `G_θ` を選ぶ規則、感度ケース、モデル digest、および source-first のロール read path は **PROTOCOL_APPROVED で一意に固定**する。CAL の難易度データや正式 holdout outcome を見てモデル／ε を都合よく選ぶことは禁止する。BLIND_DESIGN_CALCULATOR が読むのは現行 §6 ACL の `解析規則`に含めて事前に承認された `G_θ` と既存の設計メタデータだけであり、CAL 観測分散や sealed outcome の暗黙の read は許可しない。得られる同時検出力は `G_θ` を仮定した**条件付き設計値**と明記し、モデル妥当性を未検証の実測保証に読み替えない。入力モデルが不完全なら `STOP_UNKNOWN`。

**意義**: E3 の既存 closed read set を保持したまま、CAL プロトコルで`解析規則`の中身を埋めればよい。推定対象 H、HT、m=10、α/β、route の分岐は変更しない。**この案を Research Lead の第一推奨**とする。

### 代案 PATCH S1-B（CAL 分散要約を使いたい場合のみ、新たな明示 ACL を承認）

PROTOCOL_APPROVED において、独立した CAL 結果集約ロールの**非秘密・非 holdout の CAL 多変量要約**を、別名 `CAL_JOINT_SUMMARY` として事前に定義し、§6 calculator ACL の READ 項目に**明示追加**する。最低限、各 arm のペア差分布、10ゲートの joint 対応、parent cluster 共分散、欠測・不確実性と provenance digest、当該要約から `G_θ` を構築する決定的関数・範囲・合成乱数源を PROTOCOL_APPROVED に lock する。CAL GO 前には実測 summary は存在せず、GO の権限で作成されてからだけ read 可。sealed holdout の真値・score・seed・law ID の外部出力を一切許さない。**Muse と Owner が ACL の変更を採用しない限り S1-B を実行してはならない**。

**判断**: S1-A と S1-B のどちらかを明示選択し、同じ trial で都合よく後から切替えない。どちらも未許可 CAL 実施を含まない。

**最小受入試験**: 2つの判定成分の各周辺通過確率が0.9でも、失敗完全同時なら同時通過0.9、互いに排反なら0.8になる。これらの joint model が同じ `θ*` の4周辺値の下で区別でき、`G_θ` と protocol digest がない計算は `STOP_UNKNOWN` になること。10イベントの max-T / PPS cluster の同時決定則まで第三者が同じモデルで再現可能なこと。

## S2（B5）: episode と run の outcome key を分離する

v5 §4／§6 outcome に次の置換（schema field 名だけの変更）を提案する。

| 対象 | 新しいキー名 | 値／計算時点 |
|---|---|---|
| **episode ログ**（現行 §6 `outcome_kind=(SUCCESS/FAIL/ABSTAIN/FAULT_ACTION)`） | `episode_outcome_kind` | SUCCESS / FAIL / ABSTAIN / FAULT_ACTION。episode 終了時までに記録し、run が STOP_INVALID でも監査用に残す。ACTION_FAULT は event_kind として別に記録する。 |
| **主推論 run 集約**（現行 §4・§6 の `outcome_kind`） | `run_inference_outcome` | NEGATIVE / SMALL_EQUIVALENT / POSITIVE / BELOW_THRESHOLD_POSITIVE / INCONCLUSIVE。**run_status=COMPLETE** かつ有効な集約のみで計算。それ以外は null（結果を認定しない）。 |
| **family／action／run 状態**（既存の3階層） | `family_status`, `action_event`, `run_status` | **現行どおり**。FAMILY_INVALID は `run_inference_outcome` のカテゴリに入れない。 |

§6 の5分類の決定順序・K2・K4/HT の扱いは変えず、使い分ける列名だけを本文/manifest schema に固定する。旧 `outcome_kind` は「一語二義」で利用せず、バージョン付き alias が必要なら移行表に明記する。

**最小受入試験**: (a) ACTION_FAULT を含む未完 run の episode データが記録される、(b) FAMILY_INVALID で STOP_INVALID の場合 `run_inference_outcome=null` だが episode の SUCCESS/FAIL 台帳は保全、(c) 完了した run でだけ正/負/等価/不精確ラベルが計算される。第三者がログ列の意味を推測する必要がない。

## 非 blocking: S3 / S4（schema 化の際に規定）

- **S3**: `H` の二義（§5 holdout law 集合と §6/付表A の horizon）は、schema では `H_laws`／`T_horizon` として型別に命名する。数学的記法を全面書換えする必要はない。
- **S4**: v5 §7 CAL_AUTHORIZED に「§6 に明示した**評価側 BLIND_DESIGN_CALCULATOR の設計メタデータ read のみは CAL oracle の抽象定義制限に対する明示例外**」と追記してもよい。例外は実 instance/target/score/EVAL seed の読取・学習側へ計画結果を逆流させる権限を追加しない。

## Muse への一括受け入れ申請

**(i)** S1-A を推奨（別の統計根拠が必要なら S1-B の explicit ACL で改訂）、**(ii)** S2 の命名分離を採用、**(iii)** S3/S4 は CAL プロトコル schema で扱う、という最小閉鎖案の採否を **ACCEPT / ACCEPT_WITH_EXPLICIT_EDIT / REJECT** で一括判断してほしい。修正要求があれば対象行の**置換文**と反証/受入試験を返すこと。

**Research Lead の判定**: 第5版の現行テキストは B4/B5 の２契約が未明示で **全 PASS と設計合意を宣言できない**。一方、PATCH S1-A と S2 は、研究主張や評価器・比較 arm・候補数値・CAL 権限を変えずに閉じられる最小の追記である。Muse の審査と Owner の採用後、正本の exact head で再確認すれば、残る次の決定を Owner の CAL プロトコル承認可否だけにできる可能性がある。

そのときも CAL プロトコル承認と CAL 実施 GO・凍結・実装・実験 GO は、v5 §7 のとおり別々の明示判断である。
