<!-- <template>
<div class="chart-wrapper">
    <div class="chart-container" ref="chart"></div>
</div>
  
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'SalesWaterChart',
  data() {
    return {
      chartInstance: null,
      option: {
        grid: {
          top: 50,       // 鍜岀涓€涓浘琛ㄤ竴鑷?
          left: "0%",
          right: "0%",
          bottom: "0%",
          containLabel: true
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
            label: { show: true }
          },
          textStyle: { color: "#fff" },
          backgroundColor: "rgba(0,0,0,0.6)"
        },
        legend: {
          data: ["告警趋势", "告警数量(KB)"],
          top: 0,  //
          textStyle: { color: "#fff", fontSize: 14 },
          itemGap: 25
        },
        xAxis: {
          type: "category",
          boundaryGap: true,
          data: [
            "03-15 18:42:33",
            "03-15 23:47:42",
            "03-15 23:47:42",
            "03-15 23:47:42",
            "03-15 23:47:42",
            "03-15 23:47:42",
            "03-15 23:47:42",
            "03-15 23:47:42",
          ],
          axisLine: { lineStyle: { color: "#4A9DDD" } },
          axisLabel: { color: "#fff", fontSize: 10 },
          splitLine: { 
            show: true, 
            lineStyle: { color: "rgba(74,157,221,0.2)", type: "dashed" } 
          }
        },
        yAxis: [
          {
            type: "value",
            name: "",
            // nameTextStyle: { color: "#fff" },
            splitLine: { 
              show: true, 
              lineStyle: { color: "rgba(74,157,221,0.2)" } 
            },
            axisLine: { lineStyle: { color: "#4A9DDD" } },
            axisLabel: { color: "#fff" }
          },
          {
            type: "value",
            name: "",
            position: "right",
            splitLine: { show: false },
            axisLine: { lineStyle: { color: "#4A9DDD" } },
            axisLabel: { color: "#fff" }
          }
        ],
        series: [
          {
            name: "告警趋势",
            type: "line",
            yAxisIndex: 1,
            smooth: true,
            symbol: "circle",
            symbolSize: 15,
            itemStyle: { color: "rgba(5,140,255,0.7)" },      // 鎶樼嚎鐐归鑹?
            lineStyle: { color: "rgba(5,140,255,0.7)", width: 2 }, // 鎶樼嚎棰滆壊閫忔槑
            areaStyle: { color: "rgba(5,140,255,0.2)" },       // 鍖哄煙濉厖鏇撮€忔槑
            data: [27, 27, 27, 28, 26, 28, 27, 27]
          },
          {
            name: "告警数量(KB)",
            type: "bar",
            barWidth: 15,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(0,255,227,0.7)" },
                { offset: 1, color: "rgba(70,147,236,0.7)" }
              ])
            },
            data: [27, 27, 27, 28, 26, 28, 27, 27]
          }
        ]
      }
    };
  },
  mounted() {
    this.chartInstance = echarts.init(this.$refs.chart);
    this.chartInstance.setOption(this.option);
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
  methods: {
    handleResize() {
      if (this.chartInstance) this.chartInstance.resize();
    }
  }
};
</script>

<style scoped>
.chart-container {
  width: 85%;
  height: 100%;
  margin: 0 30px; 
  /* padding-top: 40px; 涓哄浘渚嬭吘鍑虹┖闂?*/
  padding-bottom: 0px; 
}

.chart-wrapper {
  position: relative;
  height: 100%;
  margin: 0 10px;
  border-radius: 16px;
  overflow: visible;
}

.chart-wrapper::before {
  content: "";
  position: absolute;
  top: -5px;
  left: 10px;
  right: 10px;
  bottom: -5px;

  background: rgba(0, 200, 255, 0.15);  
  backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 200, 255, 0.5), 
              0 0 20px rgba(0, 200, 255, 0.3),
              0 0 30px rgba(0, 200, 255, 0.2);
  z-index: -1;
}

</style> -->

<template>
  <div class="chart-wrapper">
    <div class="chart-container" ref="chart"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import http from "@/api/http";

export default {
  name: "SalesWaterChart",
  data() {
    return {
      chartInstance: null,
      option: {
        grid: {
          top: 50,
          left: "0%",
          right: "0%",
          bottom: "0%",
          containLabel: true
        },
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow", label: { show: true } },
          textStyle: { color: "#fff" },
          backgroundColor: "rgba(0,0,0,0.6)"
        },
        legend: {
          data: ["告警趋势", "告警数量(KB)"],
          top: 0,
          textStyle: { color: "#fff", fontSize: 14 },
          itemGap: 25
        },
        xAxis: {
          type: "category",
          boundaryGap: true,
          data: [], // 鎺ュ彛杩斿洖鍚庢洿鏂?
          axisLine: { lineStyle: { color: "#4A9DDD" } },
          axisLabel: { color: "#fff", fontSize: 10 },
          splitLine: {
            show: true,
            lineStyle: { color: "rgba(74,157,221,0.2)", type: "dashed" }
          }
        },
        yAxis: [
          {
            type: "value",
            name: "",
            splitLine: {
              show: true,
              lineStyle: { color: "rgba(74,157,221,0.2)" }
            },
            axisLine: { lineStyle: { color: "#4A9DDD" } },
            axisLabel: { color: "#fff" }
          },
          {
            type: "value",
            name: "",
            position: "right",
            splitLine: { show: false },
            axisLine: { lineStyle: { color: "#4A9DDD" } },
            axisLabel: { color: "#fff" }
          }
        ],
        series: [
          {
            name: "告警趋势",
            type: "line",
            yAxisIndex: 1,
            smooth: true,
            symbol: "circle",
            symbolSize: 8,
            itemStyle: { color: "rgba(5,140,255,0.7)" },
            lineStyle: { color: "rgba(5,140,255,0.7)", width: 2 },
            areaStyle: { color: "rgba(5,140,255,0.2)" },
            data: []
          },
          {
            name: "告警数量(KB)",
            type: "bar",
            barWidth: 15,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(0,255,227,0.7)" },
                { offset: 1, color: "rgba(70,147,236,0.7)" }
              ])
            },
            data: []
          }
        ]
      }
    };
  },
  mounted() {
    this.chartInstance = echarts.init(this.$refs.chart);
    this.fetchData(); // 椤甸潰鎸傝浇鍚庤姹傚悗绔暟鎹?
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
  methods: {
    handleResize() {
      if (this.chartInstance) this.chartInstance.resize();
    },
    async fetchData() {
      try {
        const res = await http.get("/api/dashboard/alerts/recent", {
          params: { limit: 20 }
        });
        const rows = Array.isArray(res?.data) ? res.data : [];
        const ordered = rows.slice().reverse();

        this.option.xAxis.data = ordered.map((row) => row.last_seen || "");
        this.option.series[0].data = ordered.map((row) => Number(row.packet_count || 0));
        this.option.series[1].data = ordered.map((row) =>
          Number((Number(row.byte_count || 0) / 1024).toFixed(2))
        );
        this.chartInstance.setOption(this.option);
      } catch (err) {
        console.error("failed to fetch alert data:", err);
      }
    }
  }
};
</script>

<style scoped>
.chart-container {
  width: 85%;
  height: 100%;
  margin: 0 30px;
  padding-bottom: 0px;
}
.chart-wrapper {
  position: relative;
  height: 100%;
  margin: 0 10px;
  border-radius: 16px;
  overflow: visible;
}
.chart-wrapper::before {
  content: "";
  position: absolute;
  top: -5px;
  left: 10px;
  right: 10px;
  bottom: -5px;
  background: rgba(0, 200, 255, 0.15);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 200, 255, 0.5),
              0 0 20px rgba(0, 200, 255, 0.3),
              0 0 30px rgba(0, 200, 255, 0.2);
  z-index: -1;
}
</style>
