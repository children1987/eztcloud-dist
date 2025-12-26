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
      <view class="attribute-info-box">
        <view class="attribute-item-box" v-for="(item,index) in baseProps" :key="index">
          <text>{{item.name}}</text>
          <text>{{item.value|valFilter(item)}}</text>
        </view>
      </view>
    </view>
    <view class="bottom">
      <!-- <view class="item">
        <view class="">
          <uni-icons class="iconfont icon-dianyuan" :style="{color:dataValue.state?'#30c64a !important':'#8f8f8f'}" type="" size="20"></uni-icons>
        </view>
        <view class="">
          {{dataValue.state?'开启':'关闭'}}
        </view>
      </view> -->
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
      deviceId:'',
      detail:{},
      baseProps:[],
      mqttClient:null,
    }
  },
  onLoad(query) {
    this.deviceId = query.id;
    this.getDetail(query.id)
  },
  beforeDestroy() {
    this.unsubscribe();
  },
  methods: {
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
              let index = this.baseProps.findIndex(item=>item.key==k);
              if(index!=-1){
                this.baseProps[index].value = msgData[k].value;
              }
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
    getLastState(id){
      this.$http({
        url:`/api/devices/${id}/get_last_report/`,
        method:'get',
        data:{}
      }).then(res=>{
        if(res.statusCode == 200){
          //your page code
           for(let k in res.data){
            if(k =='timestamp'){

            }else{
              let index = this.baseProps.findIndex(item=>item.key==k);
              if(index!=-1){
                this.baseProps[index].value = res.data[k].value;
              }
            }
          }
        }
      })
    },
    goLog(){
      uni.navigateTo({
        url:`/pages/equipment/lightSensorLog?id=${this.deviceId}`
      })
    },
    goSetting(){
      uni.navigateTo({
        url:`/pages/equipment/lightSensorSetting?id=${this.deviceId}`
      })
    },
  },
  filters:{
    valFilter(val,data){
      console.log(val,data)
      let type = data.data_type;
      let key = data.key
      let resMap = {
        battery_el:{
          val:val,
          extra:'%'
        },
        pir_state:{
          val:val?'触发':'未触发',
          extra:''
        },
        state:{
          val:val?'明亮':'黑暗',
          extra:''
        },
      }
      let tar = resMap[key];
      return tar.val+tar.extra
    }
  }
}
</script>

<style lang="scss" scoped>
.pagebox{
    display: flex;
    flex-direction: column;
    padding: 0;
    .top{
      flex:1;
    }
    .bottom{
      width: 750rpx;
      height: 128rpx;
      background: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      .item{
        width: 140rpx;
        text-align: center;
        margin:0rpx 60rpx
      }
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
