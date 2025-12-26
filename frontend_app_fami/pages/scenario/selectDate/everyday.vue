<template>
<view>
  <u-page-title>
    <view>
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <smh-time-range class="range" @confrim="nextStep" @cancel="cancel" :time="time" />
  </u-page-content>
</view>
</template>

<script>
export default {
  onLoad(query) {
    this.type = query.type
    this.scenarioData = uni.getStorageSync('scenarioModel')
    this.effect_time = this.scenarioData.cfg_info.effect_time
    this.echoTime()
  },
  data() {
    return {
      type: '',
      effect_time:{},
      time: ['0','0','0','23','59']
    }
  },
  methods: {
    // echoTime
    echoTime(){
      if(this.type == this.effect_time.timing_type){
        let start_time = this.effect_time.start_time.split(':')
        let end_time = this.effect_time.end_time.split(':')
        this.time = [
          start_time[0],
          start_time[1],
          '0',
          end_time[0],
          end_time[1],
        ]
      }
    },
    cancel() {
      uni.navigateBack()
    },
    nextStep(date) {
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      let effect_time = scenarioData.cfg_info.effect_time

      effect_time.timing_type = this.type
      effect_time.exec_date = ''
      let times = date.time
      times = times.replace(new RegExp('undefined', 'g'), '00')
      times = times.split('-')
      
      effect_time.start_time = times[0] + ':00'
      effect_time.end_time = times[1] + ':00'
      effect_time.exec_days = []
      scenarioData.cfg_info.effect_time = effect_time
      uni.setStorageSync('scenarioModel', scenarioData);
      uni.navigateTo({
          url: `/pages/scenario/details/details?type=editMode`
        })
    },
  },
};
</script>

<style lang="scss" scoped>
.range {
  position: absolute;
  bottom: 0;
}

.next-button {
  @include button;
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 20rpx;
}
</style>
