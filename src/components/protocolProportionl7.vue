<template>
  <div class="l7-protocol-pie">
    <div ref="chart" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import http from "@/api/http";
import trafficIcon from "@/assets/traffic3.png";

export default {
  name: "L7ProtocolPie",
  data() {
    return {
      chart: null,
      chartData: [] // 后端返回的数据转成 echarts 所需
    };
  },
  mounted() {
    this.fetchAndRender();
  },
  beforeUnmount() {
    clearInterval(this.jumpInterval);
    window.removeEventListener("resize", this.handleResize);
    if (this.chart) this.chart.dispose();
  },
  methods: {
    async fetchAndRender() {
      try {
        const { data } = await http.get("/api/dashboard/protocols/application");

        if (!Array.isArray(data)) {
          this.chartData = [];
          this.initChart();
          return;
        }

        // 1) 聚合相同 l7 的 bytes
        const agg = new Map();
        for (const row of data) {
          const key = row?.protocol ?? "Unknown";
          const bytes = Number(row?.byte_count ?? 0);
          agg.set(key, (agg.get(key) ?? 0) + (Number.isFinite(bytes) ? bytes : 0));
        }

        // 2) 转成 echarts pie 数据
        const totalBytes = Array.from(agg.values()).reduce((s, v) => s + v, 0);
        const safeDiv = (a, b) => (b > 0 ? a / b : 0);

        const entries = Array.from(agg.entries());
        entries.sort((a, b) => b[1] - a[1]); // 大的在前

        this.chartData = entries.map(([name, bytes]) => {
          return {
            name,
            value: +(safeDiv(bytes, totalBytes) * 100).toFixed(2), // 百分比
            rawBytes: bytes
          };
        });

        this.initChart();
      } catch (e) {
        console.error("加载协议占比数据失败：", e);
        this.chartData = [];
        this.initChart();
      }
    },
    initChart() {
      if (!this.chart) {
        this.chart = echarts.init(this.$refs.chart);
        window.addEventListener("resize", this.handleResize);
      }

      const option = {
        backgroundColor: "transparent",
        tooltip: {
          trigger: "item",
          formatter: params => {
            const percent = params.value + "%";
            const bytes = (params.data.rawBytes ?? 0).toLocaleString();
            return `${params.name}<br/>占比: ${percent}<br/>字节数: ${bytes}`;
          }
        },
        legend: {
          orient: "horizontal",
          bottom: -10,
          textStyle: { color: "#fff", fontSize: 13 }
        },
        series: [
          {
            name: "L7 协议流量占比",
            type: "pie",
            radius: ["40%", "70%"],
            center: ["50%", "36%"],
            animationDuration: 15,
            animationEasing: "cubicOut",
            animationDelay: idx => idx * 10,
            data: this.chartData.map((item, idx) => {
              const colors = [
                ["#00E5FF", "#0072ff"],
                ["#1DE9B6", "#00BFA5"],
                ["#536DFE", "#3949AB"],
                ["#FF6E40", "#D84315"],
                ["#FFD600", "#FFAB00"]
              ];
              const gradient = colors[idx % colors.length];
              return {
                ...item,
                itemStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                    { offset: 0, color: gradient[0] },
                    { offset: 1, color: gradient[1] }
                  ])
                }
              };
            }),
            label: {
              show: true,
              color: "#E0E6F1",
              fontSize: 13,
              formatter: "{d}%"
            },
            labelLine: { lineStyle: { color: "#3A80F7" } },
            itemStyle: {
              borderRadius: 6,
              borderColor: "#0F1325",
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: "rgba(0, 255, 255, 0.4)"
            },
            emphasis: {
              scale: false,
              itemStyle: { shadowBlur: 20, shadowColor: "rgba(0, 255, 255, 0.5)" }
            }
          }
        ],
        graphic: [
          {
            id: "centerIcon",
            type: "image",
            left: "center",
            top: "center",
            style: { image: trafficIcon, width: 40, height: 40 }
          }
        ]
      };

      this.chart.setOption(option);

      // 中心图标上下跳动动画
      let topPos = 28;
      let direction = -1;
      if (this.jumpInterval) clearInterval(this.jumpInterval);
      this.jumpInterval = setInterval(() => {
        topPos += direction * 0.2;
        if (topPos <= 24 || topPos >= 28) direction *= -1;
        this.chart.setOption({
          graphic: { id: "centerIcon", top: topPos + "%" }
        });
      }, 50);
    },
    handleResize() {
      if (this.chart) this.chart.resize();
    }
  }
};
</script>

<style scoped>
.l7-protocol-pie {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
