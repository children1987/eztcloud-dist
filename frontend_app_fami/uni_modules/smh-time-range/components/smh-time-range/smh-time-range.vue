<template>
<view class="time1">
  <view class="top">
    <text @tap="cancel">取消</text>
    <text @tap="confirm">确定</text>
  </view>
  <picker-view class="picker" :value="value" @change="getime" indicator-style="height:30px;">
    <picker-view-column>
      <view class="hours" style="line-height:30px; text-align: center;" v-for="(item,index) in hoursList" :key="index">{{item}}</view>
    </picker-view-column>
    <picker-view-column>
      <view class="minutes" style="line-height:30px; text-align: center;" v-for="(item,index) in minutes" :key="index">{{item}}</view>
    </picker-view-column>
    <picker-view-column>
      <view style="line-height:30px; text-align: center;">-</view>
    </picker-view-column>
    <picker-view-column>
      <view class="hours" style="line-height:30px; text-align: center;" v-for="(item,index) in hoursList" :key="index">{{item}}</view>
    </picker-view-column>
    <picker-view-column>
      <view class="minutes" style="line-height:30px; text-align: center;" v-for="(item,index) in minutes" :key="index">{{item}}</view>
    </picker-view-column>
  </picker-view>
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
  props: {
    time: {
      type: Array,
      default () {
        return ['15', '0', '0', '18', '0'];
      }
    }
  },
  watch: {
    time: function () {
      this.value = this.time
    }
  },
  created() {

  },
  data() {
    return {
      value: this.time, //默认结束开始时间
      hoursList: ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'],
      minutes,
    }
  },
  methods: {
    confirm() {
      let time = this.value[0] + ":" + this.value[1] + "-" + this.value[3] + ":" + this.value[4]
      this.$emit("confrim", {
        time: time
      })
    },
    cancel() {
      let time = this.value[0] + ":" + this.value[1] + "-" + this.value[3] + ":" + this.value[4]
      this.$emit("cancel", {
        time: time
      })
    },
    getime(e) {
      let val = e.detail.value
      this.value[0] = this.hoursList[val[0]]
      this.value[1] = this.minutes[val[1]]
      this.value[2] = val[2]
      this.value[3] = this.hoursList[val[3]]
      this.value[4] = this.minutes[val[4]]

    },
  }
}
</script>

<style lang="scss">
.time1 {
  width: 100%;
  margin: 0 auto;
  background-color: #FFFFFF;
  color: #000;
  height: 450rpx;

  .top {
    width: 690rpx;
    margin: 0 auto;
    height: 100rpx;
    line-height: 100rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;

    text {
      font-weight: bold;

      &:nth-child(1) {
        font-size: 28rpx;
        color: #999;
      }

      &:nth-child(2) {
        font-size: 28rpx;
        color: #0A84FF;
      }
    }
  }

  .tip12 {
    width: 100%;
    height: 100rpx;

    view {
      width: 50%;
      text-align: center;
      line-height: 100rpx;
      font-size: 40rpx;
      color: #000000;
    }
  }

  .hours {
    font-size: 30rpx;
    font-weight: bold;
    color: #000;
  }

  .minutes {
    font-size: 30rpx;
    font-weight: bold;
    color: #000;
  }
}

.picker {
  width: 100%;
  height: 300rpx;
}
</style>
