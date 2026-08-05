import ReactECharts from "echarts-for-react";
import { useStore } from "../store";

export const PALETTE = ["#4c8dff", "#2bb673", "#e6a23c", "#e15b64", "#9b6cff", "#39c0c8", "#f06292"];

function axisText(theme: "dark" | "light") {
  return theme === "dark" ? "#9aa7b4" : "#57636f";
}
function gridLine(theme: "dark" | "light") {
  return theme === "dark" ? "#2a323d" : "#e2e8f0";
}

export function Chart({ option, height = 260 }: { option: any; height?: number }) {
  const theme = useStore((s) => s.prefs.theme);
  const t = axisText(theme);
  const g = gridLine(theme);
  const base = {
    color: PALETTE,
    textStyle: { color: t, fontFamily: "inherit" },
    grid: { left: 40, right: 20, top: 30, bottom: 30, containLabel: true },
    tooltip: { trigger: "item" },
    ...option,
    xAxis: option.xAxis && {
      axisLine: { lineStyle: { color: g } },
      axisLabel: { color: t },
      splitLine: { show: false },
      ...option.xAxis,
    },
    yAxis: option.yAxis && {
      axisLine: { show: false },
      axisLabel: { color: t },
      splitLine: { lineStyle: { color: g } },
      ...option.yAxis,
    },
  };
  return <ReactECharts option={base} style={{ height }} notMerge={true} />;
}
