<template>
  <!-- list item box -->
<view class="listItemBox">
  <slot></slot>
</view>
</template>

<script>
export default {
  
}
</script>

<style lang="scss" scoped>
.listItemBox{
  background-color: $backgroundColor;
  border-radius: 30rpx;
  padding: 30rpx;
  box-shadow: 0px 2px 2px 1px $shadow;
  margin-top: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
