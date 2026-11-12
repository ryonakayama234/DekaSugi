---
id: WORLD-CAL-OPTIMIZATION-20261112-01
status: proposed / implementation-candidate / NOT_MET_STOP_FOR_OWNER
updated: 2026-11-12
tags: [world, cal, performance, synthetic, audit, stop-unknown]
---

# 意味論不変の高速化候補 — 5倍未達による停止報告

**結論: 同一ホストの比較で4.486倍。5倍の目安に届かず、このラウンドを停止してOwner判断へ戻す。** 実装候補・一致性証拠・再実測・変更版manifestを提出するが、採用・監督者PASS・新algorithm_digest・CAL_AUTHORIZEDを自己認定しない。

基準は監督者最終PASSのhead `834fe0dc0c33065a1b8039764097141c1d526d98`、旧algorithm_digest `sha256:1c722753379711b49c01df12bcc4be2d910e14cfc549ed65ba9d828c8a8e1e01`（[PR #206 コメント6821592224](https://github.com/ryonakayama234/DekaSugi/pull/206#issuecomment-6821592224)）。旧digestはそのheadだけの履歴として有効。旧55-file manifest自体のbytesも保持した。現在の変更版に旧digestを使わない。

## 変更範囲と不変性

- `_CounterDraws` は反復内のdomain共通prefixを再利用。同stageの連続indexをbatch評価する。episodeの4 normal、checkpointの9 normalと余剰spare、bootstrap全999 drawを旧順序と同じ消費列で生成する。Box–Muller・erfcは既存Python関数のまま。
- optional `prf_batch.c` は同じHMAC-SHA256をlibcryptoで計算する。prefixの後ろに既存 `encode_parts(index)` と同じ17 bytesを追加する。鍵・乱数・scopeは呼出元注入のみ。グローバルな鍵保持・import時のbuild・暗黙の鍵生成なし。
- parent別HT和とpointsは旧Python順序を保持。最後のbootstrap加重和だけCのbinary64逐次加算にする。Python 3.12の補償sumとの差は全中間replicateと最終区間・判定までtol内か検証する。参照 `bootstrap_vectors_cached` を残し、未buildではPython fallback。
- **MC_R=10,000、999 bootstrap、3シナリオ、n昇順/早期停止、α/β/閾値/cost cap、PRF定義、G_θモデル、世界生成器、仕様、プロトコル、ACL、scan/K0/route/receipt制御は変更していない。** 高速化したのは合成スコア計算の同じ演算の実行方法である。

nativeは1 coreの逐次処理。NumPy/BLAS、並列処理、新規Python依存追加なし。明示buildは `cc -shared -fPIC -O2 -fno-fast-math -ffp-contract=off ... -lcrypto -lm`。ソースとbuild scriptはmanifestに含め、実binaryのSHA-256・サイズ・コンパイラ・OpenSSL版は[生証跡](WORLD-CAL-OPTIMIZATION-EVIDENCE-20261112-01.json)に記録。binaryはgitへ追加せず、CI artifactへ格納する。新しい実行物を含むため、このソース閉包だけで将来のCAL launcher認証・OS隔離・binary来歴認証が完了したとは主張しない。

## 一致性の証拠

[再実行runner](../../scripts/audit_world_cal_optimization.py) はgit archiveから旧headの実ファイルを一時展開し、旧版と変更版を別のPython subprocessで実行する。旧実装を新実装で再現した参照ではない。Qは公開multiset `72×1/160 + 264×1/480`、parentは人工 `36×2 + 44×6`、keyは既存固定公開test vector `0b×32`。真正law IDs、sealed割当、CAL seedは使用しない。

| 合成入力 | ケース数 | 比較結果 |
|---|---:|---|
| n=8、全3シナリオ、repetition=0 | 3 | BASEは完結、LOWCORR/HIGHCORRは旧版同様SYG退化でUNKNOWN |
| n=96、全3シナリオ、repetition=0 | 3 | 999 bootstrapまで完結、全中間/最終を比較 |
| n=160、全3シナリオ、repetition=0 | 3 | certainty分離を含め完結、全中間/最終を比較 |
| n=336、全3シナリオ、repetition=0 | 3 | censusのSYG退化で旧版同様UNKNOWN。999完結とは数えない |
| n=96、BASE、repetition=7 | 1 | counterの別反復domainを比較、完結 |

**13/13比較PASS、完結8件・同一UNKNOWN5件。最大絶対差 `6.661338147750939e-16` ≤ `1e-10`。**

- 全使用stage/indexの32-byte digestをnativeで再計算し、旧 `draw_digest` の全bytesと比較。生証跡には全列のSHA-256を記録。一様乱数のhex列・消費順・消費数・終端spare、二値Yのcanonical bytes、sample、bootstrapのparent draw digest、ID/離散出力は一致。n=96 BASE反復0は136,036 uniform消費で一致。
- law別score、9次元vector、SYG、points、999×9 bootstrap値、max-T区間、G1/G2、Contrastとfamily診断、K2、10成分/AND、UNKNOWNの例外型・文言まで比較。最終出力の異なるSHAは許容範囲内のfloat差に由来し、離散値の不一致を許容したものではない。
- これは有限合成入力上の一致性証拠であり、MC_Rを実行してpowerを推定したものではない。各シナリオ/nのpower判定材料は生JSONのfixture別result/componentsに記録。UNKNOWNを成功率へ算入しない。

## 統合1反復の再実測

既存profilerと同条件のn=96 BASE / repetition=0 / 999回 / 9 checkpoints / 4 episodes。毎回新しいsubprocessで、per-repetitionのPPS設計・model/table読込も含む。import/起動/明示compileは既存profiler同様に反復時間の外。warm cacheやcached_designの持越しなし。5組で実行順を交互に変え、中央値を採用した。比較計装・digest再計算・cProfileは時間計測から分離した。

| 指標 | 旧head | 変更版候補 |
|---|---:|---:|
| wall秒 / 中央値 | 0.940197145 | 0.209581704 |
| CPU秒 / 中央値 | 0.940160708 | 0.209564615 |
| exec後RSS high-water / KiB / 中央値 | 18,936 | 23,168 |
| getrusage ru_maxrss / KiB / 中央値 | 47,120 | 47,120 |
| 全n線形外挿 / wall時間 | 4,620.596 h | 1,029.989 h |
| 同ホストwall速度比 | 1 | **4.486倍、5倍未達** |

環境: AMD EPYC 9V74、ホスト可視CPU数9だが**使用1 core・並列化なし**、Linux x86_64 / glibc 2.41、CPython 3.12.14、GCC 14.2.0、OpenSSL 3.5.7。PYTHONHASHSEED=0、OPENBLAS/OMP/MKL threads=1。登録CIのPython 3.12.16とは異なるローカル計測である。pin環境での再現値はCI artifactで分離する。

RSSは `/proc/self/status` のVmHWMと元profilerのru_maxrssを両方保存した。後者はsubprocess起動前に親から継承したhigh-waterを含み得るため、47,120 KiBを反復本体の実使用量と解釈しない。exec後high-waterにはPython/runtime・nativeライブラリも含む。

外挿式は旧profilerと同一の `wall × 3 × 10000 × sum(2..336) / 96 / 3600`。最初の適格nで停止する利得を見込まず、全nのコストがn比例と仮定するだけの値。nごとのPPS/DP・cluster数・退化停止・シナリオ差をモデル化していない。**1,029.989時間を実行予算・実現可能性と認定しない。CPU feasibilityはSTOP_UNKNOWN。**

過去の1.2939秒・約6,358.9時間は別環境の記録として保持する。同ホストの基準が0.9402秒なので、過去の1.2939秒を今回の0.2096秒で割って「6倍達成」とはしない。

## 残る律速と停止

cProfileは計装オーバーヘッドを含むため、以下は速度比の算定には使わない。詳細16関数は生証跡に保存した。

| 変更版の領域 | 計装下の累積秒 | 意味 |
|---|---:|---|
| 1反復全体 | 0.607 | 比較用の計装実行 |
| 合成score全体 | 0.396 | 約65%。スコープ構築、normal/HMAC、PythonでのAR/erfc/Y集計を含む |
| normal_many | 0.214 | score内の内訳。独立因子ごとの小batch呼出が残る |
| grouped_inclusions | 0.078 | exact設計と恒等式検査。省略していない |
| bootstrap parent抽選 | 0.054 | 999件の同じ抽選を保持 |

これらは入れ子であり合計しない。旧版ではPRF domainの再encodeとbootstrap抽選の反復呼出が主な律速だったが、それを削減しても因子別のスコープ処理・Python latent/Y処理・exact設計が残る。**5倍の目安未達を確認した後、新たな高速化を続行せず停止する。** 次はプロトコル改版を検討するか、追加高速化を別範囲で認めるか、候補をどう扱うかをOwnerが判断する。本書はその判断を代行しない。

## 検証・再現・manifest

- native有効: WORLD CAL合成テスト **60/60 PASS**。旧55件（fail-closed19件を含む）と新5件。cap→UNKNOWN・下流遮断を変更していない。full scanは従来どおりmockのみ。
- native未buildのfallbackでも60件を実行し、**58 PASS・native専用2件skip**。既存55件と新fallbackケースを含む。
- [新manifest](WORLD-CAL-ALGORITHM-SOURCE-MANIFEST-20261112-optimization-candidate.json) は63ファイルの変更版閉包。algorithm_digest/split_digest/seedはnull。tracked版の自己SHA循環回避markerを保持し、exact headはCI生成manifestと提出コメントに結合する。旧manifestと旧監査記録は履歴として含める。
- CIはexact headをcheckoutし、明示native build、旧headとの同じ合成比較、60件の合成テスト、既存fail-closed runner、文書検査、byte manifest検査を実行。生JSON・ログ・compiled binary・exact-head manifestをartifactに保存する。CI成功は監督者再監査PASSを意味しない。

```sh
python scripts/build_world_cal_prf_batch.py
PYTHONPATH=. python scripts/audit_world_cal_optimization.py --output world-cal-optimization-evidence.json
python -m unittest discover -s tests -p 'test_world_cal*.py' -v
PYTHONPATH=. python scripts/audit_world_cal_fail_closed.py --output world-cal-fail-closed.json
python scripts/check_docs.py
```

CAL・simulation・K0の本実行、sealed split/seed生成は実施していない。CAL_AUTHORIZED=false。Draftのまま、merge/ready化なし。変更版のalgorithm_digest固定は独立再監査PASS後の監督者判断である。
