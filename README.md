# 高卒採用バンク 社内ツール（kousotsu-tools）

Claude Code / Cowork から使える社内スキル集です。**営業メンバー全員**が同じツールを使えるようにするためのプラグインです。

含まれるスキル：

| コマンド | 何ができる |
|---|---|
| `/shodan-followup` | 商談後フォローメールのGmail下書き＋提案書PDFをワンタップ作成 |
| `/mirai-job-page` | みらいジョブ求人ページの画像8:5最適化・社員インタビュー整形・先方修正対応 |

---

## 0. 前提（最初に確認）

- Claude Code または Cowork を使えること。
- **Gmail コネクタと Google Drive コネクタを自分のアカウントで接続済み**であること。
  - `/shodan-followup`：自分宛に Google Meet「会議の記録」通知（`meetings-noreply@google.com`）が届いている必要があります。
  - `/mirai-job-page`：社内共有スプレッドシート「みらいジョブページ作成インタビュー（回答）」の閲覧権限が必要です（持っていなければ管理者に共有を依頼）。
- Python3 が入っていること（Mac標準でOK）。スキルが必要に応じて `reportlab` / `Pillow` を `pip3 install --user` で入れます。

---

## 1. インストール（各自1回だけ）

Claude Code / Cowork のチャットで以下を実行します。

```
/plugin marketplace add <your-org>/kousotsu-claude-tools
/plugin install kousotsu-tools@kousotsu-tools
```

> `<your-org>/kousotsu-claude-tools` は社内で配布されたGitHubリポジトリ名に置き換えてください。

インストール後、`/shodan-followup` と `/mirai-job-page` がコマンドとして使えるようになります。

---

## 2. 初回設定（`/shodan-followup` を使う人のみ）

フォローメールは「あなた名義」で作られます。初回起動時に **氏名（漢字）・役職・メールアドレス・電話番号** を聞かれるので答えてください。一度答えれば次回以降は聞かれません（あなたのPC内にのみ保存され、共有されません）。

---

## 3. 使い方

- **商談フォロー**：商談のあった日に `/shodan-followup`（当日分を自動検知）。特定の会社・日付なら `/shodan-followup アームズ` のように指定。
  - フォローメールはGmailの**下書き**として作られます。提案書PDFは `~/Downloads/営業資料/claude提案資料/` に保存されるので、送信前に下書きへドラッグして添付してください。
- **求人ページ**：`/mirai-job-page` を呼び、求人票PDF・求人画像・パンフレット等を渡します。最適化画像とインタビュー文は `~/Downloads/営業資料/claude提案資料/みらいジョブ掲載素材` に出力されます。

---

## 4.（任意）画像最適化を GUI アプリで使いたい人へ

ターミナルを使わず、フォルダをドラッグ＆ドロップするだけで画像最適化したい場合、Mac用のドロップレットアプリを自分で作れます。

1. ホームに `~/mirai-job-tools/` を作り、プラグイン同梱の画像最適化スクリプトをコピー：
   ```
   mkdir -p ~/mirai-job-tools
   cp <プラグイン>/skills/mirai-job-page/scripts/mirai_image_fit.py ~/mirai-job-tools/
   ```
   （`<プラグイン>` の実体パスは Claude に「mirai-job-page スキルの場所を教えて」と聞けば分かります。）
2. 同梱の `scripts/droplet.applescript` を「スクリプトエディタ」で開く。
3. メニュー「ファイル → 書き出す」で、ファイルフォーマット＝**アプリケーション** を選び、`みらいジョブ画像最適化.app` としてデスクトップに保存。
4. 以後は求人画像フォルダをこのアプリに重ねるだけで `~/Downloads/.../みらいジョブ掲載素材` に最適化画像が出ます。

---

## 5. 更新の受け取り方

管理者（遠藤）がスキルを改善して push したら、各自で以下を実行すると最新版になります。

```
/plugin update
```

---

## 管理者向けメモ

- スキル本体：`plugins/kousotsu-tools/skills/{shodan-followup, mirai-job-page}/SKILL.md`
- 同梱スクリプト/アセットは `${CLAUDE_PLUGIN_ROOT}` で参照（個人のホームパスを直書きしないこと）。
- 個人別データ（profile.json 等）は `${CLAUDE_PLUGIN_DATA}` に置く（更新後も残る／リポジトリには入れない）。
- 改善したら main に push するだけで、各メンバーの `/plugin update` に配布されます（`version` 未指定なので commit ごとに新版扱い）。
