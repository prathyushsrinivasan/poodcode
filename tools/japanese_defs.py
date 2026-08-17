# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Japanese coding-vocabulary Learn track.
#
# This file is exec()'d inside gen_seed.py's namespace (see the hook right
# after typescript_defs.py). It extends CONCEPTS / CATEGORY / LESSONS in place
# with a set of *reference* concepts whose lessons are big vocabulary tables:
# the Japanese words a Java / software engineer working in a Japanese-language
# environment will keep running into, each with its reading and a natural
# example sentence.
#
# WHY IT'S A "LANGUAGE" IN THE LEARN TAB:
#   Every concept here is marked  "language": "japanese"  so the Learn tab's
#   language toggle shows them only under the 日本語 (Japanese) view, next to
#   Java and TypeScript. There is NO code judge involved — these are
#   lesson-only reference concepts (no fill-in-the-blank drills), so there is
#   no SEED_VERSION / SQLite impact: concepts are embedded JSON, rebuilt by
#   `python tools/gen_seed.py`.
#
# TABLE FORMAT NOTE:
#   The Markdown renderer is react-markdown + remark-gfm WITHOUT rehype-raw, so
#   raw HTML (e.g. <br>) does NOT render and must never appear in a cell. Each
#   example cell therefore keeps the Japanese sentence and its English gloss on
#   one line, separated by an em dash. No cell may contain a literal '|'.
# ---------------------------------------------------------------------------

JP_LANG = "japanese"


def _jp_table(rows):
    """Build a GFM table from (term, reading, meaning, ja_example, en_example)."""
    out = [
        "| 用語 (Term) | 読み方 (Reading) | 意味 (Meaning) | 例文 (Example) |",
        "|---|---|---|---|",
    ]
    for (term, reading, meaning, ja, en) in rows:
        for cell in (term, reading, meaning, ja, en):
            assert "|" not in cell, f"cell contains a pipe: {cell!r}"
        out.append(f"| {term} | {reading} | {meaning} | {ja} — *{en}* |")
    return "\n".join(out) + "\n"


def _jp_cards(rows):
    """Structured flashcard data for a concept — the same rows the glossary
    table shows, so the Learn tab can offer a card-study mode over them."""
    return [
        {
            "front": term,
            "reading": reading,
            "meaning": meaning,
            "example_ja": ja,
            "example_en": en,
        }
        for (term, reading, meaning, ja, en) in rows
    ]


def _jp_concept(key, name, category, what, deep, note, rows, intro=""):
    """Register one Japanese vocabulary concept (lesson = intro + table)."""
    CONCEPTS[key] = {
        "name": name,
        "what": what,
        "deep": deep,
        "java": note,          # repurposed: shown under the dynamic "How to read this" card
        "language": JP_LANG,
        "cards": _jp_cards(rows),   # structured cards for flashcard study mode
    }
    CATEGORY[key] = category
    lesson = (intro.strip() + "\n\n") if intro else ""
    lesson += _jp_table(rows)
    LESSONS[key] = lesson
    # These concepts are pure reference — no fill-in-the-blank drills.
    EXERCISES.setdefault(key, [])


_READING_NOTE = (
    "The **Reading** column gives the kana pronunciation and a romaji gloss so "
    "you can say the word out loud. Loanwords written in katakana already *are* "
    "their reading, so only the romaji is shown. Example sentences are polite "
    "(です・ます) form — exactly how you'd hear them in a standup or an interview."
)


# ===========================================================================
# 1) Coding basics — プログラミングの基礎
# ===========================================================================
_jp_concept(
    "jp_coding_basics",
    "Coding Basics — プログラミングの基礎",
    "JP: Coding Basics",
    "The everyday words for code, running it, variables, functions and I/O.",
    "Start here. These are the words that show up in every conversation about "
    "code regardless of language — writing it, running it, and the pieces every "
    "program is built from (variables, values, functions, types).",
    _READING_NOTE,
    [
        ("プログラミング", "puroguramingu", "programming", "毎日プログラミングを練習しています。", "I practice programming every day."),
        ("コード", "kōdo", "code", "このコードを読んでください。", "Please read this code."),
        ("プログラム", "puroguramu", "program", "プログラムを実行します。", "I'll run the program."),
        ("開発", "かいはつ (kaihatsu)", "development", "新しいアプリを開発しています。", "I'm developing a new app."),
        ("実装", "じっそう (jissō)", "implementation", "この機能を実装してください。", "Please implement this feature."),
        ("機能", "きのう (kinō)", "feature / function", "この機能はまだできていません。", "This feature isn't done yet."),
        ("変数", "へんすう (hensū)", "variable", "変数に値を代入します。", "We assign a value to a variable."),
        ("値", "あたい (atai)", "value", "この変数の値は10です。", "This variable's value is 10."),
        ("代入", "だいにゅう (dainyū)", "assignment", "変数xに5を代入します。", "Assign 5 to variable x."),
        ("関数", "かんすう (kansū)", "function", "この関数は合計を返します。", "This function returns the sum."),
        ("引数", "ひきすう (hikisū)", "argument / parameter", "関数に引数を渡します。", "We pass an argument to the function."),
        ("戻り値", "もどりち (modorichi)", "return value", "戻り値は整数です。", "The return value is an integer."),
        ("返す", "かえす (kaesu)", "to return (a value)", "結果を返してください。", "Please return the result."),
        ("呼び出す", "よびだす (yobidasu)", "to call / invoke", "この関数を呼び出します。", "We call this function."),
        ("型", "かた (kata)", "type", "この変数の型は文字列です。", "This variable's type is string."),
        ("整数", "せいすう (seisū)", "integer", "整数を入力してください。", "Please enter an integer."),
        ("文字列", "もじれつ (mojiretsu)", "string", "二つの文字列を連結します。", "We concatenate the two strings."),
        ("真偽値", "しんぎち (shingichi)", "boolean", "真偽値はtrueかfalseです。", "A boolean is true or false."),
        ("条件分岐", "じょうけんぶんき (jōken bunki)", "conditional branch", "条件分岐でif文を使います。", "We use an if statement for branching."),
        ("繰り返し", "くりかえし (kurikaeshi)", "loop / iteration", "繰り返しで配列を処理します。", "We process the array with a loop."),
        ("処理", "しょり (shori)", "processing", "このデータを処理します。", "We process this data."),
        ("実行", "じっこう (jikkō)", "execution / run", "プログラムを実行しました。", "I ran the program."),
        ("コンパイル", "konpairu", "compile", "ソースコードをコンパイルします。", "We compile the source code."),
        ("コメント", "komento", "comment", "コードにコメントを書きます。", "I write comments in the code."),
        ("入力", "にゅうりょく (nyūryoku)", "input", "数字を入力します。", "We input a number."),
        ("出力", "しゅつりょく (shutsuryoku)", "output", "結果を出力します。", "We output the result."),
    ],
)


# ===========================================================================
# 2) Java language — Java言語
# ===========================================================================
_jp_concept(
    "jp_java_lang",
    "Java Language — Java言語",
    "JP: Java Language",
    "Classes, methods, objects, inheritance and the vocabulary of Java itself.",
    "Java's building blocks have standard Japanese names. Note that many are "
    "katakana loanwords (クラス, メソッド, オブジェクト) while the OOP concepts "
    "tend to be kanji compounds (継承, 多態性, 抽象).",
    _READING_NOTE,
    [
        ("クラス", "kurasu", "class", "新しいクラスを作ります。", "We create a new class."),
        ("メソッド", "mesoddo", "method", "このメソッドを呼び出します。", "We call this method."),
        ("オブジェクト", "obujekuto", "object", "オブジェクトを生成します。", "We instantiate an object."),
        ("インスタンス", "insutansu", "instance", "クラスのインスタンスを作ります。", "We create an instance of the class."),
        ("フィールド", "fīrudo", "field (member variable)", "このクラスには三つのフィールドがあります。", "This class has three fields."),
        ("コンストラクタ", "konsutorakuta", "constructor", "コンストラクタで初期化します。", "We initialize in the constructor."),
        ("継承", "けいしょう (keishō)", "inheritance", "このクラスは親クラスを継承します。", "This class inherits from the parent class."),
        ("親クラス", "おやクラス (oya kurasu)", "parent / superclass", "親クラスのメソッドを使います。", "We use the parent class's method."),
        ("インターフェース", "intāfēsu", "interface", "インターフェースを実装します。", "We implement the interface."),
        ("抽象クラス", "ちゅうしょうクラス (chūshō kurasu)", "abstract class", "抽象クラスはインスタンス化できません。", "An abstract class can't be instantiated."),
        ("カプセル化", "カプセルか (kapuseru-ka)", "encapsulation", "カプセル化でデータを守ります。", "Encapsulation protects the data."),
        ("多態性", "たたいせい (tataisei)", "polymorphism", "多態性で同じメソッド名を使えます。", "Polymorphism lets us reuse the same method name."),
        ("オーバーライド", "ōbāraido", "override", "メソッドをオーバーライドします。", "We override the method."),
        ("ジェネリクス", "jenerikusu", "generics", "ジェネリクスで型を指定します。", "We specify the type with generics."),
        ("修飾子", "しゅうしょくし (shūshokushi)", "(access) modifier", "privateは修飾子です。", "`private` is a modifier."),
        ("静的", "せいてき (seiteki)", "static", "静的メソッドはクラスに属します。", "A static method belongs to the class."),
        ("パッケージ", "pakkēji", "package", "このクラスは同じパッケージにあります。", "This class is in the same package."),
        ("インポート", "inpōto", "import", "ライブラリをインポートします。", "We import the library."),
        ("アノテーション", "anotēshon", "annotation", "@Overrideはアノテーションです。", "`@Override` is an annotation."),
        ("ライブラリ", "raiburari", "library", "標準ライブラリを使います。", "We use the standard library."),
        ("フレームワーク", "furēmuwāku", "framework", "このフレームワークは便利です。", "This framework is convenient."),
        ("定数", "ていすう (teisū)", "constant", "定数はfinalで宣言します。", "We declare a constant with `final`."),
        ("宣言", "せんげん (sengen)", "declaration", "変数を宣言します。", "We declare a variable."),
        ("初期化", "しょきか (shokika)", "initialization", "リストを初期化します。", "We initialize the list."),
        ("継承関係", "けいしょうかんけい (keishō kankei)", "inheritance relationship", "二つのクラスは継承関係にあります。", "The two classes have an inheritance relationship."),
        ("親子関係", "おやこかんけい (oyako kankei)", "parent-child relationship", "クラスの親子関係を確認します。", "We check the class parent-child relationship."),
    ],
)


# ===========================================================================
# 3) Control flow & operators — 制御構文と演算子
# ===========================================================================
_jp_concept(
    "jp_control_flow",
    "Control Flow & Operators — 制御構文と演算子",
    "JP: Control Flow",
    "Conditions, loops, comparisons and the operator vocabulary.",
    "Once you can name a variable, you need to name what you do with it: test a "
    "condition, branch, loop, break out, compare two values. These words come "
    "up constantly when you talk through your solution out loud.",
    _READING_NOTE,
    [
        ("条件", "じょうけん (jōken)", "condition", "条件が真なら実行します。", "If the condition is true, it runs."),
        ("分岐", "ぶんき (bunki)", "branch", "ここでコードが分岐します。", "The code branches here."),
        ("真", "しん (shin)", "true", "条件は真です。", "The condition is true."),
        ("偽", "ぎ (gi)", "false", "結果は偽でした。", "The result was false."),
        ("比較", "ひかく (hikaku)", "comparison", "二つの値を比較します。", "We compare the two values."),
        ("演算子", "えんざんし (enzanshi)", "operator", "プラスは算術演算子です。", "Plus is an arithmetic operator."),
        ("論理演算", "ろんりえんざん (ronri enzan)", "logical operation", "論理演算でANDを使います。", "We use AND in a logical operation."),
        ("反復", "はんぷく (hanpuku)", "iteration", "for文で反復します。", "We iterate with a for loop."),
        ("再帰", "さいき (saiki)", "recursion", "この関数は再帰を使います。", "This function uses recursion."),
        ("無限ループ", "むげんループ (mugen rūpu)", "infinite loop", "無限ループに注意してください。", "Watch out for infinite loops."),
        ("抜ける", "ぬける (nukeru)", "to break / exit a loop", "breakでループを抜けます。", "We exit the loop with `break`."),
        ("続ける", "つづける (tsuzukeru)", "to continue", "continueで次の反復に進みます。", "We move to the next iteration with `continue`."),
        ("場合", "ばあい (baai)", "case", "この場合、xは0です。", "In this case, x is 0."),
        ("三項演算子", "さんこうえんざんし (sankō enzanshi)", "ternary operator", "三項演算子で短く書けます。", "We can write it shorter with the ternary operator."),
        ("剰余", "じょうよ (jōyo)", "remainder / modulo", "剰余で偶数かどうか判定します。", "We check for even numbers with the remainder."),
        ("加算", "かさん (kasan)", "addition", "二つの数を加算します。", "We add the two numbers."),
        ("判定", "はんてい (hantei)", "check / determination", "素数かどうか判定します。", "We check whether it's prime."),
        ("等しい", "ひとしい (hitoshii)", "equal", "二つの値が等しいか確認します。", "We check if the two values are equal."),
        ("以上", "いじょう (ijō)", "greater than or equal", "xが5以上なら実行します。", "Run if x is 5 or more."),
        ("以下", "いか (ika)", "less than or equal", "yが10以下か確認します。", "We check if y is 10 or less."),
        ("初期値", "しょきち (shokichi)", "initial value", "カウンタの初期値は0です。", "The counter's initial value is 0."),
        ("真偽", "しんぎ (shingi)", "true-or-false", "条件の真偽を確認します。", "We check the truth of the condition."),
    ],
)


# ===========================================================================
# 4) Data structures & algorithms — データ構造とアルゴリズム
# ===========================================================================
_jp_concept(
    "jp_data_structures",
    "Data Structures & Algorithms — データ構造とアルゴリズム",
    "JP: Data Structures",
    "Arrays, lists, trees, graphs, sorting, search and complexity.",
    "This is the heart of a technical interview in Japanese. You'll be asked to "
    "pick a データ構造 (data structure), describe an アルゴリズム (algorithm), "
    "and state its 計算量 (complexity). These are the exact words for that.",
    _READING_NOTE,
    [
        ("データ構造", "dēta kōzō", "data structure", "適切なデータ構造を選びます。", "We choose the right data structure."),
        ("アルゴリズム", "arugorizumu", "algorithm", "効率の良いアルゴリズムを考えます。", "We think of an efficient algorithm."),
        ("配列", "はいれつ (hairetsu)", "array", "配列を昇順に並べます。", "We arrange the array in ascending order."),
        ("連結リスト", "れんけつリスト (renketsu risuto)", "linked list", "連結リストにノードを追加します。", "We add a node to the linked list."),
        ("スタック", "sutakku", "stack", "スタックは後入れ先出しです。", "A stack is last-in, first-out."),
        ("キュー", "kyū", "queue", "キューは先入れ先出しです。", "A queue is first-in, first-out."),
        ("木構造", "きこうぞう (ki kōzō)", "tree (structure)", "木構造を再帰で探索します。", "We traverse the tree recursively."),
        ("二分木", "にぶんぎ (nibungi)", "binary tree", "二分木には左と右の子があります。", "A binary tree has left and right children."),
        ("二分探索木", "にぶんたんさくぎ (nibun tansakugi)", "binary search tree", "二分探索木は整列されています。", "A binary search tree is kept sorted."),
        ("グラフ", "gurafu", "graph", "グラフを幅優先で探索します。", "We traverse the graph breadth-first."),
        ("ノード", "nōdo", "node", "各ノードは値を持ちます。", "Each node holds a value."),
        ("頂点", "ちょうてん (chōten)", "vertex", "グラフには頂点と辺があります。", "A graph has vertices and edges."),
        ("辺", "へん (hen)", "edge", "二つの頂点を辺でつなぎます。", "We connect two vertices with an edge."),
        ("ハッシュマップ", "hasshu mappu", "hash map", "ハッシュマップで高速に検索します。", "We search quickly with a hash map."),
        ("連想配列", "れんそうはいれつ (rensō hairetsu)", "associative array (map)", "連想配列はキーと値を持ちます。", "An associative array has keys and values."),
        ("探索", "たんさく (tansaku)", "search", "二分探索で要素を探します。", "We find the element with binary search."),
        ("整列", "せいれつ (seiretsu) / ソート", "sorting", "配列をソートします。", "We sort the array."),
        ("昇順", "しょうじゅん (shōjun)", "ascending order", "昇順に並べ替えます。", "We sort in ascending order."),
        ("降順", "こうじゅん (kōjun)", "descending order", "降順に並べ替えます。", "We sort in descending order."),
        ("計算量", "けいさんりょう (keisanryō)", "computational complexity", "このアルゴリズムの計算量はO(n)です。", "This algorithm's complexity is O(n)."),
        ("時間計算量", "じかんけいさんりょう (jikan keisanryō)", "time complexity", "時間計算量を見積もります。", "We estimate the time complexity."),
        ("空間計算量", "くうかんけいさんりょう (kūkan keisanryō)", "space complexity", "空間計算量を減らします。", "We reduce the space complexity."),
        ("効率", "こうりつ (kōritsu)", "efficiency", "コードの効率を上げます。", "We improve the code's efficiency."),
        ("要素", "ようそ (yōso)", "element", "リストの要素を数えます。", "We count the list's elements."),
        ("添字", "そえじ (soeji)", "index (subscript)", "添字で配列にアクセスします。", "We access the array by index."),
        ("再帰呼び出し", "さいきよびだし (saiki yobidashi)", "recursive call", "再帰呼び出しで木をたどります。", "We traverse the tree with recursive calls."),
        ("幅優先探索", "はばゆうせんたんさく (haba yūsen tansaku)", "breadth-first search (BFS)", "幅優先探索で最短経路を求めます。", "We find the shortest path with BFS."),
        ("深さ優先探索", "ふかさゆうせんたんさく (fukasa yūsen tansaku)", "depth-first search (DFS)", "深さ優先探索で全経路を調べます。", "We examine all paths with DFS."),
        ("動的計画法", "どうてきけいかくほう (dōteki keikakuhō)", "dynamic programming", "動的計画法で最適解を求めます。", "We find the optimal solution with DP."),
    ],
)


# ===========================================================================
# 5) Errors & debugging — エラーとデバッグ
# ===========================================================================
_jp_concept(
    "jp_errors_debug",
    "Errors & Debugging — エラーとデバッグ",
    "JP: Errors & Debugging",
    "Bugs, exceptions, stack traces and the words for fixing things.",
    "When something breaks, you'll need to describe it fast: what エラー "
    "(error) came up, its 原因 (cause), and how you 修正 (fixed) it. Verbs "
    "matter here — 直す (to fix), 再現する (to reproduce), 確認する (to check).",
    _READING_NOTE,
    [
        ("エラー", "erā", "error", "エラーが発生しました。", "An error occurred."),
        ("バグ", "bagu", "bug", "このバグを直します。", "I'll fix this bug."),
        ("デバッグ", "debaggu", "debugging", "コードをデバッグします。", "We debug the code."),
        ("例外", "れいがい (reigai)", "exception", "例外がスローされました。", "An exception was thrown."),
        ("例外処理", "れいがいしょり (reigai shori)", "exception handling", "try-catchで例外処理をします。", "We handle exceptions with try-catch."),
        ("発生", "はっせい (hassei)", "occurrence", "特定の入力でエラーが発生します。", "An error occurs on certain input."),
        ("修正", "しゅうせい (shūsei)", "fix / correction", "バグを修正しました。", "I fixed the bug."),
        ("直す", "なおす (naosu)", "to fix", "この問題を直してください。", "Please fix this problem."),
        ("原因", "げんいん (gen'in)", "cause", "エラーの原因を調べます。", "We investigate the cause of the error."),
        ("動作", "どうさ (dōsa)", "behavior / operation", "プログラムは正しく動作します。", "The program works correctly."),
        ("再現", "さいげん (saigen)", "reproduce", "そのバグを再現できません。", "I can't reproduce that bug."),
        ("ヌルポインタ例外", "ヌルポインタれいがい (nuru pointa reigai)", "null pointer exception", "ヌルポインタ例外に注意してください。", "Watch out for null pointer exceptions."),
        ("スタックトレース", "sutakku torēsu", "stack trace", "スタックトレースを確認します。", "We check the stack trace."),
        ("ログ", "rogu", "log", "ログを出力してデバッグします。", "We debug by printing logs."),
        ("ブレークポイント", "burēkupointo", "breakpoint", "この行にブレークポイントを設定します。", "We set a breakpoint on this line."),
        ("例外を投げる", "れいがいをなげる (reigai o nageru)", "to throw an exception", "不正な入力なら例外を投げます。", "If the input is invalid, we throw an exception."),
        ("キャッチ", "kyacchi", "to catch", "例外をキャッチして処理します。", "We catch and handle the exception."),
        ("警告", "けいこく (keikoku)", "warning", "コンパイラが警告を出します。", "The compiler gives a warning."),
        ("想定外", "そうていがい (sōteigai)", "unexpected", "想定外の値が入りました。", "An unexpected value came in."),
        ("確認する", "かくにんする (kakunin suru)", "to check / confirm", "出力を確認します。", "We check the output."),
        ("試す", "ためす (tamesu)", "to try / test out", "もう一度試してください。", "Please try it again."),
    ],
)


# ===========================================================================
# 6) Dev tools, Git & testing — 開発ツール・Git・テスト
# ===========================================================================
_jp_concept(
    "jp_dev_tools",
    "Dev Tools, Git & Testing — 開発ツール・Git・テスト",
    "JP: Dev Tools & Git",
    "Repositories, commits, branches, builds, tests and dependencies.",
    "Daily engineering runs on these. Git verbs are katakana loanwords "
    "(コミット, プッシュ, マージ), while process words tend to be kanji "
    "(変更, 差分, 依存関係, 設定).",
    _READING_NOTE,
    [
        ("リポジトリ", "ripojitori", "repository", "リポジトリをクローンします。", "We clone the repository."),
        ("コミット", "komitto", "commit", "変更をコミットします。", "We commit the changes."),
        ("プッシュ", "pusshu", "push", "リモートにプッシュします。", "We push to the remote."),
        ("プル", "puru", "pull", "最新の変更をプルします。", "We pull the latest changes."),
        ("マージ", "māji", "merge", "ブランチをマージします。", "We merge the branch."),
        ("ブランチ", "buranchi", "branch", "新しいブランチを作ります。", "We create a new branch."),
        ("変更", "へんこう (henkō)", "change", "この変更をレビューします。", "We review this change."),
        ("差分", "さぶん (sabun)", "diff / difference", "コミット前に差分を確認します。", "We check the diff before committing."),
        ("競合", "きょうごう (kyōgō)", "(merge) conflict", "マージで競合が起きました。", "A conflict happened during the merge."),
        ("解決", "かいけつ (kaiketsu)", "resolve", "競合を解決します。", "We resolve the conflict."),
        ("ビルド", "birudo", "build", "プロジェクトをビルドします。", "We build the project."),
        ("デプロイ", "depuroi", "deploy", "サーバーにデプロイします。", "We deploy to the server."),
        ("テスト", "tesuto", "test", "テストを書いて実行します。", "We write and run the tests."),
        ("単体テスト", "たんたいテスト (tantai tesuto)", "unit test", "この関数に単体テストを追加します。", "We add a unit test for this function."),
        ("依存関係", "いぞんかんけい (izon kankei)", "dependency", "依存関係をインストールします。", "We install the dependencies."),
        ("環境", "かんきょう (kankyō)", "environment", "開発環境を用意します。", "We set up the development environment."),
        ("設定", "せってい (settei)", "configuration / settings", "設定ファイルを編集します。", "We edit the config file."),
        ("導入", "どうにゅう (dōnyū)", "adopt / introduce", "このツールを導入します。", "We adopt this tool."),
        ("更新", "こうしん (kōshin)", "update", "ライブラリを最新版に更新します。", "We update the library to the latest version."),
        ("コードレビュー", "kōdo rebyū", "code review", "コードレビューをお願いします。", "Please review my code."),
        ("バージョン管理", "バージョンかんり (bājon kanri)", "version control", "Gitでバージョン管理します。", "We manage versions with Git."),
        ("反映", "はんえい (han'ei)", "reflect / apply", "変更を本番環境に反映します。", "We apply the changes to production."),
    ],
)


# ===========================================================================
# 7) Interview & workplace — 面接と職場
# ===========================================================================
_jp_concept(
    "jp_interview",
    "Interview & Workplace — 面接と職場",
    "JP: Interview & Workplace",
    "Phrases for a technical interview and everyday engineering-team talk.",
    "Beyond the tech words, you need the conversation itself: solving a 問題 "
    "(problem), explaining your 考え方 (approach), talking about 要件 "
    "(requirements) and 締め切り (deadlines). These carry a whole interview.",
    _READING_NOTE,
    [
        ("面接", "めんせつ (mensetsu)", "interview", "明日、技術面接があります。", "I have a technical interview tomorrow."),
        ("技術面接", "ぎじゅつめんせつ (gijutsu mensetsu)", "technical interview", "技術面接でアルゴリズムを聞かれます。", "In a technical interview, they ask about algorithms."),
        ("問題", "もんだい (mondai)", "problem", "この問題を解いてください。", "Please solve this problem."),
        ("解く", "とく (toku)", "to solve", "コーディング問題を解きます。", "We solve a coding problem."),
        ("解答", "かいとう (kaitō)", "answer / solution", "解答を説明してください。", "Please explain your solution."),
        ("説明する", "せつめいする (setsumei suru)", "to explain", "まず考え方を説明します。", "First I'll explain my approach."),
        ("要件", "ようけん (yōken)", "requirement", "要件を確認します。", "We confirm the requirements."),
        ("仕様", "しよう (shiyō)", "specification", "仕様書をよく読みます。", "We read the spec carefully."),
        ("設計", "せっけい (sekkei)", "design", "システムを設計します。", "We design the system."),
        ("実装する", "じっそうする (jissō suru)", "to implement", "この機能を実装します。", "We implement this feature."),
        ("最適化", "さいてきか (saitekika)", "optimization", "コードを最適化します。", "We optimize the code."),
        ("改善", "かいぜん (kaizen)", "improvement", "パフォーマンスを改善します。", "We improve the performance."),
        ("締め切り", "しめきり (shimekiri)", "deadline", "締め切りは金曜日です。", "The deadline is Friday."),
        ("納期", "のうき (nōki)", "delivery deadline", "納期に間に合わせます。", "We'll make the delivery deadline."),
        ("会議", "かいぎ (kaigi)", "meeting", "朝に短い会議があります。", "There's a short meeting in the morning."),
        ("進捗", "しんちょく (shinchoku)", "progress", "毎日、進捗を報告します。", "I report progress every day."),
        ("質問", "しつもん (shitsumon)", "question", "一つ質問してもいいですか。", "May I ask one question?"),
        ("考え方", "かんがえかた (kangaekata)", "approach / way of thinking", "まず考え方を整理します。", "First, let me organize my approach."),
        ("担当", "たんとう (tantō)", "in charge of", "私がこの機能を担当します。", "I'm in charge of this feature."),
        ("期待", "きたい (kitai)", "expectation", "コードは期待通りに動きます。", "The code works as expected."),
        ("報告", "ほうこく (hōkoku)", "report", "結果を上司に報告します。", "I report the results to my manager."),
        ("お疲れ様です", "おつかれさまです (otsukaresama desu)", "(standard workplace greeting)", "お疲れ様です、レビューありがとうございます。", "Thanks for your work — and thanks for the review."),
    ],
)


# ===========================================================================
# TYPESCRIPT-FOCUSED SETS
# Japanese vocabulary for the TypeScript foundations, so the TS Learn track has
# a Japanese-language companion. Loanword-heavy (katakana) with kanji for the
# type-system concepts.
# ===========================================================================

# --- 8) TypeScript basics — TypeScriptの基礎 -------------------------------
_jp_concept(
    "jp_ts_basics",
    "TypeScript Basics — TypeScriptの基礎",
    "JP: TypeScript Basics",
    "TypeScript itself: type annotations, inference, compiling, variables.",
    "TypeScript adds types on top of JavaScript. These are the words for the "
    "language itself — 型注釈 (annotation), 型推論 (inference), コンパイル — and "
    "the basic building blocks you declare and initialize.",
    _READING_NOTE,
    [
        ("TypeScript", "TypeScript", "TypeScript", "TypeScriptはJavaScriptに型を追加した言語です。", "TypeScript is a language that adds types to JavaScript."),
        ("JavaScript", "JavaScript", "JavaScript", "TypeScriptは最終的にJavaScriptに変換されます。", "TypeScript is ultimately converted to JavaScript."),
        ("型注釈", "かたちゅうしゃく (kata chūshaku)", "type annotation", "変数に型注釈を付けます。", "We add a type annotation to the variable."),
        ("型推論", "かたすいろん (kata suiron)", "type inference", "型推論で型を自動的に決めます。", "Type inference determines the type automatically."),
        ("コンパイル", "konpairu", "compile", "TypeScriptをコンパイルします。", "We compile the TypeScript."),
        ("トランスパイル", "toransupairu", "transpile", "tscがTypeScriptをJavaScriptにトランスパイルします。", "tsc transpiles TypeScript to JavaScript."),
        ("静的型付け", "せいてきかたづけ (seiteki katazuke)", "static typing", "TypeScriptは静的型付けの言語です。", "TypeScript is a statically typed language."),
        ("型安全", "かたあんぜん (kata anzen)", "type safety", "型安全なコードを書きます。", "We write type-safe code."),
        ("変数", "へんすう (hensū)", "variable", "letで変数を宣言します。", "We declare a variable with `let`."),
        ("定数", "ていすう (teisū)", "constant", "constで定数を宣言します。", "We declare a constant with `const`."),
        ("再代入", "さいだいにゅう (sai dainyū)", "reassignment", "constは再代入できません。", "A `const` cannot be reassigned."),
        ("スコープ", "sukōpu", "scope", "変数のスコープに注意します。", "We pay attention to the variable's scope."),
        ("ブロックスコープ", "burokku sukōpu", "block scope", "letはブロックスコープを持ちます。", "`let` has block scope."),
        ("宣言", "せんげん (sengen)", "declaration", "型と一緒に変数を宣言します。", "We declare the variable together with its type."),
        ("初期化", "しょきか (shokika)", "initialization", "変数を初期化します。", "We initialize the variable."),
        ("プリミティブ型", "プリミティブがた (purimitibu gata)", "primitive type", "numberはプリミティブ型です。", "`number` is a primitive type."),
        ("数値", "すうち (sūchi)", "number", "numberは数値を表します。", "`number` represents a numeric value."),
        ("文字列", "もじれつ (mojiretsu)", "string", "stringは文字列を表します。", "`string` represents text."),
        ("真偽値", "しんぎち (shingichi)", "boolean", "booleanはtrueかfalseです。", "A boolean is true or false."),
        ("テンプレートリテラル", "tenpurēto riteraru", "template literal", "テンプレートリテラルで文字列を組み立てます。", "We build strings with template literals."),
        ("実行環境", "じっこうかんきょう (jikkō kankyō)", "runtime environment", "Node.jsはJavaScriptの実行環境です。", "Node.js is a JavaScript runtime."),
        ("開発環境", "かいはつかんきょう (kaihatsu kankyō)", "development environment", "開発環境を整えます。", "We set up the development environment."),
        ("構文", "こうぶん (kōbun)", "syntax", "TypeScriptの構文を学びます。", "We learn TypeScript's syntax."),
        ("拡張子", "かくちょうし (kakuchōshi)", "file extension", "TypeScriptの拡張子は.tsです。", "The TypeScript extension is `.ts`."),
    ],
)

# --- 9) Types & interfaces — 型とインターフェース --------------------------
_jp_concept(
    "jp_ts_types",
    "Types & Interfaces — 型とインターフェース",
    "JP: TS Types",
    "The type system: interfaces, unions, generics, guards, assertions.",
    "The heart of TypeScript. You describe the shape of data with インターフェース "
    "and 型エイリアス, combine types with ユニオン型 / 交差型, and make them reusable "
    "with ジェネリクス. This is where interviews about TypeScript live.",
    _READING_NOTE,
    [
        ("型", "かた (kata)", "type", "すべての値に型があります。", "Every value has a type."),
        ("型エイリアス", "かたエイリアス (kata eiriasu)", "type alias", "typeで型エイリアスを作ります。", "We make a type alias with `type`."),
        ("インターフェース", "intāfēsu", "interface", "インターフェースでオブジェクトの形を定義します。", "We define an object's shape with an interface."),
        ("ユニオン型", "ユニオンがた (yunion gata)", "union type", "ユニオン型で複数の型を許可します。", "A union type allows several types."),
        ("交差型", "こうさがた (kōsa gata)", "intersection type", "交差型で型を組み合わせます。", "We combine types with an intersection type."),
        ("ジェネリクス", "jenerikusu", "generics", "ジェネリクスで再利用できる型を書きます。", "We write reusable types with generics."),
        ("型引数", "かたひきすう (kata hikisū)", "type parameter", "関数に型引数を渡します。", "We pass a type parameter to the function."),
        ("型ガード", "かたガード (kata gādo)", "type guard", "型ガードで型を絞り込みます。", "We narrow the type with a type guard."),
        ("型アサーション", "かたアサーション (kata asāshon)", "type assertion", "asで型アサーションを行います。", "We do a type assertion with `as`."),
        ("リテラル型", "リテラルがた (riteraru gata)", "literal type", "リテラル型で特定の値だけを許可します。", "A literal type allows only specific values."),
        ("タプル", "tapuru", "tuple", "タプルは長さと型が固定です。", "A tuple has a fixed length and element types."),
        ("列挙型", "れっきょがた (rekkyo gata)", "enum", "列挙型で定数をまとめます。", "We group constants with an enum."),
        ("読み取り専用", "よみとりせんよう (yomitori sen'yō)", "readonly", "読み取り専用のプロパティは変更できません。", "A readonly property can't be changed."),
        ("任意", "にんい (nin'i)", "optional", "任意のプロパティは省略できます。", "An optional property can be omitted."),
        ("null許容", "ヌルきょよう (nuru kyoyō)", "nullable", "null許容の値はnullになり得ます。", "A nullable value may be null."),
        ("any型", "エニーがた (enī gata)", "the any type", "any型は型チェックを無効にします。", "The `any` type disables type checking."),
        ("unknown型", "アンノウンがた (announ gata)", "the unknown type", "unknown型は使う前に型を確認します。", "The `unknown` type must be checked before use."),
        ("プロパティ", "puropati", "property", "オブジェクトのプロパティにアクセスします。", "We access the object's property."),
        ("型定義", "かたていぎ (kata teigi)", "type definition", "ライブラリの型定義を読み込みます。", "We load the library's type definitions."),
        ("構造的型付け", "こうぞうてきかたづけ (kōzōteki katazuke)", "structural typing", "TypeScriptは構造的型付けを採用しています。", "TypeScript uses structural typing."),
        ("網羅性チェック", "もうらせいチェック (mōrasei chekku)", "exhaustiveness check", "switch文で網羅性チェックをします。", "We do an exhaustiveness check in a switch."),
        ("継承", "けいしょう (keishō)", "inheritance (extends)", "インターフェースは他のインターフェースを継承できます。", "An interface can extend another interface."),
        ("型変換", "かたへんかん (kata henkan)", "type conversion", "文字列を数値に型変換します。", "We convert the string to a number."),
        ("省略可能", "しょうりゃくかのう (shōryaku kanō)", "optional / omittable", "この引数は省略可能です。", "This argument is optional."),
        ("定義", "ていぎ (teigi)", "definition", "型の定義を確認します。", "We check the type definition."),
        ("制約", "せいやく (seiyaku)", "constraint", "ジェネリクスに制約を付けます。", "We add a constraint to the generic."),
    ],
)

# --- 10) Functions & async — 関数と非同期 ----------------------------------
_jp_concept(
    "jp_ts_functions",
    "Functions & Async — 関数と非同期",
    "JP: TS Functions",
    "Functions, arrow functions, callbacks, Promises and async/await.",
    "Functions and asynchronous code are where a lot of TypeScript work happens. "
    "Learn 非同期 (async), プロミス (Promise), 待機 (await), and the words for "
    "arguments, return values and callbacks.",
    _READING_NOTE,
    [
        ("関数", "かんすう (kansū)", "function", "関数を定義します。", "We define a function."),
        ("アロー関数", "アローかんすう (arō kansū)", "arrow function", "アロー関数で短く書けます。", "We can write it shorter with an arrow function."),
        ("引数", "ひきすう (hikisū)", "argument", "関数に引数を渡します。", "We pass an argument to the function."),
        ("仮引数", "かりひきすう (kari hikisū)", "parameter", "仮引数に型を付けます。", "We type the parameter."),
        ("戻り値", "もどりち (modorichi)", "return value", "関数の戻り値の型を指定します。", "We specify the function's return type."),
        ("コールバック", "kōrubakku", "callback", "関数にコールバックを渡します。", "We pass a callback to the function."),
        ("高階関数", "こうかいかんすう (kōkai kansū)", "higher-order function", "mapは高階関数です。", "`map` is a higher-order function."),
        ("無名関数", "むめいかんすう (mumei kansū)", "anonymous function", "無名関数をその場で渡します。", "We pass an anonymous function inline."),
        ("非同期", "ひどうき (hidōki)", "asynchronous", "非同期でデータを取得します。", "We fetch the data asynchronously."),
        ("同期", "どうき (dōki)", "synchronous", "この処理は同期的に実行されます。", "This runs synchronously."),
        ("プロミス", "puromisu", "Promise", "プロミスは非同期の結果を表します。", "A Promise represents an async result."),
        ("待機", "たいき (taiki)", "await / waiting", "awaitで結果を待機します。", "We await the result with `await`."),
        ("解決", "かいけつ (kaiketsu)", "resolve", "プロミスが値で解決します。", "The promise resolves with a value."),
        ("拒否", "きょひ (kyohi)", "reject", "エラーでプロミスが拒否されます。", "The promise is rejected with an error."),
        ("副作用", "ふくさよう (fukusayō)", "side effect", "この関数は副作用がありません。", "This function has no side effects."),
        ("純粋関数", "じゅんすいかんすう (junsui kansū)", "pure function", "純粋関数はテストしやすいです。", "Pure functions are easy to test."),
        ("デフォルト引数", "デフォルトひきすう (deforuto hikisū)", "default parameter", "デフォルト引数を設定します。", "We set a default parameter."),
        ("残余引数", "ざんよひきすう (zan'yo hikisū)", "rest parameter", "残余引数で複数の値を受け取ります。", "We receive multiple values with a rest parameter."),
        ("クロージャ", "kurōja", "closure", "クロージャは外側の変数を覚えています。", "A closure remembers outer variables."),
        ("再帰", "さいき (saiki)", "recursion", "この関数は再帰を使います。", "This function uses recursion."),
        ("並行処理", "へいこうしょり (heikō shori)", "concurrency", "並行処理で複数の要求を扱います。", "We handle multiple requests with concurrency."),
        ("例外処理", "れいがいしょり (reigai shori)", "exception handling", "try-catchで例外処理をします。", "We handle exceptions with try-catch."),
        ("呼び出し", "よびだし (yobidashi)", "call / invocation", "関数の呼び出しを確認します。", "We check the function call."),
        ("遅延評価", "ちえんひょうか (chien hyōka)", "lazy evaluation", "遅延評価で計算を後回しにします。", "Lazy evaluation defers the computation."),
    ],
)

# --- 11) Objects, modules & tooling — オブジェクト・モジュール・ツール ------
_jp_concept(
    "jp_ts_objects",
    "Objects, Modules & Tooling — オブジェクト・モジュール・ツール",
    "JP: TS Objects & Tooling",
    "Objects, destructuring, immutability, modules, packages and build tools.",
    "Structuring and moving data around: オブジェクト and プロパティ, 分割代入 "
    "(destructuring), スプレッド構文 (spread), and how code is organized into "
    "モジュール and packages, then built with a バンドラー.",
    _READING_NOTE,
    [
        ("オブジェクト", "obujekuto", "object", "オブジェクトにデータをまとめます。", "We group data in an object."),
        ("プロパティ", "puropati", "property", "オブジェクトにプロパティを追加します。", "We add a property to the object."),
        ("キー", "kī", "key", "オブジェクトのキーで値を取り出します。", "We get the value by the object's key."),
        ("値", "あたい (atai)", "value", "キーに対応する値を更新します。", "We update the value for the key."),
        ("配列", "はいれつ (hairetsu)", "array", "配列に要素を追加します。", "We add an element to the array."),
        ("分割代入", "ぶんかつだいにゅう (bunkatsu dainyū)", "destructuring", "分割代入でプロパティを取り出します。", "We extract properties with destructuring."),
        ("スプレッド構文", "スプレッドこうぶん (supureddo kōbun)", "spread syntax", "スプレッド構文で配列を複製します。", "We copy an array with spread syntax."),
        ("不変", "ふへん (fuhen)", "immutable", "不変のデータは変更しません。", "We don't change immutable data."),
        ("可変", "かへん (kahen)", "mutable", "可変のオブジェクトは変更できます。", "A mutable object can be changed."),
        ("参照", "さんしょう (sanshō)", "reference", "オブジェクトは参照で渡されます。", "Objects are passed by reference."),
        ("複製", "ふくせい (fukusei)", "copy / clone", "オブジェクトを複製します。", "We clone the object."),
        ("モジュール", "mojūru", "module", "コードをモジュールに分けます。", "We split code into modules."),
        ("インポート", "inpōto", "import", "別のファイルから関数をインポートします。", "We import a function from another file."),
        ("エクスポート", "ekusupōto", "export", "関数をエクスポートします。", "We export the function."),
        ("名前空間", "なまえくうかん (namae kūkan)", "namespace", "名前空間で名前の衝突を防ぎます。", "A namespace prevents name collisions."),
        ("パッケージ", "pakkēji", "package", "npmでパッケージをインストールします。", "We install a package with npm."),
        ("依存関係", "いぞんかんけい (izon kankei)", "dependency", "プロジェクトの依存関係を管理します。", "We manage the project's dependencies."),
        ("バンドラー", "bandorā", "bundler", "バンドラーがファイルを一つにまとめます。", "A bundler combines the files into one."),
        ("ビルド", "birudo", "build", "プロジェクトをビルドします。", "We build the project."),
        ("反復処理", "はんぷくしょり (hanpuku shori)", "iteration", "配列を反復処理します。", "We iterate over the array."),
        ("マップ", "mappu", "Map", "マップはキーと値の対を保持します。", "A Map holds key-value pairs."),
        ("セット", "setto", "Set", "セットは重複を許しません。", "A Set does not allow duplicates."),
        ("JSON形式", "JSONけいしき (JSON keishiki)", "JSON format", "データをJSON形式で保存します。", "We save the data in JSON format."),
        ("直列化", "ちょくれつか (chokuretsuka)", "serialization", "オブジェクトを直列化します。", "We serialize the object."),
        ("検証", "けんしょう (kenshō)", "validation", "入力データを検証します。", "We validate the input data."),
        ("設定ファイル", "せっていファイル (settei fairu)", "config file", "tsconfigは設定ファイルです。", "`tsconfig` is a config file."),
    ],
)

# --- 12) Web & frontend — Webとフロントエンド ------------------------------
_jp_concept(
    "jp_web_frontend",
    "Web & Frontend — Webとフロントエンド",
    "JP: Web & Frontend",
    "Where TypeScript runs: components, state, requests, servers and auth.",
    "The surrounding world TypeScript is written for: フロントエンド / バックエンド, "
    "コンポーネント and 状態 (state), and the request/response cycle with a server "
    "and database.",
    _READING_NOTE,
    [
        ("フロントエンド", "furonto endo", "frontend", "フロントエンドの開発を担当します。", "I'm in charge of frontend development."),
        ("バックエンド", "bakku endo", "backend", "バックエンドとAPIでやり取りします。", "We communicate with the backend via an API."),
        ("コンポーネント", "konpōnento", "component", "UIをコンポーネントに分けます。", "We split the UI into components."),
        ("状態", "じょうたい (jōtai)", "state", "コンポーネントの状態を管理します。", "We manage the component's state."),
        ("描画", "びょうが (byōga)", "render", "画面を描画します。", "We render the screen."),
        ("再描画", "さいびょうが (sai byōga)", "re-render", "状態が変わると再描画されます。", "It re-renders when the state changes."),
        ("イベント", "ibento", "event", "クリックイベントを処理します。", "We handle the click event."),
        ("要求", "ようきゅう (yōkyū)", "request", "サーバーに要求を送ります。", "We send a request to the server."),
        ("応答", "おうとう (ōtō)", "response", "サーバーからの応答を待ちます。", "We wait for the server's response."),
        ("取得", "しゅとく (shutoku)", "fetch / get", "APIからデータを取得します。", "We fetch data from the API."),
        ("更新", "こうしん (kōshin)", "update", "画面を最新の状態に更新します。", "We update the screen to the latest state."),
        ("読み込み", "よみこみ (yomikomi)", "loading", "データの読み込み中です。", "The data is loading."),
        ("表示", "ひょうじ (hyōji)", "display", "結果を画面に表示します。", "We display the result on the screen."),
        ("入力欄", "にゅうりょくらん (nyūryoku ran)", "input field", "入力欄に名前を入れます。", "We type a name into the input field."),
        ("ボタン", "botan", "button", "ボタンを押すと送信されます。", "Pressing the button submits it."),
        ("画面", "がめん (gamen)", "screen", "画面のレイアウトを整えます。", "We arrange the screen layout."),
        ("サーバー", "sābā", "server", "サーバーを起動します。", "We start the server."),
        ("データベース", "dētabēsu", "database", "データベースに保存します。", "We save it to the database."),
        ("認証", "にんしょう (ninshō)", "authentication", "ユーザー認証を実装します。", "We implement user authentication."),
        ("権限", "けんげん (kengen)", "permission", "管理者の権限が必要です。", "Admin permission is required."),
        ("通信", "つうしん (tsūshin)", "communication", "サーバーと通信します。", "We communicate with the server."),
        ("非同期通信", "ひどうきつうしん (hidōki tsūshin)", "async communication", "非同期通信でページを更新します。", "We update the page with async communication."),
        ("再利用", "さいりよう (sairiyō)", "reuse", "コンポーネントを再利用します。", "We reuse the component."),
        ("端末", "たんまつ (tanmatsu)", "terminal", "端末でコマンドを実行します。", "We run commands in the terminal."),
    ],
)
