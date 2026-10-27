# METRO-ONTOLOGY — 知能測定の操作的定義

id: METRO-ONTOLOGY
status: proposed; not_implemented
updated: 2026-10-27
tags: metrology, constructs, plasticity, transfer, epistemology

## 目的と適用範囲
DekaSugiの知能を、課題分布D・予算B・独立検証規則Vに条件付けた **遂行能力** と、経験Eによって利用可能な知的行為を変化させる **可塑性**、その変化が別分布で役立つ **転移** の構造として操作的に研究する。単一の知能指数、人間一般知能の定義、既存DSLのマクロからの未知原始演算獲得を宣言しない。

DekaSugiの対象は知識の蓄積だけでなく、対象を選ぶ・分解する・変換する・比較する・検証する等の **知的行為の共通構造** の獲得。領域間共通性は仮説であって現在の証明ではない。技能数は能力の代理指標にすぎない。

## 状態モデル（提案）
- S_t = (P_t,L_t,M_t,π_t): P=固定/利用可能なprimitive意味論、L=外部技能・概念、M=経験・記憶、π=探索/選択/学習方策。
- S_(t+1)=U(S_t,E_t): 経験Eによる更新。学習前後の **同一の課題分布と予算** でのpaired comparisonが必要。実際にSが保存/再現できなければ state=unknown とし推測しない。
- C(S,D,B,V) = Pr[x~D]{verified_success(S,x;B,V)}: 条件付き成功確率。コストは別座標にする。有限holdoutからの推定値と真の確率を混同しない。

## 測定される構成概念と観測可能性
| Construct | 操作的な問い | 例 | 現在の可否 |
|---|---|---|---|
| competence | 同じ予算で何を解けたか | audited success / total | measured in scoped experiments |
| efficiency | 正確性を保ち何の費用が減るか | canonical calls、候補、CPU | measured with distinct units |
| plasticity | 同量の経験でどれだけ状態が変化したか | learning curve, paired gain | future independent experiment |
| retention | 後続学習で過去の能力を失うか | forgetting/backward transfer | multiple cycles required |
| transfer | 異なる分布/領域で利益をもつか | cross-domain paired gain | unseen domain & adapter controls required |
| adaptive_agency | どの情報・操作・学習課題を選ぶか | query value / abstention | future active controller required |

データ品質・測定器信頼性は能力軸に加算しない。公平性、欠測、評価機密性、構成概念妥当性は測定工程の責務。

## 三層の認識論
- L1 Observation: 計測された事実。例: verifier内canonical primitive invocationが10。
- L2 Estimate: 条件付き分布での正答率/費用差と不確実性。
- L3 Claim: 学習の寄与・転移・能力獲得についての解釈。必ず代替説明と適用範囲を記述。
L1からL3へ飛ばない。numeric gateのPASSはメカニズムの因果証明、汎用化、CPU利益の証明ではない。

## 課題の共通化と領域拡張
領域別TaskAdapterが観測・操作・正解基準を提供する。Adapterの開発努力や獲得済みドメイン知識を、AI自身が転移させた能力として数えない。共通行為（選択、分解、変換、照合）の再利用可能性は、異領域で学習済み状態と非学習状態を比べることによって初めて検証する。

Related: [metrics](metrics.md) / [validity](validity.md) / [evidence model](evidence-model.md) / [METRO plan](../../experiments/METRO-0001/plan.md).
