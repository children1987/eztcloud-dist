<template>
  <!-- 信号强度 -->
<view class="u-signal">
  <view :class="`signal ${item<num?'bg':''}`" :style="`height:${item*10*2}%`" v-for="item in 5" :key="item"></view>
</view>
</template>

<script>
export default {
  props:{
    signal:{
      type: Number,
      default: 0
    }
  },
  computed:{
    num(){
      return (this.signal*100/20) + 1
    }
  }
}
</script>

<style lang="scss" scoped>
.u-signal {
  display: inline-flex;
  height: 30rpx;
  align-items: flex-end;

  .signal {
    width: 4rpx;
    background-color: $contentWords;
    margin-right: 6rpx;
  }
  .bg{
    background-color: $actionIconToActivate !important;
  }

}
</style>
