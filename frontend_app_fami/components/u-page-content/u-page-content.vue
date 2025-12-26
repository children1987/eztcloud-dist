<template>
  <!-- 页面除navtitle以外的全屏区域 -->
<view class="slotContent">
  <slot></slot>
</view>
</template>

<script>
</script>

<style lang="scss" scoped>
.slotContent {
  margin-top: 150rpx;
  padding: 0 16rpx;
  position: absolute;
  top: 0;
  width: 100%;
  box-sizing: border-box;
  bottom: 0;
  z-index: 0;
}
</style>
