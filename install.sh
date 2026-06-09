#!/usr/bin/env bash
# 高卒採用バンク 社内スキルを ~/.claude/skills/ に導入/更新するスクリプト。
# git が無いMacでも動くよう、標準の curl でZIP/tarを取得する方式。
# 使い方:  bash install.sh
# （Cowork のチャットで Claude に「このリポジトリの install.sh を実行して」と頼んでもOK）
set -euo pipefail

REPO_TARBALL="https://github.com/endo-hayato22/kousotsu-claude-tools/archive/refs/heads/main.tar.gz"
DEST="$HOME/.claude/skills"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "▶ 最新版を取得中..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$REPO_TARBALL" -o "$TMP/repo.tar.gz"
elif command -v git >/dev/null 2>&1; then
  git clone --depth 1 "https://github.com/endo-hayato22/kousotsu-claude-tools.git" "$TMP/repo" >/dev/null 2>&1
else
  echo "❌ curl も git も見つかりません。管理者に連絡してください。" >&2
  exit 1
fi

# 展開（tar取得時）。git取得時は $TMP/repo にそのまま。
SRCROOT="$TMP/repo"
if [ -f "$TMP/repo.tar.gz" ]; then
  tar -xzf "$TMP/repo.tar.gz" -C "$TMP"
  SRCROOT="$(find "$TMP" -maxdepth 1 -type d -name 'kousotsu-claude-tools*' | head -1)"
fi

if [ ! -d "$SRCROOT/skills" ]; then
  echo "❌ ダウンロードした中身に skills フォルダが見つかりません。" >&2
  exit 1
fi

mkdir -p "$DEST"
for skill in shodan-followup mirai-job-page; do
  echo "▶ $skill を導入/更新..."
  mkdir -p "$DEST/$skill"
  # profile.json などの個人ファイルは消さず、リポジトリのファイルだけ上書き
  cp -R "$SRCROOT/skills/$skill/." "$DEST/$skill/"
done

# 検証
ok=1
for skill in shodan-followup mirai-job-page; do
  if [ -f "$DEST/$skill/SKILL.md" ]; then
    echo "  ✓ $DEST/$skill/SKILL.md"
  else
    echo "  ✗ $skill が入っていません"; ok=0
  fi
done

if [ "$ok" = 1 ]; then
  echo ""
  echo "✅ インストール完了。"
  echo "   👉 ここが重要：Cowork を【完全に終了】してから開き直してください。"
  echo "      （メニューバーのアプリ名 → 終了。⌘+Q。×ボタンで閉じるだけでは再読み込みされないことがあります）"
  echo "   再起動後、チャットで /shodan-followup や /mirai-job-page が使えます。"
else
  echo "❌ 一部が入りませんでした。エラー文を管理者（遠藤）に送ってください。" >&2
  exit 1
fi
