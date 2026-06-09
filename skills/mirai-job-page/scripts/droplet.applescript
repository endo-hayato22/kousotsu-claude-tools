-- みらいジョブ画像最適化 — ドラッグ＆ドロップアプリ
-- 求人画像のフォルダ（または画像ファイル）をこのアプリに重ねるだけで、
-- 1600×1000(8:5) の見切れない画像を「_mirai_ready」フォルダに書き出します。

-- 各自のホーム配下にコピーした mirai_image_fit.py を指す（READMEの「任意：GUIアプリ」参照）。
-- セットアップ: ~/mirai-job-tools/ を作り、プラグイン同梱の scripts/mirai_image_fit.py をそこへコピーする。
property pythonPath : "/usr/bin/python3"

on toolPath()
	return (POSIX path of (path to home folder)) & "mirai-job-tools/mirai_image_fit.py"
end toolPath

on run
	display dialog "求人画像の入ったフォルダ、または画像ファイルを、このアプリのアイコンにドラッグ＆ドロップしてください。" buttons {"OK"} default button "OK" with title "みらいジョブ画像最適化"
end run

on open theItems
	-- 企業名（ファイル名に使用）を尋ねる
	set companyName to "求人"
	try
		set companyName to text returned of (display dialog "企業名を入力してください（例：株式会社佐藤鉄工所）" & return & "→ ファイル名は「企業名_画像1.jpg」になります" default answer "株式会社" with title "みらいジョブ画像最適化")
		if companyName is "" then set companyName to "求人"
	end try

	-- ドロップされた全アイテムを引数に連結
	set itemArgs to ""
	repeat with anItem in theItems
		set itemArgs to itemArgs & " " & quoted form of (POSIX path of anItem)
	end repeat

	set cmd to quoted form of pythonPath & " " & quoted form of (my toolPath()) & itemArgs & " --prefix " & quoted form of companyName

	try
		set fullOut to do shell script cmd
		-- 出力先パスを取得（RESULT_DIR:... 行）
		set outDir to ""
		try
			set outDir to do shell script "echo " & quoted form of fullOut & " | grep '^RESULT_DIR:' | tail -1 | sed 's/^RESULT_DIR://'"
		end try
		display notification "最適化が完了しました（8:5 / 見切れなし）" with title "みらいジョブ画像最適化"
		if outDir is not "" then
			tell application "Finder"
				reveal (POSIX file outDir as alias)
				activate
			end tell
		end if
	on error errMsg
		display dialog "エラーが発生しました：" & return & return & errMsg buttons {"OK"} default button "OK" with title "みらいジョブ画像最適化" with icon stop
	end try
end open
