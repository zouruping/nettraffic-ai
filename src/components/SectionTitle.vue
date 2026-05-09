<template>
  <div class="section-title">
    <!-- 左侧斜线 -->
    <div class="slashes left">
      <span v-for="n in 5" :key="'left'+n" class="slash"></span>
    </div>

    <!-- 中间文字 -->
    <span class="title-text">{{ title }}</span>

    <!-- 右侧斜线 -->
    <div class="slashes right">
      <span v-for="n in 5" :key="'right'+n" class="slash"></span>
    </div>
  </div>
</template>

<script>
export default {
  name: "SectionTitle",
  props: {
    title: {
      type: String,
      required: true
    }
  }
};
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #fff;
}

.slashes {
  display: flex;
  gap: 3px;
}

/* 左侧斜线 */
.slashes.left .slash {
  transform: rotate(45deg);
}

/* 右侧斜线 */
.slashes.right .slash {
  transform: rotate(-45deg);
}

.slash {
  display: inline-block;
  width: 12px;  /* 可以适当加长 */
  height: 3px;
  background: linear-gradient(to right, #284D89, #0072ff);
  border-radius: 1px;
}

.title-text {
  margin: 0 8px;
}
</style>
