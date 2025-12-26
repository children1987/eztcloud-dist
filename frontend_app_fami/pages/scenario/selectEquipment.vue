<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
    <uni-icons style="margin-left: auto;" @click="toScenario" color="#333 !important" type="close" size="30" ></uni-icons>
  </u-page-title>

  <u-page-content>
    <view class="page-content">
      <!-- Render Area -->
      <view class="renderArea" :style="'margin-bottom: 120rpx'">
        <u-list-item>
          <view style="flex: 1">
            <view class="row-box-top">
              <view class="row-left">
                <text class="iconfont icon-caidan"></text>如果
              </view>
            </view>
            <view @click="openRelation" class="row-box-top" style="color:#000; font-weight: 600; padding-left: 70rpx;">
              {{relation=='and'?'同时满足所有条件':'满足任意条件'}}
              <uni-icons style="margin-left: 30rpx; font-weight: 400;"  type="right" size="18"></uni-icons>
            </view>
            <view v-for="item in conditions" :key="item.c_type+item.key">
              <view class="row-box-top" v-if="item.c_type != 'device'">
                <view class="row-left">
                  {{ item.c_type == 'timing'?item.exec_time: mapSceneConditions(item.condition) + ' ' +  item.numb}}
                </view>
                <text>
                  {{ item.c_type == 'timing'?'定时': item.c_type== 'device'?'设备':conditionsKeyMap[item.key]}}
                </text>
              </view>
              <view class="row-box-top" v-if="item.c_type == 'device'">
                <view class="row-left" v-if="item.type == 'float'">
                  {{ item.key_name }} {{ item.c_type == 'timing'?item.exec_time: mapSceneConditions(item.condition) + ' ' +  item.numb}}
                </view>
                <view class="row-left" v-if="item.type == 'select'">
                  {{item.key_name}} {{ item.numb_name}}
                </view>
                <text>
                  {{ item.device_name}}
                </text>
              </view>
            </view>
          </view>
        </u-list-item>
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

  <u-and-or ref="andOr" :relation="relation" @selection="refreshPage" />
</view>
</template>

<script>
export default {
  data() {
    return {
      conditionsKeyMap: {
        'temperature': '温度',
        'humidity': '湿度',
        'pm2.5': 'PM2.5',
      },
      scene_conditions: [],
      deviceList: [],
      currenTab: 0,
      tabs: [{
        id: '',
        name: '所有设备',
      }],
      relation: ''
    };
  },
  onLoad() {
    const scenarioModel = uni.getStorageSync('scenarioModel');
    this.relation = JSON.parse(JSON.stringify(scenarioModel)).cfg_info.relation
    this.scene_conditions = uni.getStorageSync('scene_conditions');
    this.conditions = JSON.parse(JSON.stringify(scenarioModel)).cfg_info.conditions || []
    this.getUnit()
    this.getDevice()
  },
  methods: {
    toScenario(){
      uni.switchTab({url:'/pages/scenario/scenario'})
    },
    refreshPage() {
      const scenarioModel = uni.getStorageSync('scenarioModel');
      this.relation = JSON.parse(JSON.stringify(scenarioModel)).cfg_info.relation
    },
    // 打开条件关系选择
    openRelation() {
      this.$refs.andOr.open()
    },
    // 设备作为动作跳转
    deviceNavigateTo(item) {
      // 筛选出可作为动作的属性
      // 存储到
      console.log(item)
      let obj = {
        id: item.id,
        log: item.log || item.product.log || '',
        title: item.name,
        services: item.product.cfg_info.services.filter(attribute => attribute.scene_action)
      }
      uni.setStorageSync('services', obj)
      uni.navigateTo({
        url: '/pages/scenario/equipmentMovement'
      })
    },
    mapSceneConditions(key) {
      let obj = this.scene_conditions.find(item => key == item.value)
      return obj.text
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
        scene_action: true,
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
        url
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
  }
};
</script>

<style lang="scss" scoped>
.title-center {
  flex: 1;
  text-align: center;
  color: $mainTitle;
}

.icon-xiugai {
  font-size: 30rpx;
  font-weight: 600;
}

.goback {
  display: flex;
  align-items: center;

  text {
    font-size: 28rpx;
    color: #000;
    margin-left: 10rpx;
  }
}

.page-content {
  display: flex;
  flex-direction: column;
  height: 100%;

  .renderArea {
    flex: 1;
    overflow-y: auto;
  }

}

.row-box-top {
  @include flex-box;
  flex: 1;
  width: 100%;
  padding: 16rpx;

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

.icon-jianshao {
  color: rgb(255, 38, 0);
  margin-right: 30rpx;
  font-weight: 600;
}

.line {
  @include divider;
}

.textBox {
  width: 250rpx;
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

.effect-time-button {
  @include button;
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 20rpx;
}

.equipment {
  border-bottom: 1rpx solid $dividingLine;
  padding: 50rpx 30rpx;
}

.equipment:last-child {
  border-bottom: none;
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

.topBox {
  background-color: $backgroundColor;
  border-radius: 30rpx;
  padding: 30rpx;
  box-shadow: 0px 2px 2px 1px $shadow;
  margin-top: 30rpx;
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
</style>
