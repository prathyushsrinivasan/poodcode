import { question, type ReadingPassage } from "./types";

export const INFORMATION_PASSAGES: ReadingPassage[] = [
  { id: "information-001", kind: "information", title: "市民講座の申し込み", topic: "Community", skill: "Find information", level: 2, texts: [{ text:
    `みどり市交流センター　夏の市民講座

【講座一覧】
・写真入門：7月6日・13日（日）10時～12時、全2回。対象は高校生以上。定員16名。受講料2,000円。スマートフォンでも参加できます。
・親子工作：7月12日（土）13時～16時。対象は小学生と保護者の組。定員10組。1組1,500円。子どもだけの参加はできません。
・暮らしの日本語：7月5日から毎週土曜日、10時～11時半、全4回。対象は日常会話を練習したい成人。定員12名。受講料は無料。教材費500円を初日にお支払いください。

【申し込み】
6月10日から20日までに、ホームページの申込欄、またはセンター窓口で申し込んでください。電話では申し込みできません。窓口は平日9時～17時です。市外の方も申し込めますが、定員を超えた場合は市内在住・在勤の方を優先して抽選します。先着順ではありません。結果は6月25日までにメールまたは郵送でお知らせします。

【支払いとキャンセル】
有料講座の受講料は、参加決定の通知後、6月30日までに窓口で現金にてお支払いください。教材費は各講座の初日に集めます。7月1日以降のキャンセルは受講料を返金できません。ただし、センターの都合で中止した場合は全額返金します。

【当日の案内】
開始10分前までに受付を済ませ、参加決定の通知をお見せください。写真入門の機材の貸し出しはありません。工作で使う道具は用意します。駐車場は台数が少ないため、公共交通機関をご利用ください。講座についての相談は電話でも受け付けます。`,
    translation: "Midori Community Center summer courses: photography, July 6 and 13, 10–12, high-school age and above, 16 places, ¥2,000; smartphones allowed. Parent-child crafts, July 12, 13–16, elementary pupil plus guardian, ten pairs, ¥1,500 per pair. Everyday Japanese, four Saturdays from July 5, 10–11:30, adults, twelve places, free tuition with ¥500 materials paid on day one. Apply online or at the weekday 9–17 counter June 10–20; no telephone applications. Nonresidents may apply, but residents/local workers receive lottery priority if oversubscribed; not first-come. Results by June 25. Paid-course tuition is due in cash at the counter by June 30. No refunds for cancellations from July 1, except full refunds if the center cancels. Check in ten minutes early with the acceptance notice. No photography equipment loan; craft tools supplied. Use public transport. Telephone inquiries are accepted." }], questions: [
      question("information-001-q1", { prompt: "日常会話を練習したい成人が、暮らしの日本語に参加する場合、どの案内が正しいか。", correct: "6月20日までに申し込み、教材費500円は初日に払う。", evidence: ["教材費500円を初日にお支払いください。", "6月10日から20日まで"], explanation: "Combine the shared application deadline with this course's separate materials payment. Free tuition does not mean zero total cost.", wrong: [["電話で申し込み、6月30日までに受講料500円を払う。", "Telephone applications are not accepted, and ¥500 is a materials fee due on day one."], ["市外の人は申し込めない。", "Nonresidents may apply; only selection priority differs."], ["申し込みは不要で、全て無料である。", "Application is required and materials cost ¥500."]] }),
      question("information-001-q2", { prompt: "写真入門に当選して支払った人が、7月2日に自分の都合でキャンセルする。どうなるか。", correct: "受講料は返金されない。", evidence: ["7月1日以降のキャンセルは受講料を返金できません。"], explanation: "A July 2 personal cancellation falls after the nonrefund cutoff. The center-cancellation exception does not apply.", wrong: [["初回の前なので必ず全額返金される。", "The cutoff is July 1, not the first class date."], ["センター都合の中止と同じ扱いで全額返金される。", "The question explicitly states the participant's own reasons."], ["抽選前なので支払いはなかったことになる。", "The scenario states selection and payment have already occurred."]] }),
    ] },
  { id: "information-002", kind: "information", title: "図書館の改修案内", topic: "Culture", skill: "Find information", level: 2, texts: [{ text:
    `中央図書館　改修工事中のサービスについて

中央図書館は、8月1日から31日まで閲覧室を閉鎖します。工事中は建物内の本棚、自習席、コピー機を利用できません。返却ポストは通常どおり24時間使えます。ただし、CD・DVDと大型の資料はポストに入れず、臨時窓口または分館へお持ちください。

【臨時窓口】
正面入口の右側に設けます。火曜日から土曜日の10時～17時に開き、日曜日・月曜日・祝日は休みです。予約資料の受け取り、資料の返却、利用カードの更新を行います。窓口で本を選ぶことはできません。利用カードをお持ちください。代理の方が予約資料を受け取る場合は、予約者本人のカードが必要です。

【予約と受け取り】
ホームページでの予約は工事中も可能です。予約資料が用意できた方にはメールで連絡します。受け取り期限は連絡日の翌日から7日間です。休業日もこの日数に含みます。臨時窓口で受け取りにくい方は、資料の準備ができる前に、受け取り場所を東分館または西分館に変更できます。準備完了の連絡後は変更できません。

【分館の開館時間】
東分館：火～日曜日、9時～19時。月曜日と祝日は休館。
西分館：月・水～土曜日、10時～18時。火・日曜日と祝日は休館。
両分館とも閲覧、自習、コピー、予約資料の受け取りができます。中央図書館の資料を返すこともできます。

【貸出期間】
7月20日から31日に中央図書館で借りた本は、返却期限を一律9月7日とします。分館で借りた本には通常の貸出期間が適用されます。工事に関する最新のお知らせはホームページで確認してください。`,
    translation: "Central Library's reading rooms are closed August 1–31 for renovation. Shelves, study seats, and copying are unavailable. The return slot stays open 24 hours, but discs and large materials must go to the temporary counter or a branch. The temporary counter opens Tuesday–Saturday 10–17, excluding holidays, for reserved-item pickup, returns, and card renewal, not shelf browsing. Proxy pickup requires the reserving person's card. Online reservations continue; pickup is due within seven days counted from the day after notice, including closure days. Change to East or West Branch before readiness notice only. East opens Tuesday–Sunday 9–19, closed Monday and holidays. West opens Monday and Wednesday–Saturday 10–18, closed Tuesday, Sunday, and holidays. Both support reading, study, copies, pickup, and Central returns. Books borrowed at Central July 20–31 have a uniform September 7 due date; branch loans keep ordinary periods." }], questions: [
      question("information-002-q1", { prompt: "工事中の祝日ではない日曜日に、CDを返して自習もしたい。どこを利用すればよいか。", correct: "東分館。", evidence: ["CD・DVDと大型の資料はポストに入れず", "東分館：火～日曜日、9時～19時。"], explanation: "CDs need a counter and self-study needs an open reading facility. East Branch is open Sunday; the temporary counter and West Branch are not.", wrong: [["中央図書館の返却ポストだけ。", "The slot cannot accept CDs and offers no self-study space."], ["中央図書館の臨時窓口。", "It is closed Sunday and does not provide study seats."], ["西分館。", "West Branch is closed on Sundays."]] }),
      question("information-002-q2", { prompt: "予約資料の準備完了メールを受け取った後、受け取り場所を変更したい。案内に合うものはどれか。", correct: "準備完了の連絡後なので、変更できない。", evidence: ["準備完了の連絡後は変更できません。"], explanation: "The rule is tied to readiness notification, not whether the seven-day collection period has expired.", wrong: [["受け取り期限内ならいつでも変更できる。", "The location-change deadline precedes readiness, not pickup expiry."], ["日曜日だけ変更できる。", "No Sunday exception is stated."], ["代理人が申し込めば必ず変更できる。", "The proxy rule concerns pickup with a card, not changing locations."]] }),
    ] },
  { id: "information-003", kind: "information", title: "交流施設の予約", topic: "Community", skill: "Find information", level: 3, texts: [{ text:
    `さくら交流館　部屋の利用案内

【部屋と料金】（1時間当たり）
会議室A：定員12名、800円。机・椅子あり。飲食可。楽器不可。
会議室B：定員24名、1,200円。机・椅子、映像設備あり。飲食可。楽器不可。
音楽室：定員10名、1,500円。電子ピアノあり。楽器可。水以外の飲食不可。
市内在住または在勤の代表者が申し込む場合、部屋代を20％割り引きます。備品の料金には割引がありません。

【時間と予約】
開館は9時～21時、月曜日は休館です。予約は1時間単位で、準備と片付けも予約時間に含みます。使用日の2か月前の同日9時から、ホームページまたは窓口で申し込めます。電話は空き状況の問い合わせのみです。予約後3日以内に窓口で料金を払い、利用許可書を受け取ってください。支払いがない場合、予約は自動的に取り消されます。

【備品】
プロジェクターは1回500円です。会議室Bの映像設備には画面だけが含まれ、投影機は別に予約する必要があります。各部屋ともインターネット接続は無料ですが、接続用の機器はご自身で用意してください。備品は数に限りがあるため、部屋と同時に予約してください。

【変更・取消】
使用日の7日前までの取消は全額、6日前から前日までは半額を返金します。当日の取消は返金できません。日時の変更も、いったん取消をして新しく予約する扱いとなります。施設側の事情による中止は全額返金します。

【利用当日】
代表者は利用許可書を受付に提示してください。定員を超えて入室することはできません。販売目的の催しは利用できません。ごみは持ち帰り、机と椅子を元の位置に戻してください。退出時には職員が室内を確認します。`,
    translation: "Sakura Exchange Hall hourly rates: Meeting A, capacity 12, ¥800, food allowed, no instruments; Meeting B, 24, ¥1,200, screen available, food allowed, no instruments; Music Room, ten, ¥1,500, electronic piano, instruments allowed, water only. Representatives living or working locally get 20% off room charges, not equipment. Open 9–21, closed Monday. Whole-hour bookings include setup and cleanup. Reserve online or at the counter from 9 a.m. two months before the use date; phone inquiries only. Pay at the counter within three days or the booking lapses. A projector costs ¥500 per use and is separate from Meeting B's screen. Internet is free but bring connection equipment. Reserve scarce equipment with the room. Cancellation at least seven days before gives a full refund, six days through the previous day half, and same day none. Date changes count as cancellation and rebooking. Facility-caused cancellation gives a full refund. Present the permit, obey capacity, no sales events, take rubbish home, restore furniture, and allow exit inspection." }], questions: [
      question("information-003-q1", { prompt: "市内在勤の代表者が18名の勉強会で映像を投影する。会議室Bを2時間、投影機を1回予約すると合計はいくらか。", correct: "2,420円。", evidence: ["会議室B：定員24名、1,200円。", "部屋代を20％割り引きます。備品の料金には割引がありません。", "プロジェクターは1回500円です。"], explanation: "Capacity requires B. Room cost is ¥1,200 × 2 × 0.8 = ¥1,920. Add the undiscounted ¥500 projector: ¥2,420. The screen does not include the projector.", wrong: [["1,920円。", "This omits the separate projector fee."], ["2,320円。", "This incorrectly discounts the ¥500 equipment charge too: (2,400 + 500) × 0.8."], ["2,900円。", "This ignores the representative's 20% room discount."]] }),
      question("information-003-q2", { prompt: "使用日の3日前に、予約を別の日へ移したい。どの扱いになるか。", correct: "元の予約は半額返金の取消となり、別の日を新しく予約する。", evidence: ["6日前から前日までは半額を返金します。", "日時の変更も、いったん取消をして新しく予約する扱い"], explanation: "Combine the date-change rule with the applicable cancellation window. Three days before falls in the half-refund period.", wrong: [["日にちだけの変更なので必ず全額が戻る。", "A date change is expressly treated as cancellation."], ["当日ではないので返金は一切ない。", "No refund applies only on the use day; three days before gives half."], ["電話で空き状況を聞けば自動的に移される。", "Telephone contact is for availability inquiries only, not booking."]] }),
    ] },
];
