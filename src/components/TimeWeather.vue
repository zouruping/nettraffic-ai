<template>
  <div class="time-display">
    <div class="time-left">{{ hoursMinutes }}</div>
    <div class="time-right">
      <div class="weekday">{{ weekday }}</div>
      <div class="ymd">{{ ymd }}</div>
    </div>
    <div class="temperature-display">
      <img src="@/assets/temperature.png" alt="温度图标" class="temp-icon" />
      <span class="temp-text">{{ temperature }}°C</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "TimeWeather",
  data() {
    return {
      hoursMinutes: "",
      weekday: "",
      ymd: "",
      temperature: 26, // 默认气温，可用接口更新
    };
  },
  mounted() {
    this.updateTime();
    this.timer = setInterval(this.updateTime, 1000);
  },
  beforeDestroy() {
    clearInterval(this.timer);
  },
  methods: {
    updateTime() {
      const now = new Date();
      this.hoursMinutes = `${String(now.getHours()).padStart(2,"0")}:${String(now.getMinutes()).padStart(2,"0")}`;
      const weekDays = ["日","一","二","三","四","五","六"];
      this.weekday = "星期" + weekDays[now.getDay()];
      this.ymd = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}-${String(now.getDate()).padStart(2,"0")}`;
    },
    fetchTemperature() {
      // fetch('你的天气接口').then(res=>res.json()).then(data=>this.temperature=data.temp)
    }
  }
};
</script>

<style scoped>
.time-display {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  background-color: rgba(0,0,0,0.3);
  padding: 4px 12px;
  border-radius: 6px;
  color: #fff;
  font-family: "Microsoft YaHei", sans-serif;
  gap: 15px;
  z-index: 1000;
}

.temperature-display {
  display: flex;
  align-items: center;
  font-size: 24px;
  color: #fff;
  position: relative;
  padding-left: 16px;
}

.temperature-display::before {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background-color: #fff;
  border-radius: 1px;
}

.temp-icon {
  width: 30px;
  height: 30px;
  margin-right: 6px;
}

.temp-text {
  font-weight: bold;
}

.time-left { font-size: 24px; font-weight: bold; }
.time-right { display:flex; flex-direction: column; font-size:14px; line-height:1.2; }
.weekday{}
.ymd{ font-size:14px; color:#fff; }
</style>
