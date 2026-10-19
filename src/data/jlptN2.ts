/** Original N2-preparation material. IDs are persistent progress keys: never
 * renumber an existing lesson or question when adding more material. */
export type N2Kind = "kanji" | "vocabulary";
export interface N2Question {
  id: string;
  sentence: string;
  answer: string;
  word: string;
  reading: string;
  translation: string;
  explanation: string;
  accepted: string[];
}
export interface N2Lesson {
  id: string;
  kind: N2Kind;
  title: string;
  rule: string;
  boundary: string;
  questions: N2Question[];
}
type Entry = [sentence: string, answer: string, word: string, reading: string,
  translation: string, explanation: string, accepted?: string[]];
function lesson(id: string, kind: N2Kind, title: string, rule: string, boundary: string, entries: Entry[]): N2Lesson {
  return { id, kind, title, rule, boundary, questions: entries.map((e, i) => ({
    id: `${id}-${i + 1}`, sentence: e[0], answer: e[1], word: e[2], reading: e[3],
    translation: e[4], explanation: e[5], accepted: e[6] ?? [],
  })) };
}

export const N2_LESSONS: N2Lesson[] = [
  lesson("a01", "kanji", "Systems, formats, types, shapes & sizes",
    "制 names a system; 式 a format or method; 型 a model/type; 形 a shape; 大 after an object means approximately that object's size.",
    "These are clues to established words, not interchangeable endings. 卵大 is egg-sized; 卵形 is egg-shaped. Without choices, both can describe a stone.", [
    ["私の国は大統領___を採用している。", "制", "大統領制", "だいとうりょうせい", "My country uses a presidential system.", "採用する means adopt. What is adopted here is a system of government, so use 制. Transfer this to 会員制 (membership system), 予約制 (reservation system) and 交代制 (shift system)."],
    ["この試験には記述___の問題もある。", "式", "記述式", "きじゅつしき", "This exam also includes written-response questions.", "式 identifies how answers are provided. 記述式 requires written responses; 選択式 offers choices. The issue is the question format."],
    ["この会社は来月、新___の車を発売する。", "型", "新型", "しんがた", "This company will release a new model of car next month.", "型 identifies a product model/type. 新型 pairs with cars and machines. 形 would direct attention to physical shape rather than the established word for a new model."],
    ["子どもたちは円___に並んで座った。", "形", "円形", "えんけい", "The children sat arranged in a circle.", "円形 is the standard word for circular shape. Geometrical shapes also include 三角形 and 長方形. Here the arrangement's outline is the clue."],
    ["卵___のきれいな石を見つけました。", "大", "卵大", "たまごだい", "I found a beautiful stone about the size of an egg.", "Object + 大 compares size: こぶし大 is fist-sized and 一口大 is bite-sized. This open sentence also allows 形/型 for egg-shaped; those are accepted here, but change the meaning from size to shape.", ["形", "型"]],
  ]),
  lesson("a02", "kanji", "Change with 化; description with 的",
    "X化 means becoming X or making something X. X的な describes a noun; X的に describes how an action is performed.",
    "Many combinations are productive, but not every noun can take 化 or 的. Learn the resulting word and the grammar that follows it.", [
    ["この地域では人口の高齢___が進んでいる。", "化", "高齢化", "こうれいか", "The population in this area is aging.", "高齢化 is the process of becoming older at the population level. 〜化が進む describes an ongoing social or structural transformation."],
    ["企業の国際___に伴って、外国語を使う機会が増えた。", "化", "国際化", "こくさいか", "As companies have become more international, opportunities to use foreign languages have increased.", "国際化 names a transformation. に伴って connects that change with something developing alongside it. Compare 国際的な企業, an international company."],
    ["工場では作業の自動___を進めている。", "化", "自動化", "じどうか", "The factory is advancing the automation of its operations.", "自動 means automatic; 自動化 names making a process automatic. 〜化を進める describes deliberately advancing a transformation."],
    ["もっと具体___に説明してください。", "的", "具体的", "ぐたいてき", "Please explain more specifically.", "に shows that 具体的 modifies 説明する. Compare 具体的な例 (a specific example) with 具体的に説明する (explain specifically)."],
    ["彼女は会議で積極___に発言する。", "的", "積極的", "せっきょくてき", "She actively contributes to meetings.", "積極的に describes an active, willing approach. Learn 積極的に参加する/発言する together; 消極的 is the contrasting word for a reluctant or passive attitude."],
  ]),
  lesson("a03", "kanji", "Properties with 性; abilities with 力",
    "性 often turns a description into an abstract property or tendency. 力 often identifies an ability or effective power.",
    "The distinction helps with meaning, but the full combination must be a real word. 可能性 is possibility, not an ability score.", [
    ["この製品の安全___を確認する必要がある。", "性", "安全性", "あんぜんせい", "We need to check this product's safety.", "安全性 names safety as a property that can be evaluated. Compare 安全な製品, a safe product, with 製品の安全性, the product's safety."],
    ["電車が遅れる可能___がある。", "性", "可能性", "かのうせい", "There is a possibility that the train will be delayed.", "Plain-form clause + 可能性がある expresses a possible outcome. It does not mean the train has the ability to be late."],
    ["この制度を変える必要___について話し合った。", "性", "必要性", "ひつようせい", "We discussed the necessity of changing this system.", "必要性 makes necessity the topic for discussion. Contrast 変える必要がある, we need to change it, with 必要性を検討する, examine whether it is necessary."],
    ["彼の説明には説得___がある。", "力", "説得力", "せっとくりょく", "His explanation is persuasive.", "説得力 is the power to convince. Learn 説得力がある/ない and 説得力のある説明 rather than assembling it afresh each time."],
    ["寝不足で集中___が落ちている。", "力", "集中力", "しゅうちゅうりょく", "My ability to concentrate has declined because of insufficient sleep.", "集中力 is an ability. Abilities can 落ちる (decline) or be 高める (improved). Compare 集中する, the act of concentrating."],
  ]),
  lesson("a04", "kanji", "Rates with 率; levels with 度",
    "率 often measures a proportion or percentage. 度 often measures a degree or level.",
    "A 度 word can still receive a numerical survey score. The distinction is proportion versus extent, not numbers versus no numbers.", [
    ["この学校は大学への合格___が高い。", "率", "合格率", "ごうかくりつ", "This school has a high university acceptance rate.", "The focus is the proportion of applicants who succeed. 合格者数 counts successful people; 合格率 compares successful people with the relevant total."],
    ["景気が悪くなり、失業___が上がった。", "率", "失業率", "しつぎょうりつ", "The economy worsened and the unemployment rate rose.", "失業率 is a proportion of the labor force. Learn 率が上がる/下がる for rates rising or falling."],
    ["利用者の満足___をアンケートで調べた。", "度", "満足度", "まんぞくど", "We surveyed users' satisfaction levels.", "The survey concerns how satisfied users are. 満足度 measures the degree of a feeling rather than inherently naming a ratio."],
    ["広告によって商品の知名___が上がった。", "度", "知名度", "ちめいど", "Advertising increased the product's name recognition.", "知名度 is how well-known something is. Learn 知名度が高い/低い and 知名度を上げる."],
    ["仕事に優先___をつけて、順番に処理する。", "度", "優先度", "ゆうせんど", "Assign priorities to tasks and handle them in order.", "優先度 is a level of priority. 優先度をつける assigns relative priority; 最優先 identifies the very highest priority."],
  ]),
  lesson("a05", "kanji", "Expenses, charges, bills & rent",
    "費 often names expenses for an activity; 料 a service/use charge; 代 a payment for goods or consumption; 賃 appears in rent, fares and wages.",
    "English 'cost' or 'fee' does not uniquely determine the kanji. Memorize the conventional combinations: 交通費, 入場料, 電気代, 家賃.", [
    ["出張にかかった交通___は会社が負担する。", "費", "交通費", "こうつうひ", "The company covers transportation expenses for business trips.", "交通費 groups travel expenses. The phrase 費用を負担する means bear the cost. Related words include 生活費 and 医療費."],
    ["この美術館の入場___は千円です。", "料", "入場料", "にゅうじょうりょう", "Admission to this museum costs one thousand yen.", "入場料 is the charge for entering. Learn service-related combinations such as 使用料 (usage charge) and 受講料 (course fee)."],
    ["エアコンを使いすぎて、電気___が高くなった。", "代", "電気代", "でんきだい", "Using the air conditioner too much increased the electricity bill.", "電気代 is payment for consumed electricity. ガス代 and 水道代 follow the same familiar utility-bill pattern."],
    ["駅に近い部屋は家___が高い。", "賃", "家賃", "やちん", "Rooms near the station have high rent.", "家賃 is a fixed word with the reading やちん. Related 賃 words include 運賃 (fare) and 賃金 (wages); learn their readings individually."],
    ["銀行で振り込むと、手数___がかかる。", "料", "手数料", "てすうりょう", "A bank transfer incurs a transaction fee.", "手数料 is a handling/processing charge. 手数料がかかる means a fee applies; 手数料無料 means no handling fee."],
  ]),
  lesson("a06", "kanji", "Negative prefixes: 不・無・未・非",
    "不 often marks a negative condition; 無 absence; 未 not yet; 非 non-membership in a category or lack of a status.",
    "These are tendencies. Prefixes are not freely interchangeable, and 不 has different readings in words such as 不便 (ふべん) and 不器用 (ぶきよう).", [
    ["最近は生活が___規則になっている。", "不", "不規則", "ふきそく", "My daily routine has become irregular lately.", "不規則 is the established opposite of regular. Compare 規則的な生活 and 不規則な生活."],
    ["約束を簡単に破るなんて、___責任だ。", "無", "無責任", "むせきにん", "Breaking a promise so casually is irresponsible.", "無責任 describes lacking a sense of responsibility. Learn 無責任な発言/行動 for irresponsible statements/actions."],
    ["この建物はまだ___完成です。", "未", "未完成", "みかんせい", "This building is still unfinished.", "まだ reinforces not yet complete. Transfer 未 to 未解決 (unresolved) and 未使用 (not yet used)."],
    ["これは___公式の発表なので、内容が変わる可能性がある。", "非", "非公式", "ひこうしき", "This is an unofficial announcement, so its content may change.", "非公式 lacks official status. Compare 非会員 (nonmember), where 非 marks being outside a category."],
    ["一人で一日以内に終えるのは___可能だ。", "不", "不可能", "ふかのう", "Finishing it alone within one day is impossible.", "不可能 denies possibility. 未可能 is not the ordinary word for this meaning; knowing the general 'not yet' meaning of 未 is insufficient."],
  ]),
  lesson("a07", "kanji", "Again, highest, each, all & first",
    "再 marks repetition; 最 an extreme or highest rank; 各 each; 全 all; 初 a first experience or beginning.",
    "Learn the full reading as well as the prefix: 初対面 is しょたいめん, not a reading guessed from 初めて.", [
    ["書類に間違いがあったので、___提出を求められた。", "再", "再提出", "さいていしゅつ", "The documents contained an error, so I was asked to resubmit them.", "再提出 means submit again. 再確認 means reconfirm; 再開 means resume. The earlier submission is the contextual clue."],
    ["今は安全を___優先に考えてください。", "最", "最優先", "さいゆうせん", "Please make safety the highest priority now.", "最 puts safety above all competing concerns. Related extremes include 最高, 最低 and 最重要."],
    ["飲み物は___自で持ってきてください。", "各", "各自", "かくじ", "Please each bring your own drink.", "各自 distributes responsibility to every individual. Contrast 全員で, which can mean everyone acting together."],
    ["参加者___員に資料を配った。", "全", "全員", "ぜんいん", "We distributed materials to every participant.", "全員 includes all people in the relevant group. 全部 concerns all parts or items more broadly."],
    ["昨日会った人とは___対面だった。", "初", "初対面", "しょたいめん", "Yesterday was my first meeting with that person.", "初対面 names meeting someone for the first time. Learn 初対面の人 and 初対面なのに, despite having just met."],
  ]),
  lesson("a08", "kanji", "Stages on a timeline",
    "中 marks an ongoing activity; 済み completed handling; 前 before; 後 after; 末 the end of a period.",
    "Check what the blank includes: in 予約___み, only 済 belongs in the blank. Readings change across compounds: 使用前 is しようまえ; 卒業後 is そつぎょうご.", [
    ["この道路は工事___なので、通れません。", "中", "工事中", "こうじちゅう", "This road is under construction, so you cannot pass.", "工事中 describes construction currently in progress. Compare 会議中, in a meeting, and 使用中, in use."],
    ["この席は予約___みです。", "済", "予約済み", "よやくずみ", "This seat is already reserved.", "The reservation process is complete. み is supplied outside the blank; do not put 済み into a one-kanji slot. 支払い済み means already paid."],
    ["使用___に説明書を読んでください。", "前", "使用前", "しようまえ", "Read the instructions before use.", "前 locates reading before the use. Compare 使用後, after use. A common instruction pattern is 使用前に〜してください."],
    ["卒業___は日本で働きたい。", "後", "卒業後", "そつぎょうご", "After graduation, I want to work in Japan.", "後 marks the period following graduation. Learn 帰国後 (after returning home) and 食後 (after a meal) as full words."],
    ["家賃は毎月、月___までに払ってください。", "末", "月末", "げつまつ", "Please pay the rent by the end of each month.", "月末 is month-end, and までに marks a deadline. Related period endings include 週末 and 年末."],
  ]),
  lesson("a09", "kanji", "People and professional roles",
    "者 often marks a person in a role; 員 an organizational member; 家 a creator/expert; 士 certain professions; 手 a skilled participant.",
    "Occupational endings are conventional. Do not infer that every expert uses 家 or every licensed profession uses 士.", [
    ["この施設の利用___は年々増えている。", "者", "利用者", "りようしゃ", "The number of users of this facility increases every year.", "者 identifies people who use the facility. Compare 参加者 (participants) and 担当者 (person in charge)."],
    ["父は会社___として働いている。", "員", "会社員", "かいしゃいん", "My father works as a company employee.", "員 indicates a position within an organization. Compare 職員 (staff) and 委員 (committee member)."],
    ["彼女は小説___として活躍している。", "家", "小説家", "しょうせつか", "She is active as a novelist.", "家 occurs in established creator/expert words. Learn 作曲家 (composer) and 専門家 (specialist) alongside 小説家."],
    ["法律の問題について、弁護___に相談した。", "士", "弁護士", "べんごし", "I consulted a lawyer about a legal issue.", "弁護士 is the conventional professional title. Person + に相談する identifies the person being consulted."],
    ["彼はプロのサッカー選___を目指している。", "手", "選手", "せんしゅ", "He aims to become a professional soccer player.", "選手 is a competitor/player. Other people words using 手 include 歌手 (singer) and 運転手 (driver)."],
  ]),
  lesson("a10", "kanji", "Purpose, audience, grouping & boundaries",
    "用 identifies use; 向け a target audience; 別 a grouping criterion; 内 inside a boundary; 外 outside it.",
    "向け emphasizes who something is made for; 向き emphasizes suitability. They can overlap but have different focuses.", [
    ["これは子ども___の自転車です。", "用", "子ども用", "こどもよう", "This is a bicycle for children.", "X用 identifies intended users or purpose. Related words include 家庭用 (household use) and 業務用 (commercial use)."],
    ["この本は初心者___けに書かれている。", "向", "初心者向け", "しょしんしゃむけ", "This book is written for beginners.", "The author targets beginners. Since け is already supplied, fill only 向. 初心者向き instead emphasizes that something is suitable for beginners."],
    ["アンケートの結果を年齢___にまとめた。", "別", "年齢別", "ねんれいべつ", "We organized the survey results by age group.", "別 marks classification according to the preceding noun. Compare 地域別 (by region) and 種類別 (by type)."],
    ["このチケットは有効期限___に使ってください。", "内", "有効期限内", "ゆうこうきげんない", "Please use this ticket within its validity period.", "内 places use inside a time boundary. The same idea extends to 予算内, within budget, and 範囲内, within a range."],
    ["試験には予想___の問題が出た。", "外", "予想外", "よそうがい", "Unexpected questions appeared on the exam.", "予想外 means outside what was anticipated. Contrast 予想通り, as expected. 外 is read がい in this word."],
  ]),
  lesson("a11", "kanji", "Manufacture, origin, style & method",
    "製 identifies manufacture or material; 産 production origin; 風 style/resemblance; 流 a method or school.",
    "Japanese-style does not necessarily mean made in Japan. 国産 is domestic relative to the country under discussion.", [
    ["この時計は日本___です。", "製", "日本製", "にほんせい", "This watch is made in Japan.", "Place + 製 identifies manufacturing origin. Material + 製 identifies material instead, as in 木製 (wooden)."],
    ["この店では国___の野菜を売っている。", "産", "国産", "こくさん", "This store sells domestically produced vegetables.", "産 concerns production origin. 国産 is domestic; 日本産 explicitly says produced in Japan. Agricultural produce often appears with 産."],
    ["今日は和___の料理を作った。", "風", "和風", "わふう", "Today I made Japanese-style food.", "風 identifies style. The ingredients need not all be Japanese-produced. Compare 和風の味付け, Japanese-style seasoning."],
    ["これは洋___の建物です。", "風", "洋風", "ようふう", "This is a Western-style building.", "洋風 describes the building's style. Learn 和風/洋風 as a contrast pair; 洋式 often concerns a format or arrangement."],
    ["彼は料理を自己___で覚えた。", "流", "自己流", "じこりゅう", "He learned cooking in his own way.", "自己流で means using one's own methods. 流 can identify an approach or school, not the object's manufacturing origin."],
  ]),
  lesson("a12", "kanji", "Feelings, outlooks & motivation",
    "感 often names a feeling/impression; 観 an outlook; 心 a mental inclination. 気 appears in established words about feelings and disposition.",
    "Treat these as word families rather than a formula for inventing nouns. 人気 has the whole-word reading にんき.", [
    ["難しい仕事を終えて、達成___を感じた。", "感", "達成感", "たっせいかん", "Finishing the difficult task gave me a sense of achievement.", "感 names the feeling associated with achievement. Compare 安心感 (sense of security) and 違和感 (sense that something is off)."],
    ["育った環境によって、価値___は異なる。", "観", "価値観", "かちかん", "People's values differ depending on their upbringing.", "価値観 is one's outlook on what matters. Compare 人生観 (outlook on life) and 世界観 (worldview)."],
    ["子どもは好奇___が強い。", "心", "好奇心", "こうきしん", "Children have strong curiosity.", "好奇心 names the desire to know unfamiliar things. Learn 好奇心が強い and 好奇心を持つ."],
    ["この店は若者に人___がある。", "気", "人気", "にんき", "This shop is popular with young people.", "Xに人気がある means popular with X. Learn the whole word's reading にんき; 気 does not supply a general English 'popularity' suffix."],
    ["何度失敗しても、やる___を失わなかった。", "気", "やる気", "やるき", "Despite repeated failures, I did not lose motivation.", "やる気を失う means lose motivation. やる気が出る means become motivated; やる気になる means feel willing to act."],
  ]),
  lesson("b01", "vocabulary", "Judge, decide, check, consider & resolve",
    "判断 evaluates; 決定 finalizes a choice; 確認 checks; 検討 examines options; 解決 resolves a problem. Check what is happening, not just the English word 'decide'.",
    "These can overlap in open sentences. Read the explanation for accepted alternatives. If する is already printed, supply 判断, not 判断する.", [
    ["明日の天気によって、イベントを行うかどうか___する予定です。", "判断", "判断する", "はんだん", "We plan to judge whether to hold the event based on tomorrow's weather.", "天気 supplies grounds for assessing whether proceeding is appropriate. 〜かどうか判断する is reusable. 決定 also fits, emphasizing the final decision; both are accepted.", ["はんだん", "決定", "けってい"]],
    ["話し合いの結果、旅行の行き先を京都に___した。", "決定", "決定する", "けってい", "After discussing it, we decided on Kyoto as our destination.", "The destination is finalized. XをYに決定する identifies both the matter decided and the chosen outcome. 決めた would need the printed した to change.", ["けってい"]],
    ["メールを送る前に、相手のアドレスをもう一度___する。", "確認", "確認する", "かくにん", "Check the recipient's address again before sending the email.", "The address is checked for correctness. 内容・日時・住所を確認する are common pairings. No new plan is being selected.", ["かくにん"]],
    ["新しい制度を導入するかどうか、現在___している。", "検討", "検討する", "けんとう", "We are currently considering whether to introduce a new system.", "The proposal is still being examined. Contrast 検討中 (under consideration) with 決定済み (already decided). 思案 is another possible open-ended answer, but this lesson targets 検討.", ["けんとう", "思案", "しあん"]],
    ["話し合いによって、長年の問題を___した。", "解決", "解決する", "かいけつ", "We resolved the longstanding problem through discussion.", "問題を解決する brings a problem to resolution. Compare 問題が解決する, the problem is resolved. 解消 can also fit when the issue is eliminated.", ["かいけつ", "解消", "かいしょう"]],
  ]),
  lesson("b02", "vocabulary", "Coordinate, regulate, change, postpone & cancel",
    "Look at the object: schedules often take 調整; volume/temperature 調節; replacements 変更; a later date 延期; an event that will not proceed 中止.",
    "調整 and 調節 overlap in some uses. These are strong collocations, not a rule that each object permits exactly one verb.", [
    ["会議に参加するメンバーの都合を聞いて、日程の___を行った。", "調整", "日程の調整", "ちょうせい", "We checked the participants' availability and coordinated the meeting date.", "Several people's schedules must fit together. 日程の調整を行う equals 日程を調整する. 変更 could describe changing an existing date, but 調整 best teaches the coordination clue.", ["ちょうせい", "変更", "へんこう"]],
    ["音が大きすぎるので、音量を___してください。", "調節", "音量を調節する", "ちょうせつ", "The sound is too loud; please adjust the volume.", "The level should be brought to a suitable amount. 温度・音量・明るさを調節する are useful pairings. 調整 is also accepted because the words overlap here.", ["ちょうせつ", "調整", "ちょうせい"]],
    ["参加者が増えたため、会場を大きな部屋に___した。", "変更", "変更する", "へんこう", "We changed the venue to a larger room because attendance increased.", "XをYに変更する replaces one arrangement with another. The room changes, rather than merely the date moving later.", ["へんこう"]],
    ["台風のため、試合を来週に___した。", "延期", "延期する", "えんき", "We postponed the match until next week because of the typhoon.", "来週に identifies a later time. 延期 retains the intention to hold the match later; 変更 is also possible as a more general change of schedule.", ["えんき", "変更", "へんこう"]],
    ["安全が確保できないため、今年の大会は___することになった。", "中止", "中止する", "ちゅうし", "This year's tournament has been canceled because safety cannot be ensured.", "中止 means it will not proceed. 延期 would instead promise postponement, a possible different scenario; the teaching target here is cancellation.", ["ちゅうし", "延期", "えんき"]],
  ]),
  lesson("b03", "vocabulary", "Read the timeline",
    "もともと points to an original state; かつて a former period; 相変わらず continuity; すでに prior completion; やがて a later development.",
    "以前, かつて and もともと can overlap. 'Originally' emphasizes a starting point; 'previously' simply locates something in the past.", [
    ["山本氏は、今は作家として有名だが、___は俳優をしていたのだそうだ。", "もともと", "もともと", "もともと", "Mr. Yamamoto is now famous as a writer, but apparently he originally worked as an actor.", "今は contrasts with the earlier career. もともと emphasizes the original occupation. 以前 and かつて also fit and are accepted. は is already outside the blank.", ["元々", "元もと", "以前", "いぜん", "かつて", "昔", "むかし"]],
    ["この建物は、___病院として使われていた。", "かつて", "かつて", "かつて", "This building was once used as a hospital.", "かつて locates a former use and is common in written descriptions. 以前 also fits; もともと would additionally emphasize the original use.", ["以前", "いぜん", "もともと", "元々", "昔", "むかし"]],
    ["十年ぶりに会ったが、彼は___元気だった。", "相変わらず", "相変わらず", "あいかわらず", "I met him after ten years, and he was as energetic as ever.", "The long interval contrasts with an unchanged condition. 相変わらず can describe continuing good or bad conditions; it is not inherently criticism.", ["あいかわらず"]],
    ["急いで駅に行ったが、電車は___出発していた。", "すでに", "すでに", "すでに", "I hurried to the station, but the train had already departed.", "Departure was complete before arrival. すでに〜ていた highlights prior completion. もう is a natural conversational alternative.", ["既に", "もう"]],
    ["最初は緊張していたが、___会話を楽しめるようになった。", "やがて", "やがて", "やがて", "I was nervous at first, but eventually became able to enjoy the conversation.", "やがて introduces the later development after time passes. ようやく also fits but stresses finally reaching that stage after difficulty; 次第に emphasizes gradual change.", ["ようやく", "次第に", "しだいに"]],
  ]),
  lesson("b04", "vocabulary", "Something changes; someone changes it",
    "話がそれる versus 話をそらす; 時間がずれる versus 時間をずらす. が commonly marks the thing changing; を marks the object someone changes.",
    "Particles are clues, not a universal transitivity test. Also check conjugation: before a continuing clause you may need それて rather than それる.", [
    ["仕事の話をしていたのに、いつのまにか話が___、家族の話をしていた。", "それて", "話がそれる", "それて", "We were discussing work, but the conversation drifted and we ended up discussing family.", "話がそれる describes a topic moving away from its main line. Use the て-form to connect the next clause. 脱線して also describes going off topic; 変わって is a broader change.", ["逸れて", "脱線して", "だっせんして", "変わって", "かわって"]],
    ["答えたくなかったので、彼は話を別の方向に___。", "そらした", "話をそらす", "そらした", "He did not want to answer, so he diverted the conversation.", "He actively redirects 話を. Compare 話がそれた (it drifted) with 話をそらした (he diverted it). 向けた also works with 別の方向に.", ["逸らした", "向けた", "むけた"]],
    ["時計が五分___いるので、直してください。", "ずれて", "時計がずれる", "ずれて", "The clock is five minutes off; please correct it.", "ずれる describes misalignment with a standard. いる is already printed, so the blank takes the て-form. 進んで/遅れて specify which direction the clock is off.", ["ズレて", "進んで", "すすんで", "遅れて", "おくれて"]],
    ["混雑を避けるため、出発時間を一時間___。", "ずらした", "時間をずらす", "ずらした", "We shifted departure by one hour to avoid the crowds.", "Someone deliberately changes 出発時間を. ずらす does not specify earlier or later; 早めた and 遅らせた do, and are accepted.", ["ズラした", "早めた", "はやめた", "遅らせた", "おくらせた"]],
    ["うわさが学校中に___、誰もがその話を知っていた。", "広がって", "うわさが広がる", "ひろがって", "The rumor spread throughout the school, and everyone knew about it.", "うわさが広がる describes spreading information. Contrast うわさを広める, actively spread a rumor. 広まり is another grammatical connecting form in this sentence.", ["ひろがって", "広まり", "ひろまり", "広まって", "ひろまって"]],
  ]),
  lesson("b05", "vocabulary", "Refuse, take on, keep, leave & entrust",
    "Learn the direction of responsibility: 人から預かる receives temporary care; 人に預ける hands it over. 人に仕事を任せる entrusts a task.",
    "English 'take' or 'leave' is too broad. Identify whose item it is and who will look after it. Open answers may also admit synonyms such as 辞退する.", [
    ["その日は予定があったので、飲み会への誘いを___。", "断った", "誘いを断る", "ことわった", "I had plans that day, so I declined the invitation to drinks.", "誘いを断る is a standard refusal pairing. 依頼を断る refuses a request. 辞退した also fits, sounding more formal.", ["ことわった", "辞退した", "じたいした"]],
    ["忙しかったが、友人の頼みだったので、その仕事を___。", "引き受けた", "仕事を引き受ける", "ひきうけた", "I was busy, but took on the job because a friend asked.", "引き受ける accepts responsibility. Common objects include 仕事, 役割 and 依頼. The contrast with 忙しかったが supports accepting despite being busy.", ["ひきうけた", "引受けた"]],
    ["友人が旅行している間、私は友人の犬を___。", "預かった", "犬を預かる", "あずかった", "I looked after my friend's dog while my friend traveled.", "The dog belongs to the friend, and the speaker receives temporary care of it. This direction requires 預かる rather than 預ける.", ["あずかった"]],
    ["旅行中、犬を友人に___。", "預けた", "犬を預ける", "あずけた", "I left my dog with a friend during my trip.", "友人に identifies who receives responsibility. Pair this with 友人から犬を預かった from the receiving person's viewpoint.", ["あずけた"]],
    ["パソコンに詳しい同僚に、設定の作業を___。", "任せた", "作業を任せる", "まかせた", "I entrusted the setup work to a colleague who knows computers well.", "人に仕事を任せる leaves a task in someone's hands. 頼んだ also fits as requesting the work, but 任せた emphasizes entrusting responsibility.", ["まかせた", "頼んだ", "たのんだ", "依頼した", "いらいした"]],
  ]),
  lesson("b06", "vocabulary", "Arising, causing, affecting & reaching",
    "Learn full frames: 誤解が生じる; 事故を起こす; 対象に影響を及ぼす; 混乱を招く; 数量に達する.",
    "Several words translate as 'cause'. Their objects and particles distinguish them. Synonyms may work in an open blank; explain the nuance rather than inventing exclusivity.", [
    ["説明が足りないと、誤解が___ことがある。", "生じる", "誤解が生じる", "しょうじる", "Insufficient explanation can give rise to misunderstandings.", "生じる describes something arising and is common in written language: 問題・差・疑問が生じる. 起こる and 生まれる can also fit.", ["しょうじる", "起こる", "おこる", "生まれる", "うまれる"]],
    ["不注意で事故を___しまった。", "起こして", "事故を起こす", "おこして", "I carelessly caused an accident.", "を marks the accident caused. Compare 事故が起こる. The printed しまった requires 起こして, the て-form, and adds regret here.", ["おこして"]],
    ["この政策は経済に大きな影響を___だろう。", "及ぼす", "影響を及ぼす", "およぼす", "This policy will probably have a major impact on the economy.", "AがBに影響を及ぼす means A affects B. 経済に is the affected target and 影響を is the object. 与える is a natural alternative.", ["およぼす", "与える", "あたえる"]],
    ["あいまいな説明は、かえって混乱を___おそれがある。", "招く", "混乱を招く", "まねく", "An ambiguous explanation risks causing confusion instead.", "混乱を招く is a strong collocation for bringing about an undesirable result. Compare 誤解を招く. 引き起こす also fits.", ["まねく", "引き起こす", "ひきおこす", "起こす", "おこす"]],
    ["イベントの参加者は千人に___。", "達した", "千人に達する", "たっした", "The event's attendance reached one thousand.", "に marks the reached number or level. Learn 目標・水準・数量に達する. なった is also grammatically possible but less specifically expresses reaching a threshold.", ["たっした", "なった"]],
  ]),
  lesson("b07", "vocabulary", "Identify the kind of change",
    "増加/減少 describe numerical movement; 向上 a higher level; 改善 better conditions; 回復 restoration after loss or deterioration.",
    "'Improve' covers several Japanese words. Ask whether the sentence concerns more items, higher ability, correcting conditions, or getting something back.", [
    ["新しい駅ができてから、この地域の人口は___している。", "増加", "人口が増加する", "ぞうか", "The area's population has been increasing since the new station opened.", "The population's number grows. 増加 describes a numerical increase; 向上 would suggest a higher quality/ability rather than more residents.", ["ぞうか", "増大", "ぞうだい"]],
    ["紙を使わなくなり、コピー用紙の使用量が___した。", "減少", "使用量が減少する", "げんしょう", "Using less paper reduced the amount of copier paper consumed.", "使用量 is an amount, so 減少 expresses numerical decline. Pair 増加 and 減少 when reading trends.", ["げんしょう", "低下", "ていか"]],
    ["毎日練習して、会話能力が___した。", "向上", "能力が向上する", "こうじょう", "Daily practice improved my conversational ability.", "An ability reaches a higher level. Learn 能力・技術・品質が向上する. 上達 usually describes a person becoming better at a skill.", ["こうじょう"]],
    ["社員の意見を聞いて、労働環境を___した。", "改善", "環境を改善する", "かいぜん", "We improved working conditions after hearing employees' opinions.", "改善 makes existing conditions better, often correcting problems. 環境を shows someone actively changes the conditions.", ["かいぜん"]],
    ["十分に休んだので、体力が___した。", "回復", "体力が回復する", "かいふく", "Resting sufficiently restored my strength.", "Strength returns after being depleted. Compare 健康・景気・信用が回復する. 向上 would emphasize exceeding a previous level rather than restoration.", ["かいふく"]],
  ]),
  lesson("b08", "vocabulary", "Claims, criticism, evaluation & acceptance",
    "主張 states a position; 指摘 identifies a point; 評価 judges value; 反論 argues against; 納得 accepts something as convincing.",
    "Understanding is not necessarily agreement. 理解する can mean grasping an explanation without 納得する, accepting it as reasonable.", [
    ["彼は、自分の意見が正しいと強く___した。", "主張", "〜と主張する", "しゅちょう", "He firmly asserted that his opinion was correct.", "と introduces the content of the claim. 主張する reports the position without guaranteeing it is true. 強調 also fits, emphasizing the point.", ["しゅちょう", "強調", "きょうちょう"]],
    ["先生は、作文の問題点を具体的に___した。", "指摘", "問題点を指摘する", "してき", "The teacher pointed out specific problems in the composition.", "指摘 identifies a particular issue for attention. Learn 問題点・間違い・矛盾を指摘する. 説明 is a broader possible answer.", ["してき", "説明", "せつめい"]],
    ["審査員は、作品の独創性を高く___した。", "評価", "高く評価する", "ひょうか", "The judges rated the work's originality highly.", "評価 is evaluation, which can be positive or negative. 高く supplies the positive rating here; 低く評価する means rate poorly.", ["ひょうか"]],
    ["彼の意見には賛成できず、具体的な例を挙げて___した。", "反論", "意見に反論する", "はんろん", "I could not agree with his opinion and argued against it using specific examples.", "反論 challenges an argument. 意見に identifies the opinion opposed; 例を挙げて supplies supporting examples.", ["はんろん"]],
    ["理由を詳しく説明してもらい、ようやく___した。", "納得", "納得する", "なっとく", "After receiving a detailed explanation, I finally accepted the reasoning.", "納得 means becoming convinced or finding something reasonable. 理解 also fits but only guarantees understanding, a weaker claim.", ["なっとく", "理解", "りかい"]],
  ]),
  lesson("b09", "vocabulary", "Effort, inconvenience & accidental mistakes",
    "ようやく stresses finally reaching an outcome; せっかく valuable effort/opportunity; わざわざ a special effort; あいにく inconvenient circumstances; うっかり inattention.",
    "These words add the speaker's attitude. せっかく can be positive in せっかくだから; it is the のに pattern that often signals a wasted opportunity.", [
    ["三年間勉強して、___試験に合格した。", "ようやく", "ようやく", "ようやく", "After three years of study, I finally passed the exam.", "The long preparation supports finally reaching the goal. ついに emphasizes culmination; やっと is a more conversational alternative.", ["ついに", "やっと"]],
    ["___作った料理なのに、誰も食べてくれなかった。", "せっかく", "せっかく〜のに", "せっかく", "I went to the trouble of cooking, but nobody ate it.", "せっかく values the invested effort, while のに presents a disappointing outcome. Learn this emotional relationship, not just a one-word translation.", ["折角", "わざわざ"]],
    ["忘れ物を届けるために、彼は___家まで来てくれた。", "わざわざ", "わざわざ〜てくれる", "わざわざ", "He went out of his way to bring my forgotten item to my home.", "The visit was a special effort for a purpose. With てくれた, わざわざ commonly expresses appreciation for the extra trouble taken."],
    ["店長に会いたかったが、___今日は休みだった。", "あいにく", "あいにく", "あいにく", "I wanted to meet the manager, but unfortunately today was their day off.", "The circumstance is inconvenient for the speaker's purpose. あいにくですが is common in polite explanations. 残念ながら is another natural expression.", ["生憎", "残念ながら", "ざんねんながら"]],
    ["___して、メールにファイルを添付し忘れた。", "うっかり", "うっかりする", "うっかり", "I absentmindedly forgot to attach the file to the email.", "The error comes from inattention. Learn うっかり忘れる and うっかり間違える. Deliberate action would contradict this meaning."],
  ]),
  lesson("b10", "vocabulary", "Adverbs with sentence-level partners",
    "Recognize both halves: 必ずしも〜とは限らない; めったに〜ない; まさか〜とは思わなかった; AというよりむしろB; せめて + minimum wish.",
    "Do not translate the adverb before reading the ending. 必ずしも plus a negative means 'not necessarily', not 'certainly not'.", [
    ["値段が高いものが、___良いとは限らない。", "必ずしも", "必ずしも〜とは限らない", "かならずしも", "Expensive things are not necessarily good.", "The pattern rejects an absolute generalization. It allows some expensive things to be good; it does not say all expensive things are bad.", ["かならずしも"]],
    ["忙しくて、最近は映画館に___行かない。", "めったに", "めったに〜ない", "めったに", "I have been busy and rarely go to the cinema these days.", "めったに pairs with a negative to express low frequency. あまり also fits, meaning not often, generally a less emphatic statement.", ["滅多に", "あまり", "ほとんど"]],
    ["___彼が会社を辞めるとは思わなかった。", "まさか", "まさか〜とは思わなかった", "まさか", "I never imagined that he would leave the company.", "The event contradicts a strong expectation. まさか can also introduce an incredulous question: まさか辞めるんですか。"],
    ["この仕事は面倒というより、___楽しい。", "むしろ", "AというよりむしろB", "むしろ", "Rather than troublesome, this work is actually enjoyable.", "A is rejected as the better description and B is proposed instead. むしろ expresses a corrective comparison.", ["寧ろ"]],
    ["全部できなくても、___半分は終わらせたい。", "せめて", "せめて", "せめて", "Even if I cannot finish everything, I want to finish at least half.", "Half is the minimum desired outcome. せめて often accompanies a wish or request. 少なくとも also fits but can simply state a minimum without the same wishful emphasis.", ["少なくとも", "すくなくとも"]],
  ]),
  lesson("b11", "vocabulary", "Expressive words and their strongest partners",
    "Store these as pairs: ぐっすり眠る; じっくり考える; はっきり話す; 人にそっくりだ; うろうろする.",
    "Words that sound similar do not necessarily mean similar things. じっくり is careful, unhurried attention; ぐっすり is sound sleep.", [
    ["昨日は疲れていたので、朝まで___眠った。", "ぐっすり", "ぐっすり眠る", "ぐっすり", "I was tired yesterday and slept soundly until morning.", "ぐっすり describes deep, undisturbed sleep. It strongly pairs with 眠る/寝る. よく also fits but is less vivid.", ["よく"]],
    ["大切な契約なので、内容を___読んでから署名した。", "じっくり", "じっくり読む", "じっくり", "It was an important contract, so I read it carefully before signing.", "じっくり gives the task sufficient time and attention. Learn じっくり考える/話し合う. Carefully reading a contract also permits 丁寧に and よく.", ["丁寧に", "ていねいに", "よく", "しっかり"]],
    ["小さな声では聞こえないので、もっと___話してください。", "はっきり", "はっきり話す", "はっきり", "I cannot hear a quiet voice; please speak more clearly.", "はっきり makes speech distinct. It also describes clear memory and differences. 大きな声で focuses on volume rather than clarity.", ["大きな声で", "おおきなこえで"]],
    ["この子はお母さんに___だ。", "そっくり", "人にそっくりだ", "そっくり", "This child looks just like their mother.", "そっくり describes a strong resemblance. The comparison target takes に. 似ている would need the printed だ to be removed."],
    ["道が分からず、駅の周りを___していた。", "うろうろ", "うろうろする", "うろうろ", "Not knowing the way, I wandered around the station.", "うろうろ describes moving without a clear direction or destination. It can suggest looking lost or unsure, rather than a purposeful walk.", ["ウロウロ"]],
  ]),
  lesson("b12", "vocabulary", "Read idioms as whole expressions",
    "資料に目を通す = look through; 手を抜く = cut corners; 気に入る = like; 身につける = acquire; 気がつく = notice.",
    "Particles belong to the expression. 気がつく (notice) and 気をつける (be careful) are different. Check the form needed before おく, はいけない or たい.", [
    ["会議までに、この資料に目を___おいてください。", "通して", "資料に目を通す", "とおして", "Please look through these materials before the meeting.", "資料に目を通す means read through, often relatively briefly. 〜ておく adds advance preparation, so use 通して before おいてください.", ["とおして"]],
    ["時間がなくても、仕事で手を___はいけない。", "抜いて", "手を抜く", "ぬいて", "Even if time is short, you must not cut corners at work.", "手を抜く means reduce the effort or care a task requires. 〜てはいけない prohibits it, so the blank needs 抜いて.", ["ぬいて"]],
    ["この色がとても気に___ので、これを買います。", "入った", "気に入る", "いった", "I really like this color, so I will buy this one.", "気に入る means suit one's taste. The liked item takes が: この色が気に入った. The past form expresses having taken a liking to it.", ["いった", "入っている", "いっている"]],
    ["毎日練習して、正しい発音を身に___たい。", "つけ", "身につける", "つけ", "I want to acquire correct pronunciation through daily practice.", "身につける means acquire a skill or knowledge as part of one's ability. たい attaches to the verb stem, so fill つけ, not つける or つけたい.", ["付け", "着け"]],
    ["間違いに気が___のは、送信した後だった。", "ついた", "間違いに気がつく", "ついた", "It was after sending the message that I noticed the mistake.", "間違いに気がつく means notice an error. Compare 間違えないように気をつける, take care not to make a mistake: changing the particle changes the expression.", ["付いた"]],
  ]),
];

export const N2_QUESTIONS = N2_LESSONS.flatMap((l) => l.questions);
