<template>
<swiper class="image-container" previous-margin="45rpx" next-margin="45rpx" circular autoplay @change="swiperChange">
  <swiper-item :class="currentIndex == index ? 'swiper-item' : 'swiper-item-side'" v-for="(item, index) in slotList" :key="item.name">
    <view :class="currentIndex == index ? 'item-img' : 'item-img-side'" :style="dontFirstAnimation ? 'animation: none;' : ''">
      <slot :name="item.name"></slot>
    </view>
  </swiper-item>
</swiper>
</template>

<script>
export default {
  props: {
    // 只用来接收 slot name
    slotList: {
      type: Array,
      default () {
        return []
      }
    },

  },
  data() {
    return {
      currentIndex: 0,
      dontFirstAnimation: true
    }
  },
  methods: {
    swiperChange(e) {
      this.dontFirstAnimation = false
      this.currentIndex = e.detail.current
    }
  }
}
</script>

<style scoped>
.image-container {
  width: 750rpx;
  height: 350rpx;
}

.item-img {
  width: 630rpx;
  height: 300rpx;
  border-radius: 14rpx;
  animation: to-big .3s;
}

.swiper-item {
  width: 630rpx;
  height: 300rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.item-img-side {
  width: 630rpx;
  height: 260rpx;
  border-radius: 14rpx;
  animation: to-mini .3s;
}

.swiper-item-side {
  width: 630rpx;
  height: 260rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

@keyframes to-mini {
  from {
    height: 300rpx;
  }

  to {
    height: 260rpx;
  }
}

@keyframes to-big {
  from {
    height: 260rpx;
  }

  to {
    height: 300rpx;
  }
}
</style>
