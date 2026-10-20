/** Original preparation exercises, plus the five examples supplied by the user.
 * Stable IDs are progress keys. Fragments in Entry are authored in reading order;
 * the builder shuffles their displayed numbering without changing the sentence. */
export interface N2AssemblyQuestion {
  id: string;
  before: string;
  after: string;
  choices: string[];
  order: number[]; // 1-based choice numbers, in sentence order
  starIndex: number; // 0-based slot, independent of the choice number
  translation: string;
  explanation: string;
}
export interface N2AssemblyLesson {
  id: string;
  title: string;
  strategy: string;
  questions: N2AssemblyQuestion[];
}
type Entry = [before: string, fragments: [string, string, string, string], after: string,
  translation: string, explanation: string];
const permutations = [[2, 0, 3, 1], [1, 3, 0, 2], [3, 2, 1, 0], [0, 2, 1, 3],
  [2, 1, 0, 3], [1, 0, 3, 2], [3, 0, 2, 1], [0, 3, 2, 1]];
let authored = 0;
function lesson(id: string, title: string, strategy: string, entries: Entry[]): N2AssemblyLesson {
  return { id, title, strategy, questions: entries.map(([before, fragments, after, translation, explanation], i) => {
    const permutation = permutations[authored++ % permutations.length];
    return { id: `${id}-${i + 1}`, before, after, choices: permutation.map((n) => fragments[n]),
      order: fragments.map((_, n) => permutation.indexOf(n) + 1), starIndex: 2, translation, explanation };
  }) };
}

const supplied: N2AssemblyLesson = {
  id: "examples", title: "Your five examples · worked practice",
  strategy: "The pasted examples omit the four blank positions. For this practice version, ★ is assumed to be slot 3. The full sentence order is shown after answering; check the original layout if its star is elsewhere.",
  questions: [
    { id: "examples-13", before: "水は蒸発するときに周囲の熱を奪うという性質を持っています。汗をかく", after: "ものです。",
      choices: ["と", "のも", "体温が下がる", "その性質による"], order: [1, 3, 2, 4], starIndex: 2,
      translation: "Water absorbs heat from its surroundings when it evaporates. That same property also explains why sweating lowers body temperature.",
      explanation: "汗をかくと introduces a condition. 体温が下がるの nominalizes the resulting event; も adds it as another example. その性質による modifies もの. Bind と → 体温が下がる → のも before attaching the explanation." },
    { id: "examples-14", before: "朝ご飯はなるべく", after: "済ませてしまうこともある。",
      choices: ["食べるようにしているが", "牛乳だけで", "時間がなくて", "きちんと"], order: [4, 1, 3, 2], starIndex: 2,
      translation: "I try to eat a proper breakfast, but sometimes I am short of time and make do with just milk.",
      explanation: "きちんと modifies 食べる. The が in 食べるようにしているが introduces the contrast. 時間がなくて gives the reason, and 牛乳だけで attaches directly to 済ませる: get by with only milk." },
    { id: "examples-15", before: "慌てた様子で部長と課長が", after: "たとうとしている。何があったのだろうか。",
      choices: ["会議室に", "一度も出てこないまま", "2時間が", "入っていったきり"], order: [1, 4, 2, 3], starIndex: 2,
      translation: "The department and section managers hurried into the meeting room and have not come out once; almost two hours have passed. What could have happened?",
      explanation: "会議室に marks the destination of 入っていく. 入っていったきり means that after going in, they have stayed there. 一度も requires the negative 出てこない. Finally 2時間が is the subject of the printed たとうとしている (経とうとしている)." },
    { id: "examples-16", before: "私がお昼によく行く定食屋は、全部でいくつ", after: "あって、いつも迷う。",
      choices: ["たくさんの種類の", "定食が", "あるか", "わからないぐらい"], order: [3, 4, 1, 2], starIndex: 2,
      translation: "The lunch restaurant I often visit has so many kinds of set meals that I cannot count them all, and I always have trouble choosing.",
      explanation: "いくつあるか is an embedded question. わからない completes 'do not know how many'; ぐらい makes that a degree expression. たくさんの種類の modifies 定食, and 定食が supplies the subject for あって." },
    { id: "examples-17", before: "私の部屋のたんすには、いつかまた", after: "たくさんしまってある。",
      choices: ["と思って", "着るかもしれない", "古い服が", "捨てられずにいる"], order: [2, 1, 4, 3], starIndex: 2,
      translation: "My dresser is full of old clothes that I cannot bring myself to throw away because I think I might wear them again someday.",
      explanation: "いつかまた着るかもしれない is the thought quoted by と思って. 捨てられずにいる describes the clothes that remain undiscarded and therefore precedes 古い服. 古い服が is the subject of たくさんしまってある." },
  ],
};

export const N2_ASSEMBLY_LESSONS: N2AssemblyLesson[] = [supplied,
  lesson("s01", "Find the noun · relative clauses", "Find the noun first, then attach the entire clause that describes it. A relative clause usually ends in a plain verb form directly before the noun.", [
    ["これは、", ["先週", "図書館で", "借りた", "本"], "です。", "This is the book I borrowed at the library last week.", "借りた modifies 本 directly. 図書館で marks where the borrowing happened, so it belongs inside the clause before 借りた. 本 then joins the printed です."],
    ["駅の前に", ["最近", "オープンした", "パン屋が", "ある"], "そうです。", "I hear there is a bakery that recently opened in front of the station.", "最近 modifies オープンした, which describes パン屋. パン屋が is the subject of ある. The printed そうです reports the complete plain-form statement."],
    ["私が", ["日本に", "来た", "理由を", "説明しようと"], "思います。", "I intend to explain why I came to Japan.", "日本に来た describes 理由. 理由を is the object of 説明する; 説明しようと connects to 思います as an intention. Do not separate 来た from its head noun 理由."],
    ["昨日", ["先生が", "紹介してくださった", "方に", "お礼を"], "言いたいです。", "I want to thank the person the teacher introduced yesterday.", "先生が紹介してくださった modifies 方. 方に identifies the person receiving thanks; お礼を is the object of 言う. The giver inside the relative clause is not the recipient of the thanks."],
    ["この資料は、", ["来月", "行われる", "会議で", "使う"], "予定です。", "We plan to use these materials at the meeting that will be held next month.", "来月行われる describes 会議. 会議で marks the setting for 使う, and 使う予定です expresses the plan. Meeting time belongs inside the noun phrase, before 会議."],
  ]),
  lesson("s02", "Turn a clause into a noun · の / こと", "Particles such as は, が and を often attach to a whole event through の or こと. First identify where the event ends, then build the main predicate.", [
    ["私が驚いたのは、", ["彼が一人で", "この機械を作った", "という", "こと"], "です。", "What surprised me was that he built this machine by himself.", "彼が一人で gives the actor and manner of この機械を作った. という follows the complete statement; こと turns its content into the noun needed before です. Keep ということ together after the event."],
    ["外国語を", ["毎日", "少しずつ", "勉強することが", "大切だと"], "思います。", "I think it is important to study a foreign language a little every day.", "毎日少しずつ modifies 勉強する. ことが makes the activity the subject of 大切だ; と then quotes that judgment before 思います."],
    ["この仕事を", ["期限までに", "終わらせるのは", "思ったより", "難しかった"], "です。", "Finishing this work by the deadline was harder than I expected.", "期限までに sets the deadline for 終わらせる. のは makes that task the topic. 思ったより modifies 難しかった, which connects to the printed です."],
    ["会議中に誰も", ["携帯電話が鳴った", "のを", "気にしなかった", "よう"], "です。", "It seems nobody minded the mobile phone ringing during the meeting.", "携帯電話が鳴った is the event; のを makes it the object of 気にする. The printed 誰も requires the negative 気にしなかった. ようです comments on the completed observation."],
    ["彼女が", ["毎朝", "走っているのは", "健康を", "保つため"], "です。", "She runs every morning to stay healthy.", "毎朝走っているのは introduces the activity to be explained. 健康を is the object of 保つ; 保つためです supplies the purpose. Build the explanation after the nominalized topic."],
  ]),
  lesson("s03", "Embedded questions · か / かどうか", "Question words stay inside the clause ending in か. For a yes/no uncertainty, bind the plain clause to かどうか before adding 確認する, わからない or 決める.", [
    ["明日の会議が", ["何時に", "始まるか", "知っている人は", "います"], "か。", "Does anyone know what time tomorrow's meeting starts?", "何時に始まるか is the embedded question. 知っている modifies 人, 人は introduces the person sought, and います joins the printed question particle か."],
    ["電話で、この店が日曜日も", ["開いている", "かどうかを", "確認して", "ください"], "。", "Please check by phone whether this shop is open on Sundays too.", "開いているかどうかを makes the shop's opening status the yes/no issue being checked. 確認してください is the request. The printed 電話で gives the means of checking, and 日曜日も stays inside the embedded question."],
    ["どの大学に", ["進学するかは", "家族と", "相談してから", "決めるつもり"], "です。", "I plan to decide which university to attend after discussing it with my family.", "どの大学に進学するか is the decision topic, marked by は. 家族と attaches to 相談する. 相談してから establishes that the discussion precedes 決める."],
    ["この言葉を", ["日本語で", "どう", "説明すればいいか", "わかりません"], "でした。", "I did not know how to explain this word in Japanese.", "日本語で gives the language. どう説明すればいいか asks how one should explain it. わかりません combines with the printed でした to place the uncertainty in the past."],
    ["参加者が", ["何人", "集まるかによって", "部屋の広さを", "変える必要が"], "あります。", "We need to change the room size depending on how many participants come.", "何人集まるか is an embedded quantity question; によって makes the number the determining factor. 部屋の広さを is the object of 変える, and 必要があります closes the requirement."],
  ]),
  lesson("s04", "Quote a thought · と / という", "Look for the complete thought before と. という can turn that quotation into a modifier of an idea, message or noun; ように can introduce an instruction.", [
    ["彼は", ["来年", "日本で", "働きたいと", "言って"], "います。", "He says he wants to work in Japan next year.", "来年日本で働きたい is the quoted desire. と introduces it to 言う; 言っています reports what he says. Place the location inside the desire, before 働きたい."],
    ["田中さんから、", ["電車が", "遅れているので", "少し遅れるという", "連絡が"], "ありました。", "Tanaka sent word that they would be a little late because the train was delayed.", "電車が遅れているので supplies the reason within the message. 少し遅れるという modifies 連絡. 連絡が pairs with the printed ありました."],
    ["私は", ["失敗しても", "あきらめないことが", "大切だと", "考えて"], "います。", "I believe it is important not to give up even if you fail.", "失敗しても introduces the concession inside the quoted thought. あきらめないことが is the subject of 大切だ. と attaches the entire judgment to 考える."],
    ["先生に、", ["わからないことが", "あったら", "遠慮せずに", "質問するように"], "言われました。", "My teacher told me to ask without hesitation if there was anything I did not understand.", "わからないことがあったら is the condition. 遠慮せずに modifies 質問する. 質問するように言われた reports an instruction, rather than a direct quotation ending in と."],
    ["この町では、", ["古い建物を", "大切にしようという", "考え方が", "広がって"], "います。", "The idea of preserving old buildings is spreading in this town.", "古い建物を is the object of 大切にする. The volitional 大切にしようという describes 考え方. 考え方が is the subject of 広がっています."],
  ]),
  lesson("s05", "Habits and changes · ように", "Separate a deliberate habit (ようにする) from a change in ability or behavior (ようになる). Keep ように attached to the verb it frames.", [
    ["健康のために、", ["できるだけ", "階段を", "使うように", "して"], "います。", "For my health, I make a point of using the stairs whenever possible.", "階段を is the object of 使う. 使うようにしています describes a deliberate habit. できるだけ qualifies that effort and precedes the object and verb."],
    ["日本に来てから、", ["字幕がなくても", "ニュースが", "わかる", "ように"], "なりました。", "Since coming to Japan, I have become able to understand the news even without subtitles.", "字幕がなくても is a concessive condition. ニュースが is the thing understood by わかる. Keep わかる → ように → なりました together: this frame expresses an acquired ability."],
    ["大事な約束を", ["忘れないように", "手帳に", "書いておくことに", "して"], "います。", "I make it a rule to write important appointments in my planner so I will not forget them.", "忘れないように gives the prevention goal. 手帳に marks the destination of the writing. 書いておくことにしています describes a rule for making a record in advance."],
    ["このボタンを押すと", ["自動的に電源が", "切れる", "ように", "なって"], "います。", "The device is designed so that pressing this button automatically switches off the power.", "The printed 押すと introduces the trigger. 電源が is the subject of 切れる, modified by 自動的に. 切れる → ように → なっています describes the device's arrangement; the dictionary form must precede ように."],
    ["隣の部屋で", ["子どもが", "寝ているので", "大きな声を", "出さないように"], "してください。", "A child is sleeping next door, so please avoid speaking loudly.", "子どもが寝ているので supplies the reason. 大きな声を is the object of 出す. 出さないようにしてください requests an effort to avoid the action."],
  ]),
  lesson("s06", "Decisions · ことに / ことになった", "Find whose decision it is: ことにする often presents a choice; ことになる presents an arrangement or outcome. Attach the planned action before こと.", [
    ["よく考えた結果、", ["今の会社を", "辞めて", "留学することに", "決め"], "ました。", "After careful thought, I decided to leave my current company and study abroad.", "今の会社を辞めて is the action preceding study abroad. 留学することに決めた expresses the decision. 辞めて must follow its object 会社を."],
    ["話し合いの結果、", ["来月から", "新しい制度を", "導入することに", "なり"], "ました。", "Following discussions, it was decided to introduce a new system next month.", "来月から gives the start date. 新しい制度を is the object of 導入する. 導入することになりました presents the agreed arrangement."],
    ["私は", ["夜九時以降は", "何も", "食べないことに", "して"], "います。", "I make it a rule not to eat anything after nine at night.", "夜九時以降は sets the time frame. 何も requires the negative 食べない. 食べないことにしています describes a personal rule, rather than an inability."],
    ["台風の影響で、", ["明日", "予定されていた", "試合は", "中止されることに"], "なりました。", "Because of the typhoon, the match scheduled for tomorrow has been canceled.", "明日予定されていた is a relative clause describing 試合. 試合は introduces the topic; 中止されることになりました states the resulting arrangement."],
    ["迷った末に、", ["今回は", "車ではなく", "電車で", "行くことに"], "しました。", "After some hesitation, I decided to go by train rather than by car this time.", "今回は frames the decision. 車ではなく電車で contrasts the means of transport. 行くことにしました must come last to complete the personal choice."],
  ]),
  lesson("s07", "Reasons · わけ / ため / おかげ", "Build the cause before its connector. A noun needs の before ため or おかげ; a plain verb clause can attach directly. わけではない limits a claim rather than simply denying everything.", [
    ["毎日練習した", ["おかげで", "以前より", "上手に", "話せるように"], "なりました。", "Thanks to daily practice, I can now speak better than before.", "練習したおかげで gives a favorable cause. 以前より compares ability; 上手に modifies 話せる. 話せるようになりました expresses the resulting improvement."],
    ["電車が", ["事故の", "ために", "止まってしまったので", "歩いて帰るしか"], "ありませんでした。", "The train stopped because of an accident, so I had no choice but to walk home.", "事故のために binds the noun cause to the connector. 止まってしまったので explains the consequence, and 歩いて帰るしかありませんでした states the only remaining option."],
    ["値段が", ["高いからといって", "必ずしも", "品質がいい", "わけでは"], "ありません。", "A high price does not necessarily mean good quality.", "高いからといって rejects an automatic inference from price. 必ずしも pairs with the negative わけではありません; 品質がいい is the proposition being qualified."],
    ["彼は十年間", ["日本で", "暮らしていたのだから", "日本の習慣に", "詳しい"], "わけだ。", "He lived in Japan for ten years, so it makes sense that he knows its customs well.", "日本で暮らしていたのだから supplies the evidence. 日本の習慣に詳しい is the justified conclusion. The printed わけだ marks understanding of why that conclusion holds."],
    ["この道が", ["混んでいるのは", "近くで工事を", "している", "ため"], "です。", "This road is congested because construction is taking place nearby.", "混んでいるのは frames the situation requiring explanation. 近くで工事をしている is the cause. The plain clause している directly precedes ため, and ためです closes the explanation."],
  ]),
  lesson("s08", "Concessions · のに / くせに / ながら", "Find the contrast between expectation and reality. Keep the first clause attached to のに or くせに, then check that the final predicate expresses the unexpected result.", [
    ["何度も", ["説明した", "にもかかわらず", "彼はまだ", "理解していない"], "ようです。", "Despite repeated explanations, he still does not seem to understand.", "説明したにもかかわらず marks the concession. 彼はまだ introduces the continuing unexpected situation. 理解していない joins ようです to express the speaker's observation."],
    ["彼は", ["知っている", "くせに", "何も", "教えてくれない"], "んです。", "He knows, yet he will not tell me anything.", "知っているくせに links knowledge to a critical contrast. 何も requires 教えてくれない. The negative predicate supplies the behavior criticized by くせに."],
    ["この部屋は", ["狭い", "ながらも", "必要な設備が", "すべてそろって"], "います。", "Although this room is small, it has all the necessary facilities.", "狭いながらも concedes the limited size. 必要な設備が is the subject of そろう. すべてそろっています supplies the positive fact that contrasts with the small space."],
    ["十分に", ["準備した", "つもりだったのに", "本番では", "緊張してしまい"], "ました。", "I thought I had prepared thoroughly, but I became nervous during the actual performance.", "準備したつもりだったのに states a belief followed by an unexpected result. 本番では sets the contrasting setting. 緊張してしまい joins ました to express the unfortunate outcome."],
    ["彼女は忙しい", ["と言い", "ながら", "毎週旅行に", "出かけて"], "います。", "She says she is busy, yet she goes traveling every week.", "The printed 忙しい is quoted by と言い. The stem 言い joins ながら, making a contrast with 毎週旅行に出かけています. Here ながら contrasts her words and actions."],
  ]),
  lesson("s09", "Conditions · さえ〜ば / ない限り", "Spot paired markers. さえ needs a condition such as ば; ない限り sets a boundary. Check the scope of the negative before choosing the star.", [
    ["使い方", ["さえ", "わかれば", "誰でも簡単に", "操作できる"], "機械です。", "This machine is easy for anyone to operate as long as they know how to use it.", "使い方さえわかれば states the sufficient condition. 誰でも簡単に modifies 操作できる, and 操作できる describes the printed 機械. Keep さえ adjacent to what is sufficient."],
    ["雨が", ["降らない", "限り", "予定どおり", "試合を行う"], "そうです。", "I hear the match will go ahead as scheduled unless it rains.", "降らない限り means as long as it does not rain. 予定どおり modifies 試合を行う. The printed そうです reports the complete plan; it does not belong inside the condition."],
    ["一度", ["引き受けた", "以上は", "最後まで", "責任を持つべき"], "です。", "Once you have accepted the task, you should take responsibility through to the end.", "引き受けた以上は treats acceptance as a premise that creates an obligation. 最後まで modifies 責任を持つ. べきです closes the duty that follows from the premise."],
    ["留学する", ["からには", "言葉だけでなく", "その国の文化も", "学びたい"], "です。", "Since I am going to study abroad, I want to learn the country's culture as well as its language.", "留学するからには sets the committed premise. 言葉だけでなくその国の文化も forms an additive pair. 学びたいです is the intention that follows."],
    ["実際に", ["使ってみない", "ことには", "便利かどうか", "判断できません"], "よ。", "Unless you actually try it, you cannot judge whether it is convenient.", "使ってみないことには establishes the unmet prerequisite. 便利かどうか is the question being judged. 判断できません supplies the negative outcome expected after ないことには."],
  ]),
  lesson("s10", "Sequence · てからでないと / 上で", "Identify what must happen first. てからでないと needs a negative result; た上で means after completing a prerequisite. Tense is a strong ordering clue.", [
    ["説明を", ["最後まで", "聞いてからでないと", "質問には", "答えられません"], "よ。", "I cannot answer the question until I have heard the explanation to the end.", "最後まで modifies 聞く. 聞いてからでないと requires completion first. 質問には identifies what cannot be answered, and 答えられません provides the negative consequence."],
    ["契約書を", ["よく", "読んだ", "上で", "署名して"], "ください。", "Please sign after reading the contract carefully.", "よく modifies 読む. 読んだ上で requires reading to be completed before the next action. 署名して joins ください. The past form before 上で is the key prerequisite cue."],
    ["新しい仕事を", ["始める", "にあたって", "必要な資格を", "確認しておくべき"], "です。", "Before starting a new job, you should check the qualifications you need.", "始めるにあたって marks the occasion of starting. 必要な資格を is the object of 確認する. 確認しておくべきです recommends checking in preparation."],
    ["家を", ["出た", "とたんに", "急に雨が", "降り出し"], "ました。", "Just as I left home, it suddenly started raining.", "出たとたんに requires the past form 出た and marks an immediate subsequent event. 急に雨が leads to 降り出しました. The sudden rain is the unexpected event."],
    ["電車を", ["待っている", "うちに", "だんだん", "眠くなってき"], "ました。", "While waiting for the train, I gradually became sleepy.", "待っているうちに frames the interval during which a change occurs. だんだん modifies 眠くなってきました. The progression of sleepiness belongs after the waiting interval."],
  ]),
  lesson("s11", "Time boundaries · 以来 / きり / 末に", "Look at what continues after an event. 以来 marks a continuing span; きり often signals no return or repetition; 末に introduces the outcome of a long process.", [
    ["彼とは", ["卒業式で", "会った", "きり", "一度も話していない"], "んです。", "I have not spoken to him once since seeing him at graduation.", "卒業式で locates 会った. 会ったきり marks the last contact, and 一度も話していない gives the absence of later contact. Keep the past event immediately before きり."],
    ["日本に", ["来て", "以来", "毎日", "日記をつけて"], "います。", "I have kept a diary every day since coming to Japan.", "来て以来 joins the initiating event to a continuing practice. 毎日 modifies 日記をつける. The printed います completes the ongoing habit."],
    ["何度も", ["話し合った", "末に", "ようやく", "結論が出た"], "そうです。", "I hear they finally reached a conclusion after many discussions.", "話し合った末に introduces the result of a process. ようやく emphasizes the eventual outcome. 結論が出た is the complete statement reported by そうです."],
    ["長い間", ["悩んだ", "あげく", "結局", "買うのをやめ"], "ました。", "After agonizing over it for a long time, I ended up deciding not to buy it.", "悩んだあげく frames the outcome after prolonged indecision. 結局 reinforces the eventual result. 買うのをやめました nominalizes the purchase as the action abandoned."],
    ["この本を", ["読み始めて", "からというもの", "続きが気になって", "夜も眠れない"], "んです。", "Ever since I started this book, I have been so curious about what happens next that I cannot sleep at night.", "読み始めてからというもの emphasizes a change continuing from a starting event. 続きが気になって gives the cause of 夜も眠れない. The curiosity must precede its effect."],
  ]),
  lesson("s12", "Paired expressions · だけでなく / ば〜ほど", "Treat both halves of a grammar pair as one frame. The words between them still need a complete predicate or noun phrase; matching markers alone is not enough.", [
    ["この店は", ["料理が", "おいしい", "だけでなく", "値段も安い"], "です。", "This restaurant's food is not only delicious but also inexpensive.", "料理がおいしい is the first proposition. だけでなく connects it to 値段も安い. も marks the added favorable property, so the price clause follows the connector."],
    ["日本語は", ["勉強すれば", "するほど", "面白く", "なる"], "と思います。", "I think Japanese becomes more interesting the more you study it.", "勉強すればするほど is a fixed proportional frame. 面白く is the adverbial form needed before なる. と quotes the complete conclusion before 思います."],
    ["彼は", ["英語は", "もちろん", "中国語まで", "話せる"], "そうです。", "I hear he speaks not only English, naturally, but even Chinese.", "英語はもちろん establishes the expected ability. 中国語まで adds a more surprising one. 話せる supplies the predicate for both languages before hearsay そうです."],
    ["この問題は", ["子ども", "ばかりか", "大人にも", "難しい"], "ようです。", "This problem seems difficult not only for children but also for adults.", "子どもばかりか大人にも expands the affected group. 大人にも marks who also finds it difficult. 難しい joins ようです to state the observation."],
    ["この仕事は", ["経験の", "有無を", "問わず", "応募できる"], "そうです。", "I hear you can apply for this job regardless of whether you have experience.", "経験の有無 is a noun phrase meaning the presence or absence of experience. 有無を問わず makes it irrelevant to eligibility. 応募できる is the resulting possibility."],
  ]),
  lesson("s13", "Degrees and limits · ほど / ぐらい / 限り", "Complete the comparison or degree clause before attaching ほど or ぐらい. With 限りでは, separate the limits of your evidence from the conclusion.", [
    ["昨日は", ["声が", "出なくなる", "ほど", "大声で応援した"], "んです。", "Yesterday I cheered so loudly that I lost my voice.", "声が出なくなる describes the degree of the cheering and must stay before ほど. 大声で応援した is the main event. The result-like clause is placed first in this degree construction."],
    ["この店には、", ["どれを", "選べばいいか", "迷うほど", "たくさんの商品が"], "あります。", "This shop has so many products that it is hard to decide which to choose.", "どれを選べばいいか is the embedded question. 迷うほど describes the abundance. たくさんの商品が supplies the subject for the printed あります."],
    ["私が", ["調べた", "限りでは", "その情報は", "正しい"], "ようです。", "As far as I have checked, that information seems correct.", "調べた限りでは restricts the evidence for the claim. その情報は introduces the claim's topic and 正しいようです states the tentative conclusion. Do not put the conclusion inside the evidence phrase."],
    ["忙しくても、", ["電話を", "一本", "かけるぐらいの", "時間はある"], "でしょう。", "Even if you are busy, surely you have enough time to make one phone call.", "電話を一本かける is a complete action with a counter. ぐらいの turns it into a modifier of 時間. 時間はあるでしょう gives the amount of time that should be available."],
    ["期待していた", ["ほど", "難しくは", "なかった", "というのが"], "正直な感想です。", "My honest impression is that it was not as difficult as I had expected.", "期待していたほど sets the expected degree. 難しくはなかった is the limited negative comparison. というのが nominalizes that whole impression as the subject of 正直な感想です."],
  ]),
  lesson("s14", "Viewpoints · にとって / として / 上で", "にとって marks whose evaluation it is; として marks a role; 上で marks the activity being discussed. Use the final predicate to distinguish them.", [
    ["この経験は、", ["将来", "教師を目指す", "私にとって", "とても貴重なもの"], "です。", "This experience is very valuable to me as someone hoping to become a teacher.", "将来教師を目指す modifies 私. 私にとって gives the evaluator. とても貴重なものです supplies that evaluation. The teacher aspiration stays inside the description of 私."],
    ["彼は", ["この分野の", "専門家", "として", "広く知られて"], "います。", "He is widely known as an expert in this field.", "この分野の modifies 専門家. 専門家として identifies the role in which he is known. 広く知られています is the main predicate."],
    ["海外で", ["生活する", "上で", "言葉の壁は", "大きな問題に"], "なります。", "The language barrier becomes a major issue when living abroad.", "生活する上で marks the practical context. 言葉の壁は is the main topic and 大きな問題になります states what it becomes. The dictionary form before 上で means 'in doing', not 'after doing'."],
    ["環境を", ["守る", "という点から", "考えると", "公共交通の利用が望ましい"], "です。", "From the viewpoint of protecting the environment, using public transport is desirable.", "守るという点から sets the viewpoint. 考えると introduces the evaluation from that viewpoint. 公共交通の利用が望ましい is the complete judgment."],
    ["消費者の", ["立場に", "立って", "考えた", "商品づくりが必要"], "です。", "Product development needs to be considered from the consumer's perspective.", "消費者の立場に立って forms the perspective phrase. 考えた modifies 商品づくり. 商品づくりが必要です states what is needed; the past-form modifier comes directly before that noun."],
  ]),
  lesson("s15", "Causes and dependence · によって / 応じて", "Connect the factor to the result it controls. Look for paired change expressions such as につれて and にしたがって, and distinguish a cause from a condition.", [
    ["利用者の", ["年齢に", "応じて", "サービスの内容を", "変える必要が"], "あります。", "The service needs to vary according to users' ages.", "利用者の年齢に応じて identifies the factor used for adjustment. サービスの内容を is the object of 変える. 必要があります closes the requirement."],
    ["料金は", ["利用する", "時間帯に", "よって", "異なる"], "そうです。", "I hear the charge varies depending on the time of day you use the service.", "利用する modifies 時間帯. 時間帯によって identifies the source of variation. 異なるそうです reports the differing rates. The noun must intervene between its modifier and によって."],
    ["気温が", ["上がる", "につれて", "冷たい飲み物が", "よく売れるように"], "なりました。", "As temperatures rose, cold drinks started selling well.", "上がるにつれて links a gradual temperature increase to another change. 冷たい飲み物が is the subject of 売れる. よく売れるようになりました gives the developing result."],
    ["調査が", ["進む", "にしたがって", "新しい事実が", "次々と明らかに"], "なった。", "As the investigation progressed, new facts came to light one after another.", "進むにしたがって establishes parallel development. 新しい事実が is the subject of 明らかになる. 次々と describes the successive discoveries."],
    ["この問題は、", ["見方を", "変える", "ことによって", "解決できるかもしれない"], "と思います。", "I think this problem may be solvable by changing our perspective.", "見方を変える is the means; ことによって nominalizes the action as a method. 解決できるかもしれない is the possibility quoted before 思います."],
  ]),
  lesson("s16", "Negative scope · わけには / とは限らない", "Locate exactly what is being denied: an obligation prevents an action in わけにはいかない, while とは限らない denies certainty. Do not mistake these for a simple cannot.", [
    ["大切な会議なので、", ["熱が", "あっても", "休むわけには", "いかない"], "んです。", "It is an important meeting, so I cannot take the day off even if I have a fever.", "熱があっても states the concession. 休むわけにはいかない expresses a social or practical obligation that prevents taking leave. The negative belongs to いかない, not to 休む."],
    ["安い商品が", ["必ずしも", "悪い", "とは", "限らない"], "んです。", "An inexpensive product is not necessarily bad.", "必ずしも pairs with とは限らない to deny an automatic conclusion. 悪い is the judgment whose certainty is rejected. と must follow the complete adjective proposition."],
    ["約束した", ["以上", "行かない", "わけには", "いかない"], "でしょう。", "Since you promised, you cannot simply choose not to go.", "約束した以上 establishes the obligation. 行かないわけにはいかない uses a negative action inside the obligation frame, so its overall implication is that one must go."],
    ["彼の説明は", ["理解できない", "ことも", "ないが", "納得はできない"], "です。", "It is not that I cannot understand his explanation, but I cannot accept it.", "理解できないこともない is a double-negative expression of limited understanding. が then contrasts understanding with acceptance. 納得はできない supplies the negative conclusion."],
    ["この仕事は", ["一人では", "できない", "という", "わけではない"], "んです。", "It is not the case that this job cannot be done by one person.", "一人ではできない is the claim being considered. というわけではない qualifies or rejects that claim. Putting わけではない before the quoted claim would break the scope."],
  ]),
  lesson("s17", "Possibility · かねない / ざるを得ない", "Check the form immediately before the expression. かねない follows a verb stem and often warns of harm; ざるを得ない attaches to a negative-base form and means there is no alternative.", [
    ["そんな運転を", ["続けていると", "大きな事故を", "起こし", "かねない"], "ですよ。", "If you keep driving like that, you could cause a serious accident.", "続けていると states the risky condition. 大きな事故を is the object of 起こす. The stem 起こし directly precedes かねない to warn of an undesirable possibility."],
    ["資料が", ["足りないため", "計画を", "変更せざるを", "得ない"], "状況です。", "We are in a situation where we have no choice but to change the plan because there is insufficient information.", "足りないため completes the reason begun by 資料が. 計画を is the object of 変更する. する becomes せ in 変更せざるを得ない; the whole expression modifies 状況."],
    ["このままでは", ["多くの人に", "迷惑を", "かける", "おそれがある"], "と思います。", "I think that at this rate we risk causing trouble for many people.", "多くの人に marks those affected; 迷惑を is the object of かける. かけるおそれがある describes a risk and is the complete thought quoted before 思います."],
    ["詳しい事情が", ["わからないので", "今は", "お答えし", "かねます"], "が、確認してみます。", "I do not know the details, so I cannot answer right now, but I will check.", "わからないので gives the reason. 今は frames the present limitation. お答えしかねます politely says the speaker cannot provide an answer; unlike かねない, it expresses inability."],
    ["彼が", ["そんなことを", "言う", "はずが", "ない"], "と思います。", "I do not believe he could have said such a thing.", "そんなことを言う is the action ruled out. はずがない expresses a strong expectation that it is impossible. と follows the completed negative judgment before 思います."],
  ]),
  lesson("s18", "Difficulty and feelings · にくい / がたい", "Connect the correct verb stem to にくい, がたい or ようがない. Distinguish physical difficulty from emotional inability and from having no means to do something.", [
    ["この字は", ["小さすぎて", "年を取った", "人には", "読みにくい"], "と思います。", "I think these characters are too small and difficult for elderly people to read.", "小さすぎて gives the cause. 年を取った modifies 人, and 人には identifies who has difficulty. 読みにくい is the judgment quoted before 思います."],
    ["長年", ["住み慣れた", "町を", "離れるのは", "耐えがたい"], "ことだった。", "Leaving the town I had lived in for years was unbearable.", "住み慣れた modifies 町. 町を is the place being left; 離れるのは makes that departure the topic. 耐えがたい describes the emotional difficulty before ことだった."],
    ["連絡先を", ["知らない", "のだから", "こちらからは", "連絡しようがない"], "でしょう。", "Since we do not know their contact details, there is no way for us to contact them.", "知らないのだから states the missing prerequisite. こちらからは specifies our side. 連絡しようがない means there is no means to make contact, not simply that it would be inconvenient."],
    ["何度読み返しても", ["彼の説明は", "私には理解し", "がたい", "もの"], "でした。", "No matter how many times I reread it, I found his explanation hard to understand.", "The printed 何度読み返しても is the concession. 彼の説明は introduces the topic, and 私には identifies the evaluator. The stem 理解し joins がたい; 理解しがたい modifies もの before the printed でした."],
    ["この靴は", ["軽くて", "歩きやすい", "上に", "値段も手ごろ"], "です。", "These shoes are light and easy to walk in, and they are reasonably priced too.", "軽くて歩きやすい describes the first advantage. 上に adds another advantage; 値段も手ごろ supplies it. に in 上に is part of the additive expression."],
  ]),
  lesson("s19", "Giving and receiving · てもらう / いただく", "Track who acts and who benefits. に can mark the person doing a favor in てもらう; the favor itself must precede もらう or いただく.", [
    ["先生に", ["作文を", "直して", "いただいた", "おかげで"], "助かりました。", "I was helped by having my teacher correct my essay.", "作文を is the object of 直す. 直していただいた humbly presents the favor received from the teacher. おかげで makes that favor the beneficial cause of 助かりました."],
    ["友達が", ["駅まで", "迎えに", "来てくれた", "ので"], "迷わずに済みました。", "My friend came to meet me at the station, so I did not get lost.", "駅まで sets the extent of the trip. 迎えに gives the purpose of 来る. 来てくれた presents the friend's helpful action, and ので links it to the favorable result."],
    ["こちらに", ["お名前と", "ご住所を", "ご記入", "いただけます"], "か。", "Could you please enter your name and address here?", "お名前とご住所を forms a coordinated object. ご記入いただけますか is a polite request for the listener's action. The noun 記入 must remain directly before いただけます."],
    ["急なお願いにも", ["かかわらず", "快く", "引き受けて", "くださって"], "ありがとうございます。", "Thank you for kindly agreeing despite the short notice.", "急なお願いにもかかわらず gives the concession. 快く modifies 引き受ける. 引き受けてくださって connects the favor to the printed expression of thanks."],
    ["部長には", ["お忙しい", "ところを", "相談に", "乗っていただき"], "ました。", "The department manager kindly made time to advise me despite being busy.", "お忙しいところを acknowledges the inconvenient circumstances. 相談に乗る is the fixed expression for giving advice. 乗っていただきました humbly describes receiving that help."],
  ]),
  lesson("s20", "Passive and causative · who did what?", "Use に and を to track the actor and the affected person. In させてもらう, the speaker receives permission to do the action; in a passive, the subject receives the action.", [
    ["私は", ["先生に", "作文の間違いを", "指摘されて", "初めて"], "気づきました。", "I noticed the mistake in my essay only after my teacher pointed it out.", "先生に identifies the actor in the passive 指摘される; 作文の間違いを is what was pointed out. 指摘されて leads to 初めて気づきました, the first realization after that event."],
    ["子どものころ、", ["母に", "嫌いな野菜を", "食べさせられた", "ことを"], "覚えています。", "I remember being made by my mother to eat vegetables I disliked as a child.", "母に marks the person making the child eat. 嫌いな野菜を is the object of eating. 食べさせられたことを nominalizes the remembered causative-passive event."],
    ["今日は", ["体調が", "よくないので", "早めに帰らせて", "いただいても"], "よろしいでしょうか。", "I am not feeling well today; may I leave early?", "体調がよくないので supplies the reason. 帰らせていただく humbly asks to receive permission to leave. いただいてもよろしいでしょうか forms the permission request."],
    ["この建物は", ["百年前に", "建てられた", "ものだと", "言われて"], "います。", "This building is said to have been built a hundred years ago.", "百年前に locates the construction. 建てられた modifies もの, and ものだと gives the quoted claim. 言われています is the reportative passive."],
    ["後輩に", ["同じ失敗を", "繰り返させない", "ために", "手順を説明しておく"], "必要がある。", "We need to explain the procedure in advance so that junior colleagues do not repeat the same mistake.", "同じ失敗を is the object of 繰り返す. 繰り返させないために states the prevention goal, with 後輩に as the person guided. 手順を説明しておく is the necessary advance action."],
  ]),
  lesson("s21", "Formal connectors · に際して / に基づいて", "Identify the noun phrase before a formal connector. に際して marks an occasion, に基づいて a basis, and をめぐって an issue of debate.", [
    ["新しい制度の", ["導入に", "際して", "利用者への", "説明会を開く"], "予定です。", "We plan to hold an explanatory meeting for users when introducing the new system.", "新しい制度の導入に際して marks the occasion. 利用者への modifies 説明会, identifying its audience. 説明会を開く予定です states the planned action."],
    ["今回の調査で", ["得られた", "データに", "基づいて", "報告書を作成した"], "そうです。", "I hear the report was prepared on the basis of data obtained in this survey.", "得られた modifies データ. データに基づいて identifies the basis of the report. 報告書を作成した is the complete past event reported by そうです."],
    ["駅前の", ["再開発を", "めぐって", "住民の間で", "意見が分かれて"], "います。", "Residents are divided over the redevelopment in front of the station.", "駅前の再開発 is the issue; をめぐって introduces the debate. 住民の間で identifies the group in which opinions differ. 意見が分かれています closes the statement."],
    ["この工事は", ["近隣住民の", "理解と協力", "なしには", "進められない"], "ものです。", "This construction cannot proceed without local residents' understanding and cooperation.", "近隣住民の modifies the coordinated noun phrase 理解と協力. なしには establishes the indispensable condition. 進められない supplies the required negative result."],
    ["この施設は", ["年齢や", "国籍に", "関係なく", "誰でも利用できる"], "そうです。", "I hear anyone may use this facility regardless of age or nationality.", "年齢や国籍 coordinates the two attributes. に関係なく makes them irrelevant to eligibility. 誰でも利用できる is the resulting rule reported by そうです."],
  ]),
  lesson("s22", "Compound boundaries · をはじめ / ばかりに", "Memorize expressions as complete chunks, but still identify what each chunk modifies. をはじめ introduces a representative example; ばかりに gives a cause with an unfortunate result.", [
    ["東京を", ["はじめ", "全国の", "主要都市で", "開催される"], "イベントです。", "This event will be held in Tokyo and other major cities across the country.", "東京をはじめ introduces Tokyo as a representative location. 全国の modifies 主要都市; 主要都市で marks where 開催される happens. The final verb modifies イベント."],
    ["忙しさの", ["あまり", "友人との", "大切な約束を", "忘れてしまった"], "んです。", "I was so busy that I forgot an important appointment with a friend.", "忙しさのあまり gives an excessive state as the cause. 友人との modifies 大切な約束. 約束を is the object of 忘れてしまった, the unintended result."],
    ["安いという", ["理由だけで", "買った", "ばかりに", "後悔することになった"], "んです。", "I ended up regretting the purchase because I bought it solely for its low price.", "安いという理由だけで gives the sole purchase motive. 買ったばかりに links that action to an unfortunate consequence. 後悔することになった is the resulting regret."],
    ["大雨にも", ["かかわらず", "多くの人が会場に", "足を", "運んだ"], "そうです。", "I hear many people came to the venue despite the heavy rain.", "大雨にもかかわらず marks the concession. 多くの人が会場に supplies the main subject and destination. 足を運んだ completes the action: 足を運ぶ is the fixed expression for making one's way somewhere."],
    ["彼は", ["自分の利益を", "考える", "ばかりで", "周囲のことを気にしない"], "んです。", "He only thinks of his own interests and does not care about those around him.", "自分の利益を考える is the exclusive focus. ばかりで connects it to the neglectful behavior. 周囲のことを気にしない gives the negative counterpart."],
  ]),
  lesson("s23", "Expectations · つもり / もの / ことはない", "Look for the speaker's stance after the main action. つもり can describe intention or belief, ものだ a general tendency, and ことはない can say there is no need.", [
    ["十分に", ["確認した", "つもりだったが", "実際には", "間違いが残っていた"], "んです。", "I thought I had checked thoroughly, but mistakes actually remained.", "確認したつもりだった expresses the speaker's belief about a completed action. が contrasts that belief with 実際には間違いが残っていた. The reality clause belongs after the contrast marker."],
    ["わからないことが", ["あっても", "一人で", "悩む", "ことはない"], "ですよ。", "Even if there is something you do not understand, you do not need to struggle with it alone.", "あっても completes the concessive clause begun in the printed text. 一人で modifies 悩む. 悩むことはない here says there is no need to worry, rather than making a frequency claim."],
    ["子どものころは", ["夏休みになると", "祖父の家へ", "遊びに行った", "もの"], "です。", "When I was a child, I used to visit my grandfather's house during summer vacation.", "夏休みになると sets the recurring occasion. 祖父の家へ gives the destination and 遊びに行った the action. Past verb + ものです recalls a repeated past custom."],
    ["人は", ["失敗を", "重ねる", "ことで", "成長していくもの"], "だと思います。", "I think people grow by making mistakes repeatedly.", "失敗を重ねる is the means of growth. ことで nominalizes it as a cause or method. 成長していくものだ expresses a general tendency and is quoted by と思います."],
    ["時間が", ["ない", "わりには", "よく", "できている"], "と思います。", "I think it is well done considering how little time there was.", "時間がないわりには sets the unexpectedly difficult circumstances. よくできている is the favorable evaluation. わりには requires the evaluated outcome to follow."],
  ]),
  lesson("s24", "Mixed N2 connections · final challenge", "Hide the pattern hint on your first attempt. Read the printed boundaries, join the strongest pair, place all fragments, and only then identify the choice number at ★.", [
    ["この仕事を", ["引き受ける", "かどうかは", "条件を", "確認した上で"], "決めたいと思います。", "I want to decide whether to accept this job after checking the conditions.", "引き受けるかどうかは makes the yes/no decision the topic. 条件を確認した上で establishes the prerequisite. The printed 決めたい follows completion of that check."],
    ["彼が", ["約束を", "守らない", "ことに", "腹を立てている"], "人もいる。", "There are also people who are angry that he does not keep his promises.", "約束を守らない is the nominalized event before ことに. ことに marks the target of 腹を立てる. 腹を立てている describes the printed 人."],
    ["実際に", ["現場を", "見た", "人でなければ", "わからないこともある"], "でしょう。", "There are probably things only someone who has actually seen the site would understand.", "現場を見た modifies 人. 人でなければ restricts who can understand. わからないこともある states that some matters remain inaccessible without that experience."],
    ["どんなに", ["忙しくても", "家族と", "過ごす時間を", "大切にしたい"], "と思っています。", "No matter how busy I am, I want to value the time I spend with my family.", "どんなに忙しくても forms the concession. 家族と過ごす modifies 時間; 時間を is the object of 大切にする. 大切にしたい is the intention quoted before 思っています."],
    ["専門家の", ["意見を", "聞いた", "上でなければ", "判断するのは難しい"], "問題です。", "This is an issue that is difficult to judge without first hearing an expert's opinion.", "専門家の意見を聞いた is the completed prerequisite. 上でなければ means unless that step has been taken. 判断するのは難しい modifies the printed 問題, describing its difficulty."],
  ]),
];

export const N2_ASSEMBLY_QUESTIONS = N2_ASSEMBLY_LESSONS.flatMap((l) => l.questions);
export const N2_ASSEMBLY_PROGRESS_KEY = "jlpt-n2-sentence-order-progress-v1";

export function assemblyAnswer(q: N2AssemblyQuestion): number { return q.order[q.starIndex]; }
export function assemblySentence(q: N2AssemblyQuestion): string {
  return q.before + q.order.map((n) => q.choices[n - 1]).join("") + q.after;
}
