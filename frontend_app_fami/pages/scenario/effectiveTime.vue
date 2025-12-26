<template>
<view>
  <u-page-title>
    <view>
      <u-goback />
    </view>
    <uni-icons style="margin-left: auto;" @click="toScenario" color="#333 !important" type="close" size="30" ></uni-icons>
  </u-page-title>

  <u-page-content>
    <view :class="['box-con', active == 1?'active':'']" @click="switchTime(1)">
      <view class="top">
        <view class="left">全天</view>
        <view class="icon"></view>
      </view>
    </view>

    <view :class="['box-con', active == 2?'active':'']" @click="switchTime(2)">
      <view class="top">
        <view class="left">指定时间段</view>
        <view class="icon"></view>
      </view>
      <view class="bottom" v-show="active == 2">
        <view class="time">
          <view style="color: #333">
            开始时间
          </view>
          <view @click="openPopupTime('start_time')">
            {{ start_time }}
            <uni-icons style="margin-left: 30rpx;" type="forward" size="16"></uni-icons>
          </view>
        </view>

        <view class="time">
          <view style="color: #333">
            结束时间
          </view>
          <view @click="openPopupTime('end_time')">
            {{ end_time }}
            <uni-icons style="margin-left: 30rpx;" type="forward" size="16"></uni-icons>
          </view>
        </view>
      </view>
    </view>

    <view :class="['box-con']" @click="openPopupCycle">
      <view class="top">
        <view class="left">重复</view>
        <view class="right">
          {{ timing_type_map[timing_type] }}
          <uni-icons style="margin-left: 30rpx;" type="forward" size="16"></uni-icons>
        </view>
      </view>
    </view>

    <view class="effect-time-button" @click="toEditMode">
      确定
    </view>
  </u-page-content>
  <!-- 时间选择 -->
  <uni-popup ref="popupTime" type="bottom">
    <view class="timeBox">
      <view class="confirmButtonBox">
        <view class="buttonItem" @click="$refs.popupTime.close()">取消</view>
        <view class="buttonItem" style="color:#50c3ff" @click="specifiedPeriodTime">确定</view>
      </view>
      <u-time :times="defaultTime" @change="changeTime" />
    </view>
  </uni-popup>
  <!-- 重复周期选择 -->
  <uni-popup ref="popupCycle" type="bottom">
    <view class="cycleBox">
      <view :class="['cycleItem', timing_type == 'once'?'cycleItemActive':'']">
        单次
        <uni-datetime-picker class="picker" style="margin-top: 50rpx" type="date" :value="exec_date" @change="changePicker" />
      </view>
      <view @click="repetitionPeriod('everyday')" class="cycleItem" :class="['cycleItem', timing_type == 'everyday'?'cycleItemActive':'']">
        每日
      </view>
      <view @click="openCyclePage('popupWeek')" class="cycleItem" :class="['cycleItem', timing_type == 'week'?'cycleItemActive':'']">
        每周
      </view>
      <view @click="openCyclePage('popupMonthly')" class="cycleItem" :class="['cycleItem', timing_type == 'monthly'?'cycleItemActive':'']">
        每月
      </view>
      <view @click="repetitionPeriod('holiday')" class="cycleItem" :class="['cycleItem', timing_type == 'holiday'?'cycleItemActive':'']">
        法定节假日 （中国大陆）
      </view>
      <view @click="repetitionPeriod('workday')" class="cycleItem" :class="['cycleItem', timing_type == 'workday'?'cycleItemActive':'']">
        法定工作日 （中国大陆）
      </view>
    </view>
  </uni-popup>

  <!-- 每周选择 -->
  <uni-popup ref="popupWeek" type="bottom" class="position">
    <view class="cycleBox">
      <view class="confirmButtonBox">
        <view class="buttonItem" @click="$refs.popupWeek.close()">取消</view>
        <view class="buttonItem" style="color:#50c3ff" @click="userToIdentify('popupWeek','week')">确定</view>
      </view>
      <view v-for="item in weekList" :key="item.value" class="weekItem" style="padding: 25rpx 30rpx;">
        <view>{{ item.label}}</view>
        <view class="item-right">
          <u-is-select :select="isSelect(item)" @click.native="clickOnRadio(item)" />
        </view>
      </view>
    </view>
  </uni-popup>
  <!-- 每月选择 -->
  <uni-popup ref="popupMonthly" type="bottom" class="position">
    <view class="cycleBox">
      <view class="confirmButtonBox">
        <view class="buttonItem" @click="$refs.popupMonthly.close()">取消</view>
        <view class="buttonItem" style="color:#50c3ff" @click="userToIdentify('popupMonthly','monthly')">确定</view>
      </view>
      <view v-for="item in monthList" :key="item.value" class="weekItem">
        <view>{{ item.label}}</view>
        <view class="item-right">
          <u-is-select :select="isSelect(item)" @click.native="clickOnRadio(item)" />
        </view>
      </view>
    </view>
  </uni-popup>
</view>
</template>

<script>
export default {
  onLoad(query) {
    this.selectedList = []
    this.monthList = []
    for (let index = 1; index < 29; index++) {
      this.monthList.push({
        label: index + '日',
        value: index
      })
    }
    this.scenarioData = uni.getStorageSync('scenarioModel')
    this.timing_type = this.scenarioData.cfg_info.effect_time.timing_type
    this.effect_time = this.scenarioData.cfg_info.effect_time
    this.timeDisplay()

  },
  onshow() {
    this.scenarioData = uni.getStorageSync('scenarioModel')
    this.timing_type = this.scenarioData.cfg_info.effect_time.timing_type
  },
  data() {
    return {
      active: 1,
      timeType: '',
      time: '23:59',
      scenarioData: null,
      effect_time: null,
      exec_date: null,
      start_time: '00:00',
      end_time: '23:59',
      defaultTime: ['00', '00'],
      timing_type: '',
      timing_type_map: {
        once: '单次',
        everyday: '每日',
        week: '每周',
        monthly: '每月',
        holiday: '法定节假日',
        workday: '法定工作日'
      },
      times: '',
      exec_date: '',
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
      monthList: [],
      selectedList: []
    }
  },
  methods: {
    // 时段显示
    timeDisplay(){
      if(this.effect_time.start_time && this.effect_time.end_time ){
        if(this.effect_time.start_time == '00:00:00' && this.effect_time.end_time == '23:59:00'){
          this.active = 1
        }else{
          this.active = 2
          this.start_time = this.effect_time.start_time
          this.end_time = this.effect_time.end_time
        }
      }
    },
    toScenario(){
      uni.switchTab({url:'/pages/scenario/scenario'})
    },
    // 返回编辑模式
    toEditMode() {
      uni.navigateTo({
        url: `/pages/scenario/details/details?type=editMode`
      })
    },

    // 更新整体数据
    updateDataInWhole() {
      this.effect_time.timing_type = this.timing_type
      this.effect_time.start_time = this.start_time + ':00'
      this.effect_time.end_time = this.end_time + ':00'
      this.effect_time.exec_date = this.exec_date
      this.effect_time.exec_days = this.selectedList.map(item => {
        return item.value
      })

      this.scenarioData.cfg_info.effect_time = this.effect_time
      uni.setStorageSync('scenarioModel', this.scenarioData);
    },

    // 周期日期回显
    dateShow(type) {
      let map = {
        popupMonthly: 'monthly',
        popupWeek: 'week',
      }
      if (map[type] == this.effect_time.timing_type) {
        this.selectedList = this.effect_time.exec_days.map(item => {
          return {
            label: item + type == 'popupMonthly' ? '日' : '周',
            value: item
          }
        })
      } else {
        this.selectedList = []
      }

    },

    // 周期选择，用户确定
    userToIdentify(ref, type) {
      if (!this.selectedList.length) {
        uni.showToast({
          title: '您没有选择任何可执行日期',
          icon: 'none',
        });
        return
      }
      this.timing_type = type
      this.$refs.popupCycle.close()
      this.$refs[ref].close()
      this.updateDataInWhole()
    },

    // 周期选择列表单选
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
    },

    // 判断是否已选中
    isSelect(data) {
      let select = this.selectedList.find(item => item.value == data.value)
      return !!select
    },

    // 打开月周选择界面
    openCyclePage(ref) {
      this.selectedList = []
      this.dateShow(ref)
      this.$refs[ref].open('bottom')
    },

    // 单次日期变动
    changePicker(date) {
      this.exec_date = date
      this.timing_type = 'once'
      this.$refs.popupCycle.close()
      this.updateDataInWhole()
    },

    // 每日 法定节假日 法定工作日点击处理  重复周期
    repetitionPeriod(type) {
      this.timing_type = type
      this.$refs.popupCycle.close()
      this.updateDataInWhole()
    },

    // 切换时段
    switchTime(active) {
      this.active = active
      if (this.active == 1) {
        this.start_time = '00:00'
        this.end_time = '23:59'
      }
      this.updateDataInWhole()
    },

    // 打开时间选择
    openPopupTime(timeType) {
      this.timeType = timeType
      this.defaultTime = this[this.timeType].split(':') || ['00', '00']
      this.$refs.popupTime.open('bottom')
    },

    // 打开周期选择
    openPopupCycle() {
      this.$refs.popupCycle.open('bottom')
    },

    // 指定时段确认
    specifiedPeriodTime() {
      // 用户点开后没做任何修改，点击确定直接关闭
      if (!this.time) {
        this.$refs.popupTime.close()
        return
      }

      this[this.timeType] = this.time
      // if (this.start_time > this.end_time) {
      //   uni.showToast({
      //     title: '指定时段的开始时间不能大于结束时间',
      //     icon: 'none',
      //   });
      //   this.end_time = '23:59'
      //   return
      // }
      this.$refs.popupTime.close()
      this.updateDataInWhole()
    },

    // 时间 valuechange
    changeTime(time) {
      let arr = this.time.split(':')
      if (time[0] && time[1]) {
        this.time = `${time[0]}:${time[1]}`
      } else {
        this.time = `${time[0]}:${arr[1]}`
      }
    },
  }
};
</script>

<style lang="scss" scoped>
.box-con {
  background-color: #fff;
  min-height: 100rpx;
  border-radius: 30rpx;
  margin-top: 20rpx;
  overflow: hidden;
  padding: 20rpx 40rpx;

  .top {
    height: 100rpx;
    display: flex;
    line-height: 100rpx;
    align-items: center;
    justify-content: space-between;
    font-size: 30rpx;
    color: #333;
    font-weight: 600;

    .icon {
      width: 46rpx;
      height: 46rpx;
      background-color: #eee8e8;
      border-radius: 50%;
      box-sizing: border-box;
    }

    .right {
      color: #999;
      font-weight: 500;
      font-size: 28rpx;
    }
  }
}

.active {
  .left {
    color: $mainColor !important;
  }

  .icon {
    border: 12rpx solid $mainColor;
    background-color: #fff !important;
  }

  .bottom {
    height: 140rpx;
    font-size: 28rpx;

    .time {
      display: flex;
      height: 70rpx;
      line-height: 70rpx;
      align-items: center;
      justify-content: space-between;
    }
  }
}

.timeBox {
  background-color: $backgroundColor;
  transform: translateY(30rpx);
}

.confirmButtonBox {
  display: flex;
  padding: 16rpx 10rpx 0 10rpx;
  display: flex;
  justify-content: space-between;

  .buttonItem {
    padding: 10rpx;
  }
}

.cycleBox {
  background-color: $backgroundColor;
  padding: 16rpx;

  .cycleItem {
    padding-left: 50rpx;
    line-height: 80rpx;
    font-size: 28rpx;
    color: #333;
    position: relative;
    overflow: hidden;

    .picker {
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      margin: 0 !important;

      ::v-deep .uni-date-editor {
        opacity: 0;
      }
    }
  }

  .cycleItemActive {
    font-weight: 600;
    color: $mainColor !important;
  }
}

// 多层级问题容错
.position {
  position: relative;
  z-index: 999;
}

.weekItem {
  display: flex;
  justify-content: space-between;
  padding: 10rpx 30rpx;
  height: 30rpx;
}

.effect-time-button {
  @include button;
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 20rpx;
}
</style>
