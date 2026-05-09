<template>
  <div class="active-host-table">
    <table>
      <thead>
        <tr>
          <th>序号</th>
          <th>IP地址</th>
          <th>出现时间</th>
        </tr>
      </thead>
    </table>
    <!-- 滚动容器 -->
    <div class="table-body-wrapper" ref="wrapper">
      <table>
        <tbody :style="{ transform: `translateY(-${translateY}px)` }">
          <tr v-for="(item, index) in data" :key="index">
            <td>{{ index + 1 }}</td>
            <td>{{ item.ip }}</td>
            <td>{{ item.time }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import http from "@/api/http";

export default {
  name: "ActiveHostTable",
  props: {
    pageSize: { type: Number, default: 4 },
    interval: { type: Number, default: 2000 }
  },
  data() {
    return {
      data: [], // 从后端接口获取的数据
      rowHeight: 0,
      translateY: 0,
      timer: null
    };
  },
  methods: {
    async fetchData() {
      try {
        const res = await http.get("/api/dashboard/active-ips", {
          params: { limit: 50 }
        });
        const rows = Array.isArray(res?.data) ? res.data : [];
        this.data = rows.map((row) => ({
          ip: row.ip_address || "",
          time: row.last_seen || ""
        }));
      } catch (e) {
        console.error("获取活跃主机失败：", e);
      }
    },
    startScroll() {
      this.stopScroll();
      this.timer = setInterval(() => {
        this.translateY += this.rowHeight;
        if (this.translateY >= this.rowHeight * this.data.length) {
          this.translateY = 0; // 循环
        }
      }, this.interval);
    },
    stopScroll() {
      if (this.timer) clearInterval(this.timer);
    }
  },
  async mounted() {
    await this.fetchData();
    // 获取行高
    this.$nextTick(() => {
      const firstRow = this.$refs.wrapper.querySelector("tr");
      if (firstRow) {
        this.rowHeight = firstRow.offsetHeight;
        this.$refs.wrapper.style.setProperty("--row-height", `${this.rowHeight}px`);
      }
      this.startScroll();
    });
  },
  beforeDestroy() {
    this.stopScroll();
  }
};
</script>

<style scoped>
.active-host-table {
  width: 85%;
  margin: 0 auto;
  position: relative;
  z-index: 0;
}

/* 背景层（比表格大） */
.active-host-table::before {
  content: "";
  position: absolute;
  top: -3px;
  left: -15px;
  right: -15px;
  bottom: -15px;
  background: rgba(25, 63, 214, 0.25);
  backdrop-filter: blur(12px);
  border-radius: 12px;

    /* 新增发光效果 */
  box-shadow: 0 0 10px rgba(0, 114, 255, 0.5), 
              0 0 20px rgba(0, 114, 255, 0.3),
              0 0 30px rgba(0, 114, 255, 0.2);

  z-index: -1;
}

/* 表格整体 */
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 12px;
  color: #fff;
  text-align: center;
  background: transparent;
  /* border: 3px solid rgba(0, 114, 255, 0.6); */
  border-radius: 6px;
  overflow: hidden;
  table-layout: fixed;
}

/* 表头 */
thead {
  background: linear-gradient(to right, rgba(0, 114, 255, 0.8), rgba(40, 77, 137, 0.8));
}
th {
  padding: 8px;
  font-size: 14px;
  font-weight: bold;
  color: #cce7ff;
  text-align: center;       /* 表头文字居中 */
  vertical-align: middle;   /* 垂直居中 */
}

/* 滚动主体容器 */
.table-body-wrapper {
  height: calc(var(--row-height, 30px) * 4);
  overflow: hidden;
}

/* tbody 滚动动画 */
tbody {
  transition: transform 0.6s ease-in-out;
}

/* 行样式 */
td {
  padding: 4px;
  font-size: 12px;
  color: #e6f3ff;
  text-align: center;       /* 表格文字水平居中 */
  vertical-align: middle;   /* 表格文字垂直居中 */
}
tbody tr:nth-child(odd) {
  background: rgba(0, 114, 255, 0.05);
}
tbody tr:nth-child(even) {
  background: rgba(0, 114, 255, 0.1);
}
tbody tr:hover {
  background: rgba(0, 114, 255, 0.25);
  transition: background 0.3s ease;
}

/* 固定第一列序号宽度 */
th:first-child,
td:first-child {
  width: 60px;   /* 你可以改为 50/70，根据效果调整 */
  text-align: center;
}


</style>
