<template>
  <div class="box">
    <div ref="chart" style="width: 100%; height: 100%"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import 'echarts-gl';
import http from "@/api/http";

export default {
  name: 'OfficialPie3D',
  data() {
    return {
      chart: null,
      chartData: [] // 接口返回后填充
    };
  },
  mounted() {
    this.chart = echarts.init(this.$refs.chart);
    this.fetchAndRender();
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
    if (this.chart) this.chart.dispose();
  },
  methods: {
  async fetchAndRender() {
    try {
      const { data } = await http.get("/api/dashboard/protocols/transport");
      
      // data 形如 [{ id, l7: "SSDP", bytes: 51988638 }, ...]
      if (!Array.isArray(data)) {
        this.chartData = [];
        this.chart.setOption(this.getOption(), true);
        return;
      }

      // 1) 聚合：相同 l7 的 bytes 相加
      const agg = new Map(); // l7 -> totalBytes
      for (const row of data) {
        const key = (row?.protocol ?? "Unknown") + "";
        const bytes = Number(row?.byte_count ?? 0);
        agg.set(key, (agg.get(key) ?? 0) + (Number.isFinite(bytes) ? bytes : 0));
      }

      // 2) 计算总量与占比
      const totalBytes = Array.from(agg.values()).reduce((s, v) => s + v, 0);
      // 避免除零
      const safeDiv = (a, b) => (b > 0 ? a / b : 0);

      // 颜色盘（可按需扩充/替换）
      const palette = [ '#564AF1', '#27B9CC', '#5AC3FF', '#3CD495',
        '#FF8C00', '#FF4C4C', '#9B59B6', '#2ECC71',
        '#3498DB', '#F39C12', '#1ABC9C', '#E74C3C'];
      const colorOf = (idx) => palette[idx % palette.length];

      // 3) 转为图表需要的结构：value=百分比（保留两位）
      const entries = Array.from(agg.entries()); // [[l7, bytes], ...]
      // 可按 bytes 降序排序，让大块更显眼
      entries.sort((a, b) => b[1] - a[1]);

      this.chartData = entries.map(([name, bytes], idx) => {
        const percent = +(safeDiv(bytes, totalBytes) * 100).toFixed(2);
        return {
          name,
          value: percent,      // 用百分比作为扇区权重/高度
          rawBytes: bytes,     // 备用：tooltip 显示原始字节
          itemStyle: { color: colorOf(idx) }
        };
      });

      this.chart.setOption(this.getOption(), true);
    } catch (e) {
      console.error('加载3D玫瑰图数据失败：', e);
      this.chartData = [];
      this.chart.setOption(this.getOption(), true);
    }
  },
    handleResize() {
      if (this.chart) this.chart.resize();
    },
    getParametricEquation(startRatio, endRatio, isSelected, isHovered, k, height) {
      let midRatio = (startRatio + endRatio) / 2;
      let startRadian = startRatio * Math.PI * 2;
      let endRadian = endRatio * Math.PI * 2;
      let midRadian = midRatio * Math.PI * 2;

      if (startRatio === 0 && endRatio === 1) isSelected = false;
      k = k || 1 / 3;

      let offsetX = isSelected ? Math.cos(midRadian) * 0.1 : 0;
      let offsetY = isSelected ? Math.sin(midRadian) * 0.1 : 0;
      let hoverRate = isHovered ? 1.05 : 1;

      return {
        u: { min: -Math.PI, max: Math.PI * 3, step: Math.PI / 32 },
        v: { min: 0, max: Math.PI * 2, step: Math.PI / 20 },
        x: (u, v) => {
          if (u < startRadian) return offsetX + Math.cos(startRadian) * (1 + Math.cos(v) * k) * hoverRate;
          if (u > endRadian) return offsetX + Math.cos(endRadian) * (1 + Math.cos(v) * k) * hoverRate;
          return offsetX + Math.cos(u) * (1 + Math.cos(v) * k) * hoverRate;
        },
        y: (u, v) => {
          if (u < startRadian) return offsetY + Math.sin(startRadian) * (1 + Math.cos(v) * k) * hoverRate;
          if (u > endRadian) return offsetY + Math.sin(endRadian) * (1 + Math.cos(v) * k) * hoverRate;
          return offsetY + Math.sin(u) * (1 + Math.cos(v) * k) * hoverRate;
        },
        z: (u, v) => (Math.sin(v) > 0 ? height : -1)
      };
    },
    getPie3D(pieData, internalDiameterRatio) {
      let series = [];
      let sumValue = pieData.reduce((sum, item) => sum + item.value, 0);
      let startValue = 0;
      let k = (1 - internalDiameterRatio) / (1 + internalDiameterRatio);

      pieData.forEach(item => {
        let endValue = startValue + item.value;
        series.push({
          name: item.name,
          type: 'surface',
          parametric: true,
          wireframe: { show: false },
          itemStyle: item.itemStyle,
          pieData: item,
          parametricEquation: this.getParametricEquation(
            startValue / sumValue,
            endValue / sumValue,
            false,
            false,
            k,
            item.value
          )
        });
        startValue = endValue;
      });

      // 支撑环
      [0, 1, 2].forEach(i => {
        series.push({
          name: 'mouseoutSeries',
          type: 'surface',
          parametric: true,
          wireframe: { show: false },
          itemStyle: { opacity: 0.1, color: '#E1E8EC' },
          parametricEquation: {
            u: { min: 0, max: Math.PI * 2, step: Math.PI / 20 },
            v: { min: 0, max: Math.PI, step: Math.PI / 20 },
            x: (u, v) => ((Math.sin(v) * Math.sin(u) + Math.sin(u)) / Math.PI) * (2 + i * 0.2),
            y: (u, v) => ((Math.sin(v) * Math.cos(u) + Math.cos(u)) / Math.PI) * (2 + i * 0.2),
            z: () => -5 - i * 2
          }
        });
      });

      return series;
    },
    
  getOption() {
    return {
      legend: {
        data: this.chartData.map(d => d.name),
        bottom: '0%',
        textStyle: { 
          color: '#fff', 
          fontSize: 14 
        },
        itemGap: 20
      },
      tooltip: {
        formatter: params => {
          // 过滤支撑环/空数据
          const pd = params?.data;
          if (!pd || !pd.name) return '';
          const percent = (pd.value ?? 0).toFixed(2) + '%';
          const bytes = (pd.rawBytes ?? 0).toLocaleString(); // 千分位
          return `<div style="font-size: 14px; padding: 5px;">
              <div style="color: #fff; margin-bottom: 5px;">${pd.name}</div>
              <div style="display:flex;align-items:center;margin-bottom:3px;">
                <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${params.color};margin-right:8px;"></span>
                占比：${percent}
              </div>
              <div>字节数：${bytes}</div>
            </div>`;
        },
        textStyle: { fontSize: 14 }
      },
      xAxis3D: { min: -1, max: 1 },
      yAxis3D: { min: -1, max: 1 },
      zAxis3D: { min: -1, max: 1 },
      grid3D: {
        show: false,
        boxHeight: 1.4,
        viewControl: { 
          distance: 180, 
          alpha: 25, 
          beta: 70, 
          center: [0, -16, 0],
          autoRotate: true 
        }
      },
      series: [
        ...this.getPie3D(this.chartData, 0.8),
        // 用于图例/tooltip 数据同步（不可见）
        { name: 'pie2d', type: 'pie', radius: [0, 0], data: this.chartData, itemStyle: { opacity: 0 } }
      ]
    };
    }
  }
};
</script>

<style>
.box {
  padding-left: 30px;
  padding-top: 0px;
  height: 90%;
  width: 90%;
}
</style>
