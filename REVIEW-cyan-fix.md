# 一色固定変更のレビュー（オリジナルとの差分）

このカスタムは**テーマカラーを1色固定**する前提で、レガシーな「複数色から選択」のコードを削除した。

## 比較対象
- **オリジナル**: MinimalX-JP（テーマカラー選択あり）
- **カスタム**: My-MinimalX-JPMod（アクセント色1色固定、色選択UIなし）

---

## 1. レイヤー順（UIコンポーネントの前後関係）

VLC スキンでは、同一 Panel/Layout 内で**後に書かれた要素が手前に描画**される。

### 1.1 カバーパネル（cover_panel_tb / cover_panel_info）
| オリジナル（色別3つ） | カスタム（シアン固定） | 判定 |
|------------------------|------------------------|------|
| audio → audio_border → title → title_color1 → title_color2 → title_color3 | audio → audio_border → title(非表示) → title_cyan | ✅ 順序維持。シアン用ボタンが最後＝最前面で問題なし |

### 1.2 メイン・ポジションバー（main_posbar_panel）
| オリジナル | カスタム | 判定 |
|------------|----------|------|
| bg_big → bg_sml → [color1×4, color2×4, color3×4] の12スライダー | bg_big → bg_sml → color2 の4スライダーのみ | ✅ color2 の並び（pos_big → pos_sml → handle_sml → handle_big）は同じ。重ね順も同等 |

### 1.3 プレイリスト（playlist_panel）
| オリジナル | カスタム | 判定 |
|------------|----------|------|
| slider_bg → playtree_color1 → playtree_color2 → playtree_color3(Slider内包) → native/add/remove/... → overlay → hide_color1/2/3 → border_icon | slider_bg → playtree_cyan(Slider内包) → 同様のボタン類 → overlay → hide_cyan → border_icon | ✅ 閉じるボタンは従来どおり overlay の後・border_icon の前。レイヤー順維持 |

### 1.4 設定パネル（sett_panel）
| オリジナル | カスタム | 判定 |
|------------|----------|------|
| ... → sett_posbar_check → [sett_2ブロック] → sett_hide_color1/2/3 → sett-border → sett_border_icon | ... → sett_posbar_check → sett_hide_cyan → sett-border → sett_border_icon | ✅ 「閉じる」ボタンは従来の sett_hide_color2 と同じ位置（posbar_check と border の間）。レイヤー順維持 |

### 1.5 ボリュームパネル（volume_panel）
| オリジナル | カスタム | 判定 |
|------------|----------|------|
| bg_big → bg_sml → fix_color1/2/3 → slider_color1/2/3 → slider_mute → Checkbox×3 → overlay → ... | bg_big → bg_sml → slider_cyan → slider_mute → Checkbox×1 → overlay → ... | ✅ スライダー→チェック→オーバーレイの前後関係は同じ |

### 1.6 フルスクリーン（fs_panel / fs_volume_panel）
| オリジナル | カスタム | 判定 |
|------------|----------|------|
| posbar_bg → [color1/2/3 の pos/handle] → bottombar → volume_panel 内で color1/2/3 + mute | posbar_bg → color2 の pos/handle のみ → bottombar → volume_panel 内で color2 + mute | ✅ 同一パネル内の描画順は維持 |

**結論**: 今回の変更で**レイヤー上下の入れ替わりや意図しない前面化は発生していない**。

---

## 2. その他の副作用チェック

### 2.1 img_menu_icons_all / img_sett_check
- **変更**: `img_menu_colorcheck` の SubBitmap を削除し、`img_sett_check` のみ残した。
- **参照**: `img_sett_check` は `x="0" y="50"` のまま。menu_icons.png の 2 行目（50–100px）を参照しており、オリジナルと同じ。
- **判定**: ✅ チェックマーク表示に影響なし。

### 2.2 Window "color" の Layout
- **変更**: Layout を color_1 / color_2 / color_3 の 3 つ → **color_2 のみ**に。
- **影響**: スキンは「常に color_2」で動作。デフォルトも color_2 のみのため不整合なし。
- **判定**: ✅ 意図どおり。

### 2.3 Window "sett" の Layout
- **変更**: sett_2（テーマカラー選択）を削除。宣言順は sett_3 → sett_1 → sett_0。
- **影響**: 設定表示は `sett.setLayout(sett_0)` で開くため、Layout の宣言順に依存しない。sett_2 へ遷移するボタンも削除済み。
- **判定**: ✅ 問題なし。

### 2.4 Playlist の Slider の親
- **変更**: Slider を playtree_color3 の子 → **playtree_cyan の子**に変更。
- **影響**: オリジナルでも Slider は 1 つの Playtree の子だった。1 本化後も同じ構造。
- **判定**: ✅ 問題なし。

### 2.5 削除した Bitmap の参照漏れ
- 削除した Bitmap/SubBitmap: img_color1_icons_all, img_color3_icons_all, img_menu_colors_all, gif_cover_color1/3, img_sett_color* 等。
- **確認**: これらを参照する id は theme.xml 内に残っていない（grep で確認済み）。
- **判定**: ✅ 参照漏れなし。

---

## 3. オリジナル（MinimalX-JP）との構造差（今回の変更以外）

以下は**もともと My-MinimalX-JPMod が MinimalX-JP と異なっていた点**（シアン固定とは無関係）:

- MinimalX-JP には cinema モード・titlebar_off/on・bottom_0/1/2 の展開パネル等があるが、My-MinimalX-JPMod はこれらを未採用の簡略構成。
- 設定の img_settings_all が MinimalX-JP は menu_all.png + menu_part2_all.png の 2 つに分かれ、My-MinimalX-JPMod は menu_all.png と menu_part2_all.png（img_settings_part2_all）を別 Bitmap として使用。
- 上記のため、単純な「1行ずれ」のようなレイヤーずれは今回の修正では発生していない。

---

## 4. 総合判定

| 項目               | 結果 |
|--------------------|------|
| レイヤー順の変更   | ✅ なし（意図した削除・1本化のみ） |
| img_sett_check 参照 | ✅ 正しい（y=50 のまま） |
| Window/Layout 定義 | ✅ 矛盾なし（color は color_2 のみ、sett から sett_2 削除） |
| 参照切れ・未参照 id | ✅ なし |
| その他副作用       | ✅ 特になし |

**結論**: 一色固定化・色選択UI削除により、レイヤー上下の変更やその他の副作用は発生していない。

---

## 名づけについて（レガシー → 一色前提）

- **ThemeInfo name**: `MinimalX JPMod - 1色固定` に変更済み。
- **README**: このカスタムは「テーマカラー1色固定」である旨を明記済み。
- **theme.xml 内の id**: `color_2` や `img_color2_*` は、オリジナルアセット（colors_aio）のファイル名・構造に合わせた名残。エンジン・参照の都合上そのままにしてあり、コメントで「1色固定」「アクセント用」と補足している。
