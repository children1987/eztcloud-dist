<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
    <uni-icons style="margin-left: auto;" @click="toScenario" color="#333 !important" type="close" size="30" ></uni-icons>
  </u-page-title>

  <u-page-content>
    <view class="topBox">
      <view class="topTitle">
        如果满足以下条件时
      </view>
      <view class="conditionsItem" @click="openPopupTime">
        <text class="iconfont icon-shijian" style="color:#50c3ff"></text>
        <view>定时 <uni-icons style="margin-left: 30rpx;" type="right" size="18"></uni-icons>
        </view>
      </view>
      <view class="conditionsItem" @click="navigateTo('/pages/scenario/fixedConditionChoose?type=温度')">
        <text class="iconfont icon-wendu" style="color:#5984fd"></text>
        <view>温度 <uni-icons style="margin-left: 30rpx;" type="right" size="18"></uni-icons>
        </view>
      </view>
      <view class="conditionsItem" @click="navigateTo('/pages/scenario/fixedConditionChoose?type=湿度')">
        <text class="iconfont icon-shidu" style="color:#fda261"></text>
        <view>湿度 <uni-icons style="margin-left: 30rpx;" type="right" size="18"></uni-icons>
        </view>
      </view>
      <view class="conditionsItem" @click="navigateTo('/pages/scenario/fixedConditionChoose?type=PM2.5')">
        <text class="iconfont icon-tianqi-wumai" style="color:#5bcaa9"></text>
        <view>PM2.5 <uni-icons style="margin-left: 30rpx;" type="right" size="18"></uni-icons>
        </view>
      </view>
    </view>
    <view class="vTab">
      <v-tabs field="name" v-model="currenTab" :tabs="tabs" @change="changeTab" activeColor="#000" lineHeight="6rpx" lineColor="#48A9FC"></v-tabs>
      <uni-icons type="bars" size="28" @click="openPopup"></uni-icons>
    </view>

    <view class="list topBox">
      <view class="row-box" v-for="item in deviceList" :key="item.id" @click="deviceNavigateTo(item)">
        <view class="row-left">
          <image :src="item.logo||item.product.logo || '/static/dbs.png'" class="image" mode="aspectFit" />
          <view class="textBox">
            <view class="name">
              {{ item.name }}
            </view>
            <view class="parameter">
              {{item.product.series}} | {{ item.product.name }}
            </view>
          </view>
        </view>
        <view class="row-left">
          <u-signal :signal="item.state"></u-signal>
          <!-- <text style="margin: 0 20rpx;">开启</text> -->
          <uni-icons style="margin-left: 50rpx;" type="right" size="18"></uni-icons>
        </view>

      </view>
      <view v-if="!deviceList.length" style="text-align: center">
        该单元下暂无可选设备
      </view>
    </view>

  </u-page-content>
  <!-- 弹出 更多菜单 -->
  <uni-popup ref="popup" type="right">
    <view class="popupList">
      <view class="popupItem" @click="changeTab(index)" v-for="(item,index) in tabs" :key="index">
        {{item.name}}
      </view>
    </view>
  </uni-popup>
  <!-- 弹出 条件  时间 -->
  <uni-popup ref="popupTime" type="bottom">
    <view class="timeBox">
      <view class="confirmButtonBox">
        <view class="buttonItem" @click="$refs.popupTime.close()">取消</view>
        <view class="buttonItem" style="color:#50c3ff" @click="toSelectEquipment">确定</view>
      </view>
      <u-time @change="changeTime" />
    </view>
  </uni-popup>
</view>
</template>

<script>
export default {
  onLoad(query) {
    this.type = query.type
    this.getUnit()
    this.getDevice()
  },
  onShow() {

  },
  data() {
    return {
      type: '',
      conditionsTime: '00:00:00',
      currenTab: 0,
      tabs: [{
        id: '',
        name: '所有设备',
      }],
      deviceList: []
    };
  },
  methods: {
    toScenario(){
      uni.switchTab({url:'/pages/scenario/scenario'})
    },
    // 设备作为条件跳转
    deviceNavigateTo(item) {
      // 筛选出可作为条件的属性
      // 存储到
      console.log(item)
      let obj = {
        id: item.id,
        title: item.name,
        logo: item.logo || item.product.logo,
        properties: item.product.cfg_info.properties.filter(attribute => attribute.condition_info)
      }
      uni.setStorageSync('properties', obj)
      uni.navigateTo({
        url: '/pages/scenario/conditionChoose' + (this.type == 'isEditMode' ? '?isEditMode=isEditMode' : '')
      })
    },
    // 获取单元列表
    getUnit() {
      this.$http({
        url: '/api/org_units/get_all/',
        data: {},
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          this.tabs = [{
              id: '',
              name: '所有设备',
            }

          ]
          this.tabs = this.tabs.concat(res.data)
        }
      })
    },
    // 获取设备
    getDevice() {
      let data = {
        scene_condition: true,
        org: uni.getStorageSync('org').id
      };
      let unit = this.tabs[this.currenTab] || '';
      if (unit.id) {
        data.unit = unit.id;
      }
      this.$http({
        url: '/api/devices/get_all/',
        data,
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          this.deviceList = res.data;
        }
      })
    },
    // 跳转
    navigateTo(url) {
      uni.navigateTo({
        url: url + (this.type == 'isEditMode' ? '&isEditMode=isEditMode' : '')
      })
    },
    // changeTab
    changeTab(index) {
      this.currenTab = index
      this.getDevice()
      this.$refs.popup.close()
    },
    // TAB 更多弹出层 打开
    openPopup() {
      this.$refs.popup.open('right')
    },
    // 弹出 条件  时间选择
    openPopupTime() {
      this.conditionsTime = '00:00:00'
      this.$refs.popupTime.open('bottom')
    },
    // 条件 时间 valuechange
    changeTime(time) {
      this.conditionsTime = `${time[0]}:${time[1]}:00`
    },
    // 跳转 to 选择设备 携带条件
    toSelectEquipment() {
      this.$refs.popupTime.close()
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      // 改变全局场景对应参数
      let item = scenarioData.cfg_info.conditions.find(item => item.c_type == 'timing')
      if (item) {
        item.exec_time = this.conditionsTime
      } else {
        scenarioData.cfg_info.conditions.push({
          c_type: "timing",
          exec_time: this.conditionsTime
        })
      }
      uni.setStorageSync('scenarioModel', scenarioData);
      // 然后跳转到对应页面
      if (this.type == 'isEditMode') {
        uni.navigateTo({
          url: `/pages/scenario/details/details?type=editMode`
        })
      } else {
        uni.navigateTo({
          // url: `/pages/scenario/selectEquipment`
          url: `/pages/scenario/details/details?type=editMode`
        })
      }

    },
  }
};
</script>

<style lang="scss" scoped>
.timeBox {
  background-color: $backgroundColor;
  transform: translateY(30rpx);

  .confirmButtonBox {
    display: flex;
    padding: 16rpx 10rpx 0 10rpx;
    display: flex;
    justify-content: space-between;

    .buttonItem {
      padding: 10rpx;
    }
  }
}

.topBox {
  background-color: $backgroundColor;
  border-radius: 30rpx;
  padding: 30rpx;
  box-shadow: 0px 2px 2px 1px $shadow;
  margin-top: 30rpx;
}

.topTitle {
  font-size: 36rpx;
  color: $headlines;
  line-height: 2;
  border-bottom: 1px solid $dividingLine;
  text-align: center;
}

.conditionsItem {
  padding: 26rpx 0;
  display: flex;
  justify-content: space-between;
  align-items: center;

  text {
    font-size: 32rpx;
  }

  .iconfont {
    font-size: 40rpx;
  }
}

.vTab {
  margin-top: 36rpx;
  display: flex;
  align-items: center;

  ::v-deep .v-tabs__container {
    background-color: rgba(255, 255, 255, 0) !important;
  }
}

.popupList {
  background-color: $backgroundColor;
  width: 300rpx;
  height: 600rpx;
  padding-left: 50rpx;
  box-sizing: border-box;
  overflow-y: auto;
  position: relative;
  top: 200rpx;

  .popupItem {
    height: 80rpx;
    line-height: 80rpx;
  }
}

.row-box {
  @include flex-box;
  padding: 30rpx 16rpx;

  .image {
    width: 80rpx;
    height: 80rpx;
  }

  .row-left {
    display: flex;
    align-items: center;

    .iconfont {
      font-size: 30rpx;
    }
  }

  .continue_to_add {
    color: $mainColor;
  }
}

.textBox {
  width: 340rpx;
  margin: 0 30rpx;

  .name {
    @include overflow-text;
    font-size: 32rpx;
    color: $mainTitle;
    line-height: 1.5;
  }

  .parameter {
    font-size: 26rpx;
    color: $captions;
    @include overflow-text;
  }

}

</style>
