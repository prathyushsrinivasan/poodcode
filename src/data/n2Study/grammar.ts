import { authoredChoice, type ExplainedOption } from "./builders";
import type { StudyLesson } from "./schema";

export interface GrammarPoint {
  id: string; pattern: string; group: string; meaning: string; formation: string; register: string; contrast: string;
  examples: { japanese: string; english: string }[];
}
export const GRAMMAR_POINTS: GrammarPoint[] = [
  { id: "mono-no", pattern: "ものの", group: "Concession", meaning: "Although something is true, the expected result does not follow.",
    formation: "Verb / い-adjective plain form + ものの; な-adjective + なものの; noun + であるものの.", register: "Common in written explanations and considered statements.",
    contrast: "ものの introduces an unexpected contrast; ので introduces a reason. Keep both facts when interpreting the contrast.",
    examples: [{ japanese: "資格は取ったものの、まだ仕事が見つからない。", english: "Although I obtained the qualification, I still have not found work." }, { japanese: "資格を取ったので、その仕事に応募できる。", english: "Because I obtained the qualification, I can apply for that job." }] },
  { id: "despite", pattern: "にもかかわらず", group: "Concession", meaning: "Despite a circumstance, something contrary to expectation happens.",
    formation: "Verb / い-adjective plain form + にもかかわらず; noun / な-adjective stem (+ である) + にもかかわらず.", register: "A formal contrast often used in reports and written descriptions.",
    contrast: "Despite a cause is different from because of a cause: にもかかわらず contrasts; によって can identify a cause or means.",
    examples: [{ japanese: "大雨にもかかわらず、試合は行われた。", english: "Despite the heavy rain, the match was held." }, { japanese: "大雨によって、試合は中止になった。", english: "The match was cancelled because of the heavy rain." }] },
  { id: "thanks-to", pattern: "おかげで", group: "Cause", meaning: "Attribute a favorable outcome to someone's help or a useful circumstance.",
    formation: "Verb / い-adjective plain form + おかげで; noun + のおかげで; な-adjective + なおかげで.", register: "Used in both conversation and writing. Usually expresses appreciation; ironic uses depend on context.",
    contrast: "おかげで usually credits a helpful cause; せいで usually blames a cause for an unfavorable result.",
    examples: [{ japanese: "先生のおかげで、合格できた。", english: "Thanks to my teacher, I was able to pass." }, { japanese: "寝不足のせいで、集中できなかった。", english: "Because of lack of sleep, I could not concentrate." }] },
  { id: "because-bad", pattern: "せいで", group: "Cause", meaning: "Blame a cause for an unfavorable result.",
    formation: "Verb / い-adjective plain form + せいで; noun + のせいで; な-adjective + なせいで.", register: "Common in conversation and writing, but can sound accusatory when attributing blame to a person.",
    contrast: "せいで adds a negative evaluation; ので can state the same causal relationship more neutrally.",
    examples: [{ japanese: "渋滞のせいで、会議に遅れた。", english: "I was late to the meeting because of the traffic jam." }, { japanese: "道が混んでいたので、到着が遅れた。", english: "Because the road was congested, my arrival was delayed." }] },
  { id: "bakari-ni", pattern: "ばかりに", group: "Cause", meaning: "A particular action or circumstance unexpectedly leads to an unfortunate result, often with regret.",
    formation: "Verb / い-adjective plain form + ばかりに; な-adjective + なばかりに; noun + であるばかりに.", register: "Used to explain a regrettable result in conversation or writing.",
    contrast: "ばかりに explains a regrettable cause; ばかりでなく adds another fact and means not only.",
    examples: [{ japanese: "うそをついたばかりに、信頼を失った。", english: "Because I told a lie, I ended up losing their trust." }, { japanese: "彼は親切なばかりでなく、仕事も正確だ。", english: "He is not only kind but also accurate in his work." }] },
  { id: "accompany", pattern: "に伴って", group: "Change", meaning: "As one development occurs, another related development accompanies it.",
    formation: "Noun / verb dictionary form + に伴って. Use related changes rather than unrelated events.", register: "Often used for social, organizational or large-scale changes in reports and explanations.",
    contrast: "に伴って connects accompanying changes; につれて often emphasizes gradual parallel development.",
    examples: [{ japanese: "人口の増加に伴って、住宅も増えた。", english: "As the population increased, housing also increased." }, { japanese: "練習を重ねるにつれて、自信がついてきた。", english: "As I continued practising, I gradually gained confidence." }] },
  { id: "parallel-change", pattern: "につれて", group: "Change", meaning: "As one thing gradually changes, another changes along with it.",
    formation: "Verb dictionary form / a noun expressing change + につれて.", register: "Used in conversation and writing to describe parallel changes.",
    contrast: "につれて describes a developing relationship, rather than a one-off intentional sequence expressed by てから.",
    examples: [{ japanese: "年を取るにつれて、健康を意識するようになった。", english: "As I grew older, I became more conscious of my health." }, { japanese: "食事をしてから、薬を飲んだ。", english: "After eating, I took the medicine: a sequence, rather than parallel change." }] },
  { id: "only", pattern: "に限り", group: "Limitation", meaning: "Limit an offer, permission or condition to a specified group or occasion.",
    formation: "Noun + に限り. Common with groups, dates and occasions.", register: "Frequently used in formal notices, conditions and announcements.",
    contrast: "に限り restricts the group; に限らず explicitly extends beyond it.",
    examples: [{ japanese: "会員に限り、入場料が無料です。", english: "Admission is free for members only." }, { japanese: "会員に限らず、誰でも参加できます。", english: "Anyone can participate, not only members." }] },
  { id: "not-limited", pattern: "に限らず", group: "Limitation", meaning: "A statement applies beyond the named group or example.",
    formation: "Noun + に限らず, often followed by a broader group or も.", register: "Used in conversation and writing to broaden a statement.",
    contrast: "に限らず includes others; に限り excludes those outside the specified group.",
    examples: [{ japanese: "この問題は日本に限らず、世界中で見られる。", english: "This problem occurs worldwide, not only in Japan." }, { japanese: "本日に限り、送料は無料です。", english: "Shipping is free today only." }] },
  { id: "merely", pattern: "にすぎない", group: "Limitation", meaning: "Describe something as no more than a limited amount, role or example.",
    formation: "Noun / verb plain form + にすぎない. It limits an assessment, not a quantity by overdoing it.", register: "Often used in explanations, arguments and written evaluations.",
    contrast: "にすぎない means merely; すぎる means excessive. They do not express the same judgment.",
    examples: [{ japanese: "これは一つの例にすぎない。", english: "This is merely one example." }, { japanese: "この説明は長すぎる。", english: "This explanation is too long." }] },
  { id: "risk", pattern: "かねない", group: "Possibility", meaning: "Warn that an undesirable outcome could occur.",
    formation: "Verb ます-stem + かねない: 招きます → 招きかねない.", register: "Often used in warnings and formal explanations of risk.",
    contrast: "かねない means a bad result could happen; かねる means it is difficult or impossible for the speaker to comply.",
    examples: [{ japanese: "確認を怠ると、事故を招きかねない。", english: "Neglecting the checks could cause an accident." }, { japanese: "そのご依頼には応じかねます。", english: "We are unable to comply with that request." }] },
  { id: "no-choice", pattern: "ざるを得ない", group: "Obligation", meaning: "Circumstances leave no reasonable alternative to an action.",
    formation: "Verb ない-stem + ざるを得ない. Exception: する → せざるを得ない.", register: "Common in explanations of reluctant necessity, especially considered or written statements.",
    contrast: "ざるを得ない expresses unavoidable action; ずにはいられない expresses an uncontrollable urge or feeling.",
    examples: [{ japanese: "台風のため、旅行を中止せざるを得ない。", english: "Because of the typhoon, we have no choice but to cancel the trip." }, { japanese: "その話を聞いて、笑わずにはいられなかった。", english: "Hearing that story, I could not help laughing." }] },
];

export const GRAMMAR_LESSONS: StudyLesson[] = GRAMMAR_POINTS.map((point) => ({
  id: `grammar-${point.id}`, section: "grammar", title: point.pattern, format: point.pattern,
  takeaway: point.meaning, steps: ["Identify the relationship the speaker intends.", point.formation, "Read the whole sentence, including negation and the final result."],
  trap: point.contrast, examples: point.examples,
}));

type QuestionRow = readonly [pointId: string, id: string, exercise: string, prompt: string,
  answer: string, why: string, a: ExplainedOption, b: ExplainedOption, c: ExplainedOption, translation: string];
const questions: QuestionRow[] = [
  ["mono-no", "qualification", "Selection", "「資格を取ったのに、期待した結果になっていない」という意味になる形は？\n資格は取った（　）、まだ仕事が見つからない。", "ものの", "ものの contrasts the qualification with the expected job not materializing.", ["ので", "ので introduces a reason, not the requested unexpected contrast."], ["ために", "ために gives purpose or cause, not this concession."], ["につれて", "につれて requires related developing changes, not this completed qualification and contrast."], "Although I obtained the qualification, I still have not found work."],
  ["mono-no", "formation", "Formation", "（　）ものの、予算が足りない。空欄に入る形は？", "便利な", "A な-adjective connects to ものの with な: 便利なものの.", ["便利だ", "便利だ does not directly connect to ものの in this adjective construction."], ["便利に", "便利に is adverbial and cannot directly modify ものの."], ["便利での", "便利での is not the adjective connection required here."], "Although it is convenient, we do not have enough budget."],
  ["despite", "weather", "Selection", "「大雨だったのに、試合をした」という意味になる形は？\n大雨（　）、試合は行われた。", "にもかかわらず", "にもかかわらず explicitly contrasts the adverse condition with the match taking place.", ["のせいで", "のせいで assigns a negative cause, rather than expressing despite."], ["に限り", "に限り restricts a group or occasion, not an unexpected contrast."], ["にすぎず", "にすぎず minimizes an assessment rather than expressing despite the rain."], "Despite the heavy rain, the match was held."],
  ["despite", "formation", "Formation", "「忙しい」を使った正しい接続は？\n（　）、彼は手伝ってくれた。", "忙しいにもかかわらず", "An い-adjective's plain form connects directly: 忙しいにもかかわらず.", ["忙しいなにもかかわらず", "な is not inserted after an い-adjective here."], ["忙しいのにもかかわらずだ", "The added final だ does not connect this clause to the following comma and main clause."], ["忙しいでにもかかわらず", "で is not the required connection after 忙しい."], "Despite being busy, he helped me."],
  ["thanks-to", "teacher", "Selection", "先生の助けに感謝する意味になる形は？\n先生（　）、試験に合格できた。", "のおかげで", "のおかげで credits a helpful cause and expresses appreciation.", ["のせいで", "のせいで blames a cause; the requested meaning is gratitude, not irony."], ["に限り", "に限り restricts an offer to a group, not gratitude for help."], ["にすぎず", "にすぎず means merely, not thanks to someone's help."], "Thanks to my teacher, I was able to pass the exam."],
  ["thanks-to", "formation", "Formation", "「親切だ」を使った正しい接続は？\n案内の人が（　）、迷わずに着けた。", "親切なおかげで", "A な-adjective uses な before おかげで: 親切なおかげで.", ["親切だおかげで", "だ does not connect directly before おかげで here."], ["親切におかげで", "親切に is adverbial and does not make the needed modifying clause."], ["親切をおかげで", "を is an object marker, not the adjective connection."], "Thanks to the helpful guide, I arrived without getting lost."],
  ["because-bad", "traffic", "Selection", "渋滞を「遅れた悪い原因」として述べる形は？\n渋滞（　）、会議に遅れた。", "のせいで", "のせいで negatively attributes the delay to the traffic jam.", ["のおかげで", "のおかげで normally credits a helpful cause; this question explicitly asks for blame."], ["に限らず", "に限らず broadens a group or scope, not stating a cause."], ["にすぎず", "にすぎず limits an assessment, not blaming a cause."], "I was late to the meeting because of the traffic jam."],
  ["because-bad", "formation", "Formation", "「寝不足」という名詞につなぐ正しい形は？\n（　）、集中できなかった。", "寝不足のせいで", "A noun takes の before せいで: 寝不足のせいで.", ["寝不足にせいで", "に does not connect the noun to せいで in this construction."], ["寝不足だせいで", "A noun plus だ does not directly modify せい in this construction."], ["寝不足をせいで", "を does not connect the cause noun to せいで."], "Because of lack of sleep, I could not concentrate."],
  ["bakari-ni", "lie", "Selection", "「一度のうそが残念な結果を招いた」という後悔を表す形は？\nうそをついた（　）、友人の信頼を失った。", "ばかりに", "ばかりに emphasizes a cause leading to a regrettable outcome.", ["ばかりでなく", "ばかりでなく adds another fact and means not only, not because of a regrettable cause."], ["に限り", "に限り attaches to a noun and limits an occasion or group."], ["おかげで", "おかげで credits a helpful cause; the requested meaning is regret."], "Because I told a lie, I ended up losing my friend's trust."],
  ["bakari-ni", "formation", "Formation", "「うそをつく」の過去形に接続する正しい形は？", "うそをついたばかりに", "The plain past form ついた connects directly to ばかりに.", ["うそをついたのばかりに", "の is not added after the plain past form in this construction."], ["うそをついたにばかりに", "An extra に is not inserted before ばかりに."], ["うそをついただばかりに", "だ cannot follow this plain past verb before ばかりに."], "Because I told a lie, an unfortunate result followed."],
  ["accompany", "population", "Selection", "「人口増加と関連して住宅も増えた」という意味の形は？\n人口の増加（　）、住宅も増えた。", "に伴って", "に伴って connects the population increase with accompanying housing growth.", ["に限り", "に限り restricts a group or occasion rather than connecting two developments."], ["にすぎず", "にすぎず means merely rather than accompanying change."], ["にもかかわらず", "にもかかわらず implies an unexpected contrast; the question asks for a related development."], "As the population increased, housing also increased."],
  ["accompany", "formation", "Formation", "「増加」という名詞から始める正しい接続は？", "人口の増加に伴って", "A noun expressing change connects directly with に伴って.", ["人口の増加するに伴って", "増加する is a verb, but the noun structure 人口の増加する is not the specified connection."], ["人口の増加なに伴って", "な is not inserted between the noun 増加 and に伴って."], ["人口の増加をに伴って", "を and に cannot both be inserted in this noun connection."], "Along with the population increase."],
  ["parallel-change", "age", "Selection", "「年齢の変化とともに、意識も徐々に変わった」という意味の形は？\n年を取る（　）、健康を意識するようになった。", "につれて", "につれて links growing older with a gradual change in awareness.", ["にすぎず", "にすぎず minimizes a statement rather than linking gradual changes."], ["に限り", "に限り restricts a noun-based group or occasion."], ["ばかりでなく", "ばかりでなく adds another fact, rather than expressing the requested parallel change."], "As I grew older, I became more conscious of my health."],
  ["parallel-change", "formation", "Formation", "「練習を重ねる」を接続する正しい形は？", "練習を重ねるにつれて", "につれて follows the dictionary form 重ねる.", ["練習を重ねますにつれて", "The polite ます form does not directly precede につれて."], ["練習を重ねるのにつれて", "This construction does not insert の after the dictionary form."], ["練習を重ねたなにつれて", "Neither the past plus な nor this connection fits につれて."], "As one continues practising."],
  ["only", "members", "Selection", "「無料なのは会員だけ」という制限を表す形は？\n会員（　）、入場料が無料です。", "に限り", "に限り restricts free admission to members.", ["に限らず", "に限らず extends beyond members, contradicting the stated restriction."], ["に伴って", "に伴って connects related developments, not eligibility."], ["のせいで", "のせいで blames a cause rather than stating eligibility."], "Admission is free for members only."],
  ["only", "formation", "Formation", "「本日」という名詞に接続する正しい形は？", "本日に限り", "に限り attaches directly to a noun identifying the occasion.", ["本日なに限り", "な is not inserted before に限り."], ["本日のに限り", "の is not inserted between 本日 and に限り."], ["本日をに限り", "を is not part of the noun connection to に限り."], "Today only."],
  ["not-limited", "worldwide", "Selection", "「日本だけではなく、他の国でも」という意味の形は？\nこの問題は日本（　）、世界中で見られる。", "に限らず", "に限らず extends the scope beyond Japan.", ["に限り", "に限り restricts the scope to Japan, reversing the intended meaning."], ["にすぎず", "にすぎず means merely and does not broaden the geographical scope."], ["のおかげで", "のおかげで credits a favorable cause rather than broadening scope."], "This problem occurs worldwide, not only in Japan."],
  ["not-limited", "formation", "Formation", "「学生」という名詞に接続する正しい形は？", "学生に限らず", "に限らず follows the noun directly and means not limited to students.", ["学生なに限らず", "な is not inserted after the noun in this construction."], ["学生のに限らず", "の is not required between the noun and に限らず."], ["学生をに限らず", "を is not part of the noun connection here."], "Not limited to students."],
  ["merely", "example", "Selection", "「例はこれ一つだけで、全体を代表するとは言えない」という意味の形は？\nこれは一つの例（　）。", "にすぎない", "にすぎない limits the importance or scope of the single example.", ["に違いない", "に違いない expresses a strong inference, not the requested limiting judgment."], ["のおかげだ", "のおかげだ attributes a favorable outcome to a cause."], ["に伴う", "に伴う requires a noun or related development and does not mean merely."], "This is merely one example.",],
  ["merely", "formation", "Formation", "「一つの例」に直接つなげて「それ以上ではない」と表す正しい形は？", "一つの例にすぎない", "The noun phrase connects directly to にすぎない.", ["一つの例なにすぎない", "な is not inserted before にすぎない."], ["一つの例のにすぎない", "の is not inserted in this noun connection."], ["一つの例をにすぎない", "を is not part of this construction."], "It is no more than one example."],
  ["risk", "accident", "Selection", "「事故を起こす危険がある」という意味の形は？\n確認を怠ると、事故を招き（　）。", "かねない", "招きかねない warns of a possible undesirable result.", ["かねます", "招きかねます would express difficulty in causing it, the opposite of a warning that it might occur."], ["に限る", "に限る does not attach to this verb stem to express risk."], ["にすぎない", "にすぎない does not directly attach to the ます-stem here."], "Neglecting the checks could cause an accident."],
  ["risk", "formation", "Formation", "「招く」を「かねない」に接続する正しい形は？", "招きかねない", "かねない follows the ます-stem: 招きます → 招き.", ["招くかねない", "The dictionary form 招く does not directly precede かねない."], ["招いたかねない", "The past form 招いた is not the required ます-stem."], ["招かないかねない", "The negative form 招かない is not the required stem."], "Could bring about an undesirable outcome."],
  ["no-choice", "typhoon", "Selection", "「ほかに方法がなく、残念だが中止する必要がある」という意味の形は？\n台風のため、旅行を中止（　）。", "せざるを得ない", "The する exception is せざるを得ない, expressing unavoidable action.", ["しざるを得ない", "する changes to せ, not し, before ざるを得ない."], ["するざるを得ない", "The dictionary form する does not directly precede ざるを得ない."], ["したざるを得ない", "The past form した does not form this expression."], "Because of the typhoon, we have no choice but to cancel the trip."],
  ["no-choice", "formation", "Formation", "「帰る」を「ざるを得ない」に接続する正しい形は？", "帰らざるを得ない", "Use the ない-stem 帰ら before ざるを得ない.", ["帰りざるを得ない", "帰り is the ます-stem; this pattern requires 帰ら."], ["帰るざるを得ない", "The dictionary form does not connect directly here."], ["帰れざるを得ない", "帰れ is not the negative stem of 帰る."], "Have no choice but to go home."],
];

export const GRAMMAR_QUESTIONS = questions.map(([pointId, id, exercise, prompt, answer, why, a, b, c, translation]) => {
  const point = GRAMMAR_POINTS.find((p) => p.id === pointId)!;
  return authoredChoice(`grammar-${pointId}-${id}`, `grammar-${pointId}`, prompt,
    [[answer, why], a, b, c], `${why} ${point.meaning}`, translation,
    { tags: [`group:${point.group}`, `exercise:${exercise}`, point.pattern], hint: exercise === "Formation" ? "Identify the word type and its form before connecting it to the pattern." : "Decide the relationship between the first clause and the final outcome." });
});
