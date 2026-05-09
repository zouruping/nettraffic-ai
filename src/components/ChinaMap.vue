<template>
  <div style="position: relative; width:100%; height:100%;">

    <canvas ref="bgCanvas" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:0;"></canvas>


    <div ref="chart" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:1;"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';

export default {
  name: 'ChinaMapFlyline',
  data() {
    return {
      chart: null,
      bgCtx: null,
      particles: [],
      gridLines: [],
      animationFrame: null,
      resizeHandler: null
    };
  },
  mounted() {
    const canvas = this.$refs.bgCanvas;
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    this.bgCtx = canvas.getContext('2d');

    this.initGrid(canvas);
    this.initParticles(canvas);

    const animate = () => {
      this.drawBackground(canvas);
      this.animationFrame = requestAnimationFrame(animate);
    };
    animate();

    // 初始化 ECharts
    this.chart = echarts.init(this.$refs.chart);
    this.chart.showLoading();

    axios.get('/json/china.json')
      .then(res => {
        this.chart.hideLoading();
        echarts.registerMap('China', res.data);

        const geoCoordMap = {
          "北京": [116.405285, 39.904989],
          "上海": [121.472644, 31.231706],
          "广东": [113.280637, 23.125178],
          "新疆": [87.617733, 43.792818],
          "陕西": [108.948024, 34.263161]
        };

        const flyData = Object.keys(geoCoordMap)
          .filter(name => name !== '陕西')
          .map(from => ({ from, to: '陕西' }));

        const linesData = flyData.map(item => ({
          coords: [geoCoordMap[item.from], geoCoordMap[item.to]],
        }));

        const option = {
          backgroundColor: 'transparent',
          geo: {
            map: 'China',
            roam: false,
            center: [104, 36],
            aspectScale: 0.80,   // 🔑 调整纵横比，避免拉伸
            layoutCenter: ['50%', '50%'], // 保持地图在容器居中
            layoutSize: '140%',   // 控制整体缩放，不用写 top/left/right/bottom
            label: { show: false },
            itemStyle: {
              areaColor: '#031f42',
              borderColor: '#0ff',
              borderWidth: 1,
              shadowColor: '#00ffff',
              shadowBlur: 100
            },
            emphasis: {
              itemStyle: { areaColor: '#0a4f8f' }
            }
          },
          series: [
            {
              name: '飞线',
              type: 'lines',
              coordinateSystem: 'geo',
              zlevel: 2,
              effect: 
              { 
                show: true, 
                period: 4, 
                trailLength: 0.8, 
                symbol: 'arrow', 
                symbolSize: 3, 
                color: '#ffa500' 
              },
              lineStyle: 
              { 
                color: 'rgba(0, 255, 255, 0.5)', 
                width: 1, 
                opacity: 0.05, 
                curveness: 0.2, 
                shadowBlur: 0, 
                shadowColor: 'transparent' 
              },
                        
              data: linesData
            },
            {
              name: '目标点',
              type: 'effectScatter',
              coordinateSystem: 'geo',
              zlevel: 3,
              rippleEffect: { brushType: 'stroke', period: 4, scale: 4 },
              symbolSize: 15,
              itemStyle: { color: '#ff0000', shadowBlur: 12, shadowColor: '#ff0000' },
              label: { show: false, position: 'right', color: '#fff', fontSize: 12 },
              data: [{ name: '陕西', value: geoCoordMap['陕西'] }]
            },
            {
              name: '发出点',
              type: 'effectScatter',
              coordinateSystem: 'geo',
              zlevel: 3,
              rippleEffect: {
                brushType: 'fill',
                period: 4,
                scale: 6
              },
              symbolSize: 6,
              itemStyle: {
                color: '#ffa500',       // 发出点颜色（和接收点区分）
                shadowBlur: 6,
                shadowColor: '#ffa500'
              },

              data: Object.keys(geoCoordMap)
                .filter(name => name !== '陕西')  // 发出点 = 除了陕西
                .map(name => ({ name, value: geoCoordMap[name] }))
            },

            {
              name: '中国地图',
              type: 'map',
              map: 'China',
              geoIndex: 0,
              data: [],
              itemStyle: { areaColor: 'transparent', borderColor: '#0ff' }
            }
          ]
        };

        this.chart.setOption(option);
      })
      .catch(err => { this.chart.hideLoading(); console.error('加载地图失败：', err); });

    // 窗口自适应
    this._resizeHandler = () => {
      if (this.chart) this.chart.resize();
      canvas.width = canvas.clientWidth;
      canvas.height = canvas.clientHeight;
      this.initGrid(canvas);
    };
    window.addEventListener('resize', this._resizeHandler);
  },
  beforeDestroy() {
    if (this.chart) this.chart.dispose();
    cancelAnimationFrame(this.animationFrame);
    window.removeEventListener('resize', this._resizeHandler);
  },
  methods: {
    initGrid(canvas) {
      this.gridLines = [];
      const step = 50;
      const width = canvas.width;
      const height = canvas.height;
      for (let x = 0; x <= width; x += step) this.gridLines.push({ x1: x, y1: 0, x2: x, y2: height, offset: Math.random() * 20 });
      for (let y = 0; y <= height; y += step) this.gridLines.push({ x1: 0, y1: y, x2: width, y2: y, offset: Math.random() * 20 });
    },
    initParticles(canvas) {
      this.particles = [];
      const count = 100;
      for (let i = 0; i < count; i++) this.particles.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3, r: Math.random() * 2 + 1, alpha: Math.random() * 0.5 + 0.3 });
    },
    drawBackground(canvas) {
      this.bgCtx.clearRect(0, 0, canvas.width, canvas.height);

      // 网格
      this.bgCtx.strokeStyle = 'rgba(0,255,255,0.1)';
      this.bgCtx.lineWidth = 1;
      this.gridLines.forEach(line => {
        const offset = Math.sin(Date.now()/1000 + line.offset)*2;
        this.bgCtx.beginPath();
        this.bgCtx.moveTo(line.x1 + offset, line.y1);
        this.bgCtx.lineTo(line.x2 + offset, line.y2);
        this.bgCtx.stroke();
      });

      // 粒子
      this.particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x<0) p.x=canvas.width; if(p.x>canvas.width) p.x=0;
        if (p.y<0) p.y=canvas.height; if(p.y>canvas.height) p.y=0;
        this.bgCtx.fillStyle = `rgba(0,255,255,${p.alpha})`;
        this.bgCtx.beginPath(); this.bgCtx.arc(p.x,p.y,p.r,0,Math.PI*2); this.bgCtx.fill();
      });

      // 底座光环
      const cx = canvas.width/2, cy = canvas.height*0.98;
      const rx = canvas.width*0.4, ry = canvas.height*0.03;
      for(let i=0;i<4;i++){
        const grad=this.bgCtx.createRadialGradient(cx,cy,ry*(0.5+i*0.3),cx,cy,rx*(1+i*0.1));
        grad.addColorStop(0, `rgba(0,200,255,${0.15-i*0.03})`);
        grad.addColorStop(0.7, `rgba(0,255,255,${0.08-i*0.02})`);
        grad.addColorStop(1, 'rgba(0,0,0,0)');
        this.bgCtx.fillStyle=grad;
        this.bgCtx.beginPath();
        this.bgCtx.ellipse(cx,cy,rx*(1+i*0.1),ry*(1+i*0.5),0,0,Math.PI,false);
        this.bgCtx.fill();
      }
    }
  }
};
</script>

<style scoped>
/* 背景 canvas 在最底层，echarts 在上层 */
</style>

