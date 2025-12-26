<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content class="pagebox">
    <view class="top">
      <!-- your page code -->
      <view class="content-top">
        <view class="content-top-info">
          <view class="top-info-item">
            <view class="item-top">{{today_energy}}</view>
            <view class="item-bottom">当日用电量(kWh)</view>
          </view>
          <view class="top-info-item">
            <view class="item-top">{{yesterday_energy}}</view>
            <view class="item-bottom">上日用电量(kWh)</view>
          </view>
        </view>
        <u-swiper :slot-list="slotList">
          <view class="swiperBox" slot="content1">
            <view class="info-item">
              <view class="item">{{dataValue.voltage}}</view>
              <view class="item-bottom">电压(V)</view>
            </view>
            <view class="info-item">
              <view class="item">{{dataValue.current}}</view>
              <view class="item-bottom">电流(A)</view>
            </view>
            <view class="info-item">
              <view class="item">{{dataValue.power}}</view>
              <view class="item-bottom">有功功率(kW)</view>
            </view>
          </view>
          <view class="swiperBox" slot="content2">1111</view>
          <view class="swiperBox" slot="content3">2222</view>
        </u-swiper>
      </view>

      <view class="info-chart-box">
        <view class="top-info-item">
          <view class="item-top">{{today_energy}}</view>
          <view class="item-bottom">当日用电量(kWh)</view>
        </view>
        <view class="chart-box">
          <qiun-data-charts type="area" :opts="opts" :chartData="chartData" />
        </view>
      </view>

      <view class="attribute-info-box">
        <view class="attribute-item-box">
          <text>总用电量(kWh)</text>
          <text>{{dataValue.epi}}</text>
        </view>
        <view class="attribute-item-box">
          <text>总有功功率(kW)</text>
          <text>{{dataValue.xxx}}</text>
        </view>
        <view class="attribute-item-box">
          <text>漏电电流(mA)</text>
          <text>{{dataValue.xxx}}</text>
        </view>
        <view class="attribute-item-box">
          <text>设备温度(℃)</text>
          <text>{{dataValue.xxx}}</text>
        </view>
      </view>

    </view>
    <view class="bottom">
      <view class="item" @click="doSwitch">
        <view class="">
          <uni-icons class="iconfont icon-dianyuan" :style="{color:dataValue.state?'#30c64a !important':'#8f8f8f'}" type="" size="20"></uni-icons>
        </view>
        <view class="">
          {{dataValue.state?'开启':'关闭'}}
        </view>
      </view>
     <view class="item" @click="goLog">
       <view class="">
         <uni-icons class="iconfont icon-shijian" type="" size="20"></uni-icons>
       </view>
       <view class="">
         操作记录
       </view>
     </view>
     <view class="item" @click="goSetting">
       <view class="">
         <uni-icons class="iconfont icon-shezhi1" type="" size="20"></uni-icons>
       </view>
       <view class="">
         设置
       </view>
     </view>
    </view>
  </u-page-content>

</view>
</template>

<script>
export default {
  data() {
    return {
      swiperIndex: 0,
      deviceId: '',
      slotList: [{
          name: 'content1'
        },
        // {
        //   name: 'content2'
        // }, {
        //   name: 'content3'
        // }
      ],
      chartData: {},
      opts: {
        padding: [15, 10, 0, 10],
        enableScroll: false,
        legend: {
          show: false
        },
        xAxis: {
          disableGrid: true,
          labelCount: 3
        },
        yAxis: {
          disabled: true,
          disableGrid: false,
          gridType: "dash",
          dashLength: 2
        },
        extra: {
          area: {
            type: "curve",
            opacity: 1,
            addLine: true,
            width: 2,
            gradient: true,
            activeType: "hollow"
          }
        }
      },
      detail:{},
      baseProps:[],
      mqttClient:null,
      dataValue:{
        voltage:0,//电压
        power:0,//功率
        factor:0,//功率因数
        epi:0,//有功电能
        current:0,//电流
        state:0,//开关状态
      },
      today_energy:0,
      yesterday_energy:0
    }
  },
  onReady() {
    // this.getServerData();
    this.getTotalData(this.deviceId);
  },
  onLoad(query) {
    this.deviceId = query.id;
    this.getDetail(query.id);
    this.getTotalData(query.id);
  },
  methods: {
    doSwitch(){
      let id = this.deviceId;
      this.$http({
        url:`/api/devices/${id}/execute_service/`,
        method:'post',
        data:{
          service_key:this.dataValue.state==1?"close":"open",
        }
      }).then(res=>{
        if(res.statusCode == 200){
          this.dataValue.state = this.dataValue.state==1?0:1,
          uni.showToast({
            title: res.data.msg,
            icon:'none',
          });
        }
      })
    },
    getTotalData(id){
      this.$http({
        url:`/api/devices/${id}/get_socket_energy/`,
        method:'get',
        data:{}
      }).then(res=>{
        if(res.statusCode == 200){
          this.today_energy = res.data.today_energy;
          this.yesterday_energy = res.data.yesterday_energy;
          let categories = [];
          let data = [];
          res.data.hourly_data_list.forEach(item=>{
            categories.push(item.time);
            data.push(item.value)
          })
          let chartOption = {
            categories: categories,
            series: [{
              name: "耗电量",
              data: data
            }]
          };
          this.chartData = JSON.parse(JSON.stringify(chartOption));
        }
      })
    },
    subscription(){
      let mac = this.detail.username;
      this.mqttClient = new this.$mqtt.mqttClient()
      let topicList = [`cs_isw/frontend/${mac}/data`]
      this.mqttClient.connect(topicList,(topic,msg)=>{
        console.log(topic,JSON.parse(msg.toString()),'推送数据')
        let msgData = JSON.parse(msg.toString());
        for(let k in msgData){
            if(k =='timestamp'){
    
            }else{
              this.dataValue[k] = msgData[k].value;
            }
          }
        
      })
    },
    unsubscribe(){
      if(this.mqttClient)this.mqttClient.unsubscribe();
    },
    getDetail(id){
      this.$http({
        url:`/api/devices/${id}/`,
        method:'get',
        data:{}
      }).then(res=>{
        if(res.statusCode == 200){
          this.detail = res.data;
          let props = res.data.product.cfg_info.properties;
          this.baseProps = props.map(item=>{
            return {
              ...item,
              value:0,
            }
          })||[];
          this.getLastState(id);
          this.subscription();
        }
      })
    },
    getServerData() {
      //模拟从服务器获取数据时的延时
      setTimeout(() => {
        let res = {
          categories: ["00:00", "00:00", "00:00", "00:00", "00:00", "00:00"],
          series: [{
            name: "完成量",
            data: [18, 27, 21, 24, 6, 28]
          }]
        };
        this.chartData = JSON.parse(JSON.stringify(res));
      }, 500);
    },
    selectedBanner(index) {
      this.swiperIndex = index
    },
    getLastState(id) {
      this.$http({
        url: `/api/devices/${id}/get_last_report/`,
        method: 'get',
        data: {}
      }).then(res => {
        if (res.statusCode == 200) {
          //your page code
          if(k =='timestamp'){
              
          }else{
            this.dataValue[k] = res.data[k].value;
          }
        }
      })
    },
    goLog() {
      uni.navigateTo({
        url: `/pages/equipment/airSwitchLog?id=${this.deviceId}`
      })
    },
    goSetting() {
      uni.navigateTo({
        url: `/pages/equipment/airSwitchSetting?id=${this.deviceId}`
      })
    },
  }
}
</script>

<style lang="scss" scoped>
.pagebox {
  display: flex;
  flex-direction: column;
  padding: 0;

  .top {
    flex: 1;
  }

  .bottom {
    width: 750rpx;
    height: 128rpx;
    background: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;

    .item {
      width: 140rpx;
      text-align: center;
      margin: 0rpx 60rpx
    }
  }
}

// 样式---------------------
.swiperBox {
  background: url('../../static/equipment/swp_bg.png') 100% 100% fixed no-repeat;
  background-size: cover;
  height: 160rpx;
  padding: 16rpx 40rpx;
  border-radius: 26rpx;
  transform: translateY(60rpx);
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  .info-item{
    color: #fff;
    .item{
      font-size: 40rpx;
      line-height: 1.5;
    }
  }
}

.content-top {
  margin-top: 20rpx;
  background-color: #fff;
}

.content-top-info {
  display: flex;
  justify-content: space-evenly;
  text-align: center;
  align-items: center;
  transform: translateY(30rpx);

  .item-top {
    color: rgb(33, 175, 33);
    font-size: 48rpx;
    line-height: 1.5;
  }
}

.info-chart-box {
  margin: 20rpx 30rpx;
  background-color: #fff;
  padding: 30rpx 30rpx;
  border-radius: 8rpx;
  display: flex;
  justify-content: space-between;
  text-align: center;
  align-items: center;

  .item-top {
    color: rgb(33, 175, 33);
    font-size: 48rpx;
    line-height: 1.5;
  }

  .chart-box {
    // background: rgb(8, 61, 13);
    height: 200rpx;
    width: 360rpx;
  }
}

.attribute-info-box {
  background-color: #fff;
  padding: 30rpx;
  margin-bottom: 30rpx;

  .attribute-item-box {
    padding: 20rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1rpx solid $dividingLine;
  }
}
</style>
