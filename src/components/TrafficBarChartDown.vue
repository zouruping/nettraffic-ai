<template>
  <div class="traffic-bar-chart">

        <!-- 右上角说明 -->
    <div class="chart-tip">单位/{{ unit }}（下行流量）</div>

    <div class="chart-body-wrapper" ref="wrapper">
      <div
        class="chart-body"
        :style="{ transform: `translateY(-${translateY}px)` }"
      >
        <div
          v-for="(item, index) in sortedData"
          :key="index"
          class="bar-row"
        >
          <div class="label">{{ item.ip }}</div>
          <div class="bar-wrapper">
            <div
              class="bar"
              :style="{ width: (item.value / maxValue * 100) + '%' }"
            >
              <span class="value">{{ item.value }} {{ unit }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import http from "@/api/http";

export default {
  name: "TrafficBarChart",
  props: {
    unit: {
      type: String,
      default: "MB"
    },
    pageSize: {
      type: Number,
      default: 4
    },
    interval: {
      type: Number,
      default: 2000
    }
  },
  data() {
    return {
      rowHeight: 0,
      translateY: 0,
      timer: null,
      visibleRows: 5,
      chartData: []   // 接口数据存这里
    };
  },
  computed: {
    maxValue() {
      return Math.max(...this.chartData.map(d => d.value), 1);
    },
    sortedData() {
      return this.chartData.slice().sort((a, b) => b.value - a.value);
    }
  },
  methods: {
    async fetchData() {
      try {
        const res = await http.get("/api/dashboard/high-traffic-ips", {
          params: { limit: 20 }
        });
        const rows = Array.isArray(res?.data) ? res.data : [];
        this.chartData = rows.map((row) => ({
          ip: row.ip_address || "",
          value: Number((Number(row.byte_count || 0) / (1024 * 1024)).toFixed(2))
        }));
      } catch (err) {
        console.error("获取流量数据失败:", err);
      }
    },
    startScroll() {
      this.stopScroll();
      this.timer = setInterval(() => {
        this.translateY += this.rowHeight;
        if (this.translateY >= this.rowHeight * this.chartData.length) {
          this.translateY = 0; // 循环滚动
        }
      }, this.interval);
    },
    stopScroll() {
      if (this.timer) clearInterval(this.timer);
    }
  },
  async mounted() {
    await this.fetchData();
    this.$nextTick(() => {
      const firstRow = this.$refs.wrapper.querySelector(".bar-row");
      if (firstRow) {
        this.rowHeight = firstRow.offsetHeight + 8;
        this.$refs.wrapper.style.height = `${this.rowHeight * this.visibleRows}px`;
      }
      this.startScroll();
    });

    // 定时刷新数据
    setInterval(this.fetchData, 5000);
  },
  beforeDestroy() {
    this.stopScroll();
  }
};
</script>

<style scoped>
.traffic-bar-chart {
  width: 80%;
  margin: 0 auto;
  padding: 20px;
  color: #fff;
  position: relative;
  border-radius: 12px;
  overflow: visible;

}

/* 背景层发光 - 区分第一个表格 */
.traffic-bar-chart::before {
  content: "";
  position: absolute;
  top: -3px;
  left: -10px;
  right: -10px;
  bottom: -15px;
  background: rgba(0, 200, 255, 0.15);  /* 更偏青色 */
  backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 200, 255, 0.5), 
              0 0 20px rgba(0, 200, 255, 0.3),
              0 0 30px rgba(0, 200, 255, 0.2);
  z-index: -1;
}

/* 滚动容器 */
.chart-body-wrapper {
  height: auto;
  overflow: hidden;
}

/* 滚动内容 */
.chart-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform 0.6s ease-in-out;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label {
  width: 120px;
  text-align: right;
  font-size: 12px;
  color: #e6f3ff;
}

.bar-wrapper {
  flex: 1;
  background: rgba(0, 200, 255, 0.1); /* 微调底色 */
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.bar {
  height: 20px;
  background: linear-gradient(to right, #00c8ff, #284d89); /* 主柱子渐变稍偏青蓝 */
  border-radius: 8px 0 0 8px;
  display: flex;
  align-items: center;
  padding-left: 8px;
  transition: width 0.6s ease-in-out;
}

.value {
  font-size: 8px;
  color: #fff;
}

.chart-tip {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 10px;
  color: #aeefff;  /* 更亮的青色，与表格区别 */
  font-weight: 500;
  z-index: 10;
  pointer-events: none;
}


</style>
