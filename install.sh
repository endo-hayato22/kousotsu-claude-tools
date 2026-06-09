#!/usr/bin/env bash
# 高卒採用バンク 社内スキルを ~/.claude/skills/ に導入/更新するスクリプト。
# 使い方:  bash install.sh
# （Cowork のチャットで Claude に「このリポジトリの install.sh を実行して」と頼んでもOK）
set -euo pipefail

REPO="https://github.com/endo-hayato22/kousotsu-claude-tools.git"
DEST="$HOME/.claude/skills"
TMP="$(mktemp -d)"

echo "▶ 最新版を取得中..."
git clone --depth 1 "$REPO" "$TMP" >/dev/null 2>&1

mkdir -p "$DEST"
for skill in shodan-followup mirai-job-page; do
  echo "▶ $skill を導入/更新..."
  # profile.json などの個人ファイルは消さずに、リポジトリのファイルだけ上書きコピー
  mkdir -p "$DEST/$skill"
  cp -R "$TMP/skills/$skill/." "$DEST/$skill/"
done

rm -rf "$TMP"
echo "✅ 完了。Cowork を再起動すると /shodan-followup と /mirai-job-page が使えます。"
echo "   （初回の /shodan-followup で氏名・役職・メール・電話を聞かれます）"
