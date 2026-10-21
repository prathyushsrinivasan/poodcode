"""Build the offline kanji vocabulary bank from pinned, locally downloaded CSVs.

Usage: python tools/build_kanji_words.py --source-dir DIR --dictionary FILE
Source/license/provenance are documented in src/data/kanjiWords/README.md.
Network access is deliberately separate from this reproducible content build.
"""
import argparse
import csv
import hashlib
import html
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/kanjiWords"
KANJI = "生学会人心意力行動事物合定成化性表取交分"
MODERN = {
    "知合い": "知り合い", "付合う": "付き合う", "打合せ": "打ち合わせ", "組合せ": "組み合わせ",
    "話合い": "話し合い", "待合室": "待合室", "売行き": "売れ行き", "受取": "受け取り",
    "書取": "書き取り", "取扱": "取り扱い", "取締り": "取り締まり", "引取る": "引き取る",
    "引分け": "引き分け", "落し物": "落とし物", "人差指": "人差し指", "交す": "交わす",
    "生温い": "生ぬるい", "生き甲斐": "生きがい", "塵取り": "ちり取り",
}
# A single written prompt must specify its sense when common homographs differ.
CUES = {
    ("生", "せい"): "生を受ける。", ("生", "なま"): "魚を生で食べる。",
    ("生物", "せいぶつ"): "地球には多くの生物がいる。", ("生地", "きじ"): "パンの生地をこねる。",
    ("人気", "にんき"): "若者に人気がある歌手。", ("人気", "ひとけ"): "夜の公園には人気がない。",
    ("人事", "じんじ"): "人事の担当者と面接する。", ("心中", "しんじゅう"): "二人の心中を題材にした芝居。",
    ("分", "ぶ"): "利益の一割五分を受け取る。", ("分", "ぶん"): "自分の分を受け取る。",
    ("表", "おもて"): "紙の表に名前を書く。", ("表", "ひょう"): "結果を表にまとめる。",
    ("万人", "ばんにん"): "万人に愛される作品。", ("何分", "なにぶん"): "何分、初めての経験ですので。",
    ("大分", "だいぶ"): "病気が大分よくなった。", ("生まれ", "うまれ"): "彼は東京の生まれだ。",
    ("工夫", "くふう"): "使いやすくなるように工夫する。", ("物事", "ものごと"): "物事をよく考える。",
    ("行き", "いき"): "行きは電車、帰りはバスだった。", ("行き", "ゆき"): "行きは電車、帰りはバスだった。",
}
ALTERNATIVES = {("行き", "いき"): ["ゆき"], ("行き", "ゆき"): ["いき"],
    ("出生", "しゅっせい"): ["しゅっしょう"], ("出生", "しゅっしょう"): ["しゅっせい"]}


def kana(text):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in unicodedata.normalize("NFKC", text)).strip()


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(unicodedata.normalize("NFKC", text))).strip(" ,;")


def tokens(text):
    # Conservative rejection of overlapping meanings, including morphological variants.
    stop = {"a", "an", "the", "to", "of", "for", "in", "on", "with", "and", "or", "one", "s", "e", "g", "be", "someone", "something"}
    return {word[:5] for word in re.findall(r"[a-z]+", text.lower()) if word not in stop and len(word) > 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=pathlib.Path)
    parser.add_argument("--dictionary", required=True, type=pathlib.Path)
    args = parser.parse_args()
    editorial = json.loads((DATA / "editorial.json").read_text(encoding="utf-8"))
    dictionary = json.loads(args.dictionary.read_text(encoding="utf-8"))
    lookup = {}
    for entry in dictionary["words"]:
        for spelling in entry["kanji"]:
            lookup.setdefault(spelling["text"], []).append(entry)
    words = {}
    skipped = []

    def add(written, reading, level, meaning, source, aliases=None):
        original = written
        written = MODERN.get(written, written)
        reading = kana(reading)
        if written == "行き" and reading == "ゆき":
            reading = "いき"
        if written == "出生" and reading == "しゅっしょう":
            reading = "しゅっせい"
        if not any(c in written for c in KANJI) or not re.fullmatch(r"[\u3041-\u3096ー]+", reading):
            skipped.append([original, reading, "not a whole hiragana-reading word"])
            return
        if re.search(r"[~〜～()（）,、]", written):
            skipped.append([original, reading, "phrase, annotation or productive affix"])
            return
        key = written + "|" + reading
        override = editorial["overrides"].get(key, {})
        if override.get("exclude"):
            skipped.append([original, reading, override["exclude"]])
            return
        entry_matches = []
        for entry in lookup.get(written, []) + lookup.get(original, []):
            if any(kana(r["text"]) == reading and ("*" in r["appliesToKanji"] or written in r["appliesToKanji"] or original in r["appliesToKanji"]) for r in entry["kana"]):
                entry_matches.append(entry)
        if not entry_matches:
            skipped.append([original, reading, "no matching JMdict spelling/reading; needs editorial review"])
            return
        for alternative in override.get("accepted", ALTERNATIVES.get((written, reading), [])):
            assert any(any(kana(r["text"]) == alternative for r in entry["kana"]) for entry in entry_matches), (written, alternative)
        meanings = override.get("meanings", [clean(meaning)])
        if key in words:
            words[key]["levels"] = sorted(set(words[key]["levels"] + [level]), reverse=True)
            return
        ident = hashlib.sha256(key.encode()).hexdigest()[:12]
        # Dictionary text is used only to rule out potentially synonymous distractors.
        dictionary_glosses = " ".join(g["text"] for entry in entry_matches for sense in entry["sense"] for g in sense["gloss"])
        words[key] = {"id": "kw-" + ident, "written": written, "readings": [reading] + override.get("accepted", ALTERNATIVES.get((written, reading), [])),
            "levels": [level], "meanings": meanings, "cue": override.get("cue", CUES.get((written, reading), "")),
            "note": override.get("note", ""), "source": source, "dictionaryIds": sorted({entry["id"] for entry in entry_matches}),
            "_exclusions": tokens(dictionary_glosses + " ".join(meanings)), "aliases": aliases or ([original] if original != written else [])}

    # Apply editorial definitions before loading reference rows, so a supplement
    # that already exists in the reference still gets its reviewed wording.
    for written, reading, level, meanings, note in editorial["supplements"]:
        editorial["overrides"].setdefault(written + "|" + reading, {}).update({"meanings": meanings, "note": note})
    for number in [3, 2, 1]:
        for row in csv.DictReader((args.source_dir / f"n{number}.csv").open(encoding="utf-8-sig")):
            if any(c in row["expression"] for c in KANJI):
                add(row["expression"], row["reading"], f"N{number}", row["meaning"], "reference")
    for written, reading, level, meanings, note in editorial["supplements"]:
        add(written, reading, level, "; ".join(meanings), "editorial")
    result = []
    for key, word in words.items():
        override = editorial["overrides"].get(key, {})
        pool = sorted(editorial["distractors"], key=lambda entry: hashlib.sha256((word["id"] + entry[0]).encode()).digest())
        if all(meaning.startswith("to ") for meaning in word["meanings"]):
            pool = [entry for entry in pool if entry[0].startswith("to ")]
        else:
            pool = [entry for entry in pool if not entry[0].startswith("to ")]
        negatives = []
        for label, spelling, reading in pool:
            if spelling in word["written"] or word["written"] in spelling or any(c in spelling for c in word["written"] if c in KANJI):
                continue
            if word["_exclusions"] & tokens(label) or label in override.get("avoid", []):
                continue
            negatives.append({"text": label, "correct": False, "explanation": f"This means {spelling} ({reading}); it is not a study meaning of {word['written']}."})
            if len(negatives) == 3:
                break
        assert len(negatives) == 3, key
        word["options"] = [{"text": meaning, "correct": True, "explanation": f"One study meaning of {word['written']} ({word['readings'][0]}) is {meaning}."} for meaning in word["meanings"]] + negatives
        del word["_exclusions"]
        result.append(word)
    result.sort(key=lambda word: (int(word["levels"][0][-1]) * -1, word["readings"][0], word["written"]))
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "words.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"reviewed": "2026-10-21", "sourceRevision": "1ad66734417aca9dbcca6b2d5ee440cb13ab3ba0",
        "dictionaryDate": dictionary["dictDate"], "words": len(result),
        "sourceSha256": {f"n{n}.csv": hashlib.sha256((args.source_dir / f"n{n}.csv").read_bytes()).hexdigest() for n in [1, 2, 3]},
        "excluded": skipped}
    (DATA / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(result)} words; {sum(len(w['meanings']) > 1 for w in result)} multiple-meaning items; {len(skipped)} excluded rows.")
    for character in KANJI:
        print(character.encode("unicode_escape").decode(), sum(character in word["written"] for word in result))


if __name__ == "__main__":
    main()
