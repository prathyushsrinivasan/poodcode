/** Original word-formation practice; levels are study estimates, not official
 * vocabulary assignments. IDs persist in settings: append, never renumber rows.
 * Row format: sentence | missing affix | full word | reading | translation |
 * contextual explanation | optional replacement choices (space-separated). */
export type AffixLevel = "N3" | "N2" | "N1";
export type AffixKind = "prefix" | "suffix";
export interface AffixQuestion {
  id: string;
  lessonId: string;
  level: AffixLevel;
  kind: AffixKind;
  sentence: string;
  answer: string;
  choices: string[];
  word: string;
  reading: string;
  translation: string;
  explanation: string;
}
export interface AffixLesson {
  id: string;
  level: AffixLevel;
  kind: AffixKind;
  title: string;
  rule: string;
  questions: AffixQuestion[];
}

function lesson(id: string, level: AffixLevel, kind: AffixKind, title: string,
  rule: string, choices: string[], rows: string): AffixLesson {
  return { id, level, kind, title, rule, questions: rows.trim().split("\n").map((line, i) => {
    const [sentence, answer, word, reading, translation, explanation, options] = line.split("|").map((s) => s.trim());
    return { id: `${id}-${i + 1}`, lessonId: id, level, kind, sentence, answer,
      word, reading, translation, explanation, choices: options ? options.split(" ") : choices };
  }) };
}

export const AFFIX_LESSONS: AffixLesson[] = [
  lesson("n3-praise", "N3", "prefix", "Reputation, success & new beginnings · 名・大・好・新",
    "名 marks a distinguished person or work; 大 a large degree; 好 a favorable result; 新 something new. Learn established combinations rather than attaching a positive kanji to any noun.",
    ["名", "大", "好", "新"], `
中村選手は日本を代表する___選手だ。|名|名選手|めいせんしゅ|Nakamura is an outstanding athlete who represents Japan.|名選手 is the established word for a distinguished athlete. 優 would need 秀 to form 優秀な選手.|高 優 名 真
この小説は百年以上読み継がれている___作だ。|名|名作|めいさく|This novel is a masterpiece that has been read for over a century.|Being read across generations supports the established word 名作, a masterpiece.|名 不 無 再
あの先生は難しい病気も治す___医として知られている。|名|名医|めいい|That doctor is known for treating even difficult illnesses.|A doctor renowned for exceptional skill is a 名医.|名 不 未 再
この通りには、昔から愛されているそばの___店がある。|名|名店|めいてん|There is a renowned soba restaurant on this street that has long been loved.|Long-standing renown identifies a 名店, a distinguished shop.|名 不 未 再
祭りには予想の三倍の人が来て、___成功だった。|大|大成功|だいせいこう|Three times as many people as expected came to the festival, making it a great success.|大 intensifies 成功: the turnout makes this a great success.
このゲームは子供たちに___人気だ。|大|大人気|だいにんき|This game is hugely popular with children.|大人気 means very popular; the prefix describes the degree of popularity.
笑顔で挨拶したので、面接官に___印象を与えた。|好|好印象|こういんしょう|My smiling greeting made a favorable impression on the interviewer.|好印象 is a favorable impression, reinforced by the friendly greeting.
毎日練習した結果、大会で___成績を収めた。|好|好成績|こうせいせき|Daily practice helped me achieve good results in the competition.|好成績 pairs naturally with 収める to describe good results.
四月から___学期が始まる。|新|新学期|しんがっき|The new school term starts in April.|新学期 is a new academic term, beginning at this time of year.
会社は来月、今までにない___商品を発売する。|新|新商品|しんしょうひん|The company will release a new product next month.|今までにない and 発売する identify a newly introduced product.
`),
  lesson("n3-negative", "N3", "prefix", "Not, without, not yet & again · 不・無・未・再",
    "不 negates a quality; 無 expresses absence; 未 means not yet; 再 means again. The base determines which prefix forms a natural word.",
    ["不", "無", "未", "再"], `
駅から遠く、バスもないので、この町は交通が___便だ。|不|不便|ふべん|This town has inconvenient transport because it is far from the station and has no buses.|不便 negates convenience; the lack of transport is the clue.
食事の時間が毎日違い、生活が___規則になっている。|不|不規則|ふきそく|My daily routine has become irregular because mealtimes change every day.|A routine without regular timing is 不規則.
理由もなく友達を疑うのは___自然だ。|不|不自然|ふしぜん|It is unnatural to suspect a friend without a reason.|不自然 means unnatural; 不 negates 自然.
このアプリはお金を払わずに___料で使える。|無|無料|むりょう|You can use this app free of charge.|お金を払わず explicitly states the absence of a charge: 無料.
誰も乗っていない___人のバスが駐車している。|無|無人|むじん|An unoccupied bus is parked there.|誰も乗っていない identifies the absence of people, 無人.
彼は免許を持たずに___免許で運転した。|無|無免許|むめんきょ|He drove without having a license.|免許を持たず gives the absence expressed by 無免許.
まだ開けていない___開封の箱を返した。|未|未開封|みかいふう|I returned the unopened box.|まだ開けていない means opening has not yet taken place: 未開封.
この料理は、まだ完成していないので___完成だ。|未|未完成|みかんせい|This dish is incomplete because it is not finished yet.|未完成 describes something not yet complete, rather than something repeated.
失敗したが、あきらめずにもう一度___挑戦する。|再|再挑戦|さいちょうせん|I failed, but I will try again without giving up.|もう一度 makes the repetition in 再挑戦 explicit.
見逃した番組が来週___放送される。|再|再放送|さいほうそう|The program I missed will be broadcast again next week.|A repeat broadcast of an existing program is a 再放送.
`),
  lesson("n3-scope", "N3", "prefix", "All, each, both & every · 全・各・両・毎",
    "全 covers the entire set; 各 treats members separately; 両 refers to both of two; 毎 expresses recurrence. Check the number and the relationship in the sentence.",
    ["全", "各", "両", "毎"], `
この試験では、一問も残さず___問に答えてください。|全|全問|ぜんもん|Please answer every question on this test without leaving any out.|一問も残さず emphasizes the entire set: 全問.
一人の例外もなく、___員が会議に出席した。|全|全員|ぜんいん|Everyone attended the meeting without a single exception.|The sentence includes every member, so use 全員.
この歌手は日本の___国を回ってコンサートを開く。|全|全国|ぜんこく|This singer will travel throughout Japan giving concerts.|全国 means throughout the country; 日本 fixes the scope to one country.
先生が三つのクラスを一つずつ回り、___クラスで説明した。|各|各クラス|かくくらす|The teacher visited the three classes in turn and explained it in each class.|一つずつ treats the classes individually: 各クラス.|各 再 不 未
国ごとに違うので、___国の法律を調べる必要がある。|各|各国|かっこく|Because laws differ by country, we need to examine each country's laws.|国ごとに違う focuses on countries separately, not a single nationwide rule.|各 再 不 未
左右の___手で重い箱を持ち上げた。|両|両手|りょうて|I lifted the heavy box with both hands.|左右 identifies the pair of hands: 両手.
自転車に乗る二人は___方ともヘルメットをかぶっている。|両|両方|りょうほう|Both of the two people riding bicycles are wearing helmets.|二人 and とも refer to both members of a pair, 両方.
土曜日になるたびに、___週図書館へ行く。|毎|毎週|まいしゅう|I go to the library every week, on Saturdays.|The recurring Saturday visit is 毎週.
一年に一度、___年健康診断を受ける。|毎|毎年|まいとし|I have a medical checkup every year.|一年に一度 identifies the annual recurrence in 毎年.
月末には必ず、___月の家賃を払う。|毎|毎月|まいつき|At the end of each month I always pay that month's rent.|A payment recurring each month is expressed with 毎月.
`),
  lesson("n3-time-prefix", "N3", "prefix", "First, former, previous & current · 初・元・前・現",
    "初 marks a first experience; 元 a former status; 前 a preceding period or predecessor; 現 the present holder. Context must distinguish former and immediately previous positions.",
    ["初", "元", "前", "現"], `
生まれて初めて、飛行機で___海外旅行に出かけた。|初|初海外旅行|はつかいがいりょこう|For the first time in my life, I went on an overseas trip by plane.|生まれて初めて explicitly identifies a first overseas trip.|初 再 不 無
このチームは全国大会に一度も出たことがなかったが、ついに___出場が決まった。|初|初出場|はつしゅつじょう|The team secured its first appearance in the national tournament.|一度も出たことがなかった identifies a first appearance, 初出場.|初 再 不 無
チームは決勝で勝ち、大会で___優勝を果たした。|初|初優勝|はつゆうしょう|The team won the final and achieved its first championship.|初優勝 means a first championship; 果たす describes achieving it.|初 不 無 未
今は医者だが、彼は昔、学校で教えていた___教師だ。|元|元教師|もときょうし|He is a doctor now, but he used to teach at a school.|昔 and 今は医者 identify a former career: 元教師.|元 初 再 無
今は引退しているが、姉は___プロ選手だった。|元|元プロ選手|もとぷろせんしゅ|My sister is retired now, but she used to be a professional athlete.|引退している identifies a former professional athlete.|元 初 再 未
今週は忙しいが、その一つ前の___週は暇だった。|前|前週|ぜんしゅう|This week is busy, but the previous week was quiet.|その一つ前 explicitly points to the preceding week.
今年の売上は、その一つ前の___年より増えた。|前|前年|ぜんねん|This year's sales increased compared with the previous year.|一つ前の年 is 前年, the year immediately before the reference year.
先月の一つ前の月、つまり先月から見た___月にも赤字だった。|前|前月|ぜんげつ|There was also a deficit in the month before last month.|The reference point is last month, whose preceding month is its 前月.
今も在職している___社長が、新しい計画を発表した。|現|現社長|げんしゃちょう|The current company president announced a new plan.|今も在職している explicitly identifies the current officeholder.|現 初 再 無
現在もその職に就いている___職の議員が、選挙に出馬した。|現|現職|げんしょく|An incumbent legislator who still holds office entered the election.|現在もその職に就いている identifies 現職, the current office or incumbent.|現 初 再 無
`),
  lesson("n3-degree", "N3", "prefix", "High, low, long & short · 高・低・長・短",
    "高 and 低 describe degree; 長 and 短 describe duration or extent. A high price is 高価格, while an extended period is 長期間.",
    ["高", "低", "長", "短"], `
このカメラは、画質がとてもよい___画質の映像を撮れる。|高|高画質|こうがしつ|This camera can record images of very high quality.|画質がとてもよい identifies high image quality, 高画質.
この店は、品質のよい___品質の商品だけを売っている。|高|高品質|こうひんしつ|This shop sells only high-quality products.|品質のよい restates the meaning of 高品質.
値段がとても高い___価格の商品は、なかなか売れない。|高|高価格|こうかかく|Products with very high prices are hard to sell.|値段がとても高い identifies 高価格; duration prefixes do not fit.
この食品はカロリーが少ない___カロリーの商品だ。|低|低カロリー|ていかろりー|This food is a low-calorie product.|カロリーが少ない gives the low degree expressed by 低.
気温の低い___温の場所で保管してください。|低|低温|ていおん|Please store it somewhere with a low temperature.|気温の低い identifies low temperature, 低温.
できるだけ費用を抑えた___予算の旅行を計画している。|低|低予算|ていよさん|I am planning a low-budget trip with costs kept as low as possible.|費用を抑えた identifies the small budget in 低予算.
十時間以上の___時間労働が続き、疲れてしまった。|長|長時間|ちょうじかん|I became exhausted after working long hours of over ten hours at a time.|十時間以上 emphasizes a long duration, 長時間.
半年以上海外にいるので、___期間の保険に入った。|長|長期間|ちょうきかん|I took out long-term insurance because I will be abroad for over six months.|半年以上 is an extended period, 長期間.
五分ほどの___時間で作れる料理を教えてください。|短|短時間|たんじかん|Please teach me a dish I can make in a short time of about five minutes.|五分ほど identifies the short duration, 短時間.
夏休みの一週間だけ、___期間のアルバイトをした。|短|短期間|たんきかん|I worked a short-term part-time job for just one week of summer vacation.|一週間だけ identifies a short period, 短期間.
`),
  lesson("n3-qualities", "N3", "suffix", "Description, change & qualities · 的・化・性・さ",
    "的 forms descriptive expressions, often followed by な or に. 化 expresses transformation; 性 an inherent quality; さ nominalizes an adjective stem.",
    ["的", "化", "性", "さ"], `
これは私の個人___な意見です。|的|個人的|こじんてき|This is my personal opinion.|個人的な modifies 意見; 的 creates the descriptive expression.
毎朝の運動を習慣にするため、規則___な生活を心がける。|的|規則的|きそくてき|I try to maintain a regular routine to make morning exercise a habit.|規則的な describes a regular pattern of living.
将来の夢について、具体___に説明してください。|的|具体的|ぐたいてき|Please explain your future dream in specific terms.|具体的に modifies 説明する, telling how to explain.
機械を使うようになり、工場の自動___が進んだ。|化|自動化|じどうか|The factory became more automated as it began using machines.|自動化が進む describes a process of becoming automated.
人口が都市に集まり、都市___が進んでいる。|化|都市化|としか|The population is concentrating in cities, and urbanization is advancing.|都市化 names the process of urbanization.
この計画が成功する可能___は高い。|性|可能性|かのうせい|There is a high possibility that this plan will succeed.|可能性 is the noun meaning possibility; it can be 高い.
子供が使う道具は、安全___が何より大切だ。|性|安全性|あんぜんせい|Safety is the most important quality of tools that children use.|安全性 names safety as a property of a tool.|性 的 化 たち
荷物の重___を量ってから送った。|さ|重さ|おもさ|I weighed the package before sending it.|重い loses い and takes さ to become the noun 重さ.
富士山の高___は三千メートル以上ある。|さ|高さ|たかさ|Mount Fuji has a height of over three thousand meters.|高い becomes 高さ, the noun measured in meters.
試合に負けた悔し___を、次の練習に生かしたい。|さ|悔しさ|くやしさ|I want to use the frustration of losing the match to motivate my next practice.|悔しい becomes the noun 悔しさ, the feeling of frustration.
`),
  lesson("n3-people", "N3", "suffix", "People, staff, specialists & shops · 者・員・家・屋",
    "者 identifies a person involved in an activity; 員 a member of staff; 家 a professional or specialist; 屋 a shop or shopkeeper. These are lexical patterns, not freely interchangeable job endings.",
    ["者", "員", "家", "屋"], `
イベントの参加___は、受付で名前を書いてください。|者|参加者|さんかしゃ|Participants in the event should write their names at reception.|A person who participates is a 参加者.
事故の目撃___が、警察に状況を説明した。|者|目撃者|もくげきしゃ|A witness to the accident explained the situation to the police.|A person who witnessed an event is a 目撃者.
この駐車場の利用___は、先に料金を払ってください。|者|利用者|りようしゃ|Users of this car park should pay the fee first.|A person using a facility is a 利用者.
会社___として、毎朝九時に出勤している。|員|会社員|かいしゃいん|As a company employee, I go to work at nine every morning.|会社員 is the established word for a company employee.
駅___に、次の電車が何時に来るか聞いた。|員|駅員|えきいん|I asked a station employee what time the next train would come.|Staff working at a railway station are 駅員.
図書館___に、本の場所を教えてもらった。|員|図書館員|としょかんいん|A library staff member showed me where the book was.|図書館員 names a member of library staff.
彼女は小説___として、毎年新しい本を発表している。|家|小説家|しょうせつか|She publishes a new book every year as a novelist.|The professional writer of novels is a 小説家.
地震の専門___が、建物の安全を調べた。|家|専門家|せんもんか|An earthquake specialist examined the building's safety.|専門家 is an expert in a specialized field.
朝ご飯のパンを買いに、パン___に寄った。|屋|パン屋|ぱんや|I stopped at a bakery to buy bread for breakfast.|パン屋 is the established word for a bakery or bread seller.
花___で、母の誕生日に贈る花を買った。|屋|花屋|はなや|I bought flowers for my mother's birthday at a florist's.|A shop that sells flowers is a 花屋.
`),
  lesson("n3-status", "N3", "suffix", "In progress, before, after & completed · 中・前・後・済み",
    "中 marks an ongoing state; 前 before an event; 後 after it; 済み a completed procedure. Time clues determine the intended relationship.",
    ["中", "前", "後", "済み"], `
この道は今、工事___なので通れません。|中|工事中|こうじちゅう|This road is currently under construction, so you cannot pass.|今 and 通れません show that construction is in progress.
「会議___です。終わるまで入らないでください」と書いてある。|中|会議中|かいぎちゅう|The sign says a meeting is in progress and asks people not to enter until it ends.|終わるまで indicates that the meeting is currently underway.
電話は今、使用___なので、少し待ってください。|中|使用中|しようちゅう|The phone is in use now, so please wait a moment.|Waiting is necessary because someone is using the phone now.
まだ食べていないので、食事___に薬を飲む。|前|食事前|しょくじまえ|I take the medicine before the meal, before eating anything.|まだ食べていない explicitly places the action before the meal.
授業が始まる十分前、つまり授業___に教室へ入った。|前|授業前|じゅぎょうまえ|I entered the classroom ten minutes before the lesson started.|始まる十分前 fixes the time before the lesson.
学校を出たあと、卒業___に働き始めた。|後|卒業後|そつぎょうご|I started working after graduating from school.|学校を出たあと identifies the time after graduation.
仕事が終わってから、勤務___に映画を見た。|後|勤務後|きんむご|I watched a movie after finishing work.|仕事が終わってから fixes the sequence after work.
この席はもう予約が終わっていて、予約___だ。|済み|予約済み|よやくずみ|This seat has already been reserved.|もう予約が終わっている describes a completed reservation.
料金はすでに払ったので、支払い___になっている。|済み|支払い済み|しはらいずみ|The payment is marked as completed because I have already paid.|すでに払った identifies completed payment.
登録はもう終わった。登録___の人は、そのままログインできる。|済み|登録済み|とうろくずみ|Registration is complete; registered users can log in directly.|登録はもう終わった identifies completion, not ongoing registration.
`),
  lesson("n3-costs", "N3", "suffix", "Expenses, charges, payment & taxes · 費・料・代・税",
    "費 names expenses, 料 a service charge, 代 the price paid for something, and 税 a tax. Several cost expressions have alternatives; these drills use choices that identify one established expression.",
    ["費", "料", "代", "税"], `
家賃や食べ物など、毎月の生活___を計算した。|費|生活費|せいかつひ|I calculated my monthly living expenses, including rent and food.|生活費 is the established collective term for everyday living expenses.
今月は外食を減らして、食___を節約した。|費|食費|しょくひ|I cut down on eating out this month to reduce food expenses.|食費 is the established word for food expenses.|費 者 中 化
大学に通うための学___を、アルバイトで稼いでいる。|費|学費|がくひ|I earn money for my university education through a part-time job.|学費 names educational expenses as a whole.|費 者 中 化
このホテルでは、洗濯サービスの利用___を別に払う。|料|利用料|りようりょう|At this hotel, you pay separately to use the laundry service.|利用料 is a fee charged for using a service.|料 者 中 化
荷物を届けてもらうための配達___がかかる。|料|配達料|はいたつりょう|There is a delivery charge for having the package brought to you.|配達料 is the charge for a delivery service.|料 者 中 化
喫茶店で友達のコーヒー___も一緒に払った。|代|コーヒー代|こーひーだい|I paid for my friend's coffee as well at the cafe.|コーヒー代 is the price paid for the coffee.|代 者 中 化
暑い月はエアコンを使うので、電気___が高くなる。|代|電気代|でんきだい|Electricity bills rise in hot months because we use air conditioning.|電気代 is the usual expression for the electricity bill.|代 者 中 化
商品を買うとき、国に納める消費___がかかる。|税|消費税|しょうひぜい|A consumption tax payable to the government applies when buying goods.|国に納める identifies a tax paid to the government, 消費税, rather than a service charge.
働いて得た収入には、所得___がかかる。|税|所得税|しょとくぜい|Income tax applies to income earned from work.|所得税 is the tax on income.
自動車を持っているので、自動車___を納めた。|税|自動車税|じどうしゃぜい|I paid automobile tax because I own a car.|納める and car ownership identify 自動車税, an automobile tax.
`),
  lesson("n3-purpose", "N3", "suffix", "Purpose, audience, orientation & grouping · 用・向け・向き・別",
    "用 marks an intended use; 向け an intended audience; 向き an orientation or suitability; 別 separation by category. Audience and use can overlap, so attend to the actual choices.",
    ["用", "向け", "向き", "別"], `
遊びではなく仕事で使う、仕事___のパソコンを買った。|用|仕事用|しごとよう|I bought a computer for work rather than for leisure.|仕事用 marks the intended use of the computer.|用 者 中 化
旅行のときだけ使う旅行___の小さなかばんを用意した。|用|旅行用|りょこうよう|I prepared a small bag used only for travel.|旅行用 identifies the bag's purpose.|用 者 中 化
これは見るだけの展示___の模型で、販売していない。|用|展示用|てんじよう|This model is for display only and is not for sale.|見るだけ and 販売していない identify display as the intended use.|用 者 中 化
初めて学ぶ人を対象に、初心者___の講座を開く。|向け|初心者向け|しょしんしゃむけ|We will offer a course aimed at beginners.|人を対象に identifies the audience the course is designed for.|向け 中 済み 別
子供を対象に書かれた、子供___の本を探している。|向け|子供向け|こどもむけ|I am looking for a book written for children.|対象に書かれた specifies the intended readership.|向け 中 済み 別
外国人を対象にした、外国人___の生活ガイドを配った。|向け|外国人向け|がいこくじんむけ|We distributed a living guide aimed at foreign residents.|対象にした identifies the intended audience.|向け 中 済み 別
窓が南の方を向いている、南___の部屋がほしい。|向き|南向き|みなみむき|I want a south-facing room whose windows face south.|南の方を向いている describes physical orientation.|向き 用 者 化
北の方を向いた北___の部屋は、直射日光が入りにくい。|向き|北向き|きたむき|A north-facing room receives little direct sunlight.|北の方を向いた identifies physical orientation.|向き 用 者 化
参加者を年齢で分け、年齢___のグループを作った。|別|年齢別|ねんれいべつ|We divided participants into groups by age.|年齢で分け identifies age as the grouping criterion.
アンケートの結果を、男女___に集計した。|別|男女別|だんじょべつ|We tabulated the questionnaire results separately for men and women.|男女別 means separately by male and female respondents.
`),
  lesson("n2-negation", "N2", "prefix", "Negation & absence in formal words · 非・不・無・未",
    "非 excludes a category; 不 negates a quality or state; 無 marks absence; 未 an action not yet completed. Established words control the choice: 非常識, 不十分, 無関心, 未解決.",
    ["非", "不", "無", "未"], `
深夜に大声で騒ぐのは、___常識な行動だ。|非|非常識|ひじょうしき|Making a loud disturbance late at night is inconsiderate behavior.|非常識 is the established opposite of 常識的, lacking common sense.
これは普段とは違う、___日常の体験だった。|非|非日常|ひにちじょう|This was an experience outside ordinary daily life.|普段とは違う identifies the category outside everyday life: 非日常.
この組織は政府に属さない___政府組織だ。|非|非政府組織|ひせいふそしき|This is a nongovernmental organization that does not belong to the government.|政府に属さない excludes the governmental category.
説明が足りず、内容の理解が___十分だった。|不|不十分|ふじゅうぶん|The explanation was lacking, so understanding of the content was insufficient.|足りず identifies the insufficiency in 不十分.
機械の調子が悪く、___具合の原因を調べている。|不|不具合|ふぐあい|The machine is malfunctioning, and we are investigating the cause.|不具合 names a malfunction or fault in normal operation.
彼は政治に全く興味を示さず、___関心だった。|無|無関心|むかんしん|He showed absolutely no interest in politics and was indifferent.|全く興味を示さず describes absence of interest, 無関心.
事件には関係がなく、私は___関係だと説明した。|無|無関係|むかんけい|I explained that I was uninvolved and had no connection to the incident.|関係がない is expressed by 無関係.
名前を書かず、___記名でアンケートに答えた。|無|無記名|むきめい|I answered the questionnaire anonymously, without writing my name.|名前を書かず identifies an anonymous response, 無記名.
まだ解決していない___解決の問題が残っている。|未|未解決|みかいけつ|Unresolved problems remain.|まだ解決していない means resolution has not yet occurred.
必要な書類は、まだ出していないため___提出になっている。|未|未提出|みていしゅつ|The required documents are marked as not yet submitted because I have not handed them in.|まだ出していない points to submission not yet completed.
`),
  lesson("n2-renewal", "N2", "prefix", "Again, revised, restored & newly established · 再・改・復・新",
    "再 repeats an action; 改 changes an existing structure; 復 restores a previous state; 新 introduces something newly established. Focus on repetition, alteration or restoration.",
    ["再", "改", "復", "新"], `
休業していた店が、来月から営業を___開する。|再|再開|さいかい|The shop that had been closed will resume business next month.|休業していた shows a pause followed by resumption, 再開.
一度決めた計画を、最初からもう一度___検討する。|再|再検討|さいけんとう|We will reconsider the previously decided plan from the beginning.|もう一度 makes the repeated examination explicit.
建物の土台は残し、内装を大きく___装した。|改|改装|かいそう|We left the building's foundations and substantially remodeled the interior.|内装を変える is 改装, remodeling an existing interior.
古い家の一部を建て直す___築工事を行った。|改|改築|かいちく|We carried out reconstruction work to rebuild part of the old house.|一部を建て直す changes an existing building: 改築.|改 不 無 未
任期が終わるため、役員の___選を行う。|改|改選|かいせん|We will hold an election to replace the officers whose terms are ending.|任期が終わる identifies an election to renew the officeholders: 改選.
停電のあと、電力が元どおりに___旧した。|復|復旧|ふっきゅう|Power was restored after the outage.|元どおり identifies restoration of function, 復旧.
病気で休んでいた社員が、元の職場に___職した。|復|復職|ふくしょく|An employee who had been on sick leave returned to the original workplace.|元の職場に戻る is 復職, returning to work.
休刊していた雑誌が、十年ぶりに___刊された。|復|復刊|ふっかん|A magazine that had ceased publication was revived after ten years.|休刊していた雑誌の刊行を再び始める is specifically 復刊.|復 不 無 未
この町に、これまでなかった保育所を___設する。|新|新設|しんせつ|We will establish a nursery facility that this town did not previously have.|これまでなかった identifies a newly established facility.
今年___任した先生を、歓迎会で紹介した。|新|新任|しんにん|We introduced the newly appointed teacher at the welcome party.|新任 describes a person newly appointed to a post.|新 不 無 未
`),
  lesson("n2-extremes", "N2", "prefix", "Beyond, most, extreme & exact · 超・最・極・真",
    "超 exceeds an ordinary level; 最 marks the highest degree; 極 an extreme; 真 exactness or the middle of a season or time. Compound readings differ: 真夏 is まなつ, 真正面 is ましょうめん.",
    ["超", "最", "極", "真"], `
この俳優は一流の中でも特に優れた、___一流の演技を見せる。|超|超一流|ちょういちりゅう|This actor gives performances of exceptional, world-class quality.|一流の中でも特に優れた intensifies 一流 beyond its ordinary degree.
電車は乗客でいっぱいで、身動きもできない___満員だった。|超|超満員|ちょうまんいん|The train was so overcrowded with passengers that we could not move.|身動きもできない intensifies 満員 to extreme overcrowding.
通常よりはるかに速い___高速の通信技術を開発した。|超|超高速|ちょうこうそく|We developed communication technology much faster than ordinary high-speed systems.|通常よりはるかに速い expresses speed beyond the normal high-speed level.
何より先に、安全を___優先に考える。|最|最優先|さいゆうせん|We give safety the highest priority, ahead of everything else.|何より先に identifies the top priority, 最優先.
研究所では、その分野の___先端技術を研究している。|最|最先端|さいせんたん|The laboratory researches the most advanced technology in the field.|最先端 is the established expression for the leading edge of technology.
歴代の受賞者の中で一番若い、___年少の受賞者となった。|最|最年少|さいねんしょう|They became the youngest winner in the history of the award.|一番若い identifies the superlative 最年少.
肉眼では見えないほどの___小の粒子を観察する。|極|極小|きょくしょう|We observe extremely small particles that cannot be seen with the naked eye.|極小 is the established word for extremely small size.|極 不 無 再
ほんのわずかな___少量の薬品でも、慎重に扱う。|極|極少量|ごくしょうりょう|We handle even extremely small amounts of chemicals carefully.|ほんのわずかな identifies an extremely small amount, 極少量.|極 不 無 再
八月の___夏に、冷房なしで過ごすのは大変だ。|真|真夏|まなつ|It is hard to get through midsummer in August without air conditioning.|八月 places the scene in the middle of summer, 真夏.
鏡のちょうど___正面に立ってください。|真|真正面|ましょうめん|Please stand directly in front of the mirror.|ちょうど and 正面 form 真正面, directly in front.
`),
  lesson("n2-status-prefix", "N2", "prefix", "Provisional, associate, deputy & former · 仮・準・副・元",
    "仮 marks a provisional arrangement; 準 a near or associate status; 副 a deputy; 元 a former role. A temporary appointment is not necessarily a deputy position.",
    ["仮", "準", "副", "元"], `
正式な名前はまだ決まっていないので、今は___名で呼んでいる。|仮|仮名|かめい|The official name has not been decided, so we are using a provisional name.|正式な名前はまだ決まっていない identifies 仮名, read かめい here, a provisional name.
正式な登録の前に、メールアドレスだけで___登録をした。|仮|仮登録|かりとうろく|Before full registration, I completed provisional registration using only my email address.|正式な登録の前 identifies the provisional stage.
本番の前に、部品を___組みして寸法を確かめた。|仮|仮組み|かりぐみ|Before final assembly, we temporarily assembled the parts to check the dimensions.|寸法を確かめるための一時的な組み立て is 仮組み.
優勝には届かなかったが、決勝で二位になり___優勝した。|準|準優勝|じゅんゆうしょう|We did not win the championship but finished second as runners-up.|二位 in the final identifies 準優勝.
正会員とは一部の権利が違う___会員として入会した。|準|準会員|じゅんかいいん|I joined as an associate member with some rights different from full members.|正会員と権利が違う identifies associate membership.
社長を補佐する___社長に、部長が昇進した。|副|副社長|ふくしゃちょう|The department head was promoted to vice president to assist the president.|社長を補佐する identifies the deputy position, 副社長.
校長を助ける役職として、___校長が会議に出席した。|副|副校長|ふくこうちょう|The vice principal attended the meeting in a role assisting the principal.|校長を助ける役職 is 副校長.
会長が欠席したので、補佐役の___会長が代理を務めた。|副|副会長|ふくかいちょう|The deputy chair acted for the absent chairperson.|補佐役 and 代理 identify the deputy, 副会長.
十年前に引退した___監督が、当時の思い出を語った。|元|元監督|もとかんとく|A former coach who retired ten years ago shared memories of that time.|引退した identifies a former role, 元監督.
今は別の会社で働く___同僚と、久しぶりに会った。|元|元同僚|もとどうりょう|I met a former colleague who now works for another company after a long time.|今は別の会社で働く identifies a past colleague.
`),
  lesson("n2-range", "N2", "prefix", "Total, entire, half & against · 総・全・半・反",
    "総 aggregates a total; 全 covers an entire range; 半 means half or partly; 反 expresses opposition. Some total expressions overlap, so compare only the choices given.",
    ["総", "全", "半", "反"], `
すべての住民を合計した、この国の___人口を調べた。|総|総人口|そうじんこう|We investigated the total population of this country by adding all residents.|総人口 is the aggregate population of a territory.|総 再 不 未
各階の広さを合計し、建物の___面積を出した。|総|総面積|そうめんせき|We added the areas of each floor to obtain the building's total area.|各階の広さを合計 identifies an aggregate total.|総 再 不 未
人が操作しなくても動く、___自動の洗濯機を買った。|全|全自動|ぜんじどう|I bought a fully automatic washing machine that operates without manual control.|人が操作しなくても identifies full automation rather than partial automation.
一国だけでなく、___世界に向けてニュースを配信する。|全|全世界|ぜんせかい|We distribute the news to the entire world, not just one country.|一国だけでなく expands the scope to the whole world.
外が少し透けて見える、___透明のガラスを使った。|半|半透明|はんとうめい|We used translucent glass through which the outside is partly visible.|少し透けて見える describes partial transparency, 半透明.
一部だけ手で動かす、___自動の機械を使っている。|半|半自動|はんじどう|We use a semiautomatic machine that requires some manual operation.|一部だけ手で identifies partial rather than full automation.
完全に永久ではないが、非常に長く使える___永久的な素材だ。|半|半永久的|はんえいきゅうてき|This material lasts an extremely long time, though not literally forever.|完全に永久ではない gives the near-permanent meaning of 半永久的.
政府に反対する___政府デモが行われた。|反|反政府|はんせいふ|An antigovernment demonstration was held.|政府に反対する explicitly identifies opposition to the government.
戦争に反対する人々が、___戦運動を続けている。|反|反戦|はんせん|People opposed to war continue their antiwar movement.|戦争に反対する is expressed by 反戦.
人々の安全を脅かす___社会的な行為は許されない。|反|反社会的|はんしゃかいてき|Antisocial acts that threaten people's safety are unacceptable.|社会の秩序や利益に反する行為 is 反社会的な行為.
`),
  lesson("n2-abstract", "N2", "suffix", "Descriptions, transformation, properties & systems · 的・化・性・制",
    "的 makes a description, 化 a transformation, 性 a property, 制 an organizational system. Read what follows the blank: な and に often signal 的.",
    ["的", "化", "性", "制"], `
感情ではなく、合理___な判断が求められる。|的|合理的|ごうりてき|A rational judgment rather than an emotional one is required.|合理的な modifies 判断 and describes a judgment based on reason.
無駄を省き、効率___に作業を進める。|的|効率的|こうりつてき|We eliminate waste and carry out the work efficiently.|効率的に modifies how the work is carried out.
外国との交流が増え、地域の国際___が進んだ。|化|国際化|こくさいか|More contact with other countries advanced the region's internationalization.|国際化が進む names a process of becoming more international.
古い設備を入れ替え、工場の近代___を進めた。|化|近代化|きんだいか|We replaced old equipment to modernize the factory.|設備を入れ替える is a concrete step in the transformation 近代化.
異なる背景を持つ人々の多様___を尊重する。|性|多様性|たようせい|We respect the diversity of people from different backgrounds.|多様性 names the quality of diversity.
状況に応じて変更できる、計画の柔軟___が大切だ。|性|柔軟性|じゅうなんせい|A plan's flexibility to change with circumstances is important.|状況に応じて変更できる identifies flexibility as a property.
見た目だけでなく、道具としての実用___を重視した。|性|実用性|じつようせい|We emphasized practicality as a tool, rather than appearance alone.|道具として役立つという性質 is 実用性.
登録した会員だけが利用できる、会員___の店だ。|制|会員制|かいいんせい|It is a members-only establishment that only registered members can use.|利用者を会員に限定する仕組み is 会員制.
事前の予約が必要な、完全予約___のレストランだ。|制|予約制|よやくせい|It is a restaurant that operates strictly by reservation.|事前の予約が必要 identifies a reservation-based system.
二つのチームが順番に働く、交代___を採用している。|制|交代制|こうたいせい|We use a shift system in which two teams work in turn.|順番に働く組織の仕組み is 交代制.
`),
  lesson("n2-tendencies", "N2", "suffix", "Tendencies, slight symptoms & excess · がち・気味・っぽい・だらけ",
    "がち describes a recurring tendency, often undesirable; 気味 a slight current tendency; っぽい a resemblance or strong tendency; だらけ an abundance of unwelcome things. Grammar limits the possible joins.",
    ["がち", "気味", "っぽい", "だらけ"], `
最近は学校を休むことが多く、休み___になっている。|がち|休みがち|やすみがち|Recently I have been absent from school often and tend to miss classes.|休むことが多い describes a recurring tendency; 休みがちになる is natural here.
彼は子供のころ体が弱く、病気___だった。|がち|病気がち|びょうきがち|He was physically weak as a child and was often ill.|Repeated illness during childhood is the established expression 病気がち.
留守にすることが多い留守___の家なので、配達日を指定した。|がち|留守がち|るすがち|Because nobody is home much of the time, I specified a delivery date.|留守にすることが多い identifies frequent absence from home.
熱はないが、今日は少し風邪___だ。|気味|風邪気味|かぜぎみ|I have no fever, but I feel as if I have a slight cold today.|今日は少し describes a mild current symptom, 風邪気味.
この数日は忙しくて、少し寝不足___だ。|気味|寝不足気味|ねぶそくぎみ|I have been busy these past few days and am a little short of sleep.|この数日 and 少し describe a mild current state, 寝不足気味.
水を入れすぎて、水___スープになった。|っぽい|水っぽい|みずっぽい|I added too much water, making the soup watery.|水っぽい is an い-adjective describing an unpleasantly watery quality.
もう大人なのに、子供___言い争いをしている。|っぽい|子供っぽい|こどもっぽい|They are adults but are having a childish argument.|子供っぽい describes childish behavior; it directly modifies 言い争い.
彼は何を始めてもすぐやめる、飽き___性格だ。|っぽい|飽きっぽい|あきっぽい|He has a personality that gets bored quickly and quits whatever he starts.|すぐやめる identifies the strong tendency in 飽きっぽい.
転んだので、服が泥___になった。|だらけ|泥だらけ|どろだらけ|I fell over, leaving my clothes covered in mud.|泥だらけ describes being covered with an unwanted substance.|だらけ がち 気味 的
作文は間違い___で、ほとんど全部直す必要があった。|だらけ|間違いだらけ|まちがいだらけ|The essay was full of mistakes, so almost all of it needed correction.|ほとんど全部直す indicates numerous unwanted mistakes.
`),
  lesson("n2-intervals", "N2", "suffix", "After a gap, at intervals, within & since · ぶり・おき・以内・以来",
    "ぶり marks a return after a gap; おき repeated spacing; 以内 an upper time limit; 以来 a starting point continuing to the present. These include time-expression endings as well as lexical suffixes.",
    ["ぶり", "おき", "以内", "以来"], `
三年間一度も会わず、今日、三年___に友人と再会した。|ぶり|三年ぶり|さんねんぶり|After not meeting for three years, I reunited with my friend today.|三年間一度も会わず and 再会 identify an encounter after a gap.
一週間泳いでいなかったが、今日、一週間___に泳いだ。|ぶり|一週間ぶり|いっしゅうかんぶり|I swam today for the first time in a week.|一週間泳いでいなかった makes the gap explicit.
十年会っていなかった先生に、十年___に会った。|ぶり|十年ぶり|じゅうねんぶり|I met my teacher for the first time in ten years.|十年会っていなかった identifies a return after a ten-year gap.
バスは九時、九時十分、九時二十分と、十分___に来る。|おき|十分おき|じゅっぷんおき|Buses come at ten-minute intervals, at nine, nine ten, nine twenty, and so on.|The listed times establish repeated ten-minute intervals.
薬は八時、十二時、十六時と、四時間___に飲む。|おき|四時間おき|よじかんおき|Take the medicine at four-hour intervals, at eight, twelve, and sixteen.|The listed times specify a recurring interval of four hours.
締め切りは今から一時間後だ。一時間___に提出してください。|以内|一時間以内|いちじかんいない|The deadline is one hour from now; please submit it within that hour.|締め切り identifies the upper limit for submission.
到着から一週間を過ぎる前に、一週間___に連絡してください。|以内|一週間以内|いっしゅうかんいない|Please contact us within a week, before a week has passed since arrival.|一週間を過ぎる前 places an upper bound on the waiting time.
卒業したときから今まで、卒業___ずっと同じ会社で働いている。|以来|卒業以来|そつぎょういらい|I have worked at the same company ever since graduating.|ときから今まで and ずっと identify continuity from graduation.
入社した日から今まで、入社___一度も遅刻していない。|以来|入社以来|にゅうしゃいらい|I have never been late since the day I joined the company.|した日から今まで fixes the continuing period beginning at entry.
日本に来てから今まで、来日___毎日日記を書いている。|以来|来日以来|らいにちいらい|I have written a diary every day since coming to Japan.|来てから今まで identifies arrival as the start of a continuing practice.
`),
  lesson("n2-relations", "N2", "suffix", "In terms of, under, by category & descriptively · 上・下・別・的",
    "上 means from the standpoint of; 下 under control or conditions; 別 by category; 的 creates descriptions. These endings are common in reports and formal explanations.",
    ["上", "下", "別", "的"], `
感情の問題とは別に、法律___の責任を検討する。|上|法律上|ほうりつじょう|Separately from emotional issues, we will consider legal responsibility.|法律上の means from a legal standpoint and modifies 責任.
名前だけの代表ではなく、事実___の責任者は彼だ。|上|事実上|じじつじょう|He is the person actually in charge, rather than merely a nominal representative.|事実上 means in reality or de facto.
規則では認められないため、制度___の問題がある。|上|制度上|せいどじょう|Because the rules do not allow it, there is a problem with the system.|制度上の問題 identifies a problem from the standpoint of the institutional system.
危険な薬品は、専門家の厳重な管理___に置かれている。|下|管理下|かんりか|Dangerous chemicals are kept under strict expert control.|管理下に置く is the established expression for placing something under management.
その地域は長年、外国の支配___にあった。|下|支配下|しはいか|The region was under foreign rule for many years.|支配下にある describes being under another power's rule.
新人は指導員の指導___で作業を覚える。|下|指導下|しどうか|New employees learn the work under an instructor's guidance.|指導下で describes working under someone's guidance.
国ごとに分けた国___の統計を比較する。|別|国別|くにべつ|We compare statistics separated by country.|国ごとに分けた specifies grouping by country.
書類を種類ごとに、種類___に整理してください。|別|種類別|しゅるいべつ|Please organize the documents by type.|種類ごと identifies the classification criterion.
一度に変えるのではなく、段階___に制度を変える。|的|段階的|だんかいてき|We will change the system gradually in stages rather than all at once.|段階的に modifies the manner of change.
本人ではなく、友人を通じて間接___に事情を聞いた。|的|間接的|かんせつてき|I learned the circumstances indirectly through a friend rather than from the person involved.|友人を通じて identifies the indirect manner, 間接的に.
`),
  lesson("n2-action-endings", "N2", "suffix", "Completed, unfinished, left as is & fresh · 済み・かけ・っぱなし・たて",
    "済み marks a completed procedure; かけ an unfinished action; っぱなし an action or state left unattended; たて something just done. Verb stems join these endings in different established ways.",
    ["済み", "かけ", "っぱなし", "たて"], `
料金はもう払った。支払い___の領収書を見せた。|済み|支払い済み|しはらいずみ|I had already paid, so I showed the receipt marked as paid.|もう払った identifies completed payment, not a freshly made object.
申し込みの登録は完了した。登録___の番号を確認した。|済み|登録済み|とうろくずみ|Application registration was complete, and I checked the registered number.|登録は完了した explicitly identifies completion.
まだ最後まで読んでいない読み___の本を机に置いた。|かけ|読みかけ|よみかけ|I put the partly read book that I had not finished on the desk.|まだ最後まで読んでいない identifies an unfinished reading action.
途中まで食べたが、食べ___のパンを残して出かけた。|かけ|食べかけ|たべかけ|I went out, leaving behind bread I had only partly eaten.|途中まで食べた specifies an action started but unfinished.
窓を閉め忘れ、開け___にして出かけた。|っぱなし|開けっぱなし|あけっぱなし|I forgot to close the window and went out leaving it open.|閉め忘れ and にして describe a state left unattended.
道具を片付けず、出し___にしないでください。|っぱなし|出しっぱなし|だしっぱなし|Please do not leave the tools out without putting them away.|片付けず describes leaving the result of taking something out unattended.
服を脱いだあと、脱ぎ___にせず洗濯かごに入れて。|っぱなし|脱ぎっぱなし|ぬぎっぱなし|After taking off your clothes, put them in the laundry basket instead of leaving them lying around.|脱いだあと and 洗濯かご contrast tidying with leaving clothes as they were.
オーブンから出したばかりの焼き___のパンは熱い。|たて|焼きたて|やきたて|Freshly baked bread just out of the oven is hot.|出したばかり identifies the fresh result of baking.
ご飯は炊き終えたばかりで、炊き___だ。|たて|炊きたて|たきたて|The rice has only just finished cooking and is freshly cooked.|炊き終えたばかり describes rice immediately after completion.
完成したばかりの建て___の家に引っ越した。|たて|建てたて|たてたて|I moved into a newly built house that had just been completed.|完成したばかり identifies a fresh result, rather than construction left incomplete.
`),
  lesson("n1-status", "N1", "prefix", "Already, not yet, excluded & absent · 既・未・非・無",
    "既 marks an existing or already established state; 未 a state not yet reached; 非 exclusion from a category; 無 absence. Formal contexts make these distinctions especially useful.",
    ["既", "未", "非", "無"], `
すでに出来上がっている___成の概念にとらわれない。|既|既成|きせい|Do not be bound by already established concepts.|すでに出来上がっている identifies the established state in 既成概念.
新しく作るのではなく、すでにある___存の設備を使う。|既|既存|きそん|We will use existing equipment rather than create something new.|すでにある gives the meaning of 既存, already existing.
結婚している人は、___婚の欄に印を付けてください。|既|既婚|きこん|Married people should mark the married-status box.|結婚している identifies 既婚, already married.
犯行は完了せず、___遂に終わった。|未|未遂|みすい|The crime was not completed and ended as an attempt.|完了せず identifies 未遂, an attempted but uncompleted act.
結論はまだ出ておらず、案件は___決のままだ。|未|未決|みけつ|No conclusion has been reached, so the matter remains undecided.|まだ出ておらず describes a decision not yet made.
納めるべき税金をまだ払わず、___納になっている。|未|未納|みのう|The tax that should have been paid is still unpaid.|まだ払わず identifies an unpaid obligation, 未納.
一般には見せない___公開の資料を、許可を得て閲覧した。|非|非公開|ひこうかい|With permission, I viewed documents that were not open to the public.|一般には見せない identifies the established classification 非公開.
利益の分配を目的としない___営利の団体に所属している。|非|非営利|ひえいり|I belong to a nonprofit organization that does not aim to distribute profits.|利益の分配を目的としない identifies the nonprofit category.
期限を一切設けず、___期限で活動を停止する。|無|無期限|むきげん|We will suspend activities indefinitely without setting any deadline.|期限を一切設けず identifies absence of a time limit.
条件を一切付けず、___条件で受け入れた。|無|無条件|むじょうけん|We accepted it unconditionally without attaching any conditions.|条件を一切付けず identifies unconditional acceptance.
`),
  lesson("n1-beyond", "N1", "prefix", "Opposition, departure, transcendence & difference · 反・脱・超・異",
    "反 opposes; 脱 moves away from a structure or dependence; 超 crosses a boundary; 異 marks something different. Read the underlying relationship, not just whether the sentence sounds negative.",
    ["反", "脱", "超", "異"], `
現在の体制に反対する___体制運動が広がった。|反|反体制|はんたいせい|An antiestablishment movement opposing the current system spread.|現在の体制に反対する gives the oppositional meaning of 反.
押す力とは逆向きの___作用が生じた。|反|反作用|はんさよう|A reaction force arose in the opposite direction to the pushing force.|逆向き identifies the established physics term 反作用.
原発への依存から離れる___原発の方針を示した。|脱|脱原発|だつげんぱつ|They announced a policy of moving away from dependence on nuclear power.|依存から離れる gives the departure meaning of 脱.
炭素の排出を減らす___炭素社会への移行を進める。|脱|脱炭素|だつたんそ|We are advancing the transition to a decarbonized society with reduced carbon emissions.|炭素の排出を減らす identifies the movement away from carbon emissions.
製造業中心の経済から離れ、___工業化が進んだ。|脱|脱工業化|だつこうぎょうか|The economy moved away from manufacturing, and deindustrialization advanced.|製造業中心の経済から離れ describes deindustrialization.
党の違いを超えて、___党派で協力することになった。|超|超党派|ちょうとうは|We agreed to cooperate across party lines.|党の違いを超えて identifies cooperation transcending party boundaries.
国家の枠を超える___国家的な組織が必要とされる。|超|超国家的|ちょうこっかてき|An organization that transcends national boundaries is needed.|国家の枠を超える gives the supranational meaning.
自分とは違う文化を学び、___文化への理解を深めた。|異|異文化|いぶんか|I studied cultures different from my own and deepened my intercultural understanding.|自分とは違う文化 identifies 異文化.
業界の異なる企業が集まる___業種交流会に参加した。|異|異業種|いぎょうしゅ|I attended a networking event for companies in different industries.|業界の異なる identifies different lines of business.
従来とは次元が違う、___次元の発想だと評価された。|異|異次元|いじげん|The idea was praised as being on a completely different level from conventional thinking.|次元が違う identifies 異次元, literally a different dimension.
`),
  lesson("n1-approximation", "N1", "prefix", "Associate, mimetic, false & provisional · 準・擬・偽・仮",
    "準 marks near or associate status; 擬 imitates or represents; 偽 falsifies; 仮 makes a temporary arrangement. A representation is different from information intended to deceive.",
    ["準", "擬", "偽", "仮"], `
決勝の一つ前の___決勝で、強豪同士が対戦する。|準|準決勝|じゅんけっしょう|Two strong teams will face each other in the semifinal immediately before the final.|決勝の一つ前 names the semifinal, 準決勝.
正会員より権利が限られた___会員の制度を設けた。|準|準会員|じゅんかいいん|We established associate membership with more limited rights than full membership.|正会員より権利が限られた identifies associate status.
民間だけではなく公的な性格もある、___公的な機関だ。|準|準公的|じゅんこうてき|It is a semipublic institution with public characteristics as well as private ones.|公的な性格もある identifies a near-public or semipublic status.
「ざあざあ」のように音をまねる言葉を___音語という。|擬|擬音語|ぎおんご|Words that imitate sounds, such as zaazaa, are called onomatopoeic sound words.|音をまねる identifies the representation of a sound, 擬音語.
「きらきら」のように状態を表す言葉を___態語という。|擬|擬態語|ぎたいご|Words that express states, such as kirakira, are called mimetic words.|状態を表す rather than actual sound identifies 擬態語.
動物を人間のように描く___人化の手法が使われている。|擬|擬人化|ぎじんか|The technique of personification depicts animals as if they were human.|人間のように描く identifies personification, 擬人化.
事実とは異なる情報を、意図的に___情報として流した。|偽|偽情報|にせじょうほう|They deliberately circulated false information.|事実とは異なる and 意図的に identify falsified information.
善人のふりをして利益を得る、その___善を批判した。|偽|偽善|ぎぜん|We criticized the hypocrisy of pretending to be good for personal gain.|善人のふりをして describes false goodness, 偽善.
正式な契約に先立ち、一時的な___契約を結んだ。|仮|仮契約|かりけいやく|Before the formal agreement, we entered into a provisional contract.|正式な契約に先立ち and 一時的な identify provisional status.
正式な裁判の結論を待たず、一時的な___処分を申し立てた。|仮|仮処分|かりしょぶん|Without waiting for the final court decision, we applied for provisional relief.|正式な結論の前の一時的な措置 is 仮処分.
`),
  lesson("n1-degree", "N1", "prefix", "Excess, subzones, low & high · 過・亜・低・高",
    "過 marks excess; 亜 a subcategory or adjacent climatic zone; 低 and 高 a low or high degree. These are established technical and social vocabulary combinations.",
    ["過", "亜", "低", "高"], `
子供を守りすぎる___保護は、自立を妨げることがある。|過|過保護|かほご|Overprotection can sometimes hinder a child's independence.|守りすぎる identifies excessive protection.
人が集中しすぎた___密な都市では、住宅が不足している。|過|過密|かみつ|Housing is scarce in overcrowded cities where too many people concentrate.|集中しすぎた identifies excessive density.
制限を超える荷物を積んだ___積載のトラックが摘発された。|過|過積載|かせきさい|An overloaded truck carrying cargo beyond the limit was caught.|制限を超える荷物 identifies excessive loading.
熱帯に隣接する暖かい___熱帯の地域で果物を育てる。|亜|亜熱帯|あねったい|We grow fruit in a warm subtropical region adjacent to the tropics.|熱帯に隣接する identifies the subtropical zone, 亜熱帯.
寒帯より少し温暖な___寒帯では、針葉樹林が広がる。|亜|亜寒帯|あかんたい|Coniferous forests spread in the subarctic zone, which is slightly warmer than the polar zone.|寒帯より少し温暖 identifies the subarctic climatic zone.
収入の少ない___所得世帯への支援を拡充する。|低|低所得|ていしょとく|We will expand support for low-income households.|収入の少ない identifies a low level of income.
経済の伸びが小さい___成長の時代に入った。|低|低成長|ていせいちょう|We entered an era of low economic growth.|伸びが小さい identifies a low rate of growth.
独自の技術で価値を高めた___付加価値の商品を開発した。|高|高付加価値|こうふかかち|We developed high-value-added products using proprietary technology.|価値を高めた identifies high added value.
誤差が非常に小さい___精度の測定器を導入した。|高|高精度|こうせいど|We introduced a high-precision measuring device with very little error.|誤差が非常に小さい means precision is high.
わずかな光も検出できる___感度のセンサーだ。|高|高感度|こうかんど|It is a highly sensitive sensor that can detect even faint light.|わずかな光も検出できる identifies high sensitivity.
`),
  lesson("n1-formal-prefix", "N1", "prefix", "This, the relevant, former & deceased · 本・当・旧・故",
    "本 refers to the present document or matter; 当 to the relevant organization or period; 旧 to a former system or area; 故 before a title means the person has died. Formal 本 and 当 sometimes overlap; choices exclude that overlap.",
    ["本", "当", "旧", "故"], `
これから説明する、この制度、すなわち___制度の目的を示す。|本|本制度|ほんせいど|We state the purpose of the present system, which we will now explain.|この制度 identifies the system under discussion, 本制度.|本 再 未 無
この調査で得られたデータを、___調査の報告書にまとめる。|本|本調査|ほんちょうさ|We will compile the data obtained in this study in the report of the present study.|この調査 refers back to the present investigation.|本 再 未 無
この契約の効力、つまり___契約の効力は翌月から生じる。|本|本契約|ほんけいやく|The present contract takes effect from the following month.|この契約 identifies the contract being referred to in the document.|本 再 未 無
その年度に発生した費用は、___年度の予算で処理する。|当|当年度|とうねんど|Expenses arising in that fiscal year are handled within that year's budget.|その年度 points to the fiscal year in question, 当年度.|当 再 未 無
この事務所を代表して、___事務所からご案内申し上げます。|当|当事務所|とうじむしょ|On behalf of this office, we are sending you this notice.|An organization referring formally to its own office uses 当事務所.|当 再 未 無
この会場をご利用の皆様へ、___会場は全館禁煙です。|当|当会場|とうかいじょう|To everyone using this venue: the entire venue is nonsmoking.|The notice refers to the venue in question as 当会場.|当 再 未 無
改革前の古い___体制から、新しい体制へ移行した。|旧|旧体制|きゅうたいせい|We moved from the old system before the reforms to a new system.|改革前の古い identifies the former system, 旧体制.
新市街ではなく、歴史的な建物が残る___市街を歩いた。|旧|旧市街|きゅうしがい|I walked through the old town with its historic buildings rather than the new town.|新市街との対比 identifies the old part of the city, 旧市街.
昨年亡くなった___社長の功績を、追悼式で振り返った。|故|故社長|こしゃちょう|We recalled the late president's achievements at a memorial service.|亡くなった and 追悼式 identify 故 before the title of a deceased person.
すでに亡くなられた___教授の蔵書が、大学に寄贈された。|故|故教授|こきょうじゅ|The late professor's books were donated to the university.|すでに亡くなられた identifies the deceased professor, 故教授.
`),
  lesson("n1-perspectives", "N1", "suffix", "Transformation, regarding as, theories & outlooks · 化・視・論・観",
    "化 changes a state; 視 treats or regards something in a particular way; 論 names a theory or argument; 観 an outlook or conception. Notice whether the result is an action, argument or viewpoint.",
    ["化", "視", "論", "観"], `
別々だった窓口を一つにまとめ、手続きの一元___を図る。|化|一元化|いちげんか|We will centralize the procedures by bringing separate service points together.|一つにまとめる identifies the transformation 一元化.
制度は形だけ残り、実際には機能しない形骸___が進んだ。|化|形骸化|けいがいか|The system increasingly became an empty shell that remained in form but no longer functioned.|形だけ残る describes the process of becoming hollow or merely formal.
都合のよい理由を付けて、自分の行為を正当___した。|化|正当化|せいとうか|They justified their actions by supplying convenient reasons.|理由を付けて正当なものとする is 正当化.
相手を敵とみなし、必要以上に敵___している。|視|敵視|てきし|They regard the other person as an enemy more than is necessary.|敵とみなす identifies 敵視, treating someone as an enemy.
性質の違う二つの問題を、同じものと同一___すべきではない。|視|同一視|どういつし|We should not equate two problems of different kinds as the same thing.|同じものとみなす is 同一視.
価格よりも安全を重要___して、製品を選ぶ。|視|重要視|じゅうようし|We choose products by placing importance on safety over price.|安全を重要なものとみなす is 重要視.
研究の進め方を体系的に論じる方法___を学んだ。|論|方法論|ほうほうろん|I studied methodology, which systematically examines how to conduct research.|進め方を体系的に論じる identifies methodology, 方法論.
終わったあとの結果だけで判断するのは、結果___にすぎない。|論|結果論|けっかろん|Judging solely by the outcome afterward is merely hindsight.|結果だけで判断する議論 is 結果論.
人生をどう捉えるかという人生___は、人によって異なる。|観|人生観|じんせいかん|People differ in their outlook on life.|人生をどう捉えるか identifies an outlook, 人生観.
何を大切だと考えるか、その価値___を尊重する。|観|価値観|かちかん|We respect their values concerning what they consider important.|何を大切だと考えるか is one's set of values, 価値観.
`),
  lesson("n1-properties", "N1", "suffix", "Properties, rights, feelings & abilities · 性・権・感・力",
    "性 names a property; 権 a right or authority; 感 a feeling; 力 a capacity or force. Identify whether the sentence describes how something is, what someone may do, how they feel, or what they can accomplish.",
    ["性", "権", "感", "力"], `
証拠から判断すると、その出来事が起きた蓋然___は高い。|性|蓋然性|がいぜんせい|Judging from the evidence, the probability that the event occurred is high.|蓋然性 is the formal noun for probability or likelihood.
説明同士に矛盾がないか、論理的な整合___を確かめる。|性|整合性|せいごうせい|We check logical consistency to see whether the explanations contradict each other.|矛盾がない性質 is 整合性.
古いソフトでも動くか、新機種との互換___を調べた。|性|互換性|ごかんせい|We checked compatibility with the new model to see whether the old software would run.|異なる機種で利用できる性質 is 互換性.
担当者が自ら判断できる裁量___の範囲を明確にした。|権|裁量権|さいりょうけん|We clarified the scope of the officer's discretionary authority.|自ら判断できる権限 is 裁量権.
提案を拒否する権利、つまり拒否___を行使した。|権|拒否権|きょひけん|They exercised their veto, the right to reject the proposal.|拒否する権利 is 拒否権.
この土地が誰のものか、所有___の所在を確認した。|権|所有権|しょゆうけん|We confirmed who held ownership rights to the land.|誰のものか concerns the legal right of ownership.
仲間から切り離されたような疎外___を覚えた。|感|疎外感|そがいかん|I felt a sense of alienation, as though cut off from my companions.|切り離されたような気持ち is 疎外感.
社会に貢献しなければという使命___を抱いている。|感|使命感|しめいかん|I have a sense of mission that I must contribute to society.|しなければという内面的な気持ち is 使命感.
相手の行動を思いとどまらせる抑止___が期待される。|力|抑止力|よくしりょく|It is expected to have the deterrent power to make the other side refrain from acting.|行動を思いとどまらせる力 is 抑止力.
表面の情報から本質を見抜く洞察___に優れている。|力|洞察力|どうさつりょく|They excel in the ability to see the essence beneath surface information.|本質を見抜く能力 is 洞察力.
`),
  lesson("n1-abundance", "N1", "suffix", "Covered, entirely, an assortment & an air of · まみれ・ずくめ・づくし・めく",
    "まみれ means covered in a substance; ずくめ entirely filled with a quality; づくし an assortment of related things; めく to show signs of or take on an air of something. Memorize ずくめ versus づくし.",
    ["まみれ", "ずくめ", "づくし", "めく"], `
けが人は血___の服を押さえて助けを求めた。|まみれ|血まみれ|ちまみれ|The injured person held their blood-covered clothes and called for help.|血が付着して一面を覆うこと is 血まみれ.
ぬかるみで転び、全身が泥___になった。|まみれ|泥まみれ|どろまみれ|I fell in the mud and became covered in it all over.|泥が体に付着して覆う状態 is 泥まみれ.
炎天下で働き、シャツが汗___になった。|まみれ|汗まみれ|あせまみれ|Working in the blazing sun left my shirt soaked with sweat.|汗で一面が覆われる状態 is 汗まみれ.
帽子から靴まで全部黒の、黒___の服装だった。|ずくめ|黒ずくめ|くろずくめ|The outfit was entirely black from hat to shoes.|全部黒 describes a single quality throughout: 黒ずくめ.
自由がほとんどない、規則___の生活に疲れた。|ずくめ|規則ずくめ|きそくずくめ|I grew tired of a life governed entirely by rules with almost no freedom.|自由がほとんどない indicates a life filled completely with rules.
昇進も決まり、家も見つかり、いいこと___の一年だった。|ずくめ|いいことずくめ|いいことずくめ|With a promotion and a new home, it was a year full of good things.|Good outcomes throughout a period are いいことずくめ.
刺身、焼き魚、煮魚と、魚___の献立を楽しんだ。|づくし|魚づくし|さかなづくし|We enjoyed a menu featuring an assortment of fish dishes: sashimi, grilled fish, and simmered fish.|Different dishes sharing the theme of fish form 魚づくし.|づくし まみれ めく がたい
豪華な料理が次々に出る、ごちそう___の宴会だった。|づくし|ごちそうづくし|ごちそうづくし|It was a banquet featuring one luxurious dish after another.|A succession of varied treats is ごちそうづくし.|づくし まみれ めく がたい
寒さが緩み、日ごとに春___季節になった。|めく|春めく|はるめく|The cold eased, and the season took on more signs of spring each day.|春めく is a verb meaning to become springlike; it directly modifies 季節.
彼は真相を明かさず、謎___笑みを浮かべた。|めく|謎めく|なぞめく|Without revealing the truth, he wore a mysterious smile.|謎めく is a verb meaning to have an air of mystery; it modifies 笑み.
`),
  lesson("n1-verb-endings", "N1", "suffix", "Hard to, cannot, risk & through to the end · がたい・かねる・かねない・抜く",
    "がたい conveys difficulty accepting or accomplishing something; かねる a formal inability or reluctance; かねない a risk of an undesirable outcome; 抜く persistence through completion. Some endings overlap in meaning; the supplied choices isolate the intended form.",
    ["がたい", "かねる", "かねない", "抜く"], `
弱い立場の人をだます行為は、到底許し___。|がたい|許しがたい|ゆるしがたい|Deceiving vulnerable people is utterly unforgivable.|到底 and the moral judgment support 許しがたい, hard to forgive.|がたい だらけ っぽい ずくめ
証拠はあるが、あまりに意外で信じ___話だ。|がたい|信じがたい|しんじがたい|There is evidence, but the story is so unexpected that it is hard to believe.|あまりに意外 identifies difficulty accepting a fact as true.|がたい だらけ っぽい ずくめ
助けてくれた恩師との、忘れ___出会いだった。|がたい|忘れがたい|わすれがたい|It was an unforgettable encounter with the mentor who helped me.|An encounter that remains deeply in memory is 忘れがたい.|がたい だらけ っぽい ずくめ
資料が不足しているため、現時点では判断し___。|かねる|判断しかねる|はんだんしかねる|Because the evidence is insufficient, we are unable to judge at present.|現時点では and the formal limitation support 判断しかねる.|かねる だらけ っぽい ずくめ
個人情報ですので、そのご質問にはお答えし___。|かねる|お答えしかねる|おこたえしかねる|As it concerns personal information, I am unable to answer that question.|お答えしかねる is a formal, polite way to decline to answer.|かねる だらけ っぽい ずくめ
趣旨は理解しますが、その条件には賛成し___。|かねる|賛成しかねる|さんせいしかねる|I understand the intention, but I cannot agree to those conditions.|The concession followed by a formal refusal supports 賛成しかねる.|かねる だらけ っぽい ずくめ
このまま放置すれば、重大事故になり___ので対策が必要だ。|かねない|なりかねない|なりかねない|If left unattended, it could become a serious accident, so measures are needed.|The warning concerns a real risk of an undesirable outcome, not inability.|かねない だらけ っぽい ずくめ
不用意な発言は誤解を招き___ため、注意が必要だ。|かねない|招きかねない|まねきかねない|Careless remarks could cause misunderstandings, so caution is necessary.|誤解 is the undesirable potential result expressed by かねない.|かねない だらけ っぽい ずくめ
長い苦難を最後まで耐え___覚悟がある。|抜く|耐え抜く|たえぬく|I am prepared to endure the long hardship through to the end.|最後まで gives the perseverance through completion in 耐え抜く.|抜く だらけ っぽい ずくめ
途中でやめず、四十二キロを最後まで走り___決意をした。|抜く|走り抜く|はしりぬく|I resolved to run all forty-two kilometers without quitting.|途中でやめず and 最後まで identify completion through sustained effort.|抜く だらけ っぽい ずくめ
`),
  lesson("n1-impressions", "N1", "suffix", "An appearance, resemblance, reproach & adjustment · げ・じみた・がましい・め",
    "げ suggests an outward appearance; じみた an often negative resemblance; がましい behavior perceived as intrusive or inappropriate; め a slight adjustment of degree. Check the printed adjective ending carefully.",
    ["げ", "じみた", "がましい", "め"], `
彼女は何も言わず、寂し___な表情で窓の外を見た。|げ|寂しげ|さびしげ|Without saying anything, she looked out of the window with a lonely expression.|寂しげな describes the outward appearance of loneliness; な is already printed.
少年は悲し___な目で、遠ざかる列車を見送った。|げ|悲しげ|かなしげ|The boy watched the receding train with sad-looking eyes.|悲しげな describes eyes that appear sad, without directly reporting the feeling.
彼は成功を語り、得意___な顔をしていた。|げ|得意げ|とくいげ|He talked about his success with a proud look on his face.|得意げな expresses an outward appearance of pride.
大人なのに、子供___いたずらを繰り返している。|じみた|子供じみた|こどもじみた|Despite being an adult, he repeatedly plays childish pranks.|子供じみた modifies いたずら with a disapproving resemblance to a child.
まだ若いのに、年寄り___小言ばかり言う。|じみた|年寄りじみた|としよりじみた|Despite being young, they constantly nag like an old person.|年寄りじみた describes behavior resembling an elderly person's in a critical tone.
事情の説明より、言い訳___話に聞こえてしまった。|がましい|言い訳がましい|いいわけがましい|It sounded more like excuse-making than an explanation of the circumstances.|言い訳がましい is an い-adjective that criticizes an explanation as sounding like an excuse.
相手の希望を聞かない、押し付け___態度を改めてほしい。|がましい|押し付けがましい|おしつけがましい|I want them to change their overbearing attitude that ignores the other person's wishes.|押し付けがましい criticizes an attitude that imposes something on another person.
少し長くしてほしいので、袖を長___に仕立ててもらった。|め|長め|ながめ|I had the sleeves made slightly longer because I wanted a little extra length.|少し長く identifies the comparative adjustment 長め.
量を少し減らして、ご飯を少な___によそってください。|め|少なめ|すくなめ|Please serve me a slightly smaller portion of rice.|量を少し減らして identifies a modest downward adjustment, 少なめ.
混雑を避けるため、いつもより少し早___に出発した。|め|早め|はやめ|I left a little earlier than usual to avoid the crowds.|いつもより少し早く identifies the slight adjustment in 早め.
`),
];

export const AFFIX_QUESTIONS = AFFIX_LESSONS.flatMap((l) => l.questions);
export const AFFIX_PROGRESS_KEY = "jlpt-affixes-progress-v1";
