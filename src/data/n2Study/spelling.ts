import { authoredChoice, type ExplainedOption } from "./builders";
import type { StudyLesson } from "./schema";

export const SPELLING_LESSONS: StudyLesson[] = [
  { id: "kanji-spelling", section: "kanji", title: "Choose the written word from its reading", format: "Kanji spelling",
    takeaway: "Use the sentence to recall the whole word, then check every character.",
    steps: ["Read the underlined kana and its sentence.", "Recall the written word before inspecting the options.", "Check every character, including similar shapes."],
    trap: "Recognizing one character is not enough: the entire written word must fit.",
    examples: [{ japanese: "会議の内容をきろくする。→ 記録", english: "Record the contents of the meeting." }] },
  { id: "visual-kanji", section: "kanji", title: "Notice the small differences between characters", format: "Similar kanji",
    takeaway: "A small stroke or radical can change the word completely.",
    steps: ["Identify the word required by the sentence.", "Compare the differing characters rather than the shared ones.", "Connect the correct spelling to its meaning."],
    trap: "A familiar-looking shape may be a different character or a nonexistent word.",
    examples: [{ japanese: "未来（みらい）／月末（げつまつ）", english: "The future / the end of the month: 未 and 末 differ." }] },
  { id: "homophone-spelling", section: "kanji", title: "Let context choose between homophones", format: "Same reading, different word",
    takeaway: "Words with the same reading can have different spellings and uses.",
    steps: ["Find the subject and object.", "Decide the precise meaning needed here.", "Reject a real word when its meaning belongs to a different situation."],
    trap: "Every option may be pronounced correctly. Pronunciation alone cannot choose the answer.",
    examples: [{ japanese: "学生を対象にする／二つの作品を対照する", english: "Target students / contrast two works: 対象 and 対照 are both たいしょう." }] },
  { id: "okurigana", section: "kanji", title: "Keep the correct kana after the kanji", format: "Okurigana",
    takeaway: "The written word includes its kana ending as well as its kanji.",
    steps: ["Recall the dictionary form of the word.", "Check which part is written in kanji and which in kana.", "Keep the inflection required by the sentence."],
    trap: "Do not move a syllable into or out of the kana ending just because the pronunciation stays similar.",
    examples: [{ japanese: "受け取る・確かめる・断る", english: "Receive / check / refuse: remember the complete spelling." }] },
];

type SpellingRow = readonly [id: string, sentence: string, kana: string, word: string, meaning: string,
  wrong1: ExplainedOption, wrong2: ExplainedOption, wrong3: ExplainedOption, translation: string];

const basics: SpellingRow[] = [
  ["record", "会議の内容をきろくする。", "きろく", "記録", "recording; a record", ["記緑", "緑 means green; a record uses 録."], ["紀録", "紀 is used for eras and chronicles; the standard word here is 記録."], ["記禄", "禄 concerns a stipend; recording uses 録."], "Record the contents of the meeting."],
  ["confirm", "予約の時間をかくにんしてください。", "かくにん", "確認", "confirmation", ["確任", "任 concerns duties or entrusting; confirmation uses 認."], ["格認", "格 concerns rank or form; the first character of 確認 is 確."], ["確忍", "忍 concerns enduring or concealing; recognizing uses 認."], "Please confirm the reservation time."],
  ["experience", "海外で働いたけいけんがある。", "けいけん", "経験", "experience", ["経険", "険 means steep or dangerous; experience uses 験."], ["軽験", "軽 means light; experience begins with 経."], ["経検", "検 concerns inspection; the established word for experience is 経験."], "I have experience working abroad."],
  ["explain", "使い方をせつめいしてください。", "せつめい", "説明", "explanation", ["設明", "設 concerns establishing or installing; explaining uses 説."], ["説名", "名 means name; explaining clearly uses 明."], ["節明", "節 concerns sections or seasons; the word is 説明."], "Please explain how to use it."],
  ["prepare", "旅行のじゅんびを始めた。", "じゅんび", "準備", "preparation", ["順備", "順 concerns order or sequence; preparation begins with 準."], ["準被", "被 concerns covering or suffering; preparation uses 備."], ["准備", "准 can mean quasi-; the standard spelling is 準備."], "I started preparing for the trip."],
  ["responsibility", "自分の仕事にせきにんを持つ。", "せきにん", "責任", "responsibility", ["積任", "積 concerns accumulating; responsibility begins with 責."], ["責認", "認 means recognize; responsibility uses 任."], ["績任", "績 concerns achievements; the required word begins with 責."], "Take responsibility for your own work."],
  ["contact", "変更があれば、すぐにれんらくしてください。", "れんらく", "連絡", "contact; communication", ["連落", "落 means fall; communication uses 絡."], ["練絡", "練 concerns practice; the first character is 連."], ["連格", "格 concerns rank or form, not communication."], "Please contact us immediately if anything changes."],
  ["judgment", "資料を読んでからはんだんする。", "はんだん", "判断", "judgment", ["半断", "半 means half; judging uses 判."], ["判談", "談 concerns talking; judgment uses 断."], ["反断", "反 concerns opposition; this word begins with 判."], "Make a judgment after reading the materials."],
  ["solution", "問題をかいけつする方法を考える。", "かいけつ", "解決", "resolution; solving", ["開決", "開 means open; solving a problem uses 解."], ["解結", "結 concerns tying or concluding; resolution uses 決."], ["改決", "改 concerns changing; the established word is 解決."], "Think of a way to solve the problem."],
  ["condition", "応募のじょうけんを確認する。", "じょうけん", "条件", "condition; requirement", ["状件", "状 means state or condition, but this compound uses 条."], ["条健", "健 means healthy; a requirement uses 件."], ["常件", "常 means usual; the word for application requirements is 条件."], "Check the application requirements."],
  ["approval", "上司のしょうにんが必要だ。", "しょうにん", "承認", "approval", ["承任", "任 concerns duties; approval uses 認."], ["昇認", "昇 means rise; approval begins with 承."], ["承忍", "忍 concerns endurance, not approving a request."], "The supervisor's approval is required."],
  ["trade", "二つの国の間でぼうえきが盛んだ。", "ぼうえき", "貿易", "trade", ["貿益", "益 means benefit; international trade uses 易."], ["冒易", "冒 concerns risking or venturing; trade begins with 貿."], ["貿駅", "駅 means station, not trade."], "Trade between the two countries is active."],
];

const visual: SpellingRow[] = [
  ["future", "子どもたちのみらいを考える。", "みらい", "未来", "future", ["末来", "末 means end; 未 means not yet and appears in 未来."], ["味来", "味 means taste; the future uses 未."], ["未耒", "耒 is a different character; 来 is the second character of 未来."], "Think about the children's future."],
  ["month-end", "家賃は毎月げつまつに払う。", "げつまつ", "月末", "end of the month", ["月未", "未 means not yet; the end of a month uses 末."], ["月味", "味 means taste and does not mean an ending."], ["月朱", "朱 means vermilion; the required character is 末."], "Pay the rent at the end of each month."],
  ["wait", "駅で友人をまつ。", "まつ", "待つ", "to wait", ["持つ", "持つ is もつ, to hold; waiting is 待つ."], ["侍つ", "侍 means samurai; the waiting verb uses 待."], ["時つ", "時 means time; it does not form this verb."], "Wait for a friend at the station."],
  ["hold", "重い荷物をもつ。", "もつ", "持つ", "to hold; carry", ["待つ", "待つ is まつ, to wait; carrying uses 持つ."], ["侍つ", "侍 means samurai; use the hand radical in 持."], ["特つ", "特 means special and does not form this verb."], "Carry heavy luggage."],
  ["bridge", "川に新しいはしが架かった。", "はし", "橋", "bridge", ["箸", "箸 are chopsticks, not a structure across a river."], ["端", "端 means an edge or end, not a bridge across a river."], ["矯", "矯 concerns correcting; a bridge uses the wood radical in 橋."], "A new bridge was built over the river."],
  ["chopsticks", "はしでご飯を食べる。", "はし", "箸", "chopsticks", ["橋", "橋 is a bridge; eating utensils are 箸."], ["端", "端 means edge or end, not chopsticks."], ["著", "著 concerns authorship or prominence; chopsticks have the bamboo radical."], "Eat rice with chopsticks."],
  ["continue", "明日も練習をつづける。", "つづける", "続ける", "to continue", ["読ける", "読 belongs to reading; continuing uses 続."], ["績ける", "績 concerns achievements and does not form つづける."], ["積ける", "積 concerns accumulating; the verb is 続ける."], "Continue practising tomorrow too."],
  ["investigate", "事故の原因をしらべる。", "しらべる", "調べる", "to investigate; check", ["週べる", "週 means week; investigating uses 調."], ["周べる", "周 concerns surroundings; the verb needs the speech radical in 調."], ["問べる", "問 concerns asking, but does not spell しらべる."], "Investigate the cause of the accident."],
];

const homophones: SpellingRow[] = [
  ["price", "商品のかかくを比較する。", "かかく", "価格", "price", ["科学", "科学 is かがく, science; it is not a product's price."], ["化学", "化学 is かがく, chemistry; the reading and meaning differ."], ["家格", "家格 is family standing, not the price of a product."], "Compare product prices."],
  ["target", "このサービスは学生をたいしょうにしている。", "たいしょう", "対象", "target; intended group", ["対照", "対照 means contrast or comparison, not the intended users."], ["対称", "対称 means symmetry, not the users of a service."], ["大賞", "大賞 is a grand prize, not an intended group."], "This service is intended for students."],
  ["contrast", "二つの作品をたいしょうして違いを調べる。", "たいしょう", "対照", "comparison; contrast", ["対象", "対象 is the object of an activity; here two works are compared."], ["対称", "対称 means symmetry, not examining differences."], ["大将", "大将 means a general or leader, not comparing works."], "Compare the two works and examine their differences."],
  ["guarantee", "この製品の品質をほしょうする。", "ほしょう", "保証", "guarantee", ["保障", "保障 safeguards rights or security; a product quality guarantee is 保証."], ["補償", "補償 compensates for a loss, rather than guaranteeing quality."], ["歩哨", "歩哨 means a sentry, not a quality guarantee."], "Guarantee the quality of this product."],
  ["compensate", "事故で受けた損害をほしょうする。", "ほしょう", "補償", "compensation for a loss", ["保証", "保証 guarantees quality or undertakings; an existing loss is compensated with 補償."], ["保障", "保障 safeguards rights or security; compensating damage uses 補償."], ["歩哨", "歩哨 means a sentry, unrelated to compensation."], "Compensate for damage suffered in the accident."],
  ["safeguard", "憲法は表現の自由をほしょうしている。", "ほしょう", "保障", "safeguarding rights", ["保証", "保証 is a guarantee; protecting a constitutional freedom uses 保障."], ["補償", "補償 compensates for damage rather than safeguarding a freedom."], ["歩哨", "歩哨 is a sentry, not the protection of rights."], "The constitution safeguards freedom of expression."],
  ["intention", "本人のいしを確認する。", "いし", "意思", "intention; wishes", ["医師", "医師 means a physician, not a person's wishes."], ["石", "石 means stone, not someone's intention."], ["遺志", "遺志 is the wish left by someone who has died; that is not stated here."], "Confirm the person's wishes."],
  ["doctor", "体調が悪いので、いしに相談する。", "いし", "医師", "physician", ["意思", "意思 means intention; a physician is 医師."], ["意志", "意志 is will or determination, not a medical professional."], ["石", "石 means stone, not someone who gives medical advice."], "Consult a physician because I am feeling unwell."],
];

const endings: SpellingRow[] = [
  ["receive", "受付で書類をうけとる。", "うけとる", "受け取る", "to receive", ["受け取つ", "The dictionary form ends in る, not つ: 受け取る."], ["受け取りる", "The dictionary form is 受け取る; 取りる adds an extra syllable."], ["受け採る", "採る concerns adopting or collecting; receiving documents uses 取る."], "Receive the documents at reception."],
  ["check", "出発前に時間をたしかめる。", "たしかめる", "確かめる", "to check; make sure", ["確める", "The standard spelling retains か after 確: 確かめる."], ["確かる", "確かる is not the verb たしかめる."], ["確かまる", "確かまる does not spell the intended checking verb."], "Check the time before departure."],
  ["refuse", "無理な依頼をことわる。", "ことわる", "断る", "to refuse", ["断つ", "断つ is たつ, to cut off; refusing a request is 断る（ことわる）."], ["断りる", "断り is a noun or stem; the dictionary form is 断る."], ["断れる", "断れる is potential, can refuse, rather than the requested ことわる."], "Refuse an unreasonable request."],
  ["support", "家族の生活をささえる。", "ささえる", "支える", "to support", ["支さえる", "支 already represents ささ in 支える; do not add another さ."], ["支る", "The required ending is える: 支える."], ["支ええる", "The ending える is written once, not ええる."], "Support the family's livelihood."],
  ["mix", "二つの材料をまぜる。", "まぜる", "混ぜる", "to mix", ["混る", "混る does not spell まぜる; the kana ending is ぜる."], ["混ざる", "混ざる is まざる, to become mixed, rather than mixing the materials."], ["混ぜえる", "混ぜえる contains an extra え and is not the verb."], "Mix the two ingredients."],
  ["accept", "相手の提案をうけいれる。", "うけいれる", "受け入れる", "to accept", ["受け入る", "受け入る lacks れ; the target is うけいれる."], ["受け入れれる", "受け入れれる adds an extra れ to the requested form."], ["受け要れる", "要 means need; accepting a proposal uses 入れる."], "Accept the other person's proposal."],
  ["raise", "子どもをそだてる。", "そだてる", "育てる", "to raise", ["育だてる", "育 already represents そだ; do not repeat だ."], ["育つ", "育つ is そだつ, to grow, rather than raising a child."], ["育でる", "The ending is てる, not でる."], "Raise a child."],
  ["notice", "小さな変化にきづく。", "きづく", "気づく", "to notice", ["築く", "築く（きずく）means building or establishing something, not noticing a change."], ["気つく", "The consonant is voiced in 気づく."], ["気づける", "気づける means can notice; it does not match the requested きづく."], "Notice a small change."],
];

function spellingQuestions(rows: SpellingRow[], lessonId: string) {
  return rows.map(([id, sentence, kana, word, meaning, a, b, c, translation]) => authoredChoice(
    `${lessonId}-${id}`, lessonId, `${sentence}\n下線の言葉の書き方として最も適切なものは？`,
    [[word, `${word} means ${meaning} and fits the complete sentence.`], a, b, c],
    `${word}（${kana}）means ${meaning}. ${translation}`, translation,
    { focus: kana, tags: [lessonId, word], hint: SPELLING_LESSONS.find((l) => l.id === lessonId)!.steps[0] }));
}
export const SPELLING_QUESTIONS = [
  ...spellingQuestions(basics, "kanji-spelling"), ...spellingQuestions(visual, "visual-kanji"),
  ...spellingQuestions(homophones, "homophone-spelling"), ...spellingQuestions(endings, "okurigana"),
];
