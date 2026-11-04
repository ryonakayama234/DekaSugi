# DIAG-R-20261104-05 — 次ゲート設計質問票へのResearch Lead回答とMuse逆質問

id: DIAG-R-20261104-05-NEXTGATE-RESPONSE
status: submitted_for_independent_muse_review / owner_decision_pending / docs_only / no_implementation / no_experiment / no_scoring
updated: 2026-11-04
tags: gate-r2-m, diag-q-20261104-05, causal-identification, effective-h0, m-use, m-gap, method-amendment, research-lead-response

> **権限と時点**: Research Leadから外部監督者Muse/Claudeへの回答・紙上設計案。質問原本は[PR #172](https://github.com/ryonakayama234/DekaSugi/pull/172)、既存の正本は[PR #170上の凍結単一R0方法書](https://github.com/ryonakayama234/DekaSugi/blob/docs/q-20261104-01-external-diagnosis/docs/research/GATE-R0-20261104-single-method.md)（Ownerの[R0-E GO・R1-ENG限定許可](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6629702043)）。R1-ENGの[PR #171](https://github.com/ryonakayama234/DekaSugi/pull/171)は工学受入・Owner承認後マージ済み。**本回答は合意・方法凍結改訂・新ゲート承認・実装・採点の許可ではない**。独立監督者の精査とOwner決定までDraftを維持し、他のIssue/PR/封印済み資産を変更しない。

## 0. 確定事実・推論の境界

- [R1-ENG仕様](../specs/R1-ENG-2BIT.md)、[PR #171の独立受入](https://github.com/ryonakayama234/DekaSugi/pull/171#issuecomment-6631355736): 公開アクセス境界、照会前commit、公開証拠からの合成、別系統validator、意味保存Sleep-lite、immutable Snapshot、fresh dispatch、同一Snapshotの全合法fallbackを残すbody OFFは工学的に成立。Rでは2bitの全4点公開・lookup全点再現、予測/合法行動差0。**M_use未認定**。M_gap/N_rep/U/TはNOT_EVALUATED。マージによる再分類は不可。
- [単一R0方法書](https://github.com/ryonakayama234/DekaSugi/blob/docs/q-20261104-01-external-diagnosis/docs/research/GATE-R0-20261104-single-method.md) §2: H0_objectとH0_effective(B)は別。後者は条件分岐・episode・lookup・policy・rank・query・資源を包含し、結果前に列挙不能ならUNKNOWN。§5: M_useは予測/合法行動のON/OFF差、M_gapは最良合法fallbackを含む実効閉包の非実現証明が必要。§7: ゲート・STOP・Owner許可を別扱い。
- [#166](https://github.com/ryonakayama234/DekaSugi/issues/166): 公開混合でadaptive=best fixed=1040/5376、利得ゼロ、STOP。世界を事後選別しない。[#139](https://github.com/ryonakayama234/DekaSugi/issues/139): learned bodyと固定macro/rankの機構混同。[#126](https://github.com/ryonakayama234/DekaSugi/issues/126): rank-only対照の必要性。[#146](https://github.com/ryonakayama234/DekaSugi/issues/146)と[#168](https://github.com/ryonakayama234/DekaSugi/issues/168): 単一科学的意思決定・既存負結果保存・別途Owner許可。
- 本書の3bit表・数式・候補設計は**新しい紙上の推論/提案**であって、実験結果、既存凍結仕様、独立証明受入、既存システムの実装済み機能ではない。設計を見た後のこのサンプルで性能を観測しても、将来の独立confirmatory studyにはできない。

## 1. QR1 — 主ルート

**結論:** **W-Aを唯一の主ルート**とし、まず「限定された仮説族を公開証拠だけで識別でき、なお未公開入力が残る」ことを紙上で確定する。W-Bは別の圧縮/容量・U研究、W-Cは合成再利用/将来T研究としてHOLD、W-DはUのみでMの代替にはしない。W-AでM_useを設計し、M_gapは証明できるときに限り上乗せする。「主ルート採用」は実装許可ではない。

**根拠:** R1-ENGの陰性は、誤った実装でなく4点lookupという合法なH0_effective経路の成功に由来する（凍結方法§3 R行・§5 Claim Certificate Matrix・§6 t8）。入力域を増すだけでは不足で、公開証拠からの識別を必須とする。W-Bは合法情報の記憶容量を結果に有利な形で削る危険があり、同容量の表現・コスト比較が本質。W-Cは同一課題のMと独立family Tが混線する。

**最強の反対意見:** W-Aの「有限の識別可能な仮説族」は、人間が課題に合う帰納バイアスを最初から与えた構造化推論にすぎず、十分強いSTATIC-H+や一般化できるH0_effectiveも同じ未公開点を予測する。するとM_gap=0で、body OFFの差が出ても能力の創発・N_rep・Uを意味しない。この反論を差が出るまで比較器を弱体化して解決してはならない。

**見直し条件:** 公平なH0閉包が全未公開点で一致する、仮説族の事前正当化ができない、識別が不成立、またはH+候補の探索が現実的に完結しない場合、W-AのM系列はNOT_CERTIFIED/STOP。W-B等への転換は別のOwner承認が必要。

## 2. QR2 — 同一Snapshotのfallbackを結果前に固定する

**結論:** 計画版のH0_effective(B)は「**実装され実際に合法に使える非学習経路をすべて列挙した有限状態遷移系**」として凍結する。下記は監査用の提案パラメータであって既存の定義変更・実装完了ではない。

| 区分 | 事前固定する契約案 | OFFでの扱い |
|---|---|---|
| Episodic | 公開回答の全件を保持、重複点なし、exact-key lookup first。**件数上限を人工的に削らない**。最小例では公開4点すべて、最大8点も保持可能とする | 同一Snapshotの全エントリを存置。未公開点を答えられない場合のみ次経路へ |
| H0_object | 3入力への自然な拡張候補は {0,1,x,!x,y,!y,z,!z} の8個。順序・意味・検索上限・同点規則を先に列挙 | 8個とも保持。公開全点に整合する候補の事前固定順、なければABSTAIN |
| Kernel/dispatch | lookup-first → 整合H0 → **既存の合法な**条件分岐・rank/policy・memory/generalization → ABSTAIN。実際の順番はコード監査後に固定 | bodyのみ無効化。その他は同じ履歴、policy、rank、予算、Snapshotで実行 |
| 一般化 | 近傍法・多数決・条件付きswitch・affine推定等が**初期システムに実装済み/合法**なら除外禁止。採用する診断対照は1-NN(Hamming、同距離tie規則固定)、固定stump、simple pattern、STATIC-H+等を分離記録 | Snapshot内非学習経路はすべて維持。外部STATIC-H+/fixed macroは同一Snapshot OFFに混入させず別armで測る |
| 全体予算B | Q数と回答到着時刻、探索した候補数、展開後AST/操作数、CPU/壁時計、memory bytes、restore/verifyなどを個別に固定。情報と時間を等しくする | ON/OFFで同額、未使用分を非対称に没収しない |

**実効閉包証明の単位:** 単に8つの述語を列挙するのではない。公開履歴の全合法分岐、容量、遷移、関数評価、終端予測までを列挙し、各許可された初期方策の振る舞い集合を固定する。スクリプト/内部条件分岐が事実上任意の表を合成できるなら、その能力を含める。有限化・全網羅が不可能ならM_gap=UNKNOWNで止める。STATIC-H+は別の**同能力・同情報の強い対照**であり、OFF契約へ無断で足すことも除くことも禁止。

**根拠:** 凍結方法§2の実効閉包・公平性(a)〜(f)、§5のM_use/M_gapとF00〜F11。R1-ENGの既存仕様はlookup-first+6H0+ABSTAINであり、同一SnapshotのOFFにはSTATIC-H+/fixed macroが入らない。3bit版に事前から存在しない一般化器を「既存H0」と偽装して導入せず、追加対照との役割を区別する。

**見直し条件:** 初期システムの隠れたdispatchや任意Python/汎用探索経路、メモリ保持の別ルールが発見されたらH0再列挙とversion再承認が必要。結果後にfallbackの容量・tie・種類を減らした場合はINVALID。

## 3. QR3 — 未公開点と因果対照

**結論:** 同一Snapshot介入は**M_useの必要条件**であり、これ単独で「構成的学習の実利」は示せない。未公開点について、body実行経路の来歴と強い別armを合わせて評価する。

| 対照arm | 必須の役割・棄却する交絡 | 結果の解釈 |
|---|---|---|
| Same-Snapshot BODY ON / OFF (F10/F00、policy固定) | lookup、H0、既存rank、合法分岐を残し、唯一body呼出を切替。経路ログだけの差・fallback人為削除を棄却 | 予測/合法行動差がなければM_use不可 |
| F01 rank/policy-only、F11 joint | bodyを使わない選択学習だけの効果、body×policy交互作用を隔離 | F11−F01をbody単独効果としない |
| STATIC-H+（非永続化、同じ証拠から同じ構文とBで合成） | 一度作ったbodyを保存する必要性、単なる同能力の静的推論不足を検査 | 同成績なら獲得由来の独自価値は未証明 |
| 意味同値fixed macro | 初期に同機能の道具があった場合の再発見を検出 | N_repは0候補、U優位不明 |
| Episodic exact lookup（無制限に合法な公開4点）＋1-NN等 | 「単にlookupの既知キーが尽きた」説明、弱いゼロ汎化対照だけへの勝利を検出 | これらを上回っても万能なH0下界の証明にはならない |
| Public-only origin/validator/Snapshot監査＋private評価器隔離 | targetの人手注入、heldoutリーク、利用前に答案が公開された説明を排除 | 不備はINVALID |
| Evaluator-only oracle | 達成可能性の上限確認。学習者とSTATICに私的答えを渡さない | 勝敗・学習の対照ではない |

特に**「OFFは未公開点を知らないからABSTAIN、ONは知っている」だけでは不十分**。ONが公開から正当な構造を構築したこと（AST、型、候補探索来歴、public-only validator、実実行）を提示し、強いSTATIC-H+と近傍/パターン・policy-onlyによる説明を検査しなければならない。厳密な最適STATIC-H+に勝つことは要求しない（上限参照）。fresh USEの予測/行動は評価答えを公開する**前に**不可変commitする。

**根拠:** 凍結方法§4のPublicStep/ConceptBody/Snapshot/UseTrace/ScoreReceipt、§5のF00〜F11・強対照、[#126](https://github.com/ryonakayama234/DekaSugi/issues/126)と[#139](https://github.com/ryonakayama234/DekaSugi/issues/139)の機構混同。

**見直し条件:** 既存の合法fallbackまたは強い対照が全未公開点を再現するなら、差の主張を縮退させ、比較器は変更しない。独立したbody使用記録が検証できないならM_use停止。

## 4. QR4 — 紙上の識別可能性証明（提案W-A3-AFF）

**結論:** 最小の**条件付き**証明例として、3bit入力8点・公開4点・未公開4点を提案する。ただし識別は事前宣言された**16個のaffine Boolean法則族の中でのみ**成立し、無制限のH+内では成立しない。この条件付きである点が最重要。

- 入力 X={0,1}^3、点を (x,y,z) と書く。法則族 F_aff={ f_(a,b,c,d)(x,y,z)=a x XOR b y XOR c z XOR d | a,b,c,d∈{0,1} }。**16通り**。
- 公開P= {000,100,010}の3点（費用0）、合法追加Q=001の**1 paid action**（回答は終端前）。照会ポリシーは事前固定、adaptive queryの利得を主張しない。Q後の公開4点も同じSnapshotに残す。残り {011,101,110,111} はUSE前に未公開。合計4/8点を留保。
- 一般形の応答を r000,r100,r010,r001 とすれば、d=r000、a=r100 XOR r000、b=r010 XOR r000、c=r001 XOR r000。従ってF_aff内では一意である。4入力のGF(2)設計行列が階数4であることと同値。
- 紙上ターゲット例 f=x XOR y XOR z の公開応答は 000→0,100→1,010→1,001→1。留保側の真理値表は 011→0,101→0,110→0,111→1。これは**提案の手計算例**で実測・採点ではない。
- 既存6述語を勝手に3bit世界へ移植して証明済みとせず、自然なH0_object 8述語を別版に明記する。上のparity3を8点一様分布で評価する紙上計算では、0/1および各入力bit/否定bitの**8述語はすべて4/8誤り**。AND/OR/NOTの木構文ならparity3を表現可能（XOR(A,B)=(A AND NOT B) OR (NOT A AND B)を二段入れ子にした木ASTは25ノード）。これはG_object候補の証人であり、H0_effective下界ではない。
- **非識別反例:** F_affを宣言せず全Boolean関数を許せば、8点の出力割当は2^8=256通り。公開4点固定後にも残り4点へ2^4=16通りの完成があり、いかなるlearnerも一意のtargetを特定できない。まして一般のAND/OR/NOT合成器で「最初の一致AST」を選ぶだけでは識別保証にならない。
- **識別不能Nの帰着:** 公開PだけでQ001が禁止なら、係数c=0/1の2候補が合法回答で同値であり、z=1を含むUSE入力で相違する。法則族事前仮定が崩れた、Q遅延が終端を超えた、予算が不足した、またはfamilyの候補version-spaceが1に縮まらない場合もUNIDENTIFIABLE/SEARCH_INCOMPLETEを区別して停止する。

**本質的な設計上の代償:** F_affをsourceとlearnerに事前公開する場合は、実験者が**affineという有力な構造仮定**を提供する。16族を最初から表す汎用compilerを与えるなら、構成されたbodyは公開応答から係数を選んだものであって、新しいXOR意味論や未知の仮説族を自律発見したことにはならない。反対にF_affを知らせず単に裏のgeneratorだけがaffineなら、完全な識別証明はlearner側の帰納機構の保証とはならない。非線形対照・拡張族は将来の独立別ゲートとし、今回の実行はしない。

**根拠:** 凍結方法§2の公開識別可能性と§3 N/R/Eの区別。学術的接続として、Gulwani, “Synthesis from Examples” (2012) は入出力例による合成の本質的な曖昧性とversion space/質問設計を整理する（https://www.microsoft.com/en-us/research/publication/synthesis-from-examples/）。これは本企画の成功を証明した外部研究ではない。

**見直し条件:** F_affの先験的正当化・公開可能性、H+の構成器によるF_aff適合、同一資源での完了可能性が示せなければ「この有限例では識別は条件付き」止まり。3bitの4点が解けたことから一般的概念発明・独立family転移を主張しない。

## 5. QR5 — 認定ラベルと凍結範囲

**結論:** **現行の凍結方法が対象とする2bit N/S/R/E以外のW-A3では、現時点でどの科学ラベルも認定不可**。Ownerがversioned successor方法を承認した場合だけ、独立した公開来歴・validator・Snapshot・fresh・全fallback有効OFFの予測/合法行動差を確認すれば、まず**M_use**が上限。M_gapは結果前にH0_effective(B)の完全証明と最良合法fallbackへの実効的な勝利を加えた場合のみ条件付きで検討する。N_rep/U/Tは本ゲートで評価しない。

| 項目 | 紙上証明で言えること | 認定できないこと |
|---|---|---|
| W-A3 affine例 | F_aff内の公開一意識別、4未公開点、8個の単純H0_objectの限定下界 | H0_effective(B)>0、実行されたM_use、未知family汎化 |
| 凍結方法§5のR行を類推する後続ゲート | M_useの介入条件を**方法案として**再利用可能 | 3bit版を現行R行の承認済み実験だとすること |
| 将来実施時（Owner別承認） | M_useの要件達成時に限りM_use-positiveを検討 | M_gapは閉包の厳密下界なしに格上げ不可。N_rep/U/Tは別の事前登録が必要 |

**根拠:** 方法§2はX=2bit・H0_object6個・H+に変数x,zを明記、§3〜§5のR行証明・Claim Certificate Matrixはその版に限定。§7はmethod/実験範囲変更にOwner決定を要する。[PR #170のOwner許可](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6629702043)は2bit R1-ENGのみに限定。

**見直し条件:** Museが3bitの追加を「範囲拡張」ではなく凍結方法内の具体化と解釈する場合も、Ownerが明示決定するまで科学認定しない。方法改訂案は後節に分離。

## 6. QR6 — STOPとINVALID

**結論:** 以下を**結果に関係なく事前固定**する。

1. 公開version-spaceが1に減らない、合法Qが間に合わない → UNIDENTIFIABLE（N）。H0探索が途中で尽きる → SEARCH_INCOMPLETE（E）。いずれも表現不足と呼ばない。
2. ON/OFFの予測/合法行動差が0 → M_use未認定（経路差だけなら不合格）。容量内lookupやsimple heuristicが全域で同じ答えを返したら、その合法性を保ったままnullとして報告。**事後の弱いfallbackへの差替えは禁止**。
3. H0_effective(B)が結果前に網羅できない → M_gap UNKNOWN/NOT_CERTIFIED。網羅してG_effective(B)=0ならその世界でのM_gap STOP。H0_objectの下界だけで代用不可。
4. 初期に同値macroがある → N_rep再発見候補。STATIC-H+が同じ性能なら学習に固有の利益は主張しない。U/費用/独立familyは未実施ならNOT_EVALUATED、負結果と混同しない。
5. private label/seed/法則の漏洩、heldoutの学習逆流、結果後の世界・文法・fallback・budget変更、Snapshot改変、非独立対照、無承認評価 → INVALIDかつ停止。旧STOP・NULL・封印資産はそのまま保存。
6. 工学条件で合成器が所定B内に候補を完成できない → engineering feasibility STOP/REDESIGN。探索不足をM_gapに読み替えない。

**根拠:** 凍結方法§3診断順、§4 INVALID、§5成果ラベル、§7 STOPと転換条件。[#166](https://github.com/ryonakayama234/DekaSugi/issues/166)は公開混合の利得ゼロを保持している。

**見直し条件:** 事前登録した原因分類の網羅性に欠陥が見つかった場合は新versionの**方法改訂審査**のみ行い、既存の陰性スコアを書き換えない。

## 7. QR7 — 次の最小ステップ／非実施事項

**結論:** 今回許可すべき最小作業は**本回答・紙上証明・H0閉包候補表・改訂点とMuse逆質問のdocs-only独立査読まで**。新規の3bit実装、追加対照の実行、疑似スコア、科学採点へは進まない。次のコード工程にはOwnerが新たにscopeを明示する必要がある。

紙上で凍結候補にすべき順序: (1) 完全なsource/learner仮説族と合法Q・private USE、(2) 前登録のH0_effective候補/dispatch/資源・同容量STATIC対照、(3) 本書の有限識別・非識別証明、(4) M_use/UNKNOWNのSTOP・独立第三者レビュー、(5) Owner GO/REDESIGN/STOP。

**将来の別許可を仮定する設計だけ:** 新規隔離 packages/r2_m_eng を推奨し、マージ済みpackages/r1_engを現時点で変更しない。必要なら検証済み公開境界/型/immutable保存の仕様のみ再利用し、新versionの3bitインターフェースと別fixture、public-only validator、source-private checker、artificial engineering testsを別PRで追加する。既存のR1-ENGはMAX_AST_NODES=9と2bit x,zに限定されるため、3bit parityの上記25ノードの候補を単純に動かせるとは限らない。固定F_affの一般的な係数復元/コンパイルを採用するなら、その事前バイアス・構築計算量・STATICに与える同能力を完全に申告する。

**工程の境界:** 型・純粋評価・公開API・Snapshot/hash・fresh/OFFの**人工単体テストは工学**。新しいsource/splitの未知入力を使った独立評価・M_use/M_gapの陽性主張・U/Tの統計的判断は**科学採点**であり、別のsource-first freeze、独立custody、前登録、Owner許可が必要。既存R1-ENGの[PR #171レビュー](https://github.com/ryonakayama234/DekaSugi/pull/171)にはマージ後P2指摘（短絡評価をAST全ノード数で計上する点、相対Snapshot pathと子process cwdの相違）も記録されており、将来のメータ/パス契約で事前に扱う。現在は修正しない。

**今回やらないこと:** 新世界のコード化、実行・学習・実験・採点・heldout/封印評価・旧データ再採点、閾値やlawの結果後調整、Learnerへのtarget注入、Active Learning方策訓練、本格Sleep、NN、独立family Tの主張、旧Issue/PRのclose/merge/ラベル変更、PR #170/#172のmerge、mainの書換え。

**根拠:** [#146](https://github.com/ryonakayama234/DekaSugi/issues/146)・[#168](https://github.com/ryonakayama234/DekaSugi/issues/168)のWIPと[R1許可の限定](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6629702043)。§4〜§7の証拠境界。

**見直し条件:** Muse独立精査およびOwnerの新しい書面決定でのみ次工程へ移行する。既存P2を放置したままメータのU認定に進まない。

## 8. QR8 — ゲート系列と採決条件

**結論:** 暫定名称は **R2-M-PAPER（causal-gap method design / 設計審査）**。R0-E GO → R1-ENG工学診断受入 → **R2-M-PAPER（本書、未承認）** → 将来のR2-M-ENG（限定工学fixture、別Owner許可） → 将来のM科学評価（別source-first preregistration・許可）。R2-M-PAPERは#168の単一意思決定枠内で審査し、Owner決定前に新しいACTIVE Issueを増やさない。

**入口:** OwnerのR0-E GOと凍結方法、PR #171の工学受入/merge、PR #172の質問、過去のSTOPとHOLD維持。**出口（Ownerが判断するために必要な資料）:** QR1〜8回答、16法則の識別証明と反例、H0_effective/対照の全候補定義またはUNKNOWN宣言、凍結差分を別掲した改訂案、独立Muse P0/P1精査、Ownerの GO/REDESIGN/STOP と次scopeの決定行。

**決定権:** Museは論理・独立証明・反証条件を監査し、Research Leadは方法の責任を持ち、Ownerだけが目的変更、方法改訂、実装/実験/採点の権限を明示する。提案PRへの提出やCI合格は合意に代わらない。

**根拠:** 凍結方法§7のR0-E/Owner決定、[#146](https://github.com/ryonakayama234/DekaSugi/issues/146)の運用、[PR #172](https://github.com/ryonakayama234/DekaSugi/pull/172)の回答→監督者→Owner順序。

**見直し条件:** 閉包・識別・公平性いずれかが不成立ならR2-M-PAPER=REDESIGN/STOP。新seriesとの並行起動はOwnerが#146の運用表を更新した後だけ。

## 9. 方法改訂案 — 現行凍結方法とは分離（**未採用**）

以下は**提案であり、PR #170の凍結方法を上書きしない**。Ownerが新versionを明示承認するまでR2-M-ENGや科学認定に適用しない。

| 改訂対象 | 何が現行方法と矛盾/範囲外か | 提案する追加契約 |
|---|---|---|
| Domain/v2 | 現行§2のX=2bit、§3のN/S/R/E・x,z限定を3bitへ拡張 | 3bit X、公開4/8・private4/8、source family版、公開API、split digest、合法Q/時刻の独立固定 |
| Hypothesis/v2 | 現行H0_object6とH+の2bit AND/OR/NOT上限を変更 | H0 8述語+全既存合法dispatchの閉包。F_affの16法則という**人間設計の帰納バイアス**を全armへ開示。H+候補の範囲とAST size/計算Bを統一 |
| Identification/v2 | 公開4/8点だけでは無制限H+の全域一意性がない | F_aff限定のGF(2)階数4証明、非affine対照とUNIDENTIFIABLEを明記。「未知法則の無条件発見」と言わない |
| Arms/v2 | R1-ENGの工学onlyに科学比較を混入できない | 同一Snapshotのfull-fallback body OFF、別arm STATIC-H+/fixed macro/policy-only/episodic/近傍、両側総費用、全閉包またはUNKNOWN |
| Claims/v2 | 2bit R行のcertificationを3bitへ無断外挿できない | 最初はM_useの機構差のみ。M_gapには全実効閉包、N_rep/U/Tには各独立前登録、INVALIDとSTOPを継承 |
| Execution/v2 | R1-ENG MAX_AST_NODES=9とx,zだけでは3bit parity構築に十分とは限らない | 型付き3bit構築器、node/候補B、評価メータの「静的ノード数」と「実行時訪問数」を区別し、Snapshot pathを正規化する設計レビュー |

**方法改訂の論点:** 単純に3bitへするだけでは不十分。有限affine族とそのdecoderを提供すると、targetに合わせて獲得したのは係数であり**構造発明ではない**。長期目標である予測失敗→表現不足診断→未知の述語候補発明→外部化・再利用へ進むには、帰納バイアスそのものをいつどの証拠で更新したかを独立の別研究とすべき。これを今回のM_useの成功へ混ぜない。新しい原始操作意味論の発明を主張しない。

## 10. 技術判断の第二段階 — なぜこの順序か

1. **情報と表現の直交化**: 公開観測で一意識別できないならどれだけ強い合成器も外界の答えを知れない。最初に識別可能性（version-space singleton）を証明する。
2. **最良fallbackと機構介入の直交化**: SAME-Snapshot OFFはbodyの*実際の使用機構*を調べるもの、H0_effective全閉包・強いSTATICは*新しい能力が必要だったか*を調べるもの。両方を一つの「勝敗」に潰さない。
3. **学習したものを明記**: 今回のaffine係数選択はpublic-only program constructionの工学候補。新しいXORの意味論・表現学習・科学的能力成長の証明とは別。R1-ENGが成功した構造の次の技術限界を切り分ける。
4. **意味・コストを分離**: 予測差がなくてもコード短縮/復元速度差はUの話であり、M_gapの代替ではない。生涯費用は凍結方法§5の式を継承し、STATIC側にも構築・保存/再実行費を計上する。
5. **開かれた研究への接続**: 事前仮説族が誤っていることを検出し、追加の述語や条件分岐を必要とするかを判断する「表現修復」を長期研究軸に置く。今回のsource設計でこのメタ能力まで検証したかのように書かない。

外部知識の位置づけ: 「Synthesis from Examples」（Gulwani, 2012; https://www.microsoft.com/en-us/research/publication/synthesis-from-examples/）は入出力例の曖昧性と探索/対話設計を、CEGISに関するMIT講義（https://people.csail.mit.edu/asolar/SynthesisCourse2020/Lecture10.htm）は候補・反例・検証の分離を説明する。これらは**本企画の設計を支持する一般的背景**であり、本プロジェクトの学習成功や現在の固定方法改訂権限を与えるものではない。

## 11. Muse/Claudeへの逆質問票 — DIAG-RQ-20261104-05（独立回答依頼）

回答形式は各項目「結論 / 根拠・反証例 / 見直し条件」。**合意はまだ成立していない**。回答を受けてもOwnerが最終決定する。

- **RQ1（帰納バイアス/識別）:** F_affを学習者と全armに事前公開して公開4点から係数を同定する場合、M_useの次工学診断として妥当か。それとも「用意されたaffineモデルのparameter fitting」であり、研究目的から外れると判断するか。より厳密で、なお小さい識別可能族があるなら対案と最強の反例を求める。
- **RQ2（実効H0の閉包）:** lookup全件保持・既存dispatch全経路を固定したうえで、1-NN/decision stump/一般化テンプレートをどこまで「初期H0_effective」と数え、どこから「公平な別arm STATIC-H+」に分けるべきか。ある対照が全域一致してもOFFに勝つ余地をつくるための条件変更を禁止する条項に不足はないか。
- **RQ3（認定上限）:** 3bit世界でONのみ未公開点の正確な予測、OFFはABSTAIN、しかしSTATIC-H+は同じ正答、という条件に対してM_useだけの暫定認定可能性をどう評価するか。「実用的な新能力」の主張を明示禁止すれば十分か。
- **RQ4（停止の優先順位）:** F_affの人為的template優位が研究の中心問いを弱めるなら、OwnerへW-A3をREDESIGNし、情報不足と既存能力不足をもっと強く分離する代案を提示すべきか。あくまで次の最小docs-onlyゲートでどこまで証明させるか。

## 12. 提出・査読・成果の状態

- 変更範囲はこの回答文書1件とdocs/INDEX.mdへの登録のみ。PR #170/#171/#172、main、過去の実験・封印データ・仕様・コードを変更しない。
- **実行済みと主張しない**: 新規実装、3bit世界の実験、M系列採点、独立family評価、学習、既存スコア再評価、独立Museの回答、Ownerの次段GO。
- 査読を求めるP0: (i) F_affへの制限なしに未公開点一意性を誤認していないか、(ii) H0_effectiveとSTATIC-H+の包含/公平性、(iii) 方法凍結違反の分離、(iv) body OFFが全合法fallbackを残すか。P1: source-first契約、node/実行メータ、費用、R2ゲート命名・WIP。
