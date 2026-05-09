<template>
  <div class="trend-wrapper">
    <div class="line-chart trend-chart" ref="chart"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import http from "@/api/http";

export default {
  name: "TrafficLineChart",
  data() {
    return {
      chart: null,
      option: {
        tooltip: {
          trigger: "axis",
          backgroundColor: "rgba(0,0,0,0.6)",
          borderWidth: 0,
          textStyle: { color: "#fff" },
        },
        legend: {
          data: ["实际流量(MB)", "预测流量(MB)"],
          textStyle: { color: "#fff", fontSize: 12 },
          top: 0,
          right: "10%",
          itemGap: 30,
          itemWidth: 20,
          itemHeight: 14,
        },
        grid: {
          left: "5%",
          right: "5%",
          bottom: "10%",
          top: "15%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: [], // 鍔ㄦ€佸～鍏?
          axisLabel: { color: "#fff" },
          axisLine: { lineStyle: { color: "#1f3b5b" } },
          splitLine: { show: false },
        },
        yAxis: {
          type: "value",
          nameTextStyle: { color: "#7ecbff" },
          axisLabel: { color: "#fff" },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: "rgba(126,203,255,0.2)", type: "dashed" } },
        },
        series: [
          {
            name: "实际流量(MB)",
            type: "line",
            smooth: true,
            symbol: "circle",
            symbolSize: 8,
            data: [],
            lineStyle: {
              width: 3,
              color: {
                type: "linear",
                x: 0,
                y: 0,
                x2: 1,
                y2: 0,
                colorStops: [
                  { offset: 0, color: "#00f2fe" },
                  { offset: 1, color: "#4facfe" },
                ],
              },
            },
            itemStyle: {
              color: "#00eaff",
              borderColor: "#fff",
              borderWidth: 2,
              shadowBlur: 8,
              shadowColor: "#00eaff",
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(0, 242, 254, 0.4)" },
                { offset: 1, color: "rgba(0, 242, 254, 0.05)" },
              ]),
            },
          },
          {
            name: "预测流量(MB)",
            type: "line",
            smooth: true,
            data: [],
            lineStyle: {
              width: 2,
              type: "dashed",
              color: "#ffb74d",
              shadowBlur: 6,
              shadowColor: "#ff9800",
            },
            itemStyle: {
              color: "#ff9800",
            },
          },
        ],
      },
    };
  },
  mounted() {
    this.chart = echarts.init(this.$refs.chart);
    this.fetchData(); // 鑾峰彇鍚庣鏁版嵁
    window.addEventListener("resize", this.resizeChart);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.resizeChart);
    if (this.chart) this.chart.dispose();
  },
  methods: {
    resizeChart() {
      if (this.chart) this.chart.resize();
    },
    async fetchData() {
      try {
        const response = await http.get("/api/dashboard/traffic-forecast", {
          params: {
            history_minutes: 180,
            forecast_steps: 12,
            interval_minutes: 1,
            window_size: 12,
            epochs: 30,
          },
        });
        const payload = response?.data || {};
        const history = Array.isArray(payload.history) ? payload.history : [];
        const forecast = Array.isArray(payload.forecast) ? payload.forecast : [];
        if (!history.length && !forecast.length) {
          await this.fetchFallbackData();
          return;
        }

        const labels = [
          ...history.map((p) => (p.time || "").replace("T", " ").slice(5, 16)),
          ...forecast.map((p) => (p.time || "").replace("T", " ").slice(5, 16)),
        ];
        const real = history.map((p) =>
          Number(Number(p.traffic_mb || 0).toFixed(2))
        );
        const future = forecast.map((p) =>
          Number(Number(p.traffic_mb || 0).toFixed(2))
        );

        const actualSeries = [...real, ...new Array(future.length).fill(null)];
        const predSeries = [
          ...new Array(Math.max(real.length - 1, 0)).fill(null),
          ...(real.length ? [real[real.length - 1]] : []),
          ...future,
        ];

        this.option.xAxis.data = labels;
        this.option.series[0].data = actualSeries;
        this.option.series[1].data = predSeries;
        this.chart.setOption(this.option, true);
      } catch (error) {
        await this.fetchFallbackData();
        console.error("鑾峰彇娴侀噺瓒嬪娍鏁版嵁澶辫触:", error);
      }
    },
    async fetchFallbackData() {
      try {
        const response = await http.get("/api/dashboard/high-traffic-ips", {
          params: { limit: 12 },
        });
        const rows = Array.isArray(response?.data) ? response.data : [];
        const ordered = rows.slice().reverse();
        const real = ordered.map((row) =>
          Number((Number(row.byte_count || 0) / (1024 * 1024)).toFixed(2))
        );
        const pred = real.map((v, idx) => {
          if (idx === 0) return v;
          return Number((real[idx - 1] * 0.7 + v * 0.3).toFixed(2));
        });
        this.option.xAxis.data = ordered.map((row) => row.last_seen || "");
        this.option.series[0].data = real;
        this.option.series[1].data = pred;
        this.chart.setOption(this.option, true);
      } catch (err) {
        this.option.xAxis.data = [];
        this.option.series[0].data = [];
        this.option.series[1].data = [];
        this.chart.setOption(this.option, true);
        console.error("fallback 娴侀噺瓒嬪娍鏁版嵁涔熻幏鍙栧け璐?", err);
      }
    },
  },
};
</script>

<style scoped>
.trend-wrapper {
  position: relative;
  width: 100%;
  height: 75%;
  border-radius: 16px;
  display: flex;
  justify-content: center; 
  align-items: center; 
  overflow: visible;
}

.trend-wrapper::before {
  content: "";
  position: absolute;
  top: 0%;
  left: 2%;
  right: 2%;
  bottom: 0;
  margin: -5px;
  background: rgba(0, 200, 255, 0.15);
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 200, 255, 0.5), 
              0 0 20px rgba(0, 200, 255, 0.3),
              0 0 30px rgba(0, 200, 255, 0.2);
  z-index: -1;
}

.trend-chart {
  width: 97%;
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 242, 254, 0.1);
}
</style>
