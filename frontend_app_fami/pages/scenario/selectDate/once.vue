<template>
<view>
  <u-page-title>
    <view>
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <uni-datetime-picker style="margin-top: 50rpx" type="date" :value="date" @change="changePicker" />
    <view class="toChooseTime" @click="clickOpenPopup">
      <view style="display: flex;align-items: center;">
        <text class="iconfont icon-shijian" style="font-size: 34rpx; margin-right: 20rpx"></text>
        {{ times?times:'选择时间段'}}
      </view>
      <uni-icons type="right" size="20"></uni-icons>
    </view>
    <view class="next-button" @click="nextStep">
      完成
    </view>
  </u-page-content>
  <uni-popup ref="popup" type="bottom" background-color="#fff">
    <smh-time-range class="range" @confrim="confrim" @cancel="cancel" :time="time" />
  </uni-popup>
  <uni-popup ref="popupMessage" type="message">
    <uni-popup-message type="error" message="日期 和 时间段都是必选项" :duration="700" />
  </uni-popup>
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
      date: '',
      times: '',
      type: 'once',
      effect_time:{},
      time: ['00','00','0','23','59']
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
        this.times = `${start_time[0]}:${start_time[1]}-${end_time[0]}:${end_time[1]}`
        this.date = this.effect_time.exec_date
      }
    },
    changePicker(date) {
      this.date = date
    },
    clickOpenPopup() {
      this.$refs.popup.open('bottom')
    },
    confrim(date) {
      this.times = date.time.replace(new RegExp('undefined', 'g'), '00')
      this.$refs.popup.close()
    },
    cancel() {
      this.$refs.popup.close()
    },
    nextStep(date) {
      if (this.date && this.times) {
        // '2023-01-10 00:01-23:59'
        const scenarioModel = uni.getStorageSync('scenarioModel');
        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        let effect_time = scenarioData.cfg_info.effect_time
        effect_time.timing_type = this.type
        effect_time.exec_date = this.date
        let times = this.times.split('-')
        effect_time.start_time = times[0] + ':00'
        effect_time.end_time = times[1] + ':00'
        effect_time.exec_days = []
        scenarioData.cfg_info.effect_time = effect_time
        uni.setStorageSync('scenarioModel', scenarioData);
        uni.navigateTo({
          url: `/pages/scenario/details/details?type=editMode`
        })
      } else {
        this.$refs['popupMessage'].open();
      }
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

.toChooseTime {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20rpx;
  margin: 20rpx 0;
  background-color: #fff;
  font-size: 14px;
  height: 35px;
  box-sizing: border-box;
  border-radius: 4px;
  border: 1px solid #e5e5e5;

}
</style>
