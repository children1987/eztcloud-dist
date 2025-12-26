<template>
  <!-- 首页设备展示 -->
<view class="u-equipment-square">
  <view class="signal">
    <u-signal :signal='itemObj.state'/>
  </view>
  <image :src="itemObj.logo||itemObj.product.logo || src.t1" class="image" mode="aspectFit" />
  <view class="bottom">
    <view class="textBox">
      <view class="name">
        {{itemObj.name}}
      </view>
      <view class="parameter">
        {{itemObj.unit&&itemObj.unit.name}}
      </view>
    </view>
    <view class="powerButton">
      <!-- <text :class="['iconfont','icon-dianyuan', true?'active':'']"></text> -->
    </view>
  </view>
</view>
</template>

<script>
export default {
  props: {
    itemObj: {
      type: Object,
      default: () => {
        return {}
      }
    }
  },
  data() {
    return {
      src: {
        t1: '/static/dbs.png'
      }
    }
  },
}
</script>

<style lang="scss" scoped>
.u-equipment-square {
  background-color: $backgroundColor;
  border-radius: 30rpx;
  padding: 30rpx;
  box-shadow: 0px 2px 2px 1px $shadow;
  .signal {
    display: flex;
    flex-direction: row-reverse;
  }

  .image {
    height: 100rpx;
    width: 150rpx;
  }

  .bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .textBox {
      flex: 1;
      overflow: hidden;
    }

    .powerButton {
      width: 50rpx;
      height: 50rpx;
      background-color: $pageBackground;
      border-radius: 50%;
      text-align: center;
      line-height: 50rpx;

      .active {
        color: $actionIconToActivate;
      }
    }

    .name {
      font-size: 32rpx;
      color: $mainTitle;
      line-height: 1.5;
      text-overflow: ellipsis;
      white-space: nowrap;
      overflow: hidden;
    }

    .parameter {
      font-size: 26rpx;
      color: $captions;
      text-overflow: ellipsis;
      white-space: nowrap;
      overflow: hidden;
    }
  }
}
</style>
