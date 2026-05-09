<template>
  <div id="app">
    <TimeWeather />
    <WarningInfo />
    <div class="header">
      <dv-decoration-8 :color="['#284D89', '#0072ff']" style="width:300px;height:50px;" />
      <div class="title">网络流量监测系统</div>
      <dv-decoration-8 :color="['#284D89', '#0072ff']" :reverse="true" style="width:300px;height:50px;" />
    </div>

    <div class="three-columns">
      
      <div class="column first-column-box">
        <div class="first-column-container">
          <!-- 涓婂崐閮ㄥ垎 -->
          <div class="section">
            <SectionTitle title="活跃主机" />
            <!-- 鐢?v-if 鎺у埗鏄剧ず鍝釜琛?-->
            <div class="section-content">
              <ActiveHostTable 
                v-if="showActiveHost" 
                :data="activeHosts" 
                :pageSize="4" 
                :interval="2000" 
              />
              <!-- <ActiveHostTableIP 
                v-else 
                :data="activeHostsIP" 
                :pageSize="4" 
                :interval="2000" 
              /> -->
            </div>
          </div>

            <div class="divider">
              <dv-decoration-10 style="width:100%;height:100%;" />
            </div>

            <!-- 绗簩閮ㄥ垎锛堟柊澧烇級 -->
            <div class="section">
              <SectionTitle title="活跃IP" />
              <div class="section-content">
                <ActiveHostTableIP 
                  :pageSize="4" 
                  :interval="2000" 
                />
                <NewChartOrTable :data="newData" />
              </div>
            </div>

          <div class="divider">
              <dv-decoration-10 style="width:100%;height:100%;" />
          </div> <!-- 涓棿鍒嗗壊绾?-->

          <!-- 涓嬪崐閮ㄥ垎 -->
          <div class="section">
            <SectionTitle title="高流量IP" />
            <div class="section-content">
              <!-- 鏍规嵁 currentTrafficChart 鍒囨崲缁勪欢 -->
              <TrafficBarChart v-if="currentTrafficChart === 0" /> 
              <!-- <TrafficBarChart :data="trafficData" /> -->
              <TrafficBarChartDown v-else  /> 
            </div>
          </div>
        </div>
      </div>

      <!-- 绗簩鍒?-->
      <div class="column second-column-box">
          <div class="second-column-container">

                <!-- 鏂板涓婇儴鍒?20% -->
          <div class="section upper-section">
            <div class="section-content">
              <ActiveHostBox :title="'活跃主机数'" :number="237" />
              <ActiveIPBox :title="'活跃IP数'" :number="1017" />
            </div>
          </div>

          <!-- 涓棿閮ㄥ垎 60% (鍦板浘) -->
          <div class="section middle-section">
            <div class="section-content">
              <div class="section-content active-host-row">
                <!-- 鍙斁 ActiveHostBox / ActiveIPBox -->
              </div>
              <div class="china-map-box"><ChinaMap /></div>
            </div>
          </div>

          <!-- 涓嬮儴鍒?20% (娴侀噺瓒嬪娍) -->
          <dv-border-box-12 class="section bottom-section">
            <SectionTitle title="流量趋势预测" />
            <TrafficTrend />
          </dv-border-box-12>
        
        </div>
      </div>

      <!-- 绗笁鍒?-->
      <div class="column third-column-box">
        <div class="third-column-container">
          <!-- 涓婂崐閮ㄥ垎 -->
          <div class="section">
            <SectionTitle title="应用层协议" />
            <div class="section-content">
              <protocolProportionl7></protocolProportionl7>
            </div>
          </div>
          
          <div class="divider">
            <dv-decoration-10 style="width:100%;height:100%;" />
          </div> <!-- 涓棿鍒嗗壊绾?-->

              <!-- 涓棿閮ㄥ垎锛堟柊澧烇級 -->
          <div class="section">
            <SectionTitle title="传输层协议" />
            <div class="section-content">

              <ProtocolProportionl4></ProtocolProportionl4>
            </div>
          </div>

          <div class="divider">
            <dv-decoration-10 style="width:100%;height:100%;" />
          </div>

          <!-- 涓嬪崐閮ㄥ垎 -->
          <div class="section">
            <SectionTitle title="实时报警数" />
            <div class="section-content">
              <WarningChart></WarningChart>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ChatBotWidget />
  </div>
</template>

<script>

import TimeWeather from "@/components/TimeWeather.vue";  // 寮曞叆缁勪欢
import SectionTitle from "@/components/SectionTitle.vue";
import protocolProportionl7 from '@/components/protocolProportionl7.vue';
import WarningChart from '@/components/warningChart.vue';
import ActiveHostBox from '@/components/ActiveHostBox.vue';
import ActiveIPBox from '@/components/ActiveIPBox.vue';
import ActiveHostTable from '@/components/ActiveHostTable.vue';
import TrafficBarChart from "./components/TrafficBarChart.vue";
import ChinaMap from "./components/ChinaMap.vue";
import TrafficTrend from "./components/TrafficTrend.vue"; 
import ActiveHostTableIP from "./components/ActiveHostTableIP.vue";
import ProtocolProportionl4 from "./components/protocolProportionl4.vue";
import TrafficBarChartDown from "./components/TrafficBarChartDown.vue";
import WarningInfo from "./components/WarningInfo.vue";
import ChatBotWidget from "./components/ChatBotWidget.vue";

export default {
  name: 'App',
  components: {
    TimeWeather, // 娉ㄥ唽缁勪欢
    SectionTitle,
    protocolProportionl7,
    WarningChart,
    ActiveHostBox,
    ActiveIPBox,
    ActiveHostTable,
    TrafficBarChart,
    ChinaMap,
    TrafficTrend,
    ActiveHostTableIP,
    ProtocolProportionl4,
    WarningInfo,
    TrafficBarChartDown,
    ChatBotWidget

  },
  data() {
    return {
      showActiveHost: true,  // 鎺у埗鏄剧ず鍝釜琛ㄦ牸
      switchInterval: null,  // 淇濆瓨瀹氭椂鍣?ID
      activeHosts: [
        { mac: '00:1A:2B:3C:4D:5E', time: '2025-09-10 10:00:01' },
        { mac: '00:1A:2B:3C:4D:5F', time: '2025-09-10 10:01:15' },
        { mac: '00:1A:2B:3C:4D:60', time: '2025-09-10 10:02:20' },
        { mac: '00:1A:2B:3C:4D:61', time: '2025-09-10 10:03:30' },
        { mac: '00:1A:2B:3C:4D:62', time: '2025-09-10 10:04:50' },
        { mac: '00:1A:2B:3C:4D:63', time: '2025-09-10 10:05:10' },
        { mac: '00:1A:2B:3C:4D:64', time: '2025-09-10 10:06:25' },
        { mac: '00:1A:2B:3C:4D:5E', time: '2025-09-10 10:00:01' },
        { mac: '00:1A:2B:3C:4D:5F', time: '2025-09-10 10:01:15' },
        { mac: '00:1A:2B:3C:4D:60', time: '2025-09-10 10:02:20' },
        { mac: '00:1A:2B:3C:4D:61', time: '2025-09-10 10:03:30' },
        { mac: '00:1A:2B:3C:4D:62', time: '2025-09-10 10:04:50' },
        { mac: '00:1A:2B:3C:4D:63', time: '2025-09-10 10:05:10' },
        { mac: '00:1A:2B:3C:4D:64', time: '2025-09-10 10:06:25' },
      ],
      // activeHostsIP: [
      //   { ip: '192.168.0.1', time: '2025-09-10 10:00:01' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:01:15' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:02:20' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:03:30' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:04:50' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:05:10' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:06:25' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:00:01' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:01:15' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:02:20' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:03:30' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:04:50' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:05:10' },
      //   { ip: '192.168.0.1', time: '2025-09-10 10:06:25' },
      // ],
      trafficData: [
        { ip: "192.168.0.1", value: 120 },
        { ip: "192.168.0.2", value: 300 },
        { ip: "192.168.0.3", value: 180 },
        { ip: "192.168.0.4", value: 90 },
        { ip: "192.168.0.5", value: 220 },
        { ip: "192.168.0.1", value: 120 },
        { ip: "192.168.0.2", value: 300 },
        { ip: "192.168.0.3", value: 180 },
        { ip: "192.168.0.4", value: 90 },
        { ip: "192.168.0.5", value: 220 },
      ],
      currentTrafficChart: 0,
      chartTimer: null,
    };
  },
  mounted() {
    this.chartTimer = setInterval(() => {
      this.currentTrafficChart = (this.currentTrafficChart + 1) % 2;
    }, 15000);
  },
  beforeDestroy() {
    if (this.switchInterval) {
      clearInterval(this.switchInterval);
    }
    if (this.chartTimer) clearInterval(this.chartTimer);
  }
}
</script>

<style>
body{
  background-image: url('./assets/bg.png');
}

html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}


/* 椤堕儴鏍囬鏍?*/
.header {
  height: 55px;
  display: flex;
  align-items: center;
  justify-content: center; /* 涓変釜瀛愬厓绱犳暣浣撳眳涓?*/
  color: #fff;
  margin-bottom: 5px;
}

.title {
  margin: 0 30px;   /* 鏍囬鍜屽乏鍙宠楗扮暀鐐归棿璺?*/
  font-size: 42px;
  font-weight: bold;
  color: #ffffff;
}

.three-columns {
  display: flex;
  width: 100%;
  height: calc(100% - 60px);
}



.column {
  /* flex: 1;             涓夊垪绛夊垎 */
  display: flex;       /* 淇濊瘉鍐呭灞呬腑鍙帶 */
  align-items: stretch;
  justify-content: center;
}

.three-columns {
  display: flex;
  width: 100%;
  height: calc(100% - 60px);
}

.column.first-column-box {
  flex: 1; /* 宸﹀垪 */
}

.column.second-column-box {
  flex: 2; /* 涓棿鍒?*/
}

.column.third-column-box {
  flex: 1; /* 鍙冲垪 */
}


/* 绗竴鍒楀鍣?*/
.first-column-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: 8px;
}


/* .first-column-container .section {
  flex: 1;           
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  color: #ffffff;
  padding: 10px 0;
} */

/* 绗竴鍒楃殑涓変釜section锛氬潎鍒嗛珮搴?*/
.first-column-container .section {
  flex: 1; /* 鏍稿績锛氫笁涓猻ection鍧囧垎鍓╀綑楂樺害锛堢埗瀹瑰櫒楂樺害 - 2涓猟ivider楂樺害 - gap锛?*/
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  color: #ffffff;
  padding: 8px 0;
  box-sizing: border-box; /* 纭繚padding涓嶅奖鍝嶉珮搴?*/
}

/* 绗竴鍒楀唴瀹瑰尯锛氶槻姝㈠唴瀹规孩鍑烘拺澶у鍣?*/
.first-column-container .section .section-content {
  flex: 1; /* 鍐呭鍖哄崰婊ection鍓╀綑楂樺害 */
  width: 90%; /* 鍐呭鍖哄搴︾暀杈癸紝浼樺寲瑙嗚 */
  padding: 8px;
  /* overflow: auto; 鍐呭瓒呭嚭鏃舵粴鍔紝涓嶅奖鍝嶉珮搴?*/
  min-height: 0; /* 鍏抽敭锛氳В鍐砯lex瀛愬厓绱犳孩鍑洪棶棰?*/
  box-sizing: border-box;
}

/* section 鍐呴儴鍐呭鎾戞弧 */
.section-content {
  flex: 1;
  width: 100%;
  padding: 10px;
}

/* 绗笁鍒楀鍣?*/
.third-column-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px; 
}

/* 绗笁鍒楃殑涓変釜 section */
.third-column-container .section {
  flex: 1; /* 涓変釜 section 骞冲垎鍓╀綑楂樺害 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  padding: 8px 0;
  box-sizing: border-box;
}

.third-column-container .section .section-content {
  flex: 1; /* 鍐呭鍗犳弧 section 鍓╀綑绌洪棿 */
  width: 90%; 
  min-height: 0; /* 闃叉 flex 瀛愬厓绱犳孩鍑?*/
}

/* 姣忎釜涓婁笅閮ㄥ垎 */
.section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  color: #ffffff;
  padding: 10px 0;
}

.section-content {
  width: 100%;
  /* height: 80%;  */
  flex: 1;
  padding: 10px;
}

/* 涓棿鍒嗗壊绾?*/
.divider {
  height: 2px;
  background: linear-gradient(to right, #284D89, #0072ff, #284D89);
  width: 80%;
  margin: 0 auto;
  border-radius: 1px;
}

/* 绗笁鍒楄竟妗嗙粍浠?- 宸﹀彸鍐呬晶绔栫嚎 */
.third-column-box {
  position: relative; /* 鍏抽敭锛氳浼厓绱犵浉瀵逛簬鑷繁瀹氫綅 */
}

/* 宸﹁竟鍐呬晶绔栫嚎 */
/* .third-column-box::before {
  content: ""; 
  position: absolute;
  left: 3%; 
  top: 20%; 
  bottom: 20%; 
  width: 3px; 
  
  background: linear-gradient(to bottom, #0072ff, #284D89);
  z-index: 1; 
} */

/* 鍙宠竟鍐呬晶绔栫嚎 */
/* .third-column-box::after {
  content: "";
  position: absolute;
  right: 4%; 
  top: 10%;
  bottom: 10%;
  width: 2px;
  background: linear-gradient(to bottom, #0072ff, #284D89);
  z-index: 1;
} */

/* 绗簩鍒楀鍣?*/
.second-column-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;  /* 绾靛悜鎺掑垪 */
}

.second-column-container .upper-section {
  flex: 0.5;   
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin-top: -2%;
}

.second-column-container .upper-section .section-content {
  display: flex;            /* 妯悜鎺掑垪 */
  flex-direction: row;      /* 涓昏酱姘村钩 */
  justify-content: center;  /* 灞呬腑瀵归綈 */
  align-items: center;      /* 鍨傜洿灞呬腑 */
  gap: 5%;                /* 涓や釜 box 涔嬮棿鐣欑偣闂磋窛 */
}


.second-column-container .middle-section {
  flex: 7.5;   /* 60% */
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.second-column-container .bottom-section {
  flex: 2;  
  min-height: 0;
  display: flex;
  flex-direction: column;
  /* margin-bottom: -2%; */
}


.bottom-section {
  display: flex;
  flex-direction: column; /* 涓婁笅鎺掑垪 */
}

.bottom-section > .section-title {
  flex: 0 0 auto; /* 鏍囬鍥哄畾楂樺害 */
}

.bottom-section > *:last-child {
  flex: 1;        /* 鉁?TrafficTrend 鍗犳弧鍓╀綑绌洪棿 */
  min-height: 0;  /* 鍏抽敭锛氶伩鍏嶆孩鍑?*/
}

.border-box-11-title {
  font-size: 22px;
}

.active-host-row {
  display: flex;
  justify-content: center;
  gap: 40px;
}

/* 绗竴鍒楄竟妗嗙粍浠?- 宸﹀彸鍐呬晶绔栫嚎 */
.first-column-box {
  position: relative; /* 鍏抽敭锛氳浼厓绱犵浉瀵逛簬鑷繁瀹氫綅 */
}

/* 宸﹁竟鍐呬晶绔栫嚎 */
/* .first-column-box::before {
  content: ""; 
  position: absolute;
  left: 18px; 
  top: 10%; 
  bottom: 10%; 
  width: 2px; 
  
  background: linear-gradient(to bottom, #0072ff, #284D89);
  z-index: 1; 
} */

/* 鍙宠竟鍐呬晶绔栫嚎 */
/* .first-column-box::after {
  content: "";
  position: absolute;
  right: 10px; 
  top: 10%;
  bottom: 40%;
  width: 3px;
  background: linear-gradient(to bottom, #0072ff, #284D89);
  z-index: 1;
} */

.china-map-box {
  /* background-image: url(@/assets/sky.png); */
  flex: 1;                 /* 鍗犳弧鐖跺鍣ㄥ墿浣欑┖闂?*/
  display: flex;           /* 鐢?flex 灞呬腑鍐呴儴 */
  align-items: center;     /* 鍨傜洿灞呬腑 */
  justify-content: center; /* 姘村钩灞呬腑 */
  /* margin-top: -22px; */
  /* margin-left: 75px; */
  height: 100%;
  width: 100%;
  
}

.china-map-box > * {
  width: 100%;   /* 鍦板浘瀹藉害鍗犲鍣?90% */
  height: 100%;  /* 楂樺害鍗犲鍣?90%锛屼篃鑳借嚜閫傚簲 */
}


</style>


