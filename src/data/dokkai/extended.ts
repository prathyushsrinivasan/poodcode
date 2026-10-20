import { question, type QuestionDraft, type ReadingKind, type ReadingPassage, type ReadingSkill } from "./types";

function passage(id: string, kind: ReadingKind, title: string, topic: string, skill: ReadingSkill, level: 1 | 2 | 3,
  texts: ReadingPassage["texts"], drafts: QuestionDraft[]): ReadingPassage {
  return { id, kind, title, topic, skill, level, texts, questions: drafts.map((q, i) => question(`${id}-q${i + 1}`, q)) };
}

export const EXTENDED_PASSAGES: ReadingPassage[] = [
  passage("medium-001", "medium", "会議を減らした後に", "Work", "Main point", 2, [{ text:
    `私たちの会社では、仕事に集中する時間を増やすため、定例会議を半分に減らした。最初の月は予定表が空き、全員が歓迎した。ところが、しばらくすると、別の部署がどこまで進んでいるか分からないという声が増えた。以前の会議では、議題そのもの以外にも、仕事の背景や小さな変更が伝わっていたのである。

そこで、会議を元の数に戻す前に、何の情報が不足しているかを調べた。すると、長い説明が必要な問題より、担当者や次の期限が分からない場面が多かった。各部署が週に一度、進んだ点、困っている点、他の部署に頼みたい点を短く書く場所を作った。読む時間も勤務の予定に含め、疑問があればその場で担当者に聞けるようにした。

一か月後、全ての問題が消えたわけではないが、以前の情報を探す手間は減った。込み入った相談には、今も顔を合わせる会議を使っている。会議が多いことだけを問題にしていたときには、会議が担っていた働きを見ていなかった。減らすことを成功と呼ぶ前に、失われる役割を確かめ、別の方法で支える必要があったのだ。仕事の改善では、目に見える回数だけでなく、人が次に行動できるかどうかまで見たい。`,
    translation: "Our company halved recurring meetings to create focused work time. Staff initially welcomed free calendars, but later lacked cross-department updates. Meetings had conveyed context and small changes as well as formal agenda items. Before restoring them, we investigated the missing information and found uncertainty mostly about owners and deadlines. Departments now post weekly progress, difficulties, and requests, with reading time included in work schedules and direct questions possible. Information-search effort decreased, while complex discussions still use meetings. Counting fewer meetings as success overlooks lost functions; improvement requires supporting those functions by other means and checking whether people can act." }], [
    { prompt: "会議を減らした後、どのような問題が起きたか。", correct: "他部署の状況を知る機会が減った。", evidence: ["別の部署がどこまで進んでいるか分からない"], explanation: "The first paragraph identifies loss of cross-department awareness, not a lack of free time.", wrong: [["予定表に空きがなくなった。", "The calendars initially became freer."], ["全員がすぐに会議の削減に反対した。", "Everyone initially welcomed the reduction."], ["資料を書く時間が禁止された。", "No writing ban is mentioned."]] },
    { prompt: "筆者が改善の際に必要だと考えることは何か。", correct: "減らす仕組みが担っていた役割も、別の方法で支えること。", evidence: ["失われる役割を確かめ、別の方法で支える必要があった"], explanation: "The conclusion explains the lesson of the experiment: preserve needed functions while changing their delivery. Complex meetings remain useful.", wrong: [["回数が減れば、内容に関係なく成功とすること。", "The author explicitly challenges success measured only by count."], ["情報共有を全て会議に戻すこと。", "Weekly written updates replace routine sharing; only complex discussions use meetings."], ["読む時間を全て勤務時間の外に置くこと。", "Reading time is explicitly included in the work schedule."]] },
  ]),
  passage("medium-002", "medium", "本を選ぶ棚", "Culture", "Reason", 2, [{ text:
    `図書館で本を探す方法は、一つではない。題名や著者を知っていれば、検索すればすぐ場所が分かる。だが、何を読みたいか自分でも決まっていないときは、検索する言葉を思いつくことさえ難しい。私の図書館では、そのような人のために、毎月違う問いを掲げた小さな棚を作っている。

今月の問いは『待つ時間をどう過ごすか』だった。小説、料理の本、植物を育てる本など、普段は別の場所にある本が隣り合っている。分類を正確に示す棚ではなく、まだ名前のない関心に出会うための棚なのだ。私は電車の待ち時間に読む短い物語を探すつもりだったが、種から花が咲くまでを描いた本を借りた。待つという経験を、これまでとは違う時間の長さで考えられた。

もちろん、この棚だけで全ての利用者に応えられるわけではない。目的の本を速く見つける検索も欠かせない。しかし、速く見つかることと、思いがけず見つかることは別の価値である。関心がはっきりする前にも利用できる場所があることで、図書館への入口は広がる。欲しい情報を渡すだけでなく、何を知りたいかが生まれる場でもあってほしい。`,
    translation: "Library search quickly locates a known title or author, but choosing search terms is hard when one's interest is unclear. My library offers a small monthly shelf organized by a question, this month 'How do we spend time waiting?' Fiction, cooking, and plant books meet outside their normal categories. I went for short stories for train waits but borrowed a book about seeds becoming flowers, reconsidering waiting on another timescale. The display cannot meet every need, and precise search remains essential. Fast retrieval and unexpected discovery have different value. Libraries can help interests emerge, as well as supply already desired information." }], [
    { prompt: "問いを掲げた棚を作る主な理由は何か。", correct: "読みたい内容がまだ決まっていない人にも発見の入口を作るため。", evidence: ["まだ名前のない関心に出会うための棚"], explanation: "The display supports emerging interests for which a user cannot yet formulate search terms.", wrong: [["分類番号を全てなくすため。", "The regular search and organization remain necessary."], ["全員に同じ植物の本を借りさせるため。", "The shelf contains multiple genres and purposes."], ["題名が分かる本を検索できなくするため。", "The author explicitly values precise search too."]] },
    { prompt: "筆者が植物の本を借りたことは、何を示す例か。", correct: "予定していなかった見方に出会うこと。", evidence: ["待つという経験を、これまでとは違う時間の長さで考えられた。"], explanation: "The initial plan and eventual book differ; this illustrates unexpected discovery rather than failed retrieval.", wrong: [["検索すれば必ず最初の目的どおりの本が見つかること。", "The example is a changed interest, not an exact search result."], ["小説を読む人がいなくなったこと。", "One reader's choice does not establish this."], ["植物の本しか図書館にないこと。", "The passage lists several genres."]] },
  ]),
  passage("medium-003", "medium", "学び直す時間", "Learning", "Inference", 2, [{ text:
    `社会人になってから、私は夜の講座で統計を学び始めた。学生時代には、試験で正しい答えを出すことが勉強の目的になっていた。ところが、仕事で調査の結果を読むようになると、計算できるだけでは、何を信じてよいか判断できないと感じた。数字がどのような条件で集められたかを知る必要があった。

講座では、先生が最初に答えを教えるのではなく、二つの調査を見せ、どちらを参考にしたいか尋ねる。受講者は人数の多さに注目したり、質問の仕方を気にしたりする。意見を比べてから必要な考え方を習うと、その知識が何のためにあるかが分かりやすい。公式を覚えるのも必要だが、使う場面のないまま覚えたときとは、残り方が違う気がする。

仕事の後の勉強は楽ではない。毎回、全てを理解できるわけでもない。それでも、翌日の会議で資料を見る目が少し変わると、また学びたくなる。すぐ役に立つ内容だけを学べばよいという意味ではない。自分の疑問と知識の間に橋が架かる経験が、学び続ける理由になるのだと思う。学び直しは、忘れた答えを取り戻すだけでなく、新しい問いの持ち方を身につけることでもあった。`,
    translation: "As an adult I began evening statistics classes. School study had centered on correct exam answers, but reading work surveys showed that calculation alone does not establish trustworthiness; data-collection conditions matter. The teacher first shows two surveys and asks which we would use. Comparing classmates' concerns before learning concepts clarifies their purpose. Evening study is hard and understanding incomplete, but changed perception at the next day's meeting motivates me. This is not a demand to study only immediately useful material. Connecting personal questions and knowledge sustains learning; relearning also means acquiring new ways to ask questions." }], [
    { prompt: "筆者が統計を学び始めたきっかけは何か。", correct: "調査の数字を判断するには、計算以外の理解も必要だと感じたこと。", evidence: ["計算できるだけでは、何を信じてよいか判断できない"], explanation: "The workplace exposed a need to evaluate the conditions behind figures, beyond obtaining numerical answers.", wrong: [["学生時代の試験をもう一度受けること。", "No repeat school examination is planned."], ["仕事で使う数字を全て暗記すること。", "The issue is evaluating evidence, not memorizing every figure."], ["講座の時間が勤務時間になったこと。", "Classes take place after work."]] },
    { prompt: "筆者にとって、学び続ける理由となっているのは何か。", correct: "自分の疑問が知識と結びつき、見方が変わる経験。", evidence: ["自分の疑問と知識の間に橋が架かる経験が、学び続ける理由になる"], explanation: "The bridge is a metaphor for meaningful connection between inquiry and knowledge, not a claim of complete or instant mastery.", wrong: [["毎回全てを完全に理解できること。", "The writer explicitly says complete understanding is not achieved every time."], ["役立つまで時間がかかる内容を全て避けること。", "The author explicitly rejects studying only immediately useful material."], ["公式を使う場面を考えず覚えること。", "The class helps reveal the situations that make concepts useful."]] },
  ]),
  passage("medium-004", "medium", "店を閉める一時間", "Community", "Main point", 2, [{ text:
    `商店街の小さなパン屋が、週に一日だけ閉店時刻を一時間早めた。人手が足りないのだろうと思って尋ねると、店主は、その時間を使って働く人同士で話していると答えた。忙しい営業中には、新人が気づいたことを聞く余裕がなかったそうだ。売る時間を短くするのは勇気が要るが、今後も店を続けるための時間だと言う。

話し合いから、商品の並べ方や注文の受け方が変わった。以前は、一番経験のある人が何でも答えていたが、今はよくある質問を全員が確認できる場所にまとめている。店主が一日休んだときも、他の人が判断しやすくなった。早く閉める日の売上だけを見れば減っているが、それ以外の日の無駄や、誰か一人に集中する負担は小さくなったという。

私はそれまで、店が開いている時間だけが、店のために働いている時間だと思っていた。しかし、目の前の商品を売ることと、その仕事を続けられる状態を作ることは、どちらも必要なのだ。もちろん全ての店が同じ方法を選べるわけではない。それでも、今すぐ数字に表れない時間をどう確保するかは、売る物の種類を越えて考える価値がある。働き続けるための準備も、仕事の中に含めてよいのだと思う。`,
    translation: "A bakery closes an hour early one day a week, not merely for lack of staff but to let workers discuss observations unheard during busy sales. Conversations changed display and ordering, and a shared FAQ reduced reliance on one experienced person. The early-closing day's sales fell, but waste and concentrated burden decreased elsewhere. I had assumed only open hours counted as work. Selling now and maintaining the ability to continue both matter. Not every shop can choose this method, but making room for work whose value is not immediately visible deserves consideration." }], [
    { prompt: "パン屋が早く閉める時間を作った目的は何か。", correct: "職員の意見を聞き、店を続けられる働き方を整えるため。", evidence: ["今後も店を続けるための時間"], explanation: "The reserved time improves shared knowledge and work arrangements, rather than functioning simply as reduced staffing hours.", wrong: [["全ての商品の販売をやめるため。", "The bakery continues selling on its adjusted schedule."], ["新人に意見を言わせないため。", "Hearing newcomers is part of the stated motivation."], ["閉店日の売上だけを最大にするため。", "The passage acknowledges reduced sales during that period."]] },
    { prompt: "筆者の仕事についての考えはどう変わったか。", correct: "仕事を続けられる状態を作る時間も、仕事の一部だと考えた。", evidence: ["働き続けるための準備も、仕事の中に含めてよい"], explanation: "The author's earlier restriction to selling hours is broadened to include maintenance of sustainable work.", wrong: [["売る時間以外には価値がないと考えた。", "This is the earlier view that changed."], ["全ての店が必ず一時間早く閉めるべきだと考えた。", "The author explicitly avoids a universal prescription."], ["売上は一切確認する必要がないと考えた。", "The argument broadens evaluation rather than abolishing financial measures."]] },
  ]),
  passage("medium-005", "medium", "失われた説明", "Technology", "Reference", 3, [{ text:
    `新しい予約システムを導入した施設では、窓口に並ぶ人が大きく減った。操作を知っている人には、いつでも予約できる便利な変化だった。ところが、職員への問い合わせは予想ほど減らなかった。画面には日付や料金が正しく表示されているのに、どの講座を選べばよいか分からない人がいたのだ。

以前、窓口の職員は予約を受けるだけでなく、利用者の経験や希望を聞き、講座の違いを説明していた。その会話は、手続きの記録には残っていなかった。システム化の計画では、入力してもらう項目だけを調べたため、この働きが見えなくなっていたのである。そこで、講座を比較するページと、迷ったときに短く相談できる時間を用意した。

これは、画面をやめて窓口に戻すべきだという話ではない。手続きが簡単になった利点を残しながら、選ぶための支援を補う必要があったということだ。仕事を置き換えるとき、表に見える操作だけを数えると、人がその前後にしていた小さな判断を落としてしまう。便利さを確かめるには、利用者が最後まで目的を果たせるかを見る必要がある。入力が終わったことと、納得して選べたことは、必ずしも同じではない。`,
    translation: "An online booking system reduced queues, but inquiries did not fall as expected. Dates and prices were correct, yet users did not know which course suited them. Desk staff had previously asked about experience and goals and explained differences, an unrecorded function omitted from planning based only on input fields. A comparison page and brief consultation hours were added. This does not call for abandoning the system: retain easier transactions while restoring decision support. Replacing visible operations can miss judgments around them. Completed input is not necessarily an informed choice; success means the user fulfills the whole purpose." }], [
    { prompt: "『この働き』とは何か。", correct: "希望や経験を聞き、講座選びを助けること。", evidence: ["利用者の経験や希望を聞き、講座の違いを説明していた。"], explanation: "The antecedent is the unrecorded advisory conversation, not the recorded reservation input.", wrong: [["画面に正しい料金を表示すること。", "The screen already performed that function correctly."], ["並んでいる人数だけを数えること。", "Queue size is an observed outcome, not the omitted support function."], ["全ての予約を取り消すこと。", "No cancellation policy is discussed."]] },
    { prompt: "筆者が便利さを確かめる基準としていることは何か。", correct: "利用者が納得して選び、目的を果たせるか。", evidence: ["利用者が最後まで目的を果たせるかを見る必要がある。"], explanation: "The final paragraph distinguishes transaction completion from successful end-to-end choice.", wrong: [["窓口の人数が減ったかだけ。", "Queue reduction overlooked ongoing uncertainty."], ["入力項目が増えたかどうか。", "Adding fields is not the identified remedy."], ["職員との会話を全てなくしたか。", "Brief consultation is deliberately restored."]] },
  ]),
];
