# MinimalX-JPMod（My カスタム）

現在の目標は、VLCの**動画再生中の画面と、その画面で使うUI/UXのみ**をMicrosoft Storeの[Windows メディア プレーヤー](https://apps.microsoft.com/detail/9wzdncrfj3pt?hl=ja-JP&gl=JP)と一致させることです。ホームや音楽・動画ライブラリの再現は対象に含めません。既存スキンを活用し、agent-harnessで動画画面の実機差分をCaseごとに追跡します。UI一致は未検証です。

開発は [プロジェクト設定](docs/project.md) → [Windowsセットアップ](docs/setup/windows.md) → [Issue/PRと二段階統合](docs/workflow.md) → [実機検証](docs/verification/README.md) の順で参照してください。[導入済み範囲と残条件](docs/adoption-status.md)も確認してください。

Maverick07x氏によるVLC Media Player用スキンの「MinimalX」を、日本語環境向けに最適化したスキンです。本体の日本語化はしていません。

**現在のスキン**: テーマカラー（アクセント色）は**1色固定**です。シアン系のアクセント色のみを使用し、色の切り替え機能はありません。今後は上記の実機比較結果に沿って更新します。

# ビルド（.vlt の作成）

`src/` を ZIP 圧縮して `My-MinimalX-JPMod.vlt` を生成・上書きする（worktree名に依存しない）:

```bash
./build-vlt.sh
# または
python3 build-vlt.py
```

別名で出力する場合: `python3 build-vlt.py 任意の名前`

## コミット前に自動ビルド（pre-commit フック）

`src` を変更してコミットするたびに、必ず最新の .vlt に上書きしてからコミットしたい場合は、pre-commit フックを入れます。一度だけ実行してください:

```bash
./install-hooks.sh
```

以降、番号付きIssue branchでsrc/build変更をコミットする直前にビルドが走り、更新された配布物が自動でステージされます。未ステージのsrc/buildが混在すると停止します。mainへの直接commit/pushは禁止し、push前に共通検証を実行します。Windowsの初回設定は上記のセットアップを参照してください。

# Usage
.vlt（スキンファイル）をダウンロードしたらVLCのインストールフォルダ内のskinsフォルダ内にぶち込んでください。（デフォルトでは"C:\Program Files (x86)\VideoLAN\VLC\skins"とか？）
場所は実はどこでもいいですがこれが一番わかり易いと思います。

その後VLCを起動して「ツール＞設定＞インターフェース設定＞カスタムスキンを使用」から先程の.vltファイルを設定して再起動すればOK。
