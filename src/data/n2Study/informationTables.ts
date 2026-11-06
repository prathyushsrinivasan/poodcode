import { authoredChoice, type ExplainedOption } from "./builders";
import type { StudyLesson, StudyText } from "./schema";

export const INFORMATION_TABLE_LESSON: StudyLesson = {
  id: "reading-tables", section: "reading", title: "Read the table and every condition", format: "Tables and notices",
  takeaway: "Combine the matching row with the rules outside the table before deciding.",
  steps: ["Identify the person's time, capacity and budget requirements.", "Find the row that meets every requirement.", "Apply fees, discounts and exceptions from the notice."],
  trap: "The headline price may exclude materials, equipment or other conditions.",
  examples: [{ japanese: "月謝3,500円＋教材費800円＝初月4,300円", english: "Monthly fee plus materials: check the total rather than the headline price." }],
};
type Row = readonly [id: string, prompt: string, answer: string, why: string,
  a: ExplainedOption, b: ExplainedOption, c: ExplainedOption, evidence: string[]];
interface Document { id: string; source: StudyText; questions: Row[] }
const documents: Document[] = [
  { id: "courses", source: {
    label: "地域の日本語講座", text: "全コース初心者向けです。授業は毎週行います。月謝のほか、最初の月だけ教材費800円が必要です。申し込みは先着順で、定員になり次第締め切ります。見学は無料ですが、事前に電話で予約してください。",
    translation: "All courses are for beginners and meet weekly. In addition to the monthly tuition, an 800-yen materials fee is charged in the first month only. Applications are accepted in arrival order until capacity is reached. Observation visits are free but require advance telephone booking. A: Wednesday 18:30–20:00, 4,000 yen monthly, 20 places. B: Saturday 10:00–11:30, 3,500 yen monthly, 15 places. C: Saturday 14:00–15:30, 4,500 yen monthly, 15 places.",
    table: { caption: "講座の時間と月謝", columns: ["コース", "曜日", "時間", "月謝", "定員"], rows: [
      ["A", "水曜日", "18:30–20:00", "4,000円", "20名"], ["B", "土曜日", "10:00–11:30", "3,500円", "15名"], ["C", "土曜日", "14:00–15:30", "4,500円", "15名"],
    ] },
  }, questions: [
    ["saturday-morning", "平日は参加できず、土曜日の午後にも予定がある人が参加できるコースは？", "B", "B meets on Saturday morning; the person is unavailable on weekdays and on Saturday afternoon.", ["A", "A meets on a weekday evening; the person is unavailable on weekdays."], ["C", "C meets on Saturday afternoon, when the person already has plans."], ["AとC", "Neither of these satisfies both of the stated schedule constraints."], ["土曜日", "10:00–11:30"]],
    ["first-month", "コースBの最初の月に必要な金額は？", "4,300円", "The 3,500-yen monthly fee plus the first month's 800-yen materials fee totals 4,300 yen.", ["3,500円", "This omits the first month's materials fee."], ["4,000円", "This is course A's monthly tuition, not course B's first-month total."], ["5,300円", "This uses course C's tuition instead of course B's."], ["3,500円", "最初の月だけ教材費800円が必要"]],
    ["visit", "授業を見学したい人は、どうすればよいか。", "事前に電話で予約し、見学料は払わない。", "The notice explicitly requires advance telephone booking and says the observation visit is free.", ["予約せずに行き、月謝を全額払う。", "The visit requires booking and does not require monthly tuition."], ["必ず教材費800円だけを先に払う。", "The materials fee applies to enrollment, not a free observation visit."], ["初心者は見学できない。", "The courses are for beginners and no such observation restriction is stated."], ["見学は無料ですが、事前に電話で予約してください"]],
  ] },
  { id: "rooms", source: {
    label: "市民センター会議室", text: "利用時間は9時から18時までです。日曜日は休館します。料金は1時間当たりで、1時間以上、30分単位で予約できます。登録済みの非営利団体は、平日に限り室料が20％引きになります。プロジェクターは1回500円で、割引の対象外です。",
    translation: "Rooms are available from 09:00 to 18:00; the center is closed on Sundays. Prices are per hour, with bookings of at least one hour and subsequent half-hour increments. Registered nonprofit groups receive a twenty percent room-fee discount on weekdays only. A projector costs 500 yen per use and is excluded from the discount. Small room: up to 6 people, 600 yen/hour. Medium: up to 12, 1,000 yen/hour. Large: up to 24, 1,800 yen/hour.",
    table: { caption: "会議室の定員と室料", columns: ["会議室", "定員", "1時間の室料"], rows: [
      ["小会議室", "6名", "600円"], ["中会議室", "12名", "1,000円"], ["大会議室", "24名", "1,800円"],
    ] },
  }, questions: [
    ["discount", "登録済みの非営利団体が、火曜日に10人で2時間、最も安い部屋とプロジェクターを使う。合計は？", "2,100円", "Ten people require at least the medium room: 1,000 × 2 × 0.8 + the undiscounted 500-yen projector = 2,100 yen.", ["1,280円", "This uses a too-small room and incorrectly handles the equipment charge."], ["2,000円", "Discounting the combined 2,500 yen also discounts the projector, which is excluded."], ["2,500円", "This omits the weekday room-fee discount available to this registered group."], ["12名", "1,000円", "平日に限り室料が20％引き", "割引の対象外"]],
    ["closed", "20人の団体が日曜日に利用したい。正しい案内は？", "定員に合う部屋はあるが、日曜日は利用できない。", "The large room fits twenty people, but the center is closed on Sundays.", ["大会議室を20％引きで利用できる。", "The center is closed, and the discount applies only on weekdays."], ["小会議室を三つ借りればよい。", "The listed small room holds six, and the entire center is closed on Sunday."], ["プロジェクターを借りれば休館日でも入れる。", "Equipment rental does not override the stated closure."], ["24名", "日曜日は休館"]],
    ["weekend", "5人で土曜日に1時間利用する。プロジェクターは不要。最も安い室料は？", "600円", "Five people fit the small room, costing 600 yen for one hour; no weekday discount applies on Saturday.", ["480円", "This applies the weekday-only discount on Saturday."], ["1,000円", "The medium room costs more and is not needed for five people."], ["1,100円", "This adds a projector that the group does not need."], ["6名", "600円", "平日に限り"]],
  ] },
  { id: "bus", source: {
    label: "駅前から文化会館への直通バス", text: "下の時刻表は平日のものです。すべて文化会館まで直通で、乗り換えはありません。運賃は大人1人の片道料金です。小学生は大人の半額です。予約は不要ですが、出発時刻の5分前までに乗り場へ来てください。",
    translation: "This is the weekday timetable for direct buses from the station to the cultural hall. All services are direct with no transfers. Fares are one-way adult fares; elementary-school children pay half. No reservation is needed, but passengers should reach the stop at least five minutes before departure. Service A leaves 08:10, arrives 08:45, adult fare 400 yen. B leaves 08:35, arrives 09:10, fare 400 yen. C leaves 09:00, arrives 09:40, fare 350 yen.",
    table: { caption: "文化会館行き・平日", columns: ["便", "駅前発", "文化会館着", "大人片道"], rows: [
      ["A便", "8:10", "8:45", "400円"], ["B便", "8:35", "9:10", "400円"], ["C便", "9:00", "9:40", "350円"],
    ] },
  }, questions: [
    ["arrival", "文化会館に8時55分までに着きたい。利用できる便は？", "A便", "A arrives at 08:45; B and C arrive after the 08:55 deadline.", ["B便", "B arrives at 09:10, fifteen minutes after the required arrival time."], ["C便", "C arrives at 09:40, too late for the deadline."], ["B便とC便", "Both arrive after the required 08:55 arrival time."], ["8:45", "9:10", "9:40"]],
    ["fare", "C便を大人2人と小学生1人が片道で利用する。合計運賃は？", "875円", "Two adults pay 700 yen and the child pays half of 350 yen, or 175 yen, totaling 875 yen.", ["700円", "This omits the elementary-school child's fare."], ["1,050円", "This charges the child the full adult fare instead of half."], ["1,000円", "This uses the 400-yen service fare rather than C's 350-yen fare."], ["350円", "小学生は大人の半額"]],
    ["boarding", "B便に乗る人は、遅くとも何時までに乗り場へ来る必要があるか。", "8:30", "B leaves at 08:35, and the notice requires arrival at the stop five minutes beforehand.", ["8:35", "This is departure time and ignores the five-minute advance-arrival rule."], ["9:05", "This is five minutes before destination arrival, not departure."], ["9:10", "This is arrival at the cultural hall, not arrival at the boarding stop."], ["8:35", "出発時刻の5分前まで"]],
  ] },
];
export const INFORMATION_TABLE_QUESTIONS = documents.flatMap((doc) => doc.questions.map(([id, prompt, answer, why, a, b, c, evidence]) =>
  authoredChoice(`reading-table-${doc.id}-${id}`, INFORMATION_TABLE_LESSON.id, prompt, [[answer, why], a, b, c], why, doc.source.translation,
    { texts: [doc.source], evidence, targetSeconds: 140, tags: ["exercise:Tables and notices", `document:${doc.id}`], hint: INFORMATION_TABLE_LESSON.steps[2] })));
