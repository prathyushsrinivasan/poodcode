import { READING_PASSAGES, READING_TIPS } from "../dokkai";
import { plainReading } from "../../lib/dokkaiText";
import { authoredChoice, type ExplainedOption } from "./builders";
import type { ChoiceQuestion, StudyLesson } from "./schema";

const definitions = [
  ["reading-main-point", "Main points", "Distinguish the writer's overall claim from an example or supporting detail.", "An accurate detail can still be too narrow to summarize the whole argument."],
  ["reading-reference", "Reference tracking", "Replace a reference expression with the action, idea or situation it refers to.", "The nearest noun is not always the referent; sometimes an entire preceding action is meant."],
  ["reading-argument", "Argument structure", "Identify the role of a claim, reason, example, objection or conclusion.", "An example illustrates a claim; it does not by itself prove every possible case."],
  ["reading-fact-opinion", "Fact and opinion", "Separate a reported observation from an evaluation, recommendation or prediction.", "A confident tone does not turn an opinion into a measured fact."],
  ["reading-answer-strength", "Answer strength", "Check the scope of every choice, especially all, always, never and only.", "A statement about some people or one setting does not establish a universal rule."],
  ["reading-summary", "Paragraph summaries", "Preserve the paragraph's main relationship while dropping secondary detail.", "A summary must neither add a recommendation nor reverse the stated result."],
  ["reading-structure", "Sentence structure", "Find the head noun and main predicate before interpreting modifying clauses.", "A long modifier before a noun is not necessarily the sentence's main claim."],
] as const;
export const READING_SKILL_LESSONS: StudyLesson[] = definitions.map(([id, format, takeaway, trap]) => ({
  id, section: "reading", title: format, format, takeaway, trap,
  steps: ["Identify exactly what the question asks you to find.", "Locate the relevant sentence or relationship in the passage.", "Reject a choice that changes the scope, role or meaning."],
  examples: [{ japanese: "一部の利用者 → すべての利用者、とは言えない。", english: "Some users does not establish all users. Keep the scope of the evidence." }],
}));

const existingSkills: ChoiceQuestion[] = ([ ["Main point", "reading-main-point"], ["Reference", "reading-reference"] ] as const).flatMap(([skill, lessonId]) =>
  READING_PASSAGES.filter((p) => p.skill === skill).slice(0, 12).map((p) => {
    const q = p.questions[0];
    return { id: `${lessonId}-${q.id}`, lessonId, kind: "choice" as const, prompt: plainReading(q.prompt),
      choices: q.choices.map((c) => ({ text: plainReading(c.text), why: c.explanation })), answer: q.answer,
      texts: p.texts.map((t) => ({ ...t, text: plainReading(t.text) })), translation: p.texts.map((t) => t.translation).join("\n\n"),
      evidence: q.evidence, explanation: q.explanation, hint: READING_TIPS[skill], targetSeconds: 120,
      tags: [`source:${p.id}`, `exercise:${skill === "Reference" ? "Reference tracking" : "Main points"}`, `topic:${p.topic}`] };
  }));

type AnalysisRow = readonly [skill: "argument" | "fact-opinion" | "answer-strength" | "summary" | "structure", prompt: string,
  correct: string, why: string, a: ExplainedOption, b: ExplainedOption, c: ExplainedOption, evidence: string];
interface AnalysisCase {
  id: string; text: string; translation: string; questions: AnalysisRow[];
  breakdown: NonNullable<ChoiceQuestion["breakdown"]>;
}
const cases: AnalysisCase[] = [
  { id: "library", text: "市の図書館が閉館時間を二時間遅くしたところ、平日の利用者は前年より三割増えた。仕事帰りに立ち寄る人が増えたことが理由の一つだと、担当者は考えている。\n\nただし、この結果だけで、すべての図書館が開館時間を延ばすべきだとは言えない。地域によって利用者の生活や職員の人数が異なるからだ。大切なのは、各地域の状況を調べて、利用しやすい時間を考えることである。",
    translation: "When the city library moved closing time two hours later, weekday users increased by thirty percent compared with the previous year. The person responsible thinks one reason is an increase in people stopping by after work.\n\nHowever, this result alone does not establish that every library should extend its hours. Users' lifestyles and staffing levels vary by area. What matters is examining local circumstances and considering convenient opening times.",
    breakdown: { sentence: "仕事帰りに立ち寄る人が増えたことが理由の一つだと、担当者は考えている。", mainClause: "担当者は考えている", modifiers: ["仕事帰りに立ち寄る → 人を説明する", "人が増えた → ことの内容", "理由の一つだと → 担当者が考えている内容"], explanation: "The main clause reports what the staff member thinks. Within that thought, 仕事帰りに立ち寄る modifies 人, and the increase is nominalized by こと as one proposed reason." },
    questions: [
      ["argument", "「地域によって利用者の生活や職員の人数が異なるからだ」は、どんな役割を持つか。", "すべての図書館に同じ方法を勧められない理由", "The sentence explains why one library's outcome cannot justify a universal recommendation.", ["利用者が三割増えたことを示す数値", "The numerical increase is reported earlier; this sentence explains variation between areas."], ["開館時間を必ず短くするという結論", "The passage does not conclude that hours must be shortened."], ["職員の人数を具体的に示す例", "No specific staff count is given; staffing differences support the reasoning."], "地域によって利用者の生活や職員の人数が異なるからだ"],
      ["fact-opinion", "本文で、数値による結果として報告されていることは？", "平日の利用者が前年より三割増えた。", "This is the explicitly reported numerical observation, as distinct from the proposed explanation.", ["仕事帰りの人の増加だけが原因だ。", "The staff member considers it one reason; the text does not establish it as the only cause."], ["すべての図書館が時間を延ばすべきだ。", "This is a universal recommendation the passage explicitly rejects."], ["どの地域でも職員の人数は同じだ。", "This contradicts the stated differences between regions."], "平日の利用者は前年より三割増えた"],
      ["answer-strength", "本文の内容を強めすぎている選択肢は？", "どの図書館でも、開館時間を延ばせば必ず利用者が増える。", "どの and 必ず generalize beyond a single library's observed outcome.", ["この図書館では、平日の利用者が増えた。", "This stays within the reported setting."], ["地域ごとの状況を調べる必要がある。", "This matches the writer's recommendation."], ["地域によって職員の人数が異なる。", "This is explicitly stated and does not overgeneralize the result."], "すべての図書館が開館時間を延ばすべきだとは言えない"],
      ["summary", "第二段落の要約として最も適切なものは？", "一つの成功例をそのまま一般化せず、地域に合う時間を考える必要がある。", "The paragraph limits generalization and recommends a locally informed decision.", ["すべての図書館は、必ず二時間長く開けるべきだ。", "This reverses the explicit warning against universal extension."], ["利用者が増えたので、職員を全員減らすべきだ。", "The text does not recommend removing staff."], ["図書館の利用者は、仕事をしている人だけだ。", "The text mentions more after-work visitors without excluding all other users."], "各地域の状況を調べて、利用しやすい時間を考える"],
      ["structure", "「仕事帰りに立ち寄る人が増えたことが理由の一つだ」で、「仕事帰りに立ち寄る」が説明している語は？", "人", "The relative clause immediately before 人 describes which people are increasing.", ["理由", "理由 belongs to the main predicate; it is not the head noun of this relative clause."], ["仕事", "仕事 is within 仕事帰り and is not the head noun being modified."], ["一つ", "一つ counts reasons and does not head the initial relative clause."], "仕事帰りに立ち寄る人が増えたこと"],
    ] },
  { id: "remote", text: "ある会社は、希望する社員を対象に在宅勤務を試した。参加した社員の半数は、通勤時間が減って仕事に集中しやすくなったと答えた。一方で、相談する機会が少なくなったという人もいた。\n\n在宅勤務には利点も課題もある。例えば、短い質問でも会議を設定しなければならず、負担を感じる場合がある。会社は、社員が気軽に相談できる時間を毎日設けることにした。働く場所を変えるだけでなく、相談の仕組みも整えることが必要だろう。",
    translation: "A company trialed working from home for employees who wished to participate. Half of the participating staff said reduced commuting time made it easier to concentrate. Others reported fewer opportunities to consult colleagues.\n\nWorking from home has both advantages and challenges. For example, having to schedule a meeting even for a short question can be burdensome. The company decided to provide time every day for casual consultation. It is probably necessary to improve the consultation system as well as changing where people work.",
    breakdown: { sentence: "会社は、社員が気軽に相談できる時間を毎日設けることにした。", mainClause: "会社は、ことにした", modifiers: ["社員が気軽に相談できる → 時間を説明する", "時間を毎日設ける → 決めた内容"], explanation: "The main clause describes a company decision. Its content is establishing daily time for consultation; the relative clause tells us what employees can do during that time." },
    questions: [
      ["argument", "「例えば、短い質問でも会議を設定しなければならず」は、何の例か。", "在宅勤務で相談するときの課題", "The example illustrates the burden associated with fewer informal consultation opportunities.", ["通勤時間が減る利点", "The example concerns asking questions, not reduced commuting."], ["社員全員が在宅勤務を希望する理由", "Not all employees are said to want remote work."], ["相談が完全に不要になる仕組み", "The example concerns difficulty consulting, not the elimination of the need."], "在宅勤務には利点も課題もある"],
      ["fact-opinion", "本文で調査への回答として報告されていることは？", "参加した社員の半数が、集中しやすくなったと答えた。", "The passage reports a proportion of trial participants giving this response.", ["すべての仕事を自宅で行うべきだ。", "This recommendation is not made in the text."], ["相談の仕組みは今後一切必要ない。", "This contradicts the concluding recommendation."], ["会議を増やせば、必ず全員が満足する。", "The passage gives no such universal causal claim."], "参加した社員の半数は"],
      ["answer-strength", "本文からは言えない、範囲を広げすぎた結論は？", "会社の社員は全員、在宅勤務で集中しやすくなった。", "The result concerns half of the trial participants, not every employee at the company.", ["在宅勤務を試したのは、希望する社員だった。", "This matches the stated participant group."], ["参加者の中には、相談の機会が減ったと感じる人がいた。", "This preserves the text's limited scope."], ["会社は毎日相談できる時間を設けることにした。", "This is the explicitly stated response."], "希望する社員を対象に在宅勤務を試した"],
      ["summary", "第二段落の要約として最も適切なものは？", "在宅勤務の課題に対応するため、相談しやすい仕組みを整える必要がある。", "The paragraph identifies a consultation challenge and describes a response to it.", ["在宅勤務では質問をすべて禁止するべきだ。", "This reverses the attempt to make consultation easier."], ["通勤時間が減れば、相談の課題はすべてなくなる。", "The paragraph explicitly identifies a remaining consultation problem."], ["社員の希望にかかわらず、必ず自宅で働かせるべきだ。", "This is not recommended and changes the trial's voluntary character."], "相談の仕組みも整えることが必要"],
      ["structure", "「社員が気軽に相談できる時間を毎日設ける」で、「社員が気軽に相談できる」が説明する語は？", "時間", "The modifying clause describes the time being established for consultation.", ["毎日", "毎日 modifies how frequently the main action occurs, not the head noun of the clause."], ["社員", "社員 is the subject inside the clause, not the noun that follows and is modified."], ["設ける", "設ける is the main predicate rather than the head noun of the relative clause."], "社員が気軽に相談できる時間"],
    ] },
  { id: "cups", text: "駅前のカフェが、何度も使えるカップの貸し出しを始めた。最初の一か月で、使い捨てカップの使用数は二割減った。ただし、借りたカップを返し忘れる利用者もいた。\n\n店長は、返却場所が分かりにくいことが原因の一つではないかと考えた。そこで、利用者がすぐに見つけられる返却箱を入口に置いた。ごみを減らす制度を続けるには、利用者の意識だけでなく、無理なく行動できる環境も大切だと考える。",
    translation: "A cafe by the station began lending reusable cups. In the first month, disposable cup use fell by twenty percent. However, some customers forgot to return the borrowed cups.\n\nThe manager thought one cause might be that the return point was hard to find. So a return box that customers could easily spot was placed at the entrance. I believe that sustaining a waste-reduction system requires not only awareness but also an environment that makes action easy.",
    breakdown: { sentence: "利用者がすぐに見つけられる返却箱を入口に置いた。", mainClause: "返却箱を入口に置いた", modifiers: ["利用者がすぐに見つけられる → 返却箱を説明する"], explanation: "The main action is placing a return box at the entrance. The relative clause describes the box's visibility to customers." },
    questions: [
      ["argument", "「そこで、利用者がすぐに見つけられる返却箱を入口に置いた」の役割は？", "返却場所の分かりにくさへの対応を示す。", "The box is a deliberate response to a possible reason for forgotten returns.", ["貸し出し制度をやめるという結論を示す。", "The cafe improves the system rather than abandoning it."], ["カップの材料の種類を説明する。", "The sentence concerns a return location, not cup materials."], ["すべての利用者が返却した証拠を示す。", "The action does not establish that everyone returned their cup."], "返却場所が分かりにくいことが原因の一つ"],
      ["fact-opinion", "数値として報告された結果は？", "最初の一か月で、使い捨てカップの使用数が二割減った。", "This is the reported numerical outcome of the first month.", ["利用者の意識だけが返却を決める。", "The author argues that the environment also matters."], ["返却場所だけが返し忘れの唯一の原因だ。", "The manager proposes one possible cause, not a proven exclusive cause."], ["この制度はすべての店で必ず成功する。", "The text provides no universal prediction of success."], "最初の一か月で、使い捨てカップの使用数は二割減った"],
      ["answer-strength", "本文を言い換える際、断定しすぎているものは？", "返し忘れの原因は、必ず返却場所の分かりにくさだけである。", "The manager considers one possible cause; 必ず and だけ incorrectly make it certain and exclusive.", ["借りたカップを返し忘れた人もいた。", "This matches the limited claim that some customers forgot."], ["店長は、返却場所に問題がある可能性を考えた。", "This preserves the uncertainty of the original."], ["入口に返却箱を置く対応をした。", "This is the stated action."], "原因の一つではないかと考えた"],
      ["summary", "第二段落の要約として最も適切なものは？", "返却しやすい環境を整えることも、制度の継続には大切だ。", "The paragraph links an environmental improvement to sustaining the scheme.", ["カップを返せない人は、二度と店を利用できない。", "The text does not introduce such a penalty."], ["利用者の意識を変えるだけで、環境を変える必要はない。", "This reverses the author's emphasis on an easy-to-use environment."], ["入口に箱を置けば、どんな問題も完全に解決する。", "This turns one intervention into an unsupported universal solution."], "無理なく行動できる環境も大切"],
      ["structure", "「利用者がすぐに見つけられる返却箱を入口に置いた」で、主な動作とその対象は？", "返却箱を置いた。", "The main predicate is 置いた and its object is 返却箱; 見つけられる is inside the modifier.", ["利用者を置いた。", "利用者 is the subject within the modifier, not the object of 置いた."], ["入口がカップを見つけた。", "The sentence does not make the entrance an agent finding cups."], ["利用者を見つけられた。", "This changes both the object and the main action."], "返却箱を入口に置いた"],
    ] },
  { id: "course", text: "地域の講座で授業の録画を公開したところ、欠席した回を後で見直す参加者が増えた。二か月後のアンケートでは、回答者の七割が「復習しやすくなった」と答えた。\n\nしかし、録画があれば教室での授業は不要だ、という結論にはならない。教室では、その場で質問したり、ほかの人と意見を交換したりできる。参加者が自分の都合に合わせて見られる録画と、教室での活動を組み合わせることに意味がある。",
    translation: "When a community course made lesson recordings available, more participants reviewed sessions they had missed. In a questionnaire two months later, seventy percent of respondents said reviewing had become easier.\n\nHowever, this does not mean classroom lessons are unnecessary if recordings exist. In class, people can ask questions immediately and exchange views with others. There is value in combining recordings that participants can watch at their convenience with classroom activities.",
    breakdown: { sentence: "参加者が自分の都合に合わせて見られる録画と、教室での活動を組み合わせることに意味がある。", mainClause: "ことに意味がある", modifiers: ["参加者が自分の都合に合わせて見られる → 録画を説明する", "教室での → 活動を説明する", "録画と活動を組み合わせる → ことの内容"], explanation: "The main clause evaluates combining the two resources as meaningful. Within the nominalized action, と joins recordings and classroom activities, and the long relative clause modifies 録画." },
    questions: [
      ["argument", "「教室では、その場で質問したり、ほかの人と意見を交換したりできる」の役割は？", "教室での授業にも価値があることを支える理由", "These classroom benefits support the argument for combining recordings with in-person activities.", ["録画をすべて禁止するための命令", "The author recommends a combination, not banning recordings."], ["アンケートの回答者数を示す資料", "The sentence gives no count of respondents."], ["教室が不要だという意見への賛成", "The benefits counter, rather than support, the claim that classrooms are unnecessary."], "教室では、その場で質問したり、ほかの人と意見を交換したりできる"],
      ["fact-opinion", "アンケートの結果として報告されたものは？", "回答者の七割が、復習しやすくなったと答えた。", "The text reports a proportion of questionnaire respondents giving this answer.", ["全参加者が、録画だけで十分だと答えた。", "The text says seventy percent of respondents and does not report a recordings-only preference."], ["授業の録画は必ずすべての講座に必要だ。", "This is an unsupported universal recommendation."], ["教室での活動には一切価値がない。", "This contradicts the stated classroom benefits."], "回答者の七割が「復習しやすくなった」と答えた"],
      ["answer-strength", "アンケートについて、本文より範囲を広げすぎている文は？", "すべての参加者が、録画で復習しやすくなったと答えた。", "Seventy percent of respondents is not all participants; both the population and the proportion have been overstated.", ["回答した人の中には、復習しやすくなったと感じる人がいた。", "This cautious statement is supported by the reported seventy percent."], ["アンケートは二か月後に行われた。", "This is explicitly reported."], ["七割の回答者が、復習しやすくなったと答えた。", "This retains the exact reported scope."], "回答者の七割"],
      ["summary", "第二段落の要約として最も適切なものは？", "録画と教室にはそれぞれ利点があり、組み合わせることが有用だ。", "The paragraph contrasts the uses of recordings and classrooms before recommending a combination.", ["録画があるので、教室はすべて閉じるべきだ。", "The paragraph explicitly denies that recordings make classrooms unnecessary."], ["録画は復習には全く役立たない。", "This contradicts the reported reviewing benefit."], ["参加者は他人と意見を交換してはいけない。", "The text presents exchange of views as a classroom benefit, not something forbidden."], "録画と、教室での活動を組み合わせることに意味がある"],
      ["structure", "「参加者が自分の都合に合わせて見られる録画」の中心となる名詞は？", "録画", "The entire preceding clause describes the recordings that participants can watch at a convenient time.", ["参加者", "参加者 is the subject inside the modifier, not the head noun of the complete phrase."], ["都合", "都合 is part of the adverbial expression 自分の都合に合わせて."], ["見られる", "見られる is a verb within the modifying clause, not a noun."], "参加者が自分の都合に合わせて見られる録画"],
    ] },
];

export const READING_SKILL_QUESTIONS: ChoiceQuestion[] = [
  ...existingSkills,
  ...cases.flatMap((source) => source.questions.map(([skill, prompt, answer, why, a, b, c, evidence]) => authoredChoice(
    `reading-skill-${source.id}-${skill}`, `reading-${skill}`, prompt, [[answer, why], a, b, c], why, source.translation,
    { texts: [{ text: source.text, translation: source.translation }], evidence: [evidence], targetSeconds: 120,
      tags: [`exercise:${definitions.find(([id]) => id === `reading-${skill}`)![1]}`, `passage:analysis-${source.id}`],
      ...(skill === "structure" ? { breakdown: source.breakdown } : {}),
      hint: "Check the exact scope of the passage and the role of the sentence the question identifies." },
  ))),
];
