/**
 * The icon set (UI_ROADMAP C6).
 *
 * Emoji were the icons: every nav item, most buttons and many headings. They
 * render differently on every OS, cannot follow the theme colour, and turn a
 * dense toolbar into confetti. These are Lucide's stroke icons, bundled with
 * the app (it is offline, so nothing is fetched) and tree-shaken, so only the
 * ones named below ship.
 *
 * Callers name an icon by *meaning* — `curriculum`, `run`, `reset` — never by
 * the Lucide name. The mapping is this one table, so swapping a glyph, or the
 * whole set, is a change here rather than a sweep of every page.
 *
 * Emoji stay where they are content rather than chrome: flags, celebrations,
 * 日本語 flashcards.
 */

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  BookMarked,
  BookOpen,
  Bookmark,
  Boxes,
  Braces,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Circle,
  CircleDashed,
  Clipboard,
  ClipboardCheck,
  Clock,
  Code2,
  Coffee,
  Columns3,
  Compass,
  Copy,
  Database,
  Download,
  ExternalLink,
  Eye,
  EyeOff,
  FileCode2,
  FileText,
  Filter,
  FlaskConical,
  Flame,
  Focus,
  GitCompare,
  GraduationCap,
  Hammer,
  HardDrive,
  HelpCircle,
  History,
  Home,
  Inbox,
  Info,
  Keyboard,
  Languages,
  Layers,
  Lightbulb,
  ListChecks,
  ListTree,
  Lock,
  Map as MapIcon,
  Maximize2,
  Minimize2,
  Minus,
  MoreHorizontal,
  NotebookPen,
  Palette,
  PanelLeftClose,
  PanelLeftOpen,
  Pencil,
  Play,
  Plus,
  RefreshCw,
  Repeat,
  RotateCcw,
  Save,
  Search,
  Send,
  Server,
  Settings,
  Shuffle,
  SlidersHorizontal,
  Sparkles,
  Star,
  Target,
  Terminal,
  Timer,
  Trash2,
  TrendingDown,
  TrendingUp,
  Trophy,
  Upload,
  Wrench,
  X,
  XCircle,
  type LucideIcon,
} from "lucide-react";

const ICONS = {
  // Navigation and places.
  today: Home,
  curriculum: BookMarked,
  learn: BookOpen,
  paths: Compass,
  playground: FlaskConical,
  stepper: Repeat,
  typescript: FileCode2,
  java: Coffee,
  backend: Server,
  projects: Boxes,
  mastery: GraduationCap,
  japanese: Languages,
  settings: Settings,
  insights: BarChart3,
  browse: ListTree,
  map: MapIcon,

  // Actions.
  run: Play,
  submit: Send,
  save: Save,
  reset: RotateCcw,
  refresh: RefreshCw,
  copy: Copy,
  copied: ClipboardCheck,
  clipboard: Clipboard,
  edit: Pencil,
  add: Plus,
  remove: Minus,
  delete: Trash2,
  close: X,
  search: Search,
  filter: Filter,
  columns: Columns3,
  sliders: SlidersHorizontal,
  shuffle: Shuffle,
  download: Download,
  upload: Upload,
  external: ExternalLink,
  more: MoreHorizontal,
  show: Eye,
  hide: EyeOff,
  compare: GitCompare,
  focus: Focus,
  expand: Maximize2,
  shrink: Minimize2,
  sidebarClose: PanelLeftClose,
  sidebarOpen: PanelLeftOpen,

  // Direction.
  back: ArrowLeft,
  forward: ArrowRight,
  chevronLeft: ChevronLeft,
  chevronRight: ChevronRight,
  chevronDown: ChevronDown,
  chevronUp: ChevronUp,

  // Status.
  check: Check,
  done: CheckCircle2,
  failed: XCircle,
  warning: AlertTriangle,
  info: Info,
  help: HelpCircle,
  todo: Circle,
  partial: CircleDashed,
  locked: Lock,
  star: Star,
  bookmark: Bookmark,

  // Things.
  code: Code2,
  braces: Braces,
  terminal: Terminal,
  notes: NotebookPen,
  document: FileText,
  hint: Lightbulb,
  checklist: ListChecks,
  layers: Layers,
  database: Database,
  disk: HardDrive,
  keyboard: Keyboard,
  palette: Palette,
  target: Target,
  timer: Timer,
  clock: Clock,
  history: History,
  streak: Flame,
  trophy: Trophy,
  sparkles: Sparkles,
  tools: Wrench,
  build: Hammer,
  inbox: Inbox,
  trendUp: TrendingUp,
  trendDown: TrendingDown,
} satisfies Record<string, LucideIcon>;

export type IconName = keyof typeof ICONS;

export const ICON_NAMES = Object.keys(ICONS) as IconName[];

/**
 * An icon. Decorative by default (`aria-hidden`), because nearly every icon
 * sits beside a text label that already says what it means. Pass `label` for
 * the rare icon that stands alone and carries meaning.
 */
export function Icon({
  name,
  size = 16,
  label,
  className = "",
  strokeWidth = 2,
}: {
  name: IconName;
  size?: number;
  label?: string;
  className?: string;
  strokeWidth?: number;
}) {
  const Glyph = ICONS[name];
  return (
    <Glyph
      className={`icon ${className}`}
      width={size}
      height={size}
      strokeWidth={strokeWidth}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? "img" : undefined}
      focusable="false"
    />
  );
}
