<template>

  <uni-popup ref="popup" type="bottom">
    <view class="and-or">
      <view :class="['item',relation=='or'?'active':'']" @click="onClick('or')">满足任意条件</view>
      <view :class="['item',relation=='and'?'active':'']" @click="onClick('and')">同时满足所有条件</view>
    </view>
  </uni-popup>

</template>

<script>
export default {

  data() {
    return {

    }
  },
  props: {
    relation: {
      type: String,
      default: ''
    }
  },
  methods: {
    open() {
      this.$refs.popup.open('bottom')
    },
    close() {
      this.$refs.popup.close()
    },
    onClick(type) {
      let scenarioData = uni.getStorageSync('scenarioModel')
      scenarioData.cfg_info.relation = type
      uni.setStorageSync('scenarioModel', scenarioData)
      this.close()
      this.$emit('selection')
    }
  }
}
</script>

<style lang="scss" scoped>
.and-or {
  padding: 30rpx;
  background-color: #fff;
  width: 100%;
}
.active{
  color: #000;
  font-weight: 600;
}
.item {
  text-align: center;
  margin: 30rpx 0;
}
</style>
