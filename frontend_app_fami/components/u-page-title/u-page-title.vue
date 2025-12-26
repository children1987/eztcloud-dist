<template>
  <!-- 页面navTitle -->
<view class="title">
  <view class="content">
    <slot></slot>
  </view>
</view>
</template>

<script>
</script>

<style lang="scss" scoped>
.title {
  padding-top: 80rpx;
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 99;
  .content {
    min-height: 70rpx;
    display: flex;
    align-items: center;
    background-color: #fff;
    // box-shadow: 0px 1rpx 1rpx #bdbbbb;
    padding: 0 16rpx;
    flex-wrap:wrap;
  }
  
}
</style>
