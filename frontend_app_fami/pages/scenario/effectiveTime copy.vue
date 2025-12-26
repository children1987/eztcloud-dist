<template>
<view>
  <u-page-title>
    <view>
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <view style="margin-top: 60rpx;">
      <uni-list style="width: 100%;">
        <uni-list-item  showArrow title="单次" @click.native="onClick('once')">
          <view slot="body">
            <text :class="timing_type == 'once' ? 'active' : 'text' " >单次</text>
				  </view>
        </uni-list-item>
        <uni-list-item  showArrow title="每日" @click.native="onClick('everyday')">
          <view slot="body">
            <text :class="timing_type == 'everyday' ? 'active' : 'text' " >每日</text>
				  </view>
        </uni-list-item>
        <uni-list-item showArrow title="每周" @click.native="onClick('week')">
          <view slot="body">
            <text :class="timing_type == 'week' ? 'active' : 'text' " >每周</text>
				  </view>
        </uni-list-item>
        <uni-list-item showArrow title="每月" @click.native="onClick('monthly')">
          <view slot="body">
            <text :class="timing_type == 'monthly' ? 'active' : 'text' " >每月</text>
				  </view>
        </uni-list-item>
        <uni-list-item showArrow title="法定节假日" @click.native="onClick('holiday')">
          <view slot="body">
            <text :class="timing_type == 'holiday' ? 'active' : 'text' " >法定节假日</text>
				  </view>
        </uni-list-item>
        <uni-list-item showArrow title="法定工作日" @click.native="onClick('workday')">
          <view slot="body">
            <text :class="timing_type == 'workday' ? 'active' : 'text' " >法定工作日</text>
				  </view>
        </uni-list-item>
      </uni-list>
    </view>

  </u-page-content>

</view>
</template>

<script>
export default {
  onLoad(query) {
    this.scenarioData = uni.getStorageSync('scenarioModel')
    this.timing_type = this.scenarioData.cfg_info.effect_time.timing_type
  },
  onshow(){
    this.scenarioData = uni.getStorageSync('scenarioModel')
    this.timing_type = this.scenarioData.cfg_info.effect_time.timing_type
  },
  data() {
    return {
      timing_type:''
    }
  },
  methods: {
    onClick(type) {
      if (type == 'everyday' || type == 'holiday' || type == 'workday') {
        this.navigateTo(`/pages/scenario/selectDate/everyday?type=${type}`)
      } else {
        this.navigateTo(`/pages/scenario/selectDate/${type}?type=${type}`)
      }
    },
    navigateTo(url) {
      uni.navigateTo({
        url
      })
    },
    nextStep() {
      this.$refs.form.validate().then(res => {
        const scenarioModel = uni.getStorageSync('scenarioModel');

        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        // 改变全局场景对应参数

        uni.setStorageSync('scenarioModel', scenarioData);
        uni.navigateTo({
          url: `/pages/scenario/effectiveTime`
        })
      }).catch(err => {

      })
    },
  },
};
</script>

<style lang="scss" scoped>
.next-button {
  @include button;
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 20rpx;
}
.active{
  font-size: 28rpx;
  font-weight: 600 !important;
  color: #000 !important;
}
.text{
  font-size: 28rpx;
  color: #3b4144 !important;
}
</style>
