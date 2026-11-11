# R-20261104-03 — DV1〜DV10: REDESIGN後のAI開発方針へのResearch Lead回答

id: DIAG-R-20261104-03-DEVELOPMENT-DIRECTION
status: proposed / submitted_for_muse_independent_review / owner_pending / no_implementation
updated: 2026-11-04
tags: dekasugi, gate-r0, development-direction, representation-repair, causal-attribution, wake-sleep, no-go

> **判定:** 開発主ルートは **D「因果識別先行の最小概念獲得ループ」**。R0は **REDESIGN / NO GO** のまま。本書は設計回答であり、実装・実験・採点・封印済み評価・close / mergeの承認ではない。質問原本 [Q-20261104-03](Q-20261104-03-development-direction.md) を変更しない。Museの後続査読とOwnerの明示判断は未了。

## 0. 比較・前提・証拠の規律

**既存の観測:** [#168](https://github.com/ryonakayama234/DekaSugi/issues/168)はR0の唯一の活動中科学的決定。[#146](https://github.com/ryonakayama234/DekaSugi/issues/146)は実装停止・WIP=1を要求。[#166](https://github.com/ryonakayama234/DekaSugi/issues/166)ではEXT448の世界ごとのOracle陽性25/448にもかかわらず、学習者に利用可能な公開混合分布で適応=最良固定 **1040/5376、利得0**。[#139](https://github.com/ryonakayama234/DekaSugi/issues/139)／[Draft #141](https://github.com/ryonakayama234/DekaSugi/pull/141)では修正後の問い合わせ行動切替が消失し、学習bodyと静的macroの同値性が露呈。[EXP-0002Bの正式記録](../../experiments/EXP-0002B/runs/20261025-final112.md)は全arm 80/112、LEARNED原始操作6,880 vs OFF6,944で、総CPU利益は未実証。これらはその対象・版の事実であり、別世界への一般化ではない。

**既存合意候補（決定ではない）:** [R-20261104-02 Muse査読](R-20261104-02-muse-review.md)は、H0実効閉包、N/S/R＋探索不足負対照、body OFF、prequential事前コミット、機構M／実用U分離を支持・条件付き支持。ただしOwner判断未了。以下のD案・順序・契約は**Research Leadの新規設計提案**であって測定結果ではない。

| 案 | 初手 | 強み | 最大の失敗モード | 本回答での扱い |
|---|---|---|---|---|
| A 証明先行 | H0/機会/強対照の全面凍結 | 混同・後付けの防止 | 方法が自己目的化しAIを作らない | **必要十分な紙上証明だけ**従属採用 |
| B 縦切り一体 | Wake→問い→body→Sleep→fresh一括設計 | AIの全体像・統合性 | 複数要素同時導入で原因不明、偽の成功 | **将来の統合目標のみ**。初回の主経路から除外 |
| C 段階育成 | S/N/R/質問/転移を順次拡張 | 局所化、プロセスが見える | カリキュラム・アダプタ作成が研究より膨張 | **4つの診断対照**に縮約 |
| **D 最小因果閉ループ** | 公開反例→型付きbody→検証→保存→fresh実行→body OFF介入 | 研究中心仮説を最短の介入経路で検証 | H0の人為的制限、静的H+との実用差が出ない | **唯一の主ルート**。M確認後にU、さらに問い合わせ学習を別ゲート |

### DV1 — 主ルート

- **結論:** **Dを選択**。主張の優先順位は (i) 表現不足が公開証拠から診断可能か、(ii) 人間がターゲットbodyを書かずにそれを形成・永続化・freshで実利用できるか（**機構M**）、(iii) それが同等の候補空間・総費用の強対照に対して役立つか（**実用U**）。Aからは有限証明・アクセス契約だけ、Cからは負対照の順序だけを使用する。Bの全機能同時実装、当初のDREAM生成課題、学習型質問方策、NN、GUI、自然言語、異分野転移、独立family成功主張は初段から**除外**。
- **根拠:** #166の機会ゼロと#139のbody/policy同値性は、「機能を全部入れれば概念学習の証拠が出る」という期待に反する。[精密ドシエ](GATE-R0-20261104-design-precision.md)のM/U分離、およびMuse査読§3に基づく。Dそのものは新提案。
- **見直し条件:** 機構Mを単独に切り出せない、またはRの証明が実効H0を正当に定義できず循環的ならDはREDESIGN。限定Mだけで前進の研究価値がないとOwnerが判断するならSTOPを審議。

### DV2 — 最小の「DekaSugiらしいAI」：完全エピソード（紙上仮説・未実行）

**環境:** Boolean二入力 `x,z` から次の観測bit `y` を予測する小世界。R系列の対象を `y=x XOR z` とする。初期の**限定H0**候補は `0,1,x,!x,z,!z`。学習用H+は型付き `AND/OR/NOT` 構成子で深さ・コード長制約つき。XORの実装bodyは初期Libraryに存在しない。H0のKernel/方策/メモリも、外側の条件分岐でXORを密かに表現できないよう**実効閉包として記述・監査**する。これは能力の宇宙的限界ではなく限定装置の診断である。

| 時点 | 学習者に公開される事実／行動 | 内部仮説／証拠の扱い |
|---|---|---|
| t0 初期 | H0で各入力の予測を**観測前にコミット** | H0のみでは対象真理値表を表せない（証明は評価者側）。未知targetを学習者へ直接渡さない |
| t1 失敗 | 公開 `(0,0)→0`、`(1,0)→1`、`(0,1)→1` を順次観測 | 複数点で単項H0に整合する単一仮説が消える。不一致を記録。単なる探索未完か、モデル空間の矛盾かを分離 |
| t2 問い | 公開候補のうち識別的な `(1,1)` を選び合法に質問 | 今回は**固定された決定的クエリ選択器**でもよい。選択器を手で作った部分はActive Learningを獲得した証拠にしない |
| t3 観測 | `(1,1)→0` を受け取る | `OR` 等の他候補と区別。公開照会不可・遅すぎ・予算不足ならABSTAINし「表現不能」と決めつけない |
| t4 概念候補 | 許可された汎用演算子で `OR(AND(x,NOT(z)),AND(NOT(x),z))` などの型付きbody候補を**自動構成** | ターゲット式のハードコードは禁止。構成子の意味論は人間が与えた前提。固定H+探索と同一候補空間・公開例で照合 |
| t5 公開検証 | 新規許可された公開検証例と、型・効果・不変条件を検査 | 他の整合候補が残る場合は確信しない。検証例を評価用freshに流用しない |
| t6 Sleep | `body AST / 型 / 生成元公開証拠digest / 依存 / 反例 / 版 / status` を外部Libraryへ登録 | WAKEの暫定候補をSleepでcanonical化・同値検査・競合処理し、**採用/拒否を変化**させる。単に保存しただけならSleep効果は未成立 |
| t7 fresh USE | 新ID・新表面配置の同型世界で保存bodyをロードし、実行して予測 | **構造的に独立なfamilyへの転移とは呼ばない**。snapshot保存/ロードと、実行時のbody dispatchを証拠として記録 |
| t8 介入 | 公開履歴・rank・policy・候補集合を可能な限り固定したまま同一SnapshotのbodyだけOFF | fresh予測・合法行動・primitive呼び出しに差があるか。差がなければM不成立。性能改善はUとして別判定 |

**スタブと学習の境界:** 世界の遷移法則、legal action一覧、型付きメタ文法、参照評価器、安全Runtime、固定クエリ方策、負対照の作成は人手可。**XOR body、targetの意味ラベル、family ID、非公開評価答えをlearnerに教えることは不可**。静的H+が全4表を丸暗記できるので、このtoyの良好な予測は「自律的な意味論創造」「独立familyへの一般化」「U」を証明しない。Mには、公開生成由来、body実実行、body OFF差分、既存macroとの意味同値の開示が必要。

- **結論:** 最小完成像は上記の一件の**再現可能な証拠経路**であり、「一つのAI全体を完成させた」という性能宣言ではない。
- **根拠:** [精密ドシエ§3,§7](GATE-R0-20261104-design-precision.md)、[Muse査読MQ1/MQ4/MQ5](R-20261104-02-muse-review.md)、[#142](https://github.com/ryonakayama234/DekaSugi/issues/142)。表のエピソードは本回答で作成した未実行例。
- **見直し条件:** 真に未知の公開反例が合法・時間内に取得できない、H0が外側のdispatcherでXORを表現できる、またはbodyのON/OFF介入が独立にできないなら再設計。

### DV3 — 能力の実装順序

| 能力 | 分類（次段） | 理由と先行依存 |
|---|---|---|
| 不一致・表現不足の検出 | **必須** | H0全候補の整合性と探索未完を別ステータスにする |
| 観測・質問の選択 | **必須（固定・非学習）** | 合法・公開・費用つき照会。**学習型の適応質問は後回し** |
| 型付き操作の候補生成 | **必須** | 対象bodyを教えずH+メタ構文から構築 |
| 候補の検証 | **必須** | 型/構成意味論/公開例/反例の独立チェック |
| 外部道具庫への保存 | **必須（最小）** | immutable typed Snapshot、provenance、digest |
| Sleepでの統合・圧縮・忘却 | **後回し（最小canonical化・保留/拒否は必須）** | 高度なMDL圧縮・自動忘却は二次機構であり同時に導入しない |
| 保存操作の検索と再利用 | **必須** | freshプロセスでのtyped lookup、body dispatchを追跡 |
| 未見課題への転移・合成 | **後回し** | fresh同型USEは必須だが、異family/多段合成は別研究 |
| パラメータ学習 | **当面禁止** | 先に概念体の実験機会・帰属を成立させる。巨大LLMも不採用 |

- **結論:** 「不一致→候補→検証→永続化→fresh body介入」だけを初期の学習可能な核とする。
- **根拠:** #139ではlearned bodyの機構的寄与と静的macroが混同された。#166では問い合わせの機会が存在しなかった。新しい優先順位は提案。
- **見直し条件:** 固定問い合わせでは公開識別可能性が失われる場合だけ、**学習を伴わない**厳密な適応クエリを最小追加。先行ゲートで介入が識別できない場合は増築しない。

### DV4 — 三軸の主張・証拠・対照・中止条件（別仮説）

| 軸 | 主張する効果 | 観測証拠 | 分離対照／ablation | NULL/有害停止 |
|---|---|---|---|---|
| **Active Learning（後段の学習型）** | 公開履歴から学んだ問い合わせ方針が、同予算で終端効用/情報を改善 | 更新前にコミットされた次の合法質問が変化し、同一公開機会でfresh予測差が出る | 最強固定開ループ、静的H+適応プランナー、rank-only、learned query OFF。同一前分岐情報・予算 | `G_inq=0`、公開経路で行動差なし、終端便益なし、情報漏洩ならINVALID |
| **道具化・外部化知能（初段のM）** | 公開反例から構成した型付きbodyが永続化後のfresh推論を変える | 生成履歴→検証→digest→fresh load→実dispatch→body OFF予測差 | 同一Snapshot body OFF（rank固定）、固定macro、episodic retrieval、同容量静的H+ | body未生成/未使用/無差分、意味同値なのに「新規意味」と主張する場合は新規性NULL |
| **Wake–Sleep（後段の追加効用）** | Sleepによる候補整理・抽象化が将来の探索/総費用を変える | WAKE終了時の候補群とSleep後ライブラリに**検証可能な構造差**、fresh利用の費用差 | Sleep OFF（WAKE直後の同容量保存）、単なる重複除去、固定macro、学習量・容量一致 | snapshot内容もfresh挙動も不変、CPU/管理費用増でnet不利 |

**Wake/Sleepの非同義語条件:** 「夜になったから関数を保存した」だけならSleepではない。候補の汎化・統合・競合棄却により**将来参照される表現と行動が因果的に変化**し、その差がSleep OFFと比較可能な場合に限り機構を主張。初段のSleepは整理工程の**最低限の準備動作**であって「Sleepによる性能改善」は未主張。

- **結論:** 三軸は統合アーキテクチャを共有しても、効果主張とゲートを別々にする。
- **根拠:** #166の0、#139のmacro同値、[Muse査読§3](R-20261104-02-muse-review.md)。比較行は新規提案。
- **見直し条件:** 独立介入できないならその軸の成功主張を保留。正対照機会が無いなら学習実験をSTOPし世界定義に戻る。

### DV5 — 三つの学習層

| 層 | 初期の責務 | 学習とは何を呼ぶか | 初期導入 |
|---|---|---|---|
| **記号合成** | bounded typed ASTを公開反例で構成・検証・保存 | 再利用可能bodyの発見。**それ自体を勾配学習と呼ばない** | **必須** |
| **非パラメトリック統計** | 過去の履歴と証拠を索引化し、近傍・頻度を利用。初回は単純な決定的検索に抑える | kNN等はデータ保持に依存する統計的学習。記号合成の効果と分離 | **最小検索のみ**。学習型検索は後回し |
| **パラメータ表現** | 将来、演算選択・圧縮・質問順を学習する小規模モデル | 独立した訓練で共有パラメータが更新されfresh予測が変化 | **当面禁止** |

- **結論:** 現時点でNNを導入する合理的トリガーはない。導入条件は、(a) Mが確認され、(b) 固定/非パラメトリック/学習rank強対照の計算上のボトルネックが実測され、(c) 同一機会・予算で小規模パラメータモデルに固有の予測があり、(d) Ownerが別ゲートを承認、の全て。
- **根拠:** [Muse査読QD4](R-20261104-02-muse-review.md)はkNNの非パラメトリック性を訂正。NNもLLMも、観測できない情報・表現能力不足の証明漏れ・リーク・不公平なH0比較・実験機会ゼロを解決しない。
- **見直し条件:** 記号/検索を工夫しても計算制約内で候補提案が成立せず、かつパラメータモデルの独自学習信号が外部情報として成立したとき、独立した研究提案として検討。

### DV6 — 最初の世界・関係family・操作型

- **結論:** **Rの2bit有限関係世界**、関係候補は `XOR(x,z)` と `OR(x,z)` など、獲得対象は **`Bool×Bool→Bool` の型付き二項合成述語body** を推奨する。証明用の**単一構造family**から始め、生成seed、role-renaming、構文同値を独立familyと呼ばない。これは最初の「科学的陽性母集団」ではなく、方法診断装置である。
- **根拠:** [精密ドシエ§3–4](GATE-R0-20261104-design-precision.md)でH0の6候補とH+の全4真理値表が紙上比較可能。H0最小誤りはXOR 2/4、OR 1/4（**限定H0に対してのみ**）。H+で表現可能ゆえ仮の `G_expr>0`。公開 `(1,1)` を費用内に観測できればXOR/ORを区別できる。ただし未知候補集合全体の識別可能性は**対象モデルと質問集合に対する網羅的証明が必要**。`G_inq` は今回は主張しない。たとえ最良固定問い合わせで同じ結果が得られてもMの機会はあり得る。
- **対照配置:** N=合法公開照会では区別不能、S=H0に真の関数あり、R=H0全候補不整合かつH+整合、E=H0内に正解があるのに探索を打切って誤診する**探索不足負対照**（Muse追加要求）。それぞれ公開可達性、照会の時機、cost、有限全列挙を紙上で固定。Nは学習器の失敗とは呼ばない。
- **見直し条件:** H0の外側のKernel/memory/dispatchに正解が隠れていたら `G_expr` の証明撤回。全公開データが到達不能なら `public_identifiability=false`。単一familyで学習の機構Mを示せても、実用U・分野間転移へ一般化しない。

### DV7 — 実装開始までのロードマップと承認境界

| Gate | 目的・成果物 | 入口 → 出口条件 | Ownerの決定 / STOP–REDESIGN | 禁止する並走 |
|---|---|---|---|---|
| **R0-P（現時点）** | このDV回答、N/S/R/Eの紙上法、R0-A証拠のリンク | #168 ACTIVE → 実効H0定義、有限全列挙の論証、公開アクセス・費用・強対照の契約を**単一方法文書**へ統合 | OwnerはD採否とR0-Eを決定。証明不能/循環ならREDESIGN/STOP | **全新規実装、実験、採点、PR整理** |
| **R0-T** | 1エピソードの紙上時系列、M判定ロジック、データ型と信頼境界、前登録の停止表 | R0-P完成 → Muse独立査読P0なし、Ownerが仕様を承認 | この段階でもコードは**まだ不可**。P0/P1あればR0-Pへ戻す | コード、別world、別学習器、旧評価 |
| **R1-ENG（将来・条件付き）** | 1 world / 1 relation type / CPU・stdlib・隔離パッケージの**診断実装** | **R0-Eの明示GOとR0-Tの独立査読完了、Ownerの新規coding指示**を両方満たす時だけ許可。型/公開境界/負対照の人工unit testのみ | 漏洩/不公平比較/変更された旧score経路はSTOP。**fresh科学スコアは不可** | NN、学習質問方策、自然言語、複数family、過去のsealed評価 |
| **R2-M（将来・別承認）** | 公開Wake→候補→Sleep最低限→Snapshot→fresh body OFFの機構的診断 | R1の最新head安全・方法査読 → 新規の許可と独立証拠保全 | 成果はM/意味的新規性/不確実性別記。M不成立なら別能力を足さずREDESIGN | 別研究の同時実験、formal FINAL |
| **R3-U（将来・別承認）** | 同一H+容量のSTATIC、episodic、fixed macro、rank-only、body OFF等との総費用比較 | Mとfamily独立性、分布・power・source lock・custodyの先行凍結 → Ownerが独立評価を**別途**発動 | UがNULL/NEGATIVEならそのまま保存。従来のFINALは再利用しない | 評価後の世界選別、旧シーリング解除 |
| **R4（将来）** | 問い合わせ学習／Sleepの正味効果／異family転移を**各一研究**として提案 | U結果・資源ボトルネック確認 → 別のOwner決定 | `G_inq=0`で問い合わせ学習STOP。失敗を別成果で覆わない | 複数科学的決定の並走 |

- **結論:** **今許されるのは設計文書と査読だけ**。R1でコードが許されるのは、**OwnerがR0-E GOを明示し、R0-Tの方法契約を再査読した後**の隔離されたtoy診断に限る。M実験、fresh科学採点、NNは各々さらに別許可が要る。
- **根拠:** [#168](https://github.com/ryonakayama234/DekaSugi/issues/168)のR0-A〜E、[#146](https://github.com/ryonakayama234/DekaSugi/issues/146)のWIP=1、Muse査読§5。
- **見直し条件:** OwnerがSTOP、査読のP0未解決、source custodyの問題、旧評価トリガーの安全性未確認。

### DV8 — 資産と滞留物

| 分類 | 基準 | 例と扱い |
|---|---|---|
| **参照・採用候補（ただし読み込みのみ）** | main上の安全境界・測定契約・型仕様と、正負両方の原本が明示されている | [README](../../README.md)、[ARCH-001](../architecture/system.md)、[ARCH-002](../architecture/contracts.md)、[EXP-0002B正式記録](../../experiments/EXP-0002B/runs/20261025-final112.md)、[#168](https://github.com/ryonakayama234/DekaSugi/issues/168)、[本PRのR0設計](GATE-R0-20261104-design-precision.md)。将来の移植は独立した小PRとレビュー |
| **HOLD／歴史的証拠固定** | 実験系列・Draftに未統合の実装がある、結果がNULL/NEGATIVE、方法確証が未了 | [#142](https://github.com/ryonakayama234/DekaSugi/issues/142)、[#162](https://github.com/ryonakayama234/DekaSugi/issues/162)、[#139](https://github.com/ryonakayama234/DekaSugi/issues/139)、[#166](https://github.com/ryonakayama234/DekaSugi/issues/166) / [Draft #167](https://github.com/ryonakayama234/DekaSugi/pull/167)。元結果・SHA・保護workflow・source lockを変更せず残す |
| **将来の整理候補（今回は操作禁止）** | superseded設計・重複・HEAD競合・証拠不明 | [#146](https://github.com/ryonakayama234/DekaSugi/issues/146)に根拠付き分類を提案するだけ。close/merge/label変更は別途Owner決定 |

- **結論:** 「資産を再利用する」= 過去の実験結論を借りることではなく、監査可能な**契約・負対照・安全機構**を新しい世界へ適応すること。Draft実装をmain実装とみなさない。
- **根拠:** #146のHOLD、#168の停止条件、#166の厳密ZERO、Muse査読QD8。
- **見直し条件:** 個別資産のSHA、依存、信頼境界が独立確認できた場合だけ別Owner承認で移植を検討。

### DV9 — 知能を「過程」として測る

**最小の追記専用証拠レコード（新提案）:** `episode_id, seq, public_state_digest, hypothesis_space_version, pre_observation_prediction, prediction_digest, query_choice_before_answer, legal_action_set_digest, paid_cost, public_answer_digest, posterior_or_version_space_digest, mismatch_kind, candidate_body_digest, validator_receipt_digest, sleep_before/after_digest, frozen_snapshot_digest, fresh_dispatch_digest, wall/cpu/primitive_calls, evaluator_artifact_digest`。各ステップで**答え受領前に予測をコミット**し、その後に結果を記録。hashはコミット整合性の手掛かりであって、独立原本custodyの代替ではない。

- **結論:** prequentialな更新前予測の損失系列、仮説改訂、却下候補と理由、body使用率、コストの推移を記録。最終のfresh正解率と区別する。相手側が学習しない現行環境で「対話の互恵性」を科学的に主張することはできない。長期VISIONに**研究上の問いとしてのみ**残し、現段階は「問い合わせを通じて自己の予測を更新した軌跡」まで。
- **根拠:** [Muse査読MQ6](R-20261104-02-muse-review.md)、[精密ドシエ§6](GATE-R0-20261104-design-precision.md)、[VISION](../vision/mission.md)。レコード案は提案であり未実装。
- **見直し条件:** 将来、双方向に学習可能な相手と独立した計測・相互効果の介入が設計された場合のみ、互恵性を別課題として定式化。

### DV10 — 最強の反対意見・STOP線

- **結論:** Museの「Bを背骨、Aをガードレール、Cを提示順序」は**現段階では不同意**。最初から質問学習・概念body・Sleep圧縮・転移を揃えると、陽性の原因を同定できず、#139の失敗を繰り返す。Dの欠点は人為的に狭いH0でもMが成立してしまう点であるため、**H0の完全開示とSTATIC-H+等の強対照を義務化**し、Mから一般知能・実用Uを推論しない。
- **根拠:** #166は強い固定比較で利得ZERO、#139では学習bodyとmacroが区別不能、[精密ドシエ§2](GATE-R0-20261104-design-precision.md)は理想STATIC-H+を超えることが一般に不可能と明記。縦切り成功でも、target bodyの人手注入、テスト漏洩、任意表現力H+への変更、既存macro同値、body未実行、rankだけによる改善なら概念M/Uの証拠にならない。
- **「方法論で停止」の反証:** R0-Tは**単一方法文書、有限N/S/R/E表、エピソード一件、比較条件表**が上限。新しい図・測定器・世界の案を増やすことをR0達成条件へ加えない。これでもH0閉包の有限証明ができなければ実装して解決するのでなくREDESIGN/STOP。
- **STOP基準:** (1) 公開情報から候補を識別できる妥当な世界を固定できない、(2) 有利なように制限したH0しか用意できず、同容量対照で機構Mを識別できない、(3) source漏洩・独立性違反を防げない、(4) モデルが実効的に既存macro再発見しかしないのに研究目的が「意味的新規性」を要求し続ける、(5) 反復しても正味UがNULLかつOwnerがMの機構研究自体を優先しない、のいずれかでは研究仮説/系列のSTOPを明示的に議論する。**STOPはDekaSugi全構想の否定ではなく、その定義された科学的主張の停止**を基本とする。
- **見直し条件:** Museが「全機能同時でも識別可能な介入設計」または「Dでは達成しえないMの必要十分条件」を具体的な紙上反例で示し、Ownerが採用する場合、主ルートを再審議する。

## 11. Ownerが最終的に決定する事項（Leadの提案であり既決ではない）

1. **主ルート D**（Bの同時全部入りを退けるか）。
2. 初段の主張を **M機構実証**に限定し、**U正味便益**を別の後段ゲートへ分離するか。
3. 2bit XOR/ORと限定H0/H+を最初の**工学診断**として採り、科学的独立family転移とは呼ばないか。
4. 非学習の固定クエリを許し、学習型Active Learning・高度Sleep・NNを初段から除外するか。
5. R0-Pの単一方法文書とR0-Tの紙上エピソード・査読後に限り、R1-ENGの**限定コード**を別途承認するか（本回答自体はNO GO）。
6. 長期VISIONに対話の互恵性を残し、現在の成功条件から除外するか。
7. mainの安全・証拠契約を選択的再利用し、DraftのHOLDと#166のSTOPを保全するか。
8. Museの指摘P0/P1に対する最終裁定、およびR0-E GO/REDESIGN/STOPのOwner最終判断。

## 12. Museへの査読依頼（回答は合意ではない）

特に **Dに対する最強の反例、限定H0の公正性、Mと意味的新規性の境界、どの段階からSleepを「学習」扱いできるか、R1の実装許可境界** を独立に精査していただきたい。採否は `同意 / 条件付き / 不同意 / 判断不能` と、反例・代替案・見直し条件を明示してほしい。**無回答を合意に換算しない。**

## 出典（既存資料と設計推論を区別）

- [Q-20261104-03 質問票](Q-20261104-03-development-direction.md) / [Muse精査 R-20261104-02](R-20261104-02-muse-review.md) / [GATE-R0精密ドシエ](GATE-R0-20261104-design-precision.md)
- [GATE-R0 #168](https://github.com/ryonakayama234/DekaSugi/issues/168) / [REPO-GOV #146](https://github.com/ryonakayama234/DekaSugi/issues/146)
- [EXP-ACTIVE-002 G0B STOP #166](https://github.com/ryonakayama234/DekaSugi/issues/166) / [EXP-REP-005 #142](https://github.com/ryonakayama234/DekaSugi/issues/142) / [EXP-REP-004R #139](https://github.com/ryonakayama234/DekaSugi/issues/139)
- [README](../../README.md) / [EXP-0002B FINAL112](../../experiments/EXP-0002B/runs/20261025-final112.md) / [AGENTS](../../AGENTS.md)

**未実行／未査読事項:** 上記の紙上トレース、能力順序、予測ログ契約、費用/ablation案、将来のゲートはすべて設計提案であり、数値的な新成果・実装済み動作・Owner決定・Muse合意を含意しない。
