# Windows メディア プレーヤーとの実機比較

正本は [cases.json](cases.json)。ユーザー指定のComputer UseでWindows メディア プレーヤーとVLCを同じ環境・同じfixtureで操作し、各Caseを比較する。スクリーンショットの見た目だけで再生操作のUX一致を認定しない。

1. 実在IssueとGUI ownerを決め、共通leaseを取得する。
2. Windows、表示倍率、ウィンドウの寸法、言語、テーマ、参照アプリ版、VLC版を記録する。
3. 個人の音楽/動画ではなく、共有可能な固定fixtureを用意しSHA-256を記録する。
4. 候補のfull source SHAから`.vlt`を生成し、実際にロードした配布物のSHA-256を記録する。dirtyなsourceを既存HEADのbuildと扱わない。
5. 両アプリで同じ初期状態・順序の操作を行い、画面・動作・観察結果をCase別に保存する。私的データを含む画面は公開しない。
6. 差分が残ればfail、操作環境の障害ならblocked、未実施ならpending。passには証拠参照、版、環境、fixture、候補SHA、配布物hash、差分なしが必要。

```powershell
./scripts/python.ps1 scripts/verification.py validate
# 実機比較後の固定候補受入。未実施のCaseが1件でもあれば失敗する。
./scripts/python.ps1 scripts/verification.py accept --candidate FULL_SHA --artifact .harness-local/dist/My-MinimalX-JPMod.vlt
```

schema検査は証拠の真偽や画面の一致を自動判定しない。独立レビュアーが実際の証拠とbuildを照合する。caseの削除・期待値の緩和は受入変更としてレビューする。

## mainへの固定候補

mainをdevelopへ同期後、対象develop SHAとmain SHAを固定し、候補に含まれる全commit・Case・配布物hashを記録する。

```powershell
./scripts/python.ps1 scripts/promotion.py --candidate FULL_DEVELOP_SHA --base FULL_MAIN_SHA
```

候補以降の差分は`cases.json`の結果と`promotion.json`だけにする。`Integration: promotion`のPRでpolicyが候補の祖先関係、mainの移動、Case定義変更・不足、配布物hashの相違、未合格Caseを拒否する。packageは候補のGit blobから標準ZIP形式で再構成し、PR内のビルドscriptをこの判定のために実行しない。実機へはその候補から作った同じhashの成果物をロードする。

初回導入時はmainにCase正本がまだないため、そのままpromotionは行えない。管理ツールのみのbootstrap PRを先にmainへ入れ、製品修正はdevelopの実装PRに分ける。[GitHubセットアップ](../setup/github.md)を参照。

## 初回観察（2026-10-02）

Windows Computer UseでVLCのアプリ登録を確認した。比較対象のインストーラーからMicrosoft Storeへのウィンドウ切替を観測したが、そのStoreウィンドウの取得は `no screenshot targets found for Microsoft.WindowsStore_8wekyb3d8bbwe!App` で失敗した。参照アプリ本体の起動・インストール状態は未確認。VLCへ今回の成果物をロードした事実もまだない。

次のGUI担当は、参照アプリ本体が起動し操作可能なwindowが返ることを確認してからUI-001を再開する。今回のハーネス導入をUI一致の合格として引き継がない。
