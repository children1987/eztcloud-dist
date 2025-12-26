<template>
<view>
  <u-page-title>
    <view class="select">
      <uni-data-select v-model="orgValue" :localdata="orgList" :clear="false" @change="orgChange"></uni-data-select>
    </view>
    <view class="titleRight">
      <view class="location">
         &nbsp; &nbsp; &nbsp;{{org.city.full_name | remProvince}}
      </view>
      <view class="notificationBox">
        <uni-icons type="notification" class="icons" size="28" @click.native="navigateTo('/pages/message/message')"></uni-icons>
        <uni-badge :text="messageNum" size="small" class="badge" ></uni-badge>
      </view>
    </view>
  </u-page-title>

  <u-page-content>
    <view class="content">
      <view class="swiperBox">
        <!-- 加了主设备 统计信息后释放下边一行 -->
        <!-- <uni-swiper-dot :info="swiperInfo" :current="currentSwiper" field="content" mode="dot"> -->
        <swiper @change="changeSwiper" class="uni-swiper">
          <swiper-item v-for="(item ,index) in swiperInfo" :key="index">
            <view class="swiperItem swiperItemBG1">
              <view class="swiperItemTitle">
                户外环境 
              </view>
              <view class="swiperItemContent">
                <view class="swiperItemImgBox">
                  <img src="static/equipment/wendu.png">
                  温度 {{ weather.tem  || '/'}} °c
                </view>
                <view class="swiperItemImgBox">
                  <img src="static/equipment/shidu.png">
                  湿度 {{ weather.humidity || '/' }}
                </view>
                <view class="swiperItemImgBox">
                  <img src="static/equipment/pm.png">
                  PM2.5 {{ weather.air_pm25 || '/' }}
                </view>
              </view>
            </view>
          </swiper-item>
        </swiper>
        <!-- </uni-swiper-dot> -->
      </view>

      <view class="devices">
        <view class="deviceTotal">
          设备 <text>{{deviceList.length}}</text>
        </view>
        <view class="deviceOnline">
          <u-signal :signal="1" /> <text>{{stateNum.onlineNum}}</text>
          <text style="margin-left:10rpx">在线</text>
        </view>
        <view class="deviceDontOnline">
          <u-signal :signal="0" /> <text>{{stateNum.offlineNum}}</text>
          <text style="margin-left:10rpx">离线</text>
        </view>
      </view>

      <view class="vTab">
        <v-tabs field="name" v-model="currenTab" :tabs="tabs" @change="changeTab" activeColor="#000" lineHeight="6rpx" lineColor="#48A9FC"></v-tabs>
        <uni-icons type="bars" size="28" @click="openPopup"></uni-icons>
      </view>

      <view class="list">
        <u-equipment-square class="listItem" @click.native="tapDevice(item)" v-for="(item,index) in deviceList" :key="index" :itemObj="item" />
        <view v-if="!deviceList.length" style="text-align: center; flex: 1; margin-top: 60rpx;">
          该单元下暂无可选设备
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
</view>
</template>

<script>
export default {
  data() {
    return {
      weather:{},
      currenTab: 0,
      tabs: [{
        id: '',
        name: '所有设备',
      }, ],
      orgValue: '',
      orgList: [],
      messageNum: '',
      swiperInfo: [{
        content: '内容 A'
      }],
      currentSwiper: 0,
      deviceList: [],
      orgs: [],
      org: {
        city: {full_name:''}
      }
    }
  },
  onLoad() {
    this.getUserInfo();
    this.getConditions()
  },
  onShow() {
    this.orgValue = uni.getStorageSync('org').id || ''
    // 获取组织
    this.getOrg();
    // 获取单元列表
    this.getUnit();
    
  },
  computed: {
    stateNum() {
      let onlineNum = 0;
      let offlineNum = 0;
      this.deviceList.forEach(item => {
        if (item.state) {
          onlineNum++
        } else {
          offlineNum++
        }
      })
      return {
        onlineNum,
        offlineNum
      }
    },

  },
  methods: {
    tapDevice(data) {
      console.log(data)
      let key = data.product.product_key;
      let deviceMap = {
        elctn: 'curtain', //窗帘
        b: 'airSwitch', //空开
        wx501: 'switch', //开关
        wx502: 'switch', //开关
        wx503: 'switch', //开关
        ws202: 'lightSensor', //光照传感器
        wx51x: 'socket', //插座
        wx52x: 'socket', //插座
      }
      if (!deviceMap[key]) {
        uni.showToast({
          icon: 'none',
          title: '该设备暂无详情页'
        })
        return
      }
      uni.navigateTo({
        url: `/pages/equipment/${deviceMap[key]}?id=${data.id}`
      })
    },
    // 获取当前组织户外天气
    getWeather(){
      // http://127.0.0.1:8888/api/orgs/1/get_weather
      this.$http({
        url: `/api/orgs/${this.org.id}/get_weather`,
        method: 'get',
        data: {}
      }).then(res => {
        if (res.statusCode == 200) {
          this.weather = res.data[0] || {}
        }
      })
    },
    // 全局获取数据存储
    getConditions() {
      this.$http({
        url: '/api/const_data?data_type=scene_conditions',
        method: 'get',
        data: {}
      }).then(res => {
        if (res.statusCode == 200) {
          uni.setStorageSync('scene_conditions', res.data);
        }
      })
    },
    orgChange(data) {
      console.log(data)
      this.orgValue = data;
      let org = this.orgs.find(item => data == item.id)
      this.org = org
      uni.setStorageSync('org', org);
      this.getOrg();
      // 获取单元列表
      this.getUnit();
    },
    getOrg() {
      this.$http({
        url: '/api/orgs/get_all/',
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          this.orgList = res.data.map(item => {
            return {
              value: item.id,
              text: item.name
            }
          });
          this.orgs = res.data
          if(this.orgList[0] && !this.orgValue){
            this.orgValue = this.orgList[0].value
          } 
          let org = this.orgs.find(item => this.orgValue == item.id)
          this.org = org
          // 获取所有设备
          this.getDevice();
          this.getWeather()
          uni.setStorageSync('org', org);
        }
      })
    },
    getUserInfo() {
      let userInfo = uni.getStorageSync('userInfo');
      this.userInfo = userInfo;
      let default_org = userInfo.default_org;
      if (default_org && !uni.getStorageSync('org')) {
        this.orgValue = default_org.id;
      }
    },
    // 获取单元列表
    getUnit() {
      this.$http({
        url: '/api/org_units/get_all/',
        data: {
          org:this.orgValue
        },
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
        org:this.orgValue
      };
      let unit = this.tabs[this.currenTab];
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
    changeTab(index) {
      this.currenTab = index
      this.$refs.popup.close()
      this.getDevice();
    },
    // 跳转非tabBar页面 参数用?分隔,页面在onLoad接收
    navigateTo(url) {
      console.log(url)
      uni.navigateTo({
        url
      })
    },
    changeSwiper(e) {
      this.currentSwiper = e.detail.current;
    },
    // TAB 更多菜单弹出层 打开
    openPopup() {
      this.$refs.popup.open('right')
    }
  },
  filters:{
    remProvince(value){
      let ind = value.indexOf('省')
      if(ind != -1){
        return value.substring(ind + 1 ,  value.length)
      }else{
        return value
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.select {
  width: 260rpx;

  ::v-deep .uni-select__input-text {
    font-size: $textInputSize;
    color: $mainTitle;
  }

  ::v-deep .uni-select {
    border: none !important;
  }

}

.titleRight {
  flex: 1;
  height: 100%;
  position: relative;

  .notificationBox {
    width: 40rpx;
    position: absolute;
    right: 20rpx;
    top: 50%;
    transform: translateY(-50%);

    .badge {
      position: absolute;
      top: -8rpx;
      right: -20rpx;
      z-index: 99;
    }
  }

  .location {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    right: 100rpx;
    color: $mainTitle;
  }
}

.content {
  height: 100%;
  // display: flex;
  // flex-direction: column;
  overflow-y: auto;

  .swiperBox {
    background-color: $backgroundColor;
    box-shadow: 0px 2px 2px 1px $shadow;
    margin: 36rpx 0;
    border-radius: 30rpx;
    overflow: hidden;
    height: 360rpx;
    position: relative;

    .swiperItem {
      height: 360rpx;
      display: flex;
      flex-direction: column;
      padding: 0 30rpx;
      color: #333;

      .swiperItemTitle {
        padding-top:10rpx;
        font-size: 32rpx;
      }

      .swiperItemContent {
        flex: 1;
        display: flex;
        justify-content: space-around;
        align-items: center;
        .swiperItemImgBox{
          display: flex;
          flex-direction: column;
          align-items: center;
          img{
            margin-bottom: 10rpx;
            width: 120rpx;
            height: 120rpx;
          }
        }
      }
    }

    .swiperItemBG1 {
      background: url('../../static/equipment/environment.png') 100% 100% no-repeat;
      background-size: cover;
    }

    ::v-deep .uni-swiper {
      height: 360rpx !important;
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }

    ::v-deep .uni-swiper__warp {
      height: 360rpx !important;
    }

  }

  .devices {
    height: 128rpx;
    background: $backgroundColor;
    box-shadow: 0px 2px 2px 1px $shadow;
    border-radius: 30rpx;
    padding: 24rpx 0;
    display: flex;
    box-sizing: border-box;
    align-items: center;

    text {
      margin-left: 30rpx;
    }

    .deviceTotal {
      width: 30%;
      height: 100%;
      line-height: 80rpx;
      text-align: center;
      border-right: 1px solid $dividingLine;
    }

    .deviceOnline,
    .deviceDontOnline {
      width: 30%;
      text-align: center;
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

  .list {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-bottom: 36rpx;

    .listItem {
      width: 40%;
      margin-top: 30rpx;
    }
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
  padding: 30rpx;
  border-radius: 30rpx 0 0 30rpx;

  .popupItem {
    height: 80rpx;
    line-height: 80rpx;
  }
}
</style>
