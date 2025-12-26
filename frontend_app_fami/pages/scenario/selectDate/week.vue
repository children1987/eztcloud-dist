<template>
<view>
  <u-page-title>
    <view>
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content style="padding-top: 30rpx">
    <view v-for="item in weekList" :key="item.value" class="weekItem">
      <view>{{ item.label}}</view>
      <view class="item-right">
        <u-is-select :select="isSelect(item)" @click.native="clickOnRadio(item)" />
      </view>
    </view>
    <view class="weekItem" @click="clickOpenPopup">
      {{ times?times:'选择时间段'}}
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
    <uni-popup-message type="error" message="至少选择一个日期和时间段" :duration="700" />
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
      type: '',
      selectedList: [],
      times: '',
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
      ],
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
        this.selectedList = this.effect_time.exec_days.map(item=>{
          return {
            label: this.weekList.find(week => week.value == item).label,
            value: item
          }
        })
      }
    },
    // 判断是否已选中
    isSelect(data) {
      let select = this.selectedList.find(item => item.value == data.value)
      return !!select
    },
    // 单选
    clickOnRadio(data) {
      let select = this.selectedList.find(item => item.value == data.value)
      if (select) {
        this.selectedList.forEach((item, i) => {
          if (select.value == item.value) {
            this.selectedList.splice(i, 1);
          }
        })
      } else {
        this.selectedList.push(data);
      }
      console.log(this.selectedList)
    },
    clickOpenPopup() {
      this.$refs.popup.open('bottom')
    },
    confrim(date) {
      console.log(date)
      this.times = date.time.replace(new RegExp('undefined', 'g'), '00')
      this.$refs.popup.close()
    },
    cancel() {
      this.$refs.popup.close()
    },
    nextStep() {
      if (this.selectedList && this.selectedList.length > 0 && this.times) {
        const scenarioModel = uni.getStorageSync('scenarioModel');
        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        let effect_time = scenarioData.cfg_info.effect_time
        effect_time.timing_type = this.type
        effect_time.exec_date = null
        let times = this.times.split('-')
        effect_time.start_time = times[0] + ':00'
        effect_time.end_time = times[1] + ':00'
        effect_time.exec_days = this.selectedList.map(item => item.value)
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

.weekItem {
  display: flex;
  justify-content: space-between;
  padding: 10rpx 30rpx;
}
</style>
