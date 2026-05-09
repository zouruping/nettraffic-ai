<template>
  <div class="active-host-table">
    <table>
      <thead>
        <tr>
          <th>序号</th>
          <th>MAC地址</th>
          <th>出现时间</th>
        </tr>
      </thead>
    </table>
    <!-- 婊氬姩瀹瑰櫒 -->
    <div class="table-body-wrapper" ref="wrapper">
      <table>
        <tbody :style="{ transform: `translateY(-${translateY}px)` }">
          <tr v-for="(item, index) in data" :key="index">
            <td>{{ index + 1 }}</td>
            <td>{{ item.mac }}</td>
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
      data: [], // 浠庡悗绔帴鍙ｈ幏鍙栫殑鏁版嵁
      rowHeight: 0,
      translateY: 0,
      timer: null
    };
  },
  methods: {
    async fetchData() {
      try {
        const res = await http.get("/api/dashboard/active-hosts", {
          params: { limit: 50 }
        });
        const rows = Array.isArray(res?.data) ? res.data : [];
        this.data = rows.map((row) => ({
          mac: row.mac_address || "",
          time: row.last_seen || ""
        }));
      } catch (e) {
        console.error("failed to fetch active hosts:", e);
      }
    },

    startScroll() {
      this.stopScroll();
      this.timer = setInterval(() => {
        this.translateY += this.rowHeight;
        if (this.translateY >= this.rowHeight * this.data.length) {
          this.translateY = 0; // 寰幆
        }
      }, this.interval);
    },
    stopScroll() {
      if (this.timer) clearInterval(this.timer);
    }
  },
  async mounted() {
    await this.fetchData();
    // 鑾峰彇琛岄珮
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

/* 鑳屾櫙灞傦紙姣旇〃鏍煎ぇ锛?*/
.active-host-table::before {
  content: "";
  position: absolute;
  top: -3px;
  left: -15px;
  right: -15px;
  bottom: -15px;
  background: rgba(25, 63, 214, 0.25);
  backdrop-filter: blur(0px);
  border-radius: 12px;

  box-shadow: 0 0 10px rgba(0, 114, 255, 0.5), 
              0 0 20px rgba(0, 114, 255, 0.3),
              0 0 30px rgba(0, 114, 255, 0.2);

  z-index: -1;
}

/* 琛ㄦ牸鏁翠綋 */
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
}

/* 琛ㄥご */
thead {
  background: linear-gradient(to right, rgba(0, 114, 255, 0.8), rgba(40, 77, 137, 0.8));
}
th {
  padding: 8px;
  font-size: 14px;
  font-weight: bold;
  color: #cce7ff;
}

/* 婊氬姩涓讳綋瀹瑰櫒 */
.table-body-wrapper {
  height: calc(var(--row-height, 30px) * 4);
  overflow: hidden;
}

/* tbody 婊氬姩鍔ㄧ敾 */
tbody {
  transition: transform 0.6s ease-in-out;
}

/* 琛屾牱寮?*/
td {
  padding: 4px;
  font-size: 12px;
  color: #e6f3ff;
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

/* 鍥哄畾绗竴鍒楀簭鍙峰搴?*/
th:first-child,
td:first-child {
  width: 40px;   /* 浣犲彲浠ユ敼涓?50/70锛屾牴鎹晥鏋滆皟鏁?*/
  text-align: center;
}


</style>

