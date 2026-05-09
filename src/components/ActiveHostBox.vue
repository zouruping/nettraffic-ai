<template>
  <div class="active-host-box">
    <!-- 左边图标（叠加两个图层） -->
    <div class="icon">
      <img src="@/assets/u132.png" alt="base" class="icon-base" />
      <img src="@/assets/u155.svg" alt="overlay" class="icon-overlay" />
    </div>

    <!-- 中间标题 + 数字 -->
    <div class="content">
      <div class="title">{{ title }}</div>
      <div class="digit-box">
        <div v-for="(digit, index) in sixDigits" :key="index" style="display: flex; align-items: center;">
          <dv-digital-flop
            :config="getDigitConfig(digit)"
            class="digit"
          />
          <!-- 在第三位后面加逗号 -->
          <span v-if="index === 2" class="comma">,</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import http from "@/api/http";

export default {
  name: "ActiveHostBox",
  props: {
    title: {
      type: String,
      default: "活跃主机数"
    },
    // number: {
    //   type: Number,
    //   default: 237
    // }
  },
  data() {
    return {
      number: [] // 接口数据存这里
    };
  },
  computed: {
    sixDigits() {
      return String(this.number).padStart(6, '0').split('');
    }
  },
  methods: {
    async fetchData() {
      try {
        const res = await http.get("/api/dashboard/overview");
        this.number = Number(res?.data?.active_host_count ?? 0);
      } catch (e) {
        console.error("获取活跃主机数失败：", e);
      }
    },
    getDigitConfig(digit) {
      return {
        number: [Number(digit)],
        content: '{nt}',
        style: {
          fontSize: 24,
          fill: '#00f6ff'
        }
      };
    }
  },
  async mounted() {
    await this.fetchData();
    // 每5秒更新一次数据
    // setInterval(this.fetchData, 5000);
  }
};
</script>

<style scoped>
.active-host-box {
  display: flex;
  align-items: center;
  padding: 0.4em 0.8em;
  border: 1px solid rgba(0, 114, 255, 0.6);
  border-left: 6px solid #00f6ff;
  border-radius: 6px;
  background: rgba(38, 65, 137, 0.6);
  box-shadow: 0 0 5px rgba(0, 114, 255, 0.6);

  /* 自适应大小 */
  width: 400px;
  height: 60px;
}

.icon {
  width: 4em;
  height: 3em;
  margin-right: 1em;
  position: relative;
}

.icon-base {
  width: 100%;
  height: 100%;
  position: relative; /* 相对定位 */
  left: 0.3em;        /* 向右移动0.5em，可根据需要调整 */
  top: 0.4em;

}

.icon-overlay {
  position: absolute;
  top: -7%;
  left: 6%;
  width: 100%;
  height: 100%;
  animation: bounce 1s infinite ease-in-out;
}

/* 跳动动画 */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-0.3em);
  }
}

.content {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 1.2em;
  font-weight: bold;
  color: #00f6ff;
  margin-bottom: 0.3em;
  margin-left: 5em;
}

.digit-box {
  display: flex;
  gap: 0.3em;
  /* padding-left: 2em; */
}

.digit {
  width: 2.8em;   /* 固定宽度，确保所有数字框一样大 */
  height: 1.8em;  /* 高度也可以固定 */
  border: 1px solid rgba(0, 246, 255, 0.6);
  border-radius: 4px;
  background: rgba(38, 65, 137, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.comma {
  font-size: 24px;
  color: #00f6ff;
  margin-left: 0.2em; /* 可调整间距 */
}

</style>
