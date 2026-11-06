import { authoredChoice } from "./builders";
import type { StudyLesson, StudyQuestion } from "./schema";

export const READING_DRILL_LESSONS: StudyLesson[] = [
  { id: "reading-choice", section: "kanji", title: "Recognize the full reading", format: "Reading choices",
    takeaway: "Choose the reading of the whole underlined word, including every vowel and small kana.",
    steps: ["Recall the reading before looking at the options.", "Compare long vowels, small kana and voiced sounds.", "Read the chosen word back in the sentence."],
    trap: "A reading that sounds almost right may lose a long vowel or use a full-sized kana.",
    examples: [{ japanese: "出張 → しゅっちょう", english: "A business trip: retain both the small っ and long vowel." }] },
  { id: "compound-sound-changes", section: "kanji", title: "Hear the sound change inside a compound", format: "Compound sound changes",
    takeaway: "Learn the reading of the complete compound instead of concatenating isolated character readings.",
    steps: ["Identify both parts of the word.", "Check whether a sound contracts into っ or becomes voiced.", "Recall another word with the same sound pattern."],
    trap: "Sound changes are not universal rules. The accepted reading belongs to the individual word.",
    examples: [{ japanese: "発表（はっぴょう）・手紙（てがみ）", english: "Announcement / letter: contraction and voicing change the component readings." }] },
  { id: "context-readings", section: "kanji", title: "Use meaning to choose a homograph's reading", format: "Readings in context",
    takeaway: "The same written form can have a different reading when its meaning changes.",
    steps: ["Read the complete context before typing.", "Identify which sense of the written word is intended.", "Recall the reading associated with that sense."],
    trap: "A valid dictionary reading can still be wrong for this sentence.",
    examples: [{ japanese: "生物を冷蔵する（なまもの）／生物を研究する（せいぶつ）", english: "Refrigerate perishables / research living organisms." }] },
];

// Explicit alternatives are distractors, never machine-derived dictionary readings.
type ReadingRow = readonly [id: string, word: string, reading: string, sentence: string,
  meaning: string, translation: string, distractors: readonly [string, string, string], note: string, alternatives?: readonly string[]];
const compounds: ReadingRow[] = [
  ["announcement", "発表", "はっぴょう", "調査の結果を発表する。", "announcement; presentation", "Present the results of the survey.", ["はつひょう", "はっびょう", "はぴょう"], "発 contracts to はっ and 表 is ぴょう in this compound."],
  ["development", "発達", "はったつ", "子どもの言葉が発達する。", "development", "The child's language develops.", ["はつたつ", "はっだつ", "はたつ"], "発 becomes はっ before 達; retain the small っ."],
  ["departure", "出発", "しゅっぱつ", "電車は九時に出発する。", "departure", "The train departs at nine.", ["しゅつはつ", "しゅっばつ", "しゅぱつ"], "出発 combines しゅっ and ぱつ, rather than しゅつ and はつ."],
  ["failure", "失敗", "しっぱい", "失敗から多くを学んだ。", "failure", "I learned a lot from failure.", ["しつはい", "しっばい", "しぱい"], "失 contracts to しっ and 敗 begins with ぱ in 失敗."],
  ["school", "学校", "がっこう", "学校まで歩いて通う。", "school", "Walk to school.", ["がくこう", "がっこ", "かっこう"], "学 contracts to がっ; 校 retains the long こう."],
  ["term", "学期", "がっき", "新しい学期が始まる。", "school term", "A new school term begins.", ["がくき", "がき", "がっぎ"], "学 contracts to がっ before 期, producing がっき."],
  ["one-volume", "一冊", "いっさつ", "図書館で本を一冊借りた。", "one book; one volume", "I borrowed one book from the library.", ["いちさつ", "いさつ", "いっざつ"], "一 becomes いっ with the counter 冊."],
  ["one-cup", "一杯", "いっぱい", "水を一杯飲んだ。", "one cup; one glass", "I drank a glass of water.", ["いちはい", "いっはい", "いっばい"], "一杯 is いっぱい: the contracted っ is followed by ぱ."],
  ["letter", "手紙", "てがみ", "祖母に手紙を書いた。", "letter", "I wrote a letter to my grandmother.", ["てかみ", "しゅがみ", "てがめ"], "紙 is voiced to がみ in 手紙; the whole word is てがみ."],
  ["fireworks", "花火", "はなび", "夏祭りで花火を見た。", "fireworks", "I watched fireworks at the summer festival.", ["はなひ", "かび", "はなぴ"], "火 is voiced to び after 花 in this word."],
];
const contextual: ReadingRow[] = [
  ["organisms", "生物", "せいぶつ", "大学で海の生物を研究している。", "living organisms", "I research marine organisms at university.", ["なまもの", "しょうぶつ", "せいもの"], "Researching organisms calls for せいぶつ; なまもの refers to raw or perishable food."],
  ["perishables", "生物", "なまもの", "生物は傷みやすいので、すぐ冷蔵庫に入れてください。", "raw or perishable food", "Perishables spoil easily, so put them in the refrigerator immediately.", ["せいぶつ", "しょうぶつ", "なまぶつ"], "Refrigeration and spoilage identify food, so the reading is なまもの."],
  ["popularity", "人気", "にんき", "この歌手は若者に人気がある。", "popularity", "This singer is popular with young people.", ["ひとけ", "じんき", "にんけ"], "人気がある describes popularity here and is read にんき."],
  ["human-presence", "人気", "ひとけ", "深夜の駅には人気がなかった。", "sign of people; human presence", "There was no sign of anyone at the station late at night.", ["にんき", "じんき", "ひとき"], "The deserted late-night setting identifies ひとけ, the presence of people."],
  ["skilled", "上手", "じょうず", "妹は絵を描くのが上手だ。", "skillful; good at", "My younger sister is good at drawing.", ["かみて", "うわて", "じょうしゅ"], "絵を描くのが上手 describes a skill and is read じょうず."],
  ["stage-side", "上手", "かみて", "舞台の上手は、客席から見て右側だ。", "stage left; the audience's right", "Stage left is on the right as seen from the audience.", ["じょうず", "うえて", "じょうて"], "In theatre terminology, 上手 is かみて, the audience's right side."],
  ["whole-day", "一日", "いちにち", "昨日は一日中、家で勉強した。", "one day; a whole day", "Yesterday I studied at home all day.", ["ついたち", "いちじつ", "ひとにち"], "一日中 is いちにちじゅう and means throughout the day; ついたち names a date."],
  ["first-day", "一日", "ついたち", "来月の一日は月曜日です。", "the first day of a month", "The first of next month is a Monday.", ["いちにち", "ひとひ", "いっにち"], "A calendar date on the first of a month is read ついたち."],
  ["economic-market", "市場", "しじょう", "海外の市場に新しい製品を売り出す。", "market in an economic sense", "Launch a new product in overseas markets.", ["いちば", "しば", "いちじょう"], "An overseas commercial market for a product is 市場（しじょう）."],
  ["marketplace", "市場", "いちば", "朝早く市場へ行って、新鮮な魚を買った。", "physical marketplace", "I went to the market early in the morning and bought fresh fish.", ["いちじょう", "しば", "いちま"], "A physical marketplace is commonly read いちば. しじょう can also describe a marketplace and is accepted in this sentence.", ["しじょう"]],
  ["sorting", "分別", "ぶんべつ", "ごみを種類ごとに分別する。", "sorting; separation", "Sort rubbish by type.", ["ふんべつ", "ぶんべち", "ふんべち"], "Sorting items into categories is 分別（ぶんべつ）."],
  ["good-sense", "分別", "ふんべつ", "大人としての分別を持って行動してほしい。", "good sense; discretion", "I want you to act with the good sense expected of an adult.", ["ぶんべつ", "ふんべち", "ぶんべち"], "Judgment or discretion is 分別（ふんべつ）, rather than sorting（ぶんべつ）."],
];
const additional: ReadingRow[] = [
  ["business-trip", "出張", "しゅっちょう", "来週、大阪へ出張する。", "business trip", "I will go on a business trip to Osaka next week.", ["しゅつちょう", "しゅっちょ", "しゅうちょう"], "出張 contains a small っ and the long vowel ちょう."],
  ["situation", "状況", "じょうきょう", "現在の状況を説明してください。", "situation", "Please explain the current situation.", ["じょきょう", "じょうきょ", "しょうきょう"], "Both じょう and きょう have long vowels; the first sound is voiced."],
  ["cooperation", "協力", "きょうりょく", "皆さんの協力に感謝します。", "cooperation", "Thank you all for your cooperation.", ["きょりょく", "きょうりょうく", "きゅうりょく"], "協 is きょう and 力 is りょく, without a long vowel after りょ."],
  ["employment", "就職", "しゅうしょく", "卒業後は地元で就職したい。", "finding employment", "After graduation I want to find a job in my hometown.", ["しゅしょく", "しゅうしょうく", "じゅうしょく"], "就 has the long reading しゅう; 職 is the short しょく."],
  ["efficiency", "能率", "のうりつ", "休憩を取ると仕事の能率が上がる。", "efficiency", "Taking a break improves work efficiency.", ["のりつ", "のうりっつ", "のうりち"], "能率 is のうりつ, retaining the long のう and full-sized つ."],
  ["procedure", "手続き", "てつづき", "入学の手続きを済ませた。", "procedure; formalities", "I completed the enrolment formalities.", ["てつずき", "てっづき", "てつつき"], "続き retains づ in 手続き; do not substitute ず."],
  ["demand", "需要", "じゅよう", "夏は冷たい飲み物の需要が増える。", "demand", "Demand for cold drinks rises in summer.", ["じゅうよう", "じゅよ", "しゅよう"], "需要 is じゅよう; 重要 is the different word じゅうよう."],
  ["important", "重要", "じゅうよう", "これは将来に関わる重要な問題だ。", "important", "This is an important issue affecting the future.", ["じゅよう", "じゅうよ", "しゅうよう"], "重要 keeps long vowels in both じゅう and よう; compare 需要（じゅよう）."],
];

function typedRows(rows: ReadingRow[], lessonId: string): StudyQuestion[] {
  return rows.map(([id, word, reading, prompt, meaning, translation, , explanation, alternatives = []]) => ({
    id: `${lessonId}-${id}`, lessonId, kind: "typed", word, answers: [reading, ...alternatives], prompt, focus: word,
    meaning, translation, explanation, hint: "Use the meaning of the whole sentence; check long vowels and small kana.",
    targetSeconds: 25, tags: [word, lessonId],
  }));
}
export const READING_DRILL_QUESTIONS: StudyQuestion[] = [
  ...typedRows(compounds, "compound-sound-changes"), ...typedRows(contextual, "context-readings"),
  ...typedRows(additional, "compound-readings"),
  ...[...compounds, ...contextual, ...additional].map(([id, word, reading, sentence, , translation, wrong, note]) => authoredChoice(
    `reading-choice-${id}`, "reading-choice", `${sentence}\n下線の言葉の読み方として最も適切なものは？`,
    [[reading, note],
      [wrong[0], `${wrong[0]} is not the reading of ${word} in this sentence. ${note}`],
      [wrong[1], `${wrong[1]} is not the reading of ${word} in this sentence. ${note}`],
      [wrong[2], `${wrong[2]} is not the reading of ${word} in this sentence. ${note}`]],
    note, translation, { focus: word, tags: [word, "reading-choice"], targetSeconds: 25 })),
];
