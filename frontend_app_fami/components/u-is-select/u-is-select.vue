<template>
  <!-- 是否选中 -->
<view class="u-is-select">
  <uni-icons v-if="select" type="checkbox-filled" size="20" class="select"/>
  <view v-else class="notselect"></view>
</view>
</template>

<script>
export default {
  props:{
    select:{
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
.u-is-select {
  display: inline-block;
  .select{
    color: $actionIconToActivate !important;
  }
  .notselect{
    width: 14px;
    height: 14px;
    border: 1rpx $dividingLine solid;
    border-radius: 50%;
    transform: translateX(-4rpx);
  }
}
</style>
