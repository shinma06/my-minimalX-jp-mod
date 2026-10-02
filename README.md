# VLC WMP Video Skin

VLCの**動画再生中の画面と、その画面で使うUI/UXのみ**を、Microsoft Storeの[Windows メディア プレーヤー](https://apps.microsoft.com/detail/9wzdncrfj3pt?hl=ja-JP&gl=JP)と一致させるプロジェクトです。ホームや音楽・動画ライブラリ、アプリ全体のナビゲーションは対象に含めません。[GitHub repository](https://github.com/shinma06/vlc-wmp-video-skin)で動画画面の実機差分をCaseごとに追跡します。

現在は既存のVLC Skins2スキンを基に開発しています。動画画面の一致は未検証で、全10件のGUI Caseはpendingです。名称変更やビルド成功を、UI/UXの完成や実機合格として扱いません。

開発は [プロジェクト設定](docs/project.md) → [Windowsセットアップ](docs/setup/windows.md) → [Issue/PRと二段階統合](docs/workflow.md) → [実機検証](docs/verification/README.md) の順で参照してください。[導入済み範囲と残条件](docs/adoption-status.md)も確認してください。

## ビルドと検証

Python 3.11以上の標準ライブラリで、`src/theme.xml` と `src/files/` から `VLC-WMP-Video.vlt` を生成します。成果物名はrepositoryやworktreeのフォルダー名に依存しません。

WindowsのPowerShellでは、初回に以下を実行します。

```powershell
python scripts/bootstrap.py
./scripts/python.ps1 scripts/check.py
./scripts/python.ps1 build-vlt.py --output-dir .harness-local/dist
```

macOS/Linux/Git Bashでは `bash scripts/python.sh scripts/check.py` と `./build-vlt.sh --output-dir .harness-local/dist` を使います。出力先を省略すると、repository直下の配布物を更新します。

番号付きIssue branchでsrc/build変更をコミットすると、通常のpre-commitフックが配布物を再生成してステージします。配布名の正本は `scripts/validate_skin.py` の `ARTIFACT_NAME` で、ビルダーと検証が共有します。未ステージのsrc/build変更が混在すると停止します。main/developへの直接commit/pushは禁止し、push前に共通検証を実行します。

## VLCでの利用と実機比較

固定候補コミットに含まれる `VLC-WMP-Video.vlt` を保存し、VLCの「ツール → 設定 → インターフェース → カスタムスキンを使用」で指定して再起動します。実機比較では候補SHAと、実際にロードした配布物のSHA-256を[検証記録](docs/verification/README.md)へ残します。別環境で生成した異なるhashの配布物を同じ候補の合格証拠に使いません。

## 出典と過去の資料

原作はMaverick07x氏によるVLCスキン「MinimalX」で、rexent_gx氏による日本語環境向けの「MinimalX JPMod」を経て本プロジェクトへ引き継いでいます。現在の動画画面の目標は、過去のシアン固定化とは別に実機比較から定めます。

元のXMLと過去のレビューは [legacy/minimalx](legacy/minimalx/README.md) に原文のまま保存しています。この資料は履歴参照用で、現在のビルド入力やGUI合格の根拠ではありません。
