<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <view class="box">
      <view class="row-item flex-box">
        <text>类型</text>
        {{effect_time.timing_type?timing_type_map[effect_time.timing_type]:""}}
      </view>
      <view v-show="effect_time.exec_date" class="row-item flex-box">
        <text>生效日期</text>
        {{effect_time.exec_date}}
      </view>
      <view v-show="effect_time.start_time" class="row-item flex-box">
        <text>生效时段</text>
        {{effect_time.start_time}} - {{effect_time.end_time}}
      </view>
      <view v-if="effect_time.exec_days.length" class="row-item">
        <text>生效周期</text>
        <view v-for="item in effect_time.exec_days" :key="item" class="item">
          {{item | weekOrMonthly(that)}}
        </view>
      </view>
    </view>
  </u-page-content>

</view>
</template>

<script>
export default {
  onLoad() {
    this.effect_time = uni.getStorageSync('scenarioModel').cfg_info.effect_time
  },
  data() {
    return {
      that: this,
      effect_time: {
        timing_type: '',
      },
      timing_type_map: {
        once: '单次',
        everyday: '每日',
        week: '每周',
        monthly: '每月',
        holiday: '法定节假日',
        workday: '法定工作日'
      },
      weekList: [{
          label: '星期一',
          value: 0
        },
        {
          label: '星期二',
          value: 1
        },
        {
          label: '星期三',
          value: 2
        },
        {
          label: '星期四',
          value: 3
        },
        {
          label: '星期五',
          value: 4
        },
        {
          label: '星期六',
          value: 5
        },
        {
          label: '星期日',
          value: 6
        },
      ]
    }
  },
  methods: {

  },
  filters: {
    weekOrMonthly(item, that) {
      if (that.effect_time.timing_type == 'week') {
        return that.weekList.find(week => item == week.value).label
      }
      if (that.effect_time.timing_type == 'monthly') {
        return item + '日'
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.box {
  background-color: #fff;
  margin: 30rpx;
  padding: 30rpx;
  border-radius: 20rpx;
}

.row-item {
  margin-bottom: 20rpx;

  text {
    display: inline-block;
    width: 120rpx;
    margin-right: 180rpx;
    // color: #000;
  }
  .item{
    margin-top: 20rpx;
    text-align: right;
  }
}
.flex-box{
  display: flex;
  justify-content: space-between;
}
</style>
