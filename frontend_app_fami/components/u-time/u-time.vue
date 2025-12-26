<template>
<view class="contentBox">
  <view class="boxs">
    <span class='line'></span>
    <view>
      <picker-view :indicator-style="indicatorStyle" :value="hour" @change="bindChangeHour" class="picker-view">
        <picker-view-column>
          <view class="item" v-for="(item,index) in hoursList" :key="index">{{item}}</view>
        </picker-view-column>
      </picker-view>
    </view>
    <span class='line'></span>
    <span class='minies'>时</span>
  </view>
  <view class="boxs">
    <span class='line'></span>
    <view>
      <picker-view :indicator-style="indicatorStyle" :value="min" @change="bindChangeMin" class="picker-view">
        <picker-view-column>
          <view class="item" v-for="(item,index) in minutes" :key="index">{{item}}</view>
        </picker-view-column>
      </picker-view>
    </view>
    <span class='line'></span>
    <span class='minies'>分</span>
  </view>
</view>
</template>

<script>
let minutes = []
for (let i = 0; i <= 59; i++) {
  if (i < 10) {
    i = "0" + i
  }
  minutes.push(i)
}
export default {

  data() {
    return {
      hour: [Number(this.times[0])],
      min: [Number(this.times[1])],
      indicatorStyle: `height: 144rpx;`,
      hoursList: ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15',
        '16', '17', '18', '19', '20', '21', '22', '23'
      ],
      minutes,
    }
  },
  props: {
    times: {
      type: Array,
      default: () => {
        return ['00', '00']
      }
    }
  },
  methods: {
    bindChangeMin(e) {
      this.min = e.detail.value
      let minutes = this.minutes[e.detail.value]
      let hours = this.hoursList[this.hour]
      let arr = [hours, minutes]
      this.$emit('change', arr)

    },
    bindChangeHour(e) {
      this.hour = e.detail.value
      let minutes = this.hoursList[this.min]
      let hours = this.hoursList[e.detail.value]
      let arr = [hours, minutes]
      this.$emit('change', arr)
    },

  }
}
</script>

<style lang="scss" scoped>
.picker-view {
  width: 180rpx;
  height: 482rpx;

}

.uni-picker-view-indicator:before {
  border: none !important;
}

.uni-picker-view-indicator:after {
  border: none !important;
}

.item {
  height: 144rpx;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 96rpx;
  font-weight: 600;
  color: #333333;
  line-height: 144rpx;
}

.contentBox {
  margin: 30rpx;
  height: 500rpx;
  background-color: #FFFFFF;
  display: flex;
  border-radius: 12rpx;
  justify-content: space-around;

  .boxs {
    display: flex;
    align-items: center;

    .line {
      width: 2rpx;
      height: 144rpx;
      background: linear-gradient(180deg, #EEEEEE 0%, #CACBCF 52%, #FFFFFF 100%);
    }

    .minies {
      font-size: 24rpx;

      font-weight: 600;
      color: #333333;
      padding-left: 20rpx;

    }
  }
}
</style>
