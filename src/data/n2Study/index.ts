import { N2_ASSEMBLY_LESSONS } from "../jlptN2SentenceOrder";
import { READING_PASSAGES, READING_TIPS } from "../dokkai";
import { plainReading } from "../../lib/dokkaiText";
import type { ChoiceQuestion, StudyLesson, StudyQuestion } from "./schema";
export * from "./schema";

export const STUDY_LESSONS: StudyLesson[] = [
  { id: "compound-readings", section: "kanji", title: "Read the compound, not isolated kanji", format: "Typed reading",
    takeaway: "Recall the whole word in context. A familiar kanji can have a different reading in another compound.",
    steps: ["Read the surrounding sentence to identify the word.", "Recall its full hiragana reading before checking.", "Say the word silently with its meaning; save troublesome compounds for review."],
    trap: "Long vowels and small kana matter: しゅ and しゆ are different. This drill accepts hiragana, not romaji.",
    examples: [{ japanese: "生産（せいさん）／生活（せいかつ）", english: "Production / daily life: learn each complete compound." }],
    next: { label: "Explore Kanji Word Builder", href: "/japanese/n2/kanji" } },
  { id: "word-formation", section: "vocabulary", title: "Build words with meaningful endings", format: "Word formation",
    takeaway: "Suffixes narrow the meaning, but established word combinations decide the answer.",
    steps: ["Identify what is measured: ability, rate, expense or extent.", "Recall an established compound.", "Read the entire sentence with that compound."],
    trap: "An English translation such as 'cost' does not uniquely choose 費, 料 or 代.",
    examples: [{ japanese: "集中力・失業率・交通費", english: "Concentration / unemployment rate / transportation expenses." }] },
  { id: "context", section: "vocabulary", title: "Choose a word from its neighbors", format: "Contextual blanks",
    takeaway: "Learn a word together with its objects and particles.",
    steps: ["Identify the object and the intended action.", "Check which words naturally occur together.", "Reject a related word if its usual object does not fit."],
    trap: "Related meanings do not guarantee interchangeable usage.",
    examples: [{ japanese: "日程を調整する／音量を調節する", english: "Coordinate a schedule / adjust the volume." }] },
  { id: "paraphrase", section: "vocabulary", title: "Keep the original meaning", format: "Paraphrases",
    takeaway: "A good paraphrase preserves the action, degree and speaker's attitude.",
    steps: ["Restate the target expression in simple Japanese.", "Check whether each option adds a new claim.", "Keep tense and degree unchanged."],
    trap: "An option can be on the same topic while reversing the meaning.",
    examples: [{ japanese: "延期する → 予定より後にする", english: "Postpone: move something to a later time." }] },
  { id: "usage", section: "vocabulary", title: "Recognize natural usage", format: "Usage",
    takeaway: "Check a word's typical subject, object, particle and register.",
    steps: ["Recall one reliable example sentence.", "Compare how the word connects in each option.", "Explain what would need to change in a wrong option."],
    trap: "Do not select a sentence only because its English translation seems possible.",
    examples: [{ japanese: "経験を生かす／約束を守る", english: "Put experience to use / keep a promise." }] },
  { id: "wake", section: "grammar", title: "Partial denial or impossibility?", format: "わけではない / わけがない",
    takeaway: "わけではない denies a broad interpretation; わけがない strongly rejects a possibility.",
    steps: ["Decide whether the speaker limits a claim or rejects it completely.", "Look for concessions such as 'some, but not all'.", "Check the plain form before わけ."],
    trap: "Not all are expensive does not mean all are cheap.",
    examples: [{ japanese: "全部が高いわけではない。", english: "They are not all expensive." }, { japanese: "一日で全部できるわけがない。", english: "There is no way to finish everything in one day." }] },
  { id: "limit", section: "grammar", title: "A tendency is not a guarantee", format: "とは限らない / に違いない",
    takeaway: "とは限らない rejects certainty; に違いない expresses a strong inference.",
    steps: ["Find the evidence and the strength of the conclusion.", "Distinguish a possible exception from a confident inference.", "Reread the complete statement, including negation."],
    trap: "Always, never, all and only are stronger claims than the evidence often permits.",
    examples: [{ japanese: "高ければ品質がいいとは限らない。", english: "A high price does not necessarily mean good quality." }, { japanese: "電気がついている。誰かいるに違いない。", english: "The light is on. Someone must be there." }] },
  { id: "change", section: "grammar", title: "Habit or acquired ability?", format: "ようにしている / ようになった",
    takeaway: "ようにしている expresses a deliberate continuing effort; ようになった describes a change in state or ability.",
    steps: ["Find whether the sentence describes effort or a change.", "Look for daily routines versus before-and-after clues.", "Check whether the preceding verb is potential or negative."],
    trap: "A routine you try to maintain is different from something you have become able to do.",
    examples: [{ japanese: "毎日歩くようにしている。", english: "I make a point of walking every day." }, { japanese: "漢字が読めるようになった。", english: "I have become able to read kanji." }] },
  { id: "assembly-links", section: "assembly", title: "Build connected groups first", format: "Sentence assembly ★",
    takeaway: "Join fragments that must connect before deciding where the star belongs.",
    steps: ["Find a noun and the clause that modifies it.", "Connect particles and fixed grammar expressions.", "Place all four fragments, read the full sentence, then check ★."],
    trap: "The fragment number is different from the slot number. This drill checks the complete order.",
    examples: [{ japanese: "先週 → 図書館で → 借りた → 本", english: "The noun 本 follows the clause that describes it." }],
    next: { label: "Open the full assembly course", href: "/japanese/n2/sentence-order" } },
  { id: "paragraph-links", section: "text", title: "Follow the paragraph's logic", format: "Text grammar",
    takeaway: "Choose a connector or reference by the relationship between sentences.",
    steps: ["Read the whole paragraph before filling a blank.", "Name the relationship: contrast, consequence, example or reference.", "Replace a reference with its intended meaning to check it."],
    trap: "The nearest noun is not always the reference. A word like それ can refer to a whole preceding situation.",
    examples: [{ japanese: "便利だ。しかし、費用がかかる。", english: "Useful, but costly: the second sentence adds a contrasting limitation." }] },
];

/** Rotation is stable: answer order may vary, persistent IDs never do. */
function choice(id: string, lessonId: string, prompt: string, options: [string, string, string?][], explanation: string,
  translation: string, extra: Partial<ChoiceQuestion> = {}): ChoiceQuestion {
  const offset = [...id].reduce((sum, c) => sum + c.charCodeAt(0), 0) % options.length;
  const choices = options.map(([text, why, trap]) => ({ text, why, trap }));
  return { id, lessonId, kind: "choice", prompt, explanation, translation,
    hint: STUDY_LESSONS.find((l) => l.id === lessonId)!.steps[0], targetSeconds: 35, tags: [],
    choices: [...choices.slice(offset), ...choices.slice(0, offset)], answer: (options.length - offset) % options.length, ...extra };
}

export const STUDY_QUESTIONS: StudyQuestion[] = [
  ...([
    ["production", "新しい工場で生産を始めた。", "生産", "せいさん", "production", "Production began at the new factory."],
    ["adjustment", "会議の日程を調整する。", "調整", "ちょうせい", "adjustment; coordination", "We will coordinate the meeting schedule."],
    ["condition", "申し込みの条件を確認してください。", "条件", "じょうけん", "condition; requirement", "Please check the application requirements."],
    ["experience", "留学は貴重な経験になった。", "経験", "けいけん", "experience", "Studying abroad became a valuable experience."],
  ] as const).map(([id, prompt, word, reading, meaning, translation]) => ({ id: `read-${id}`, lessonId: "compound-readings", kind: "typed" as const,
    prompt, word, answers: [reading], meaning, translation, targetSeconds: 20, tags: [word],
    hint: "Recall the entire compound. Check long vowels and voiced sounds.", explanation: `${word} is read ${reading} and means ${meaning}. Learn it with the complete example sentence.` })),
  choice("formation-ability", "word-formation", "睡眠不足で集中（　）が落ちている。", [
    ["力", "集中力 is the ability to concentrate."], ["率", "率 describes a proportion; 集中率 is not the target compound.", "Wrong compound"],
    ["費", "費 names expenses, not an ability.", "Wrong meaning"], ["料", "料 can name a charge or material; it does not form 集中力.", "Wrong compound"]
  ], "The subject is a declining ability. Recall 集中力が落ちる as a phrase.", "My concentration is declining because of insufficient sleep."),
  choice("formation-rate", "word-formation", "景気が悪くなり、失業（　）が上がった。", [
    ["率", "失業率 measures unemployment as a proportion."], ["力", "An ability is not being measured.", "Wrong meaning"],
    ["料", "This is not a service charge.", "Wrong meaning"], ["費", "失業費 is not the established word for unemployment rate.", "Wrong compound"]
  ], "A proportion that rises or falls takes 率 in the established compound 失業率.", "The economy worsened and unemployment rose."),
  choice("context-schedule", "context", "全員が参加できるように、日程を（　）した。", [
    ["調整", "日程を調整する means coordinate a schedule."], ["調節", "調節 usually adjusts a degree or setting, such as volume.", "Unnatural collocation"],
    ["整理", "整理 arranges or sorts things; it does not express coordinating availability here.", "Different action"], ["整備", "整備 means putting facilities or systems in working order.", "Different object"]
  ], "The goal is coordinating people's availability. The reliable collocation is 日程を調整する.", "We coordinated the schedule so everyone could attend."),
  choice("context-volume", "context", "音が大きすぎるので、音量を（　）してください。", [
    ["調節", "音量を調節する means adjust the volume."], ["解決", "解決 is for resolving a problem, not directly adjusting a volume setting.", "Different object"],
    ["整理", "整理 means sort or organize.", "Wrong action"], ["維持", "維持 would keep the current volume; the speaker wants it changed.", "Reversed intention"]
  ], "The speaker asks for a change to a setting, so 調節 fits.", "It is too loud; please adjust the volume."),
  choice("paraphrase-delay", "paraphrase", "「会議を延期した」の「延期した」に最も近い意味は？", [
    ["予定より後にした", "延期 moves an event to a later date."], ["予定より早くした", "This means bringing it forward.", "Reversed meaning"],
    ["行わないことにした", "This means cancellation, not postponement.", "Added claim"], ["予定どおりにした", "This means keeping the original schedule.", "Contradicts the word"]
  ], "延期 changes when the meeting happens; it does not say the meeting is canceled.", "The meeting was postponed."),
  choice("paraphrase-almost", "paraphrase", "「作業はほぼ終わった」の「ほぼ」に最も近い意味は？", [
    ["だいたい", "Both express approximately or almost in this context."], ["まったく", "まったく expresses complete degree, not almost.", "Too strong"],
    ["やっと", "やっと emphasizes finally achieving something.", "Different emphasis"], ["まだ", "まだ means still or not yet, and does not replace ほぼ here.", "Different meaning"]
  ], "ほぼ終わった is almost finished. It leaves room for a little remaining work.", "The work is almost finished."),
  choice("usage-experience", "usage", "「生かす」の使い方として最も適切な文は？", [
    ["留学の経験を仕事に生かした。", "経験を生かす means put experience to practical use."], ["明日の会議を来週に生かした。", "Use 延期した to postpone a meeting.", "Wrong verb"],
    ["駅までバスを生かした。", "Use 利用した for taking a bus.", "Unnatural object"], ["疲れたので体を生かした。", "Resting is 体を休めた, not 生かした.", "Wrong action"]
  ], "生かす can mean making useful use of an ability or experience. Learn 経験を仕事に生かす.", "I put my study-abroad experience to use at work."),
  choice("usage-promise", "usage", "「守る」の使い方として最も適切な文は？", [
    ["友人との約束を守った。", "約束を守る means keep a promise."], ["昼ご飯を守って食べた。", "守る does not describe the manner of eating lunch.", "Unnatural usage"],
    ["電車を守って駅に着いた。", "This does not naturally mean taking a train.", "Wrong action"], ["新しい単語を守って覚えた。", "Words are learned, not 守る in this sense.", "Unnatural object"]
  ], "守る is used with promises, rules and things being protected. 約束を守る is a reliable pair.", "I kept my promise to my friend."),
  choice("wake-partial", "wake", "「部分否定」を表す形を選んでください。\nこの店の商品が全部高い（　）。安い物もある。", [
    ["わけではない", "The following sentence gives an exception: some items are cheap."], ["わけがない", "This strongly rejects the possibility; the speaker is only limiting a generalization.", "Too strong"],
    ["に違いない", "This asserts certainty that all items are expensive.", "Reversed meaning"], ["に決まっている", "This confidently asserts the claim instead of qualifying it.", "Reversed meaning"]
  ], "安い物もある supplies an exception. The point is 'not all', expressed by わけではない.", "Not everything in this shop is expensive. There are inexpensive items too."),
  choice("wake-impossible", "wake", "百ページの資料を一分で全部読める（　）。そんなことは不可能だ。", [
    ["わけがない", "The speaker explicitly says it is impossible."], ["ようになった", "This describes an acquired ability, contradicting the next sentence.", "Contradiction"],
    ["に違いない", "This expresses confidence it can be done.", "Reversed meaning"], ["ことになった", "This describes a decision or arrangement.", "Wrong relationship"]
  ], "不可能だ calls for a strong rejection: 読めるわけがない.", "There is no way to read all one hundred pages in one minute. That is impossible."),
  choice("limit-exception", "limit", "「必ずそうだとは言えない」と、例外の可能性を表す形を選んでください。\n値段が高ければ、品質がいい（　）。", [
    ["とは限らない", "This rejects the guarantee that price always means quality."], ["に違いない", "This asserts strong certainty rather than rejecting it.", "Reversed certainty"],
    ["ことにした", "A personal decision does not fit this general judgment.", "Wrong relationship"], ["ようにしている", "This expresses a deliberate habit, not a relationship between price and quality.", "Wrong relationship"]
  ], "The instruction asks you to allow exceptions: a high price does not guarantee quality.", "A high price does not necessarily mean good quality."),
  choice("limit-inference", "limit", "部屋の電気がついている。誰か中にいる（　）。", [
    ["に違いない", "The light is evidence for the speaker's confident inference."], ["ようにしている", "This expresses intentional effort, not inference.", "Wrong relationship"],
    ["ことにした", "This would describe deciding to be there.", "Wrong relationship"], ["わけがない", "This rejects the presence of anyone despite the supporting evidence.", "Reversed inference"]
  ], "に違いない marks a strong inference from evidence; it is still the speaker's judgment.", "The room's light is on. Someone must be inside."),
  choice("change-habit", "change", "「意識して続けている習慣」を表す形を選んでください。\n健康のために、毎日三十分歩く（　）。", [
    ["ようにしている", "This describes a continuing deliberate effort."], ["に違いない", "This infers certainty, rather than describing one's own routine.", "Wrong intent"],
    ["わけがない", "This rejects the possibility of walking.", "Reversed meaning"], ["とは限らない", "This qualifies a claim rather than describing the intended health habit.", "Wrong intent"]
  ], "健康のために and 毎日 frame a deliberate routine: 歩くようにしている.", "For my health, I make a point of walking thirty minutes every day."),
  choice("change-ability", "change", "練習を続けた結果、難しい漢字も読める（　）。", [
    ["ようになった", "Practice resulted in a newly acquired ability."], ["ことにした", "This would be a decision, not the achieved change described by 結果.", "Wrong relationship"],
    ["わけがない", "This denies the ability despite the positive outcome.", "Reversed meaning"], ["とは限らない", "This expresses uncertainty, not the stated result of practice.", "Wrong intent"]
  ], "読める is potential form; 練習を続けた結果 marks the cause of the change in ability.", "After continued practice, I became able to read difficult kanji too."),
  choice("text-contrast", "paragraph-links", "空欄に入る最も適切な表現は？", [
    ["しかし", "Convenience is followed by a drawback: cost."], ["そのため", "The fee is not presented as a consequence of convenience.", "Wrong connection"],
    ["たとえば", "The fee is not an example of being able to order anywhere.", "Wrong connection"], ["つまり", "The fee does not restate the convenience.", "Wrong connection"]
  ], "The paragraph moves from an advantage to a limitation, so a contrast marker fits.", "Online ordering is convenient. However, delivery costs money.",
  { targetSeconds: 75, texts: [{ text: "このサービスなら、家からいつでも注文できるので便利だ。（　）、配達には一回五百円かかる。利用する前に、便利さだけでなく費用も考えたい。", translation: "This service is convenient because you can order from home at any time. However, delivery costs 500 yen each time. Before using it, consider the cost as well as the convenience." }], evidence: ["配達には一回五百円かかる"] }),
  choice("text-reference", "paragraph-links", "「それ」が指していることは？", [
    ["閉館時間を二時間延ばしたこと", "それ refers to the preceding change in opening hours."], ["利用者が減ったこと", "The text says user numbers increased, not decreased.", "Reversed fact"],
    ["新しい図書館を建てたこと", "No new library is mentioned.", "Unsupported"], ["仕事を早く終えること", "The library changed its hours; workers did not change their jobs.", "Wrong agent"]
  ], "Replace それ with the entire preceding action: extending the closing time made after-work visits possible.", "The library extended its hours, enabling more people to visit after work.",
  { targetSeconds: 75, texts: [{ text: "市の図書館は、先月から平日の閉館時間を二時間延ばした。それによって、仕事の帰りに立ち寄れる人が増えた。", translation: "Since last month, the city library has extended its weekday closing time by two hours. As a result, more people can drop in after work." }], evidence: ["平日の閉館時間を二時間延ばした"] }),
  choice("text-consequence", "paragraph-links", "空欄に入る最も適切な表現は？", [
    ["そこで", "The team responds to the problem by changing its procedure."], ["ところが", "The new procedure is a response, not an unexpected contradiction.", "Wrong connection"],
    ["一方", "The text is not comparing two parallel situations.", "Wrong connection"], ["たとえば", "The action is not merely an example of running out of time.", "Wrong connection"]
  ], "そこで introduces an action taken in response to the preceding situation.", "The team responded to unfinished discussion by sharing materials in advance.",
  { targetSeconds: 75, texts: [{ text: "毎週の会議では、資料を読むだけで時間がなくなり、十分に話し合えなかった。（　）、資料を前日に配り、会議では意見の交換に集中することにした。", translation: "At the weekly meetings, simply reading the materials used up the time, leaving little room for discussion. So the team decided to distribute the materials the day before and concentrate on exchanging opinions during the meeting." }], evidence: ["資料を前日に配り"] }),
  ...N2_ASSEMBLY_LESSONS.slice(1, 5).map((l) => l.questions[0]).map((q) => ({ id: `assembly-${q.id}`, lessonId: "assembly-links", kind: "assembly" as const,
    prompt: "Put all four fragments in order. Which fragment lands at ★?", before: q.before, after: q.after,
    fragments: q.choices, order: q.order.map((n) => n - 1), starIndex: q.starIndex,
    // Time and place adjuncts may swap without changing these sentences.
    acceptedOrders: q.id === "s01-1" ? [[3, 1, 0, 2]] : q.id === "s04-1" ? [[3, 0, 2, 1]] : [],
    explanation: q.explanation, translation: q.translation, targetSeconds: 60, tags: ["sentence connections"], hint: "Find connected groups, then place the noun and its modifiers." })),
];

for (const kind of ["short", "medium", "ab", "long", "information"] as const) {
  const p = READING_PASSAGES.find((item) => item.kind === kind)!;
  const format = { short: "Short passage", medium: "Medium passage", ab: "Paired texts A/B", long: "Long argument", information: "Information search" }[kind];
  const id = `reading-${kind}`;
  STUDY_LESSONS.push({ id, section: "reading", title: format, format,
    takeaway: READING_TIPS[p.skill], steps: ["Read the question to identify what you need to find.", "Read for the argument or conditions; underline the evidence in your mind.", "Eliminate answers that add, reverse or exaggerate a claim."],
    trap: "Matching a word from the passage does not prove the entire answer. Check every part of the choice.",
    examples: [{ japanese: "すべて・必ず・だけ", english: "All / always / only: check whether the text supports this strength of claim." }],
    next: { label: `Explore ${format.toLowerCase()} practice`, href: `/japanese/n2/reading/${kind}` } });
  for (const q of p.questions) STUDY_QUESTIONS.push({ id: `study-${q.id}`, lessonId: id, kind: "choice", prompt: plainReading(q.prompt),
    choices: q.choices.map((c) => ({ text: plainReading(c.text), why: c.explanation })), answer: q.answer,
    hint: READING_TIPS[p.skill], explanation: q.explanation, translation: "Read the full translation below after your attempt.",
    targetSeconds: { short: 90, medium: 150, ab: 180, long: 240, information: 150 }[kind], tags: [format, p.topic, p.skill],
    texts: p.texts.map((t) => ({ ...t, text: plainReading(t.text) })), evidence: q.evidence });
}

export const STUDY_QUESTION_MAP = new Map(STUDY_QUESTIONS.map((q) => [q.id, q]));
export const STUDY_LESSON_MAP = new Map(STUDY_LESSONS.map((l) => [l.id, l]));
