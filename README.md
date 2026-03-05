# MinimalX-JPMod
Maverick07x氏によるVLC Media Player用スキンの「MinimalX」を、デフォルトだと文字化けするので日本語環境に最適化したスキンです。本体の日本語化はしてません。

# ビルド（.vlt の作成）

`src/` を ZIP 圧縮してリポジトリ名の `.vlt` を生成・上書きする:

```bash
./build-vlt.sh
# または
python3 build-vlt.py
```

別名で出力する場合: `python3 build-vlt.py MinimalX_JPMod_VLC_2.6.2`

## コミット前に自動ビルド（pre-commit フック）

`src` を変更してコミットするたびに、必ず最新の .vlt に上書きしてからコミットしたい場合は、pre-commit フックを入れます。一度だけ実行してください:

```bash
./install-hooks.sh
```

以降、`git commit` を実行する直前にビルドが走り、更新された .vlt が自動でステージされて一緒にコミットされます。

# Usage
.vlt（スキンファイル）をダウンロードしたらVLCのインストールフォルダ内のskinsフォルダ内にぶち込んでください。（デフォルトでは"C:\Program Files (x86)\VideoLAN\VLC\skins"とか？）
場所は実はどこでもいいですがこれが一番わかり易いと思います。

その後VLCを起動して「ツール＞設定＞インターフェース設定＞カスタムスキンを使用」から先程の.vltファイルを設定して再起動すればOK。
