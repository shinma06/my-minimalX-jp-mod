# MinimalX由来の履歴資料

このディレクトリは、VLC WMP Video Skinへ移行する前の資料を原文のまま保持する、読み取り専用の履歴保管場所です。

- [origin.xml](origin.xml): 旧スキンのXML。元のThemeInfo、作者・連絡先・URLを保持しています。当時の参照assetがすべて揃っているわけではなく、単独でビルド・ロードできるスキンではありません。
- [REVIEW-cyan-fix.md](REVIEW-cyan-fix.md): 以前のシアン固定化に関するレビュー記録。ここにある判定は当時の変更に対する記述で、現在の動画再生画面の合格を示しません。

原作「MinimalX」はMaverick07x氏、日本語環境向けの「MinimalX JPMod」はrexent_gx氏によるものです。新しいプロジェクト名への変更で、この由来を置き換えません。

現在のビルド入力はrepository直下の `src/theme.xml` と `src/files/` です。このディレクトリのファイルは `.vlt` に収録せず、過去の色・画面構成・判定を現在の要件として適用しません。現行の範囲と検証は [project.md](../../docs/project.md) と [実機検証](../../docs/verification/README.md) を参照してください。
