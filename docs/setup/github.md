# GitHub側への反映

対象は`shinma06/vlc-wmp-video-skin`。ローカル導入とGitHub反映は別で、現状は[導入記録](../adoption-status.md)を参照する。原典のIssue番号・ruleset ID・過去承認を再利用しない。

## 名称移行時の確認

[Issue #4](https://github.com/shinma06/vlc-wmp-video-skin/issues/4)でrepository名・表示名・配布名の移行を追跡する。GitHubの改名とremoteの更新はPMが担当し、repository ID、Issue/PR、rulesetsを読み戻して既存資源の連続性を確認する。

開発中のGitHub既定branchは `develop` とする。開発の入口を新しい目標へ合わせ、`main` は実機確認済み候補のrelease経路として保つ。初回promotionまで `main` の旧SHA `3c3cb11b9d290351b72be8bdb06549d24cddd4aa` を保持し、既定branchの変更でGUI受入や保護を省略しない。実際の外部設定と読戻し結果はIssue #4を正本とし、完了はAPI読戻し後に記録する。

## 反映順序

1. GitHub CLIまたは認証済みconnectorでrepository、visibility、既存Issue/PR、main/develop、rulesetsを読み戻す。認証値は表示・転記しない。
2. 作業Issueと既存claimを確認し、owner、scope、受入、GUI残条件を登録・読戻す。変更は番号付き専用worktreeで行う。`codex/harness-setup`の番号なしbranchではcommit/pushしない。
3. 通常の変更は確認済み `origin/develop` から作業branchを作り、PRをdevelopへ提出する。スキンと配布物の変更はGUI対象なので、main toolingへ混ぜない。
4. 別sessionレビューと実CI `test` / `PR policy`を通し、developへの統合を確認する。GUIはCase正本とQA Issueに引き継ぐ。
5. 各required checkの実行実績を確認後、[develop設定案](../../.github/develop-ruleset.json)と[main設定案](../../.github/main-ruleset.json)を必要な権限で適用し、GET rulesetとbranchのeffective rulesを照合する。既存設定を盲目的に置換しない。
6. mainへの初回導入も[固定候補手順](../verification/README.md)を使う。確認済みの旧main SHAに限り、台帳がない状態から全10件の初期Caseを必須として移行できる。全CaseのGUI合格・独立レビューを省略しない。

2026-10-02にユーザーがrepositoryをpublicへ変更し、main/developのrulesetsを適用した。設定とbranchのeffective rulesを読戻し、両方がactiveであることを確認済み。実際のrulesetへのリンクは[導入記録](../adoption-status.md)に残す。今後プラン等によりrulesetsが利用できない場合は未適用と記録し、ローカルguardをサーバー保護の代用として報告しない。

## 設定案

両branchともPR必須、strictな`test`と`PR policy`、会話解決、force push/削除禁止、bypassなし。developはsquash、mainはtoolingのsquashまたはpromotionのmerge commitを使う。GitHubユーザーが同一でも別sessionレビューを必須とするが、架空の`Agent review`checkをrequiredへ登録しない。

```powershell
gh api repos/shinma06/vlc-wmp-video-skin/rulesets
gh api repos/shinma06/vlc-wmp-video-skin/rules/branches/main
gh api repos/shinma06/vlc-wmp-video-skin/rules/branches/develop
```

CIはPRコードのテスト用の最小`contents: read`権限で動かし、checkoutに資格情報を残さない。artifactはCIでbuildしたSHAに対応する名前で保存する。独立レビューとlive Issue ownershipをCI内の自己申告に置き換えない。trusted coordinatorによる自動review/mergeは別途実装・検証が必要。

## Issue・Project・Milestone

Issue題名は`[機能]`、`[修正]`、`[調査]`、`[試験]`、`[運用]`、`[追跡]`から作業種別を選ぶ。typeはfeature/bug/research/qa/maintenance/tracking、priorityはP0/P1/P2、statusはready/in-progress/review/blocked/deferred/doneのlabelを使う。

Issueは具体作業、Projectは全体状況、Milestoneは到達目標。必要なものだけ作り、実際の親子・依存関係を登録して読み戻す。分類のためだけに親を捏造しない。初期の受入候補は環境識別、スキン機能限界の調査、Case別差分修正、固定候補QAの順。
