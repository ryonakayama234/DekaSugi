# PART-REFERENCE-1 — 実行結果と Muse 独立確認

id: PART-REFERENCE-1-RUNS
status: evaluated_independent_review_pending
updated: 2026-11-18
tags: synthetic, evidence, review

Owner GO6970376396に基づくlocal-01はCOMPLETE、固定ラインの作者検算はMET。Muse VM独立確認はpending。

| 方式 | 主評価 完全一致/8 | 片側対照 完全一致/8 | 主REFとの差 |
|---|---:|---:|---:|
| REF | 8 | 8 | 0 |
| CHAR | 0 | 8 | +1.0 |
| MASK | 0 | 8 | +1.0 |

REF主8行は全件で左右2参照を実使用。全48行・288候補枠を、学習器をimportしない独立した表と二重ループで照合した。獲得状態、全REF/MASK選択前候補・計数、全方式の候補枠・展開長は全件一致。監査不整合0、選択規則の上限違反0。長さ違反として棄却した候補も全てtraceに残っている。

| 費用 | REF | CHAR | MASK |
|---|---:|---:|---:|
| 学習行 / 走査文字 / 獲得数 | 8 / 40 / 4 | 8 / 40 / 4 | 8 / 40 / 4 |
| 候補枠 / 選択検査枠 | 96 / 96 | 96 / 96 | 96 / 96 |
| 全候補の展開命令数 | 544 | 544 | 544 |
| 選択後の実行命令数 | 112 | 80 | 80 |

各入力traceに学習費用を付記しているが、総費用では学習を方式ごとに一度だけ計上。候補列挙と選択の費用は別カウンタ。CPU命令数や高速化の指標として合算しない。

実行環境はLinux / Python 3.12（完全版はpredictions.json）。[外部プロセス計測](process-cost.json)はPython stdlibのresource.getrusage(RUSAGE_CHILDREN)差分とperf_counterで各CLIの起動から終了までを測った。予測CPU0.087652秒・wall0.091366秒、採点CPU0.092693秒・wall0.094395秒。CLI内部の段別計測と別記し、import・git照合・最終目録保存を含む外部計測を省略しない。最初に試した/usr/bin/timeは環境に存在せず、実験プロセスは起動されなかった。計測方法をstdlibへ変更した。公開commitに揃える前の実行もあり、そのraw記録と実行コードを[prepublication-01.zip](prepublication-01.zip)に保存した。Git pushの書込み認証が得られずGitHub接続でcommitを作成したため、固定commit参照だけを公開SHAへ更新してlocal-01を実行した。判定線・入力・演算・候補順・上限は同一で、全方式の獲得状態・48行の候補/予測traceは公開前記録と全件一致した。追加の時間・総操作・保存byte停止枠は置かず、固定有限処理の費用を報告した。

全6ファイルの成果物は364,069 byte。[全予測](local-01/predictions.json)、[予測固定](local-01/PREDICTIONS-LOCK.json)、[採点・論理費用](local-01/report.json)、[予測段費用](local-01/predict-cost.json)、[採点段費用](local-01/score-cost.json)、[全payloadのraw SHA目録](local-01/COMPLETE.json)を保存した。予測raw SHA256は `0e191abebd85c91e78311cedf538288583dcab20649ba670670d01795c2b9bf5`。正解は予測固定後の別プロセスだけが読む。

固定commitは `5ea88306a957bc85385cacfa2a57cf24eac4b9ea`、実行sourceは `a41054415dfd9af11c5fc0e004317997aba6549b`。固定→実装→実行→証跡記録の順。実行後に追加したのは証跡の改変拒否テスト6件・結果票で、学習器／runner／auditorのコードは実行sourceから不変。専用テスト15/15、文書検査133件、diff検査はPASS。作者による別計算とMuseの独立確認をそれぞれ記録する。

## Muse VM 確認手順

全履歴を含むcloneで作業する。既存local-01は上書きしない。

```sh
python -m unittest tests.test_part_reference -v
python scripts/check_docs.py
python scripts/audit_part_reference.py experiments/PART-REFERENCE-1/runs/local-01
python scripts/run_part_reference.py predict /tmp/part-reference-muse-01
python scripts/run_part_reference.py score /tmp/part-reference-muse-01
python scripts/audit_part_reference.py /tmp/part-reference-muse-01
git diff --check
```

1. 固定commitの4ファイルが現行とbyte一致し、実装より前であることを確認する。保存予測が固定入力のSHAと実行sourceに一致することはauditorでも検査する。
2. 新runのcounts、paired差、logical_cost、verdictをlocal-01のreportと比較する。各方式のchunksとrecordsは全件一致を要求する。実時間、runtime、source commit、予測ファイルSHAは環境や記録headに依存する。
3. 別のコピーで予測・参照依存・候補・費用を改変し、hash照合／独立再計算の拒否を確認する。専用テストはこれらの破損を含む。REF/MASKの選択直前traceと費用が一致し、MASKで文字候補の再選択が起こることも確認する。
4. 各CLIの外部CPU/wallと全成果物byteを別途測る。内部段別costのpayload byteは小票保存前の値、最終総byteはCOMPLETEを含むことに注意する。

観測したのは、設計者が合成型と役割を与えた人工課題で、格納上限5のもとでは獲得参照を使うことで未見組合せが表現・実行できるという結果。文字経路は片側に到達し、上限9なら両側も表現できる。一般的な言語獲得・合成方法の発見・日本語への転移は今回の測定対象に含まれない。モデル採用・E1完了・マージはOwner別判断。
