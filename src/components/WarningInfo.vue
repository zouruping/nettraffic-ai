<template>
  <div class="warning-info" v-if="messages.length">
    <img class="icon" :src="iconSrc" alt="warning" />
    <div class="message-wrapper">
      <transition-group name="slide" tag="div">
        <div
          v-for="(msg, index) in displayedMessages"
          :key="msg + index"
          class="text"
        >
          {{ msg }}
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script>
import warningIcon from "@/assets/warning.png";

export default {
  name: "WarningInfo",
  props: {
    iconSrc: {
      type: String,
      default: warningIcon, // 小喇叭图标路径
    },
  },
  data() {
    return {
      messages: [
        "网络异常，请检查服务器！",
        "防火墙检测到异常流量！",
        "服务器CPU使用率过高！",
        "网络丢包率超过阈值！",
      ],
      currentIndex: 0,
      intervalId: null,
    };
  },
  computed: {
    displayedMessages() {
      // 只显示当前一条消息
      return [this.messages[this.currentIndex]];
    },
  },
  mounted() {
    // 每 3 秒切换一次消息
    this.intervalId = setInterval(() => {
      this.currentIndex =
        (this.currentIndex + 1) % this.messages.length;
    }, 3000);
  },
  beforeDestroy() {
    if (this.intervalId) clearInterval(this.intervalId);
  },
};
</script>

<style scoped>
.warning-info {
  position: absolute;
  top: 10px;
  right: 20px;
  display: flex;
  align-items: center;
  /* background: rgba(255, 50, 50, 0.1); */
  padding: 6px 12px;
  border-radius: 6px;
  color: #fff;
  /* font-weight: bold; */
  font-size: 18px;
  z-index: 999;
  /* box-shadow: 0 2px 6px rgba(0,0,0,0.2); */
  overflow: hidden;
  width: 17%; /* 宽度固定，可调整 */
}

.warning-info .icon {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  flex-shrink: 0;
}

.message-wrapper {
  flex: 1;
  overflow: hidden;
  height: 20px; /* 与图标同高 */
  position: relative;
  display: flex;           /* ✅ 使用 flex 居中内容 */
  align-items: center;     /* 垂直居中 */
}

.text {
  white-space: nowrap;
  position: absolute;
  width: 100%;
  top: 0;                  /* 保持绝对定位上下移动动画可用 */
  display: flex;
  align-items: center;     /* 垂直居中文字 */
  height: 100%;            /* 占满父容器高度 */
}

/* 滑动动画 */
.slide-enter-active, .slide-leave-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}

.slide-enter {
  transform: translateY(100%);
  opacity: 0;
}

.slide-enter-to {
  transform: translateY(0);
  opacity: 1;
}

.slide-leave {
  transform: translateY(0);
  opacity: 1;
}

.slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
