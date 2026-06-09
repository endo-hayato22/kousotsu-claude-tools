# 高卒採用バンク 社内スキル（kousotsu-claude-tools）

Cowork（Claudeデスクトップアプリ）から使える社内スキル集です。**営業メンバー全員**が同じツールを使えるように、スキルを `~/.claude/skills/` に置いて共有します。

含まれるスキル：

| コマンド | 何ができる |
|---|---|
| `/shodan-followup` | 商談後フォローメールのGmail下書き＋提案書PDFをワンタップ作成 |
| `/mirai-job-page` | みらいジョブ求人ページの画像8:5最適化・社員インタビュー整形・先方修正対応 |

---

## 0. 前提（最初に確認）

- Cowork（Claudeアプリ）を使っていること。
- **Gmail コネクタと Google Drive コネクタを自分のアカウントで接続済み**であること。
  - `/shodan-followup`：自分宛に Google Meet「会議の記録」通知（`meetings-noreply@google.com`）が届いている必要があります。
  - `/mirai-job-page`：社内共有スプレッドシート「みらいジョブページ作成インタビュー（回答）」の閲覧権限が必要です（持っていなければ管理者に共有を依頼）。
- Python3 が入っていること（Mac標準でOK）。スキルが必要に応じて `reportlab` / `Pillow` を `pip3 install --user` で入れます。

---

## 1. インストール（各自1回だけ）

Cowork のチャットに、次のように頼むのが一番かんたんです：

> **「https://github.com/endo-hayato22/kousotsu-claude-tools の install.sh を実行して、社内スキルを入れて」**

Cowork（Claude）がターミナル作業を代わりにやって、スキルを `~/.claude/skills/` に入れてくれます。

ターミナルが使える人は、直接これでもOK：

```bash
git clone --depth 1 https://github.com/endo-hayato22/kousotsu-claude-tools.git /tmp/kct && bash /tmp/kct/install.sh
```

**インストール後、Cowork を再起動**すると `/shodan-followup` と `/mirai-job-page` が使えるようになります。

---

## 2. 初回設定（`/shodan-followup` を使う人のみ）

フォローメールは「あなた名義」で作られます。初回起動時に **氏名（漢字）・役職・メールアドレス・電話番号** を聞かれるので答えてください。一度答えれば次回以降は聞かれません（`~/.claude/skills/shodan-followup/profile.json` にあなたのPC内のみ保存され、共有されません）。

---

## 3. 使い方

- **商談フォロー**：商談のあった日に `/shodan-followup`（当日分を自動検知）。特定の会社・日付なら `/shodan-followup アームズ` のように指定。
  - フォローメールはGmailの**下書き**として作られます。提案書PDFは `~/Downloads/営業資料/claude提案資料/` に保存されるので、送信前に下書きへドラッグして添付してください。
- **求人ページ**：`/mirai-job-page` を呼び、求人票PDF・求人画像・パンフレット等を渡します。最適化画像とインタビュー文は `~/Downloads/営業資料/claude提案資料/みらいジョブ掲載素材` に出力されます。

---

## 4.（任意）画像最適化を GUI アプリで使いたい人へ

ターミナルもCoworkも使わず、フォルダをドラッグ＆ドロップするだけで画像最適化したい場合、Mac用のドロップレットアプリを自分で作れます。

1. ホームに `~/mirai-job-tools/` を作り、スクリプトをコピー：
   ```bash
   mkdir -p ~/mirai-job-tools
   cp ~/.claude/skills/mirai-job-page/scripts/mirai_image_fit.py ~/mirai-job-tools/
   ```
2. `~/.claude/skills/mirai-job-page/scripts/droplet.applescript` を「スクリプトエディタ」で開く。
3. メニュー「ファイル → 書き出す」で、ファイルフォーマット＝**アプリケーション** を選び、`みらいジョブ画像最適化.app` としてデスクトップに保存。
4. 以後は求人画像フォルダをこのアプリに重ねるだけで `~/Downloads/.../みらいジョブ掲載素材` に最適化画像が出ます。

---

## 5. 更新の受け取り方

管理者（遠藤）がスキルを改善して push したら、各自もう一度インストール手順（手順1）を実行すれば最新版になります。個人設定（profile.json）は消えません。

---

## 管理者向けメモ

- スキル本体：`skills/{shodan-followup, mirai-job-page}/SKILL.md`
- 同梱スクリプト/アセットは固定パス `~/.claude/skills/<skill>/...` で参照（各メンバーのホーム配下なので全員で動く。個人のホーム名を直書きしないこと）。
- 個人別データ（profile.json）は `~/.claude/skills/shodan-followup/profile.json`（`.gitignore` 済み・リポジトリには入らない）。
- この環境（Cowork）では Claude Code の `/plugin` は使えないため、配布はプラグインではなく `~/.claude/skills/` への配置で行う。
- 改善したら main に push → 各メンバーが手順1を再実行で配布。
