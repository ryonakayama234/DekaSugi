# WORLD-R-20261110-01 — Research Lead回答：世界経験から操作言語を成長させる

id: WORLD-R-20261110-01
status: research_lead_proposal / pending_muse_review / pending_owner_decision / docs_only / NOT_PREREGISTERED / NOT_RUN
updated: 2026-11-10
author_role: Research Lead (ChatGPT)
question: [WORLD-Q-20261110-01 / Draft PR #190](https://github.com/ryonakayama234/DekaSugi/pull/190)
tracking: [Issue #191](https://github.com/ryonakayama234/DekaSugi/issues/191)
reverse_questions: [WORLD-RQ-20261110-01](WORLD-RQ-20261110-01-muse-questions.md)

> **権限境界**: これは質問への設計回答・仮説・反証条件であり、事前登録稿でも採用稿でもない。実装、データ生成、先行sealed/holdout閲覧、事前登録凍結、学習、実験実行、実PCログ収集、評価、既存認定状態の変更を許可しない。回答へのMuse独立精査とOwnerの採否は未了。

## 0. 前提・証拠・設計原則

### 0.1 Owner決定を固定する

1. R2-M-A（実験A）の**後継**として設計する。AはG6-4まで完了して閉じた記録であり、Aの認定状態を本軸へ持ち越さない。
2. 最初の世界は**小さなテキストエディタ世界**、第1.5世界は**フォーム世界**で固定する。Minecraft、実PC、自由文章生成は初期実験に入れない。
3. 巨大な事前学習済みLLMを初期実験では使用せず、LLMの常識由来の一般化を本軸の成果としない。
4. Aの安全上の工程――source-first、Owner権限、独立監督、明示ON/OFF、真の実測、証拠保全――は**規律**として継承する。既存のスコア・封印・認定は継承しない。

### 0.2 確認した既存成果と限界

- [README](../../README.md) と [docs/INDEX.md](../INDEX.md) は歴史的な段階注記を積層しているため、「最上部にある古い日付」や旧来の NOT_RUN を現在の研究状態と読み違えない。
- [Issue #146、G6-4報告](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6754631517): 実験Aは448/448件の本番receiptが存在し、arm間のwall中央値0.0874〜0.0877秒で方法間の費用優位は観測されず、固定費が支配。準備費が分離できず C_life はUNMEASURED。測定は単回で誤差未評価。M_use NOT_CERTIFIED、M_gap UNKNOWN、N_rep/U/T NOT_EVALUATED、closure UNKNOWNを維持。これをWORLDの実験成績へ転用しない。
- [Issue #166](https://github.com/ryonakayama234/DekaSugi/issues/166) は別の有限文法で公開側の適応的質問価値が厳密に0だったSTOP例。**世界を用意しただけでは情報獲得の利得は生まれない。**
- [Issue #142](https://github.com/ryonakayama234/DekaSugi/issues/142) は既存の固定マクロと学習済みbodyを比較する際の表現力・情報・費用の不均衡を警告する。本軸にも能力を備えた固定体系対照が必須。
- [PR #190](https://github.com/ryonakayama234/DekaSugi/pull/190) の質問票は本回答時点でDraftであり、mainにあるものとして扱わない。

### 0.3 主張を3層に切断する（最重要）

- **L-Skill / ライブラリ圧縮**: 原子操作をまとまりにし、記述長や探索効率が変わる。同じ基本計算で表現できることを認める。
- **L-Concept / 状態・関係の発見**: 未命名の特徴、前提条件、遷移関係、相違点を経験から構成し、予測と選択を改善する。
- **L-Schema / 操作言語の実用上の拡張**: 新規述語と新規下位行動を引数に持つ条件付き計画など、別の組み合わせへ再学習なしで再利用できる構造を経験から形成する。

「L-Schemaが成立した」ことと「原始言語の数学的な表現力の上限を越えた」ことは異なる。後者を主張するには、比較対象のH0が有限な課題分布で目的挙動を表現できないこととH+ではできることの証人が必要。無制限の汎用計算機や巨大な状態表までH0に許せば、一般には厳密な表現力差を主張できない。

**不可避の帰納バイアス**: システムが全く与えられていない演算意味論を無から作り出すことは証明できない。何らかの変数結合・組立て・比較・実行のメタ機構は実装者が設計する。成果と呼ぶのは、個々の述語・行為の選択、分節化、スキーマの形成と有効化が、与えた意味ラベルや手製の正解対応表ではなく経験に由来すること。

## 1. QW1 主張と認定

**結論**: 認定は段階制とする。まず新しい実行可能表現の生成（生成履歴と依存元）、次に介入による有効性（USEでON/OFFすると合法な決定が変化）、最後に強い対照を越えた未知世界での経験効率を別々に示す。全段階を通って初めて「再利用可能な操作言語成長の証拠」と呼ぶ。

**根拠**:
- DreamCoderは既にプログラムライブラリと探索方針を共同学習するため、**発明一般の初出を主張しない**。本軸の識別焦点は「世界の観測・介入→現モデルの不足診断→述語/条件方策の修復→移転先での合法使用」という因果経路。
- 必要証拠は (i) 訓練経験から構築されたtype付き新記号の署名・body・適用域、(ii) 現実の同一USE時点でのON/OFF差と代替経路の監査、(iii) 比較対象と同じ公開情報・原始操作予算・提案grammar能力・学習経験、(iv) 未見の組合せ/世界での改善。
- 旧知識への新たな**名前付け**、固定マクロの照合、モデルの重み更新のみ、事前用意の汎用Ifの単純呼出、正解を直接受け取るAdapterを認定から除外。

**見直し条件**: 健全な固定H+・同容量の記憶/検索・rank-only方策に劣る/同等、追加表現をOFFにしてもUSE不変、または数値改善がtrain familyの暗記で説明できたとき、主張は対応する下位層へ降格する。

## 2. QW2 世界v0仕様

**結論**: v0は**完全に観測可能な編集状態**と**未知の課題規則・操作の使い方**を区別した、CPU上で有限列挙できる決定的な環境とする。設計候補は以下（**未確定、要事前の工学的到達性検証**）。

| 軸 | v0候補 | 理由・取り扱い |
|---|---|---|
| 文字 | 4記号 A/B/C/D（感度分析で6記号） | 同じ文字の反復と位置依存を持ち、表層改名を可能にする |
| 初期buffer | 長さ4〜12、buffer上限は暫定16 | 深すぎる軌跡を避ける。長さ拡張は上限を別途設定 |
| 状態 | buffer、cursor、selection（anchor/headまたはnone）、clipboard | 状態遷移は厳密。選択範囲の半開区間を明示 |
| 原子行動 | MOVE_LEFT/RIGHT、INSERT(symbol)、DELETE_BACK/RIGHT、SET_ANCHOR、EXTEND_LEFT/RIGHT、COPY、PASTE、CLEAR_SELECTION | 一回のキー/選択に相当する小粒度。SEARCH/REPLACEや意味名付きマクロなし |
| 関数境界 | reset、observe、legal_actions、step | 汎用Interfaceだが、状態ラベルから意味カテゴリへの対応表は渡さない |
| 合法性 | cursor端、selection空、clipboard空、容量超過等の動作は仕様に固定 | 非合法は失敗かno-opかを設計時に一意化 |
| 評価 | 独立決定的verifier。学習者には評価用の真のtarget bufferや将来の正解列を渡さない | 一発でtargetを読んで再入力する抜け道を抑える |

- 小ささの境界は状態数ではなく、**(A) 解ける課題が複数ある、(B) 特定の変換の区別が必要、(C) 予測不能を情報獲得で解消できる、(D) 違う表面形でも同じ構造を再利用できる**ことを、設計側のみで形式確認できるかで定める。
- bufferとcursorのみの下位条件を保持し、selection/clipboardを追加する条件と分ければ「複写」が繰り返しINSERTと同一になる問題を診断できる。これは別世界への変更ではなくエディタ世界内のアブレーション。
- 動作の意味（挿入/削除）を世界側が実装すること自体は許容。ただし学習側の技能カタログには「こうすれば複写できる」といった抽象解法を先渡ししない。
- **重要**: 完全観測可能な状態に対して有限の反応方策を無制限に許せばどの行動分岐も表現できる。Ifの発明は「無制限な方策クラスに対する不可能性」とは主張しない。

**見直し条件**: 全課題が機械的な一括消去→target再入力で済む、選択/clipboardなしでは構造差が起きない、buffer超過で大半の実行が無効になる、または全件総当たりの強いH+が飽和するなら、仕様は凍結前に再検討する。

## 3. QW3 課題族と無条件方策の天井

**結論**: 4族――転写、反復コピー、観測依存編集、2段連結――を持つ。条件分岐の最小証人は「共通の公開課題タグを持つ2初期状態で、正解到達に必要な行動が互いに異なる」という**対称な対照ペア**で構成する。ただし固定行動列での不可能性を証明しても、状態依存のLOOKUPが不可能とは言えないので、強い条件付き表・静的スキーマを別の対照へ加える。

**根拠**:
- 生成側だけが知る課題テンプレート例: RULE(ROLE_1, RELATION_π, ACTION_x, ACTION_y, TARGET_ROLE)。表示は意味ラベルでなく匿名なtask ID/初期観測/許可行動と公開TRAINでの試行結果に限定する。
- 全合法な行動列を予算H以内で列挙し、二つの対照状態を**同じ開ループ列ではともに成功できない**ことを検査する。表面的な初期違いだけでなく、双方に合法な別々の到達系列が存在することも検証。
- testは (1) 未見文字名、(2) 未見長さ、(3) 未見の「述語×分岐先操作×対象」組合せ、(4) フォーム世界の変換を**役割・生成法則単位**で封印する。三項組合せだけを隠して片方の近傍を大量に見せるsplitは、構造的一般化の強い証明にはならない。
- **Goal leakageの予防**: USEで最終targetをそのまま公開したら、学習者は単純にbufferを消してtargetを再入力でき、Ifは不要になる。公開するのは共通課題識別子と合法な観測・行動であり、真の目標buffer/ルールと採点は独立verifierに留める。TRAIN時の公開フィードバックは予算に課金する。

**見直し条件**: open-loop共通成功列を発見、targetリーク、適用述語を表層で特定できる、または静的H+が全例正解するなら当該試験の識別可能性がない（UNDERIDENTIFIED/STOP）。後から陽性になる課題だけ選別しない。

## 4. QW4 経験収集、自己生成、ログ

**結論**: はじめは自己生成なしの公開事前配分条件を基準とし、(R) ランダム合法探索、(A) 版空間に基づく能動探索、(S) 意味を教えない合法操作カバレッジ台本を別arm比較する。自己課題生成は識別可能性が示された後の追加条件であり、最初から主要能力の証明に使わない。

**根拠**:
- EIG候補: 公開の仮説集合V_t、合法行動a、観測結果oとすると、EIG(a)=H(V_t)-Σ_o P(o|a)H(V_t|o,a)。一様仮説分布は方法仮定で、未知真値を先取りしたoracle値を学習器へ注入しない。有限Vで計算可能でも真の遷移法則がV外なら空集合を返すため、EMPTY_VERSION_SPACEという明示的な表現修復候補を生成する。
- 問題生成側はEIGだけでなく「学習者が実際に到達できる」「未見答案を参照しない」「新しく学んだ表現の同一内循環ではない」「公開インターフェース上で有効に観測できる」条件を満たす必要がある。実際の評価は新しい独立法則でのみ認定。
- ログv0最小契約: episode_id、task_family_id（匿名）、source_manifest_digest、train/sandbox/eval境界、agent_snapshot_digest、step_index、observation_before、legal_action_set_digest、chosen_atomic_action、observation_after、delta、outcome_kind（SUCCESS/FAIL/INVALID/ABSTAIN/STOP）、cost（paid_probe、primitive_calls、wall/CPU separately）、symbol_proposal_event、policy_decision_reason、receipt_digest。観測用ログに正解Oracle内部状態やhidden ruleを含めない。
- エピソードの相関を無視せず、独立単位は「生成規則/意味family」。同じ世界の連続行動100回を独立n=100として扱わない。

**見直し条件**: 情報利得が0、合法行動による仮説の分離不能、自己生成が訓練側の予測を過学習させる、または受動/能動比較で同じ公開情報・経験上限を保証できない場合は方式を変える。

## 5. QW5 分節化、引数抽出、技能昇格

**結論**: 決定的な世界の遷移から、まず意味ラベルを使わず**効果signature**を抽出し、次に可変長の軌跡を圧縮して共通部分を検出し、変化する対象位置・文字・境界を**anti-unification（一般化単一化）**で束縛変数として抽出する。候補は型付き述語/技能/スキーマとして版を分ける。

**根拠**:
1. prefix/suffix・cursor・selection・clipboardの変化を編集前後の差分として記録。原子的な「何が起きたか」を学習側が直接正解タグで受け取らない。
2. 予測成功区間、失敗区間、繰返し境界、相異なる軌跡の整列を候補分節として保持。唯一の分節へ早く固定しない。
3. 複数の軌跡を対応づけ「同じ位置/値」ではなく「カーソル直後」「現在の選択領域」「保存済みの値」のような関係変数候補を構成。ラベルは内部OP_n/P_n等の無意味ID。
4. 構成物は type、precondition、postcondition候補、依存操作、適用反例、失敗域、形成時の公開証拠digest、定義コスト、再利用回数を持つ。新たな反例で前提を狭める/分割する/廃止する。
5. 単一加重和で費用単位を混ぜない。**昇格のANDゲート**: 有限holdout前逐次予測/実証例で損失改善または維持、総MDL（library header + body + data residual）が改善、独立課題族への利用証拠、必要な原始呼出予算を超過しない。費用ベクトルは付帯し、量を変換する重みは事前指定できる場合に限る。強い対照が同様の性能を出す場合、概念成長を認定しない。
6. 圧縮率だけで高度な技能と呼ばない。実験Aでは固定費支配と観測されたため、wallを主エンドポイントにしない。

**見直し条件**: 使用されない技能の量産、train専用MDL改善、偽の役割同定、負例が矛盾したままの昇格、あるいは新技能で探索分岐数が増えて未知課題が悪化した場合は候補削除/保留を検討。

## 6. QW6 二階Ifスキーマ

**結論**: 試験で狙う構造は抽象的に SELECT_BRANCH(Predicate p, Policy then, Policy else) と表せるが、**この名前・完成済み実行器を学習者に渡してはならない**。学習者は複数の相反する履歴から役割を抽出し、未見のp/then/elseへ再束縛できる構造を保存する。実行機が受け取る内部命令は、構成された条件分岐グラフを評価できる最小のメタ機構とする。

**根拠**:
- 第一階:「Aが在る→DELETE、ない→INSERT」の固定規則だけを獲得。第二階: Bを含むか、clipboardが空か等の異なる候補述語を、COPY/PASTE/MOVE等の新しい行動ペアへ**再学習なし**で束縛して同様の分岐を使える。
- 評価は (p_i,a_i,b_i,target_i) に対し、p_j,a_k,b_l,target_mの各成分を分離封印した**組合せ直積holdout**。新規パラメータの推定に要した使用時の公開観測は課金する。初見フォームadapterでも部分的に相当する関係を発見できるか試す。
- 同条件の**固定高階IF（同じ実行機能と候補集合）**、固定条件付きlookup、学習した一階規則の検索、発見スキーマだけOFFを必ず含める。H0は同一の実行可能メタ言語を許す対照とし、目的は「自己発見の経験効率」とする。厳密な表現力拡大が欲しければ別の有限H0/H+証人として二次主張にする。
- 発見は単に任意のニューラルスコアで次行動を選べることではない。**可視化可能な再束縛・独立した再実行・role swapでの安定性**を必要とする。

**見直し条件**: 個別lookupや固定IFによる同予算対照に勝てない、見せていない部分に人間の役割対応表が入っている、または違う述語で作用が破綻するなら、二階If認定を取り下げる。

## 7. QW7 表現不足の点火

**結論**: 予測誤差の頭打ちだけで新記号を作らない。4つの診断を順番に行う: (D0) 情報不足、(D1) 有効探索予算不足、(D2) 現行H0で表現可能だが学習不足、(D3) H0表現限界を示す公的反例。D3に近いときのみ表現修復を優先する。

**根拠**:
- 公開観測と反例から現行version space V_tを更新し、V_tが空になる・既知の行動列では同時に説明できない・必要な記述長が反例ごとに発散する、といった複合サインを収集する。V_t空は**仮説族相対の失敗**であり、真の世界で一切の説明が不可能という証明ではない。
- 短期保持を延長すれば解ける場合はD0/D1、代替候補の再探索で説明可能な場合はD2とする。候補修復で予測が改善しなければ戻す。
- 偽陽性制御: 既存のH0で完全説明可能な**陰性世界**、ランダム雑音、無関係な文字改名、適用域外の観測を、事前に分けて保留。修復に対するパラメータ費用/最小反例数/改善持続性を要求する。

**見直し条件**: 充足H0下でも高頻度の誤点火、ノイズに追随する記号乱造、必要なときに発火しない、公開version spaceには真の法則が含まれないため推定利得が系統的に0と誤る場合。

## 8. QW8 転移、経験効率、ゲート、キル条件

**結論**: 独立した3ゲートを提案する。以下は**数値閾値案であり未凍結**。G1:文字改名、G2:長さ外挿、G3:フォーム世界。各ゲートには**絶対達成率**と**強い対照に対する差**と**修復ON/OFFの実使用差**を併置する。

| ゲート | 暫定閾値案（別の校正ラウンドが必要） | 対照と重要な留保 |
|---|---|---|
| G1 rename | targetで再学習0、成功率90%以上、最強の固定同予算対照に+10 percentage points以上 | near-ceilingなら識別不能としてSTOPし、後付けで難問だけ抽出しない |
| G2 length | TRAIN最大長より長い独立組成で成功率80%以上、最強対照に+10pp以上 | 文字数・行動ホライズンの増加を両arm等しく計上する |
| G3 form | 入力欄とポップアップの新法則族に成功率70%以上、一定の公開学習行動予算内で学習曲線面積（AULC）が最強対照+0.15以上（0〜1正規化） | 「0-shot transfer」と「許容n回のtarget適応」は分けて表示する。生成器が同じなら強い転移とは呼ばない |

- 改名/長さは**ターゲット再学習0**で原則評価。フォームでは0-shotと数回の公開適応を分ける。性能は family-level paired difference と最悪サブグループ（文字頻度、長さ、role swap、誤条件）で見る。family間の独立性を前提にした区間推定を行う場合は、その生成階層を事前に明示。行動ステップを独立family数へ水増ししない。
- AULC(B) = [Σ_(n=0)^B success(n)]/(B+1)。問題に「解けるまでの回数」が無限になるケースはBで打切り、成功/棄権/INVALIDを必ず分母に残す。学習のための初期経験も正しく計上する。
- 提案閾値に統計的な保証はまだない。事前の非採点の到達可能性診断・想定独立family数・必要検出力・期待する対照成功域をMuseと協議し、**独立したOwner凍結許可が出る場合のみ**確定する。
- **キル条件**: (K0) 全ての正例familyが固定H+やベスト合法open-loopで解ける→機会なし、(K1) 学習ON/OFFで合法行動・使用差なし、(K2) 表現修復の有無を統制すると差消失、(K3) 最強対照との差が負または実質0、(K4) 成績差は形式上のtarget漏洩/比較予算差、(K5) 未見フォームでrole correspondenceがすべて手製Adapterに埋込済み。K0は実験前STOP、K1〜K5は各認定を不成立とする。特定の世界の不成立は一般的な「自律概念学習は不可能」の証明ではない。

**見直し条件**: 校正でこの絶対値が容易すぎる/不可能すぎる、強い固定対照の天井が高い、独立familyが不足する場合。**データ確認後に閾値を上げ下げして同じFINALを再採点しない**。

## 9. QW9 共通項の自力発見

**結論**: 先に「選択→変更→確定」というラベルを教えない。学習側は多様な行動軌跡から、編集対象や文字の同一性ではなく**状態・行動・結果の関係保存**を示す抽象グラフ候補を生成する。正当性は未見の役割交換とその場の予測・計画改善で評価する。

**根拠**:
- 新しい記号は、表面名称を一様に改名しても役割関係が維持されること、入力欄/文字位置の異なる適用先に再束縛できること、予測的に等価でない関係を誤って同一視しないことを確認する。
- 同じ遷移グラフを持つ2世界でも観測が同じとは限らない。抽象状態h、具体の遷移T、抽象遷移T'に対し h(T(s,a))=T'(h(s),h_a(a)) が可能な範囲で成り立つような**行為保存写像**を、学習後の解析側が検証する。これは開発者が最初からhを与える意味ではない。
- 最低限の対照:文字名だけ変えた偽転移、時系列をシャッフルした共起、課題IDだけから行動を記憶する検索、分布内頻出列、関係のみを壊したcounterfactual negative。
- 「共通インターフェースを与えた」ことと「抽象を発見した」ことは別に報告する。

**見直し条件**: 改名で崩壊、順序破壊でも同じ性能、下位行動の効果が異なる世界まで無差別に同一視、学習した抽象が別familyの合法行動選択に寄与しない場合。

## 10. QW10 多様性と連結課題

**結論**: 経験の**総行動回数・有料問い合わせ数・成功フィードバック数・真の法則露出数**を等しくし、反復優位・中間・多様性優位の3配分を比較する。連結は別の交互作用評価とし、成功済み技能を単純につなぐだけの条件と、前段の結果で後段初期状態が分布ずれする条件を区別する。

**根拠**:
- 例: 暫定配分（反復:変種）80:20、50:50、20:80。ただしこれらは**同一予算の配分率案**であって実験回数指定でも凍結値でもない。
- 課題レベルの多様性（文字、長さ）、構造レベルの多様性（述語、依存、分岐）、世界レベルの多様性（フォームのレイアウト・ポップアップ遷移）を別々の軸として要因化し、訓練暴露の分布を定量記録する。
- 2段連結では前段を単体で成功と見せてから、後段初期状態の分布が変わる場合の前提条件推定、failure recovery、再計画の可否を確認する。最初から後段の正解を知るlookahead oracleは比較対象でも評価側のみ。
- 多様な変種の効用を示す他分野の大型研究は存在するが、LLMを訓練したスケーリング結果をこの有限記号世界の陽性根拠にはしない。

**見直し条件**: 多様なarmだけ正解情報量や環境時間を多く得る、探索上限が不公平、連結課題の失敗が外部Adapterの型エラーに集中、または想定した新規組合せが出現しないとき。

## 11. QW11 実PC操作ログと後段世界

**結論**: v0の発見器を将来の実PC操作へ接続するため、**観測・行動・変化・根拠**の共通データ契約を維持し、視覚/アクセシビリティ由来の操作対象の発見は**別の未確立能力**として切り出す。第1.5フォーム世界が成功してもPC操作能力は認定しない。

**根拠**:
- 想定される将来のAdapter: (screen/UIA/DOM observation) → 局所object候補・位置/属性・時系列変化 → 匿名role/関係候補 → 汎用計画/構成技能 → (click/type/select) → 事後観測。
- editorから転用可能: 実行可能な前提条件、行動前後の予測誤差、選択範囲/値の依存、失敗からの述語修復、再利用可能な条件付き下位方策、エピソードの証拠分離。
- 転用が保証されない: OCR/画像認識、focusの罠、ウィンドウ重なり、非同期イベント、通信遅延、未観測状態、マルチユーザー権限、取り消せない操作、意図の曖昧な自然言語、セキュリティ境界。実PCでの情報収集・実行は別のOwner許可とプライバシー/権限契約を必要とする。
- 後段の序列: Editor v0 → Form v1.5（別表示/同類操作+ポップアップ） → sandboxed実アプリ（最小GUI、外部副作用なし） → 複数アプリ/文書 → Minecraftなどの長期部分観測世界。これは将来位置づけのみ。

**見直し条件**: フォーム世界への成功が人間の固定写像の結果、実PCへの適用が画面認識の成功だけ、または検証器が目的達成の代わりに単なる入力イベント数を採点している場合は、転移主張を撤回する。

## 12. PW1〜PW7への明示回答

| PW | 判定 | 理由・修正点 |
|---|---|---|
| PW1 | **同意** | OP_17等の内部名を推奨。ただし「名前を隠すだけで自力発見」ではない。役割・意味の先渡し禁止を追加 |
| PW2 | **修正** | MDL、予測損失、実行コストの次元を保存。異種単位の恣意的加重和で技能を昇格させず、独立ANDゲート＋実行費用ベクトル |
| PW3 | **同意** | 主評価は構造転移と累積経験効率。成功率/棄権/INVALID/CPU/RSS等も副次・安全基準として併記 |
| PW4 | **同意** | 再束縛できる二階スキーマを未見直積で検証。予め与えたIf runtimeと経験から得たスキーマを分ける |
| PW5 | **修正** | EIGは候補選択のproxy。合法性・到達可能性・公開情報での有効性・行動費用を必要条件とし、外部holdoutで最終判定 |
| PW6 | **同意** | 学習側へ共通カテゴリを教えない。一方、実装側の型、Interface、演算意味論の初期バイアスは正直に監査 |
| PW7 | **同意** | 多様性を分布設計変数として要因化。大型LLM研究のスケーリング則をこの小型世界へ無検証で外挿しない |

## 13. 統合アーキテクチャ候補（設計のみ）

~~~mermaid
flowchart TD
    ENV["Editor World / Form World"] --> OBS["Adapter: observe, legal_actions, step"]
    OBS --> HIST["Public-only Episode / Evidence ledger"]
    HIST --> WM["World Model: typed transition hypotheses"]
    WM --> DIAG["Representation Gap Diagnoser: D0-D3"]
    DIAG --> EXP["Active Explorer: finite EIG & lawful interventions"]
    EXP --> OBS
    DIAG --> PROP["Predicate / Skill / Schema Proposer"]
    HIST --> PROP
    PROP --> CHECK["Semantic Validator: counterexamples, types, MDL"]
    CHECK --> SNAP["Versioned Library Snapshot"]
    SNAP --> POLICY["Kernel: grounded plan and action selection"]
    POLICY --> OBS
    OBS -.-> EVAL["Independent Verifier / heldout store"]
    SNAP -.-> ABL["Fair OFF and static-Hplus controls"]
    ABL -.-> EVAL
    EVAL --> AUDIT["Independent evidence and decision gates"]
~~~

責務の厳密な境界:
- **環境**は真の遷移を保持するが、学習器へ公開するのは合法なインタラクション出力のみ。実世界の内部状態/真の課題式/評価答えへの参照を不可とする。
- **Kernel**はその時点で実行可能な合法行為しか選べない。自分の失敗から新記号を生成する責務はLearner側に置く。
- **World Model**は有限な仮説族の暫定予測器。分布外の未知性・V_tが空の場合の失敗を隠さない。
- **Proposer**は観測データから型付き構造を構築する。実装者が完成人間命名の「条件分岐技能」をseedしない。一方でメタ機構の存在を実験資源として計上する。
- **Library**は候補/検証/保留/失効の状態を区別し、Snapshot保存と戻しを可能にする。推論時に手製のtarget対応表を付けない。
- **Evaluator**は課題生成レシピ、正解、評価family splitを分離し、失敗/停止/欠測も記録する。実験Aから一切の認定を移植しない。

### 制御・学習のロジック（手順案、実装ではない）

~~~text
observe public episode
  -> update version-space / transition predictions
  -> diagnose: unknown data? insufficient exploration? H0 fit? H0 counterexample?
  -> if diagnostic repair opportunity:
       propose anonymous relation/typed body/variable binding
       verify on permitted training-only counterexamples
       score MDL and prequential prediction and primitive budget separately
       store candidate with lineage, never mark certified yet
  -> construct policy using available candidate and public observation
  -> save every action choice, primitive expansion, error, cost and provenance
  -> new independent family: compare matched fixed-Hplus/episodic/rank-only/ON/OFF
  -> independent evaluator makes tiered decision, Owner makes adoption decision
~~~

## 14. 強い対照と因果帰属（本軸の設計中心）

| 条件 | 何を切り分けるか |
|---|---|
| C0 Open-loop fixed sequence | 分岐が必要であることの弱い証人に限定 |
| C1 Fixed H+ exhaustive or capacity-matched search | 既知の総当たり・固定grammarの能力上限、同じ情報と実行器 |
| C2 Episodic exact lookup / nearest-neighbor | 記憶・近傍再利用だけで説明できないか |
| C3 Learned rank-only over fixed grammar | 探索の優先順位学習だけで説明できないか |
| C4 Library macro without predicate/schema repair | DreamCoder型の圧縮との切り分け |
| C5 Full proposed learner vs identical learner with acquired symbol/schema USE disabled | 獲得した道具の実利用効果 |
| C6 Fixed higher-order IF with the same meta-runtime | 「ifがそもそも実行できる」ことの人間由来の恩恵を切り分ける |
| C7 Evaluator-only ORACLE | 達成可能性/機会診断用。学習側には渡さず科学主張のarmとはしない |

**公正な比較**: 全armで同一の合法な public experience、primitive budget、問い合わせ課金、保存/復元上限、学習終了時点とholdout、world adapter、停止条件を明示する。追加のH+構築/学習費、rootメタ文法、catalog構築費、CPU/wall/RSSは個別記帳。単にC0に勝っても認定しない。表現力を固定H+に揃えたときの**獲得効率差**と、H0/H+差を証明したときの**相対的な表現能力差**を混同しない。

### 特に排除したい「見かけの成功」

1. TARGET自体を読む、世界のhidden ruleをAdapterが名付ける、生成器のseedやtruthを漏らす。
2. 文字の改名だけの効果を「別世界へ転移」と主張。
3. 一階の個別ルールを一度選び直すだけで二階スキーマを「発明」したと主張。
4. 人間が完成させた万能分岐構造を使用しただけなのに新しい文法を獲得したと主張。
5. 原始展開後の操作回数・探索候補・準備費を無視し、保存bodyの一回の呼出を無償扱い。
6. 教師ありのデモから教えられたカテゴリを「自力で共通項を発見」と主張。
7. 対照間の表現力・観測費・予算の非対称な制約と、最も弱い対照だけを報告。

## 15. 段階的研究ゲート案（計画、未許可）

- **D0 / Design**: 世界の到達性、無条件方策の天井、機会ゼロの排除条件、H0/H+署名、強い対照表、goal漏洩脅威モデル、family分割ルールを紙上で定義。本回答はここ。
- **D1 / Independent methods review**: Museが設計上の帰属、役割写像の先渡し、費用、閾値、独立family数、ソース分離について精査。Ownerが採用範囲を決めるまで次へ行かない。
- **D2 / Future engineering authorization only if separately approved**: 認可された場合のみ世界・logger・validatorの人工fixture工学検証。実験ではない。証拠の読み書き・停止仕様を整える。
- **D3 / Future preregistration**: source/封印/統計/閾値/ゲートを別手続きで凍結。D2の人工fixture値を真の性能と呼ばない。
- **D4 / Future authorized evaluation**: このラウンドでは禁止。少なくともG1〜G3の独立評価とNULL/NEGATIVEの保存、第三者監査、Owner判定が必要。

**最小の次のアクション**: Museは[逆質問票](WORLD-RQ-20261110-01-muse-questions.md)を含めて、(a)無限のH0と有限H0の主張境界、(b)goal漏洩を防ぐタスク表示、(c)高階Ifの構成機構、(d)強い対照の同予算、(e)独立family/数値閾値の未凍結、を重点精査し、賛否と修正案を記録する。**協議完了や採用決定は本書では主張しない。**

## 16. 原典・照合状況

### 原典照合済み（外部研究、DekaSugiの実証と混同しない）

1. Ellis et al., *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning*, PLDI 2021, https://doi.org/10.1145/3453483.3454080 — ライブラリと探索方針の共同学習。**我々の新規性主張の上限を規定**。
2. Hocquette, Dumancic, Cropper, *Learning Logic Programs by Discovering Higher-Order Abstractions*, IJCAI 2024, https://www.ijcai.org/proceedings/2024/379 — 高階抽象の発見と別領域転移。**Ifや転移一般を初出と呼ばない**。圧縮単独では転移効用の十分な指標でない。
3. Ferns, Panangaden, Precup, *Metrics for Finite Markov Decision Processes*, UAI 2004, https://mlanthology.org/uai/2004/ferns2004uai-metrics/ — bisimulationによる状態関係を理解する基礎。Editor→Formの自動写像を証明するものではない。
4. Rissanen, *Stochastic Complexity*, JRSSB 1987, https://doi.org/10.1111/j.2517-6161.1987.tb01694.x — MDLによるモデル選択と予測。新記号の因果効用を保証するものではない。
5. Tu et al., *ScaleEnv*, ICML 2026, https://proceedings.mlr.press/v306/tu26a.html — 異なる環境の多様性と学習成果の関係。ただし事前学習モデルのツール使用への研究で、DekaSugiの小さな記号学習器への直接証明ではない。
6. He et al., *How Data Scales in Agentic Reinforcement Learning: Laws and Synthesis Strategies*, arXiv 2610.23946 (2026), https://arxiv.org/abs/2610.23946 — タスク・環境・軌跡の多様性を分割する近年の研究。有限世界への縮小再現ではなく**実験軸の着想**として参照。

### 未照合・根拠から除外

質問票に現れる固有名の **HALO / FLEX** と、注記の **PARL / ShowUI-Aloha** は、特定の原典と論点の同一性がこの回答時点で十分確認できていない。固有名を根拠として性能や因果関係を断定しない。先述の一次論文は別途独立して確認した出典である。

## 17. Research Lead の暫定結論

**推奨する研究上の一点集中は「反例から観測述語を構成し、その述語を再束縛可能な条件付き行為スキーマへ高め、同じ資源を持つ固定If/記憶/探索と未知フォームで比較する」こと。** 技能を多く集めることよりも、どの状況で新しい区別が必要かを見抜く機能が重要である。一方、最も強い固定H+に勝てなければ、自己拡張による付加価値はまだ示されない。そのNULLを恣意的に再定義しない。

本書は**Research Lead 提案**であり、Muse精査・Owner採用前である。