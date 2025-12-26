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
      <view class="box">
        <view class="innerbox">
          <view class="item" v-for="(item,index) in baseProps" :key="index" :style="{width:baseProps.length==3&&index==0?'100%':'50%'}">
            <!-- <view @click="switchOpen(item,index)" :style="{color:item.value?'#23D642':'#c2c2c2'}" class="txt">L{{index+1}}</view> -->
            <view class="btn" :class="[item.value?'on'+index:'off'+index]">
              
            </view>
          </view>
        </view>
      </view>
    </view>
    <view class="bottom">
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
      console.log(this.$mqtt)
      try{
        this.mqttClient = new this.$mqtt.mqttClient()
      }catch(e){
        //TODO handle the exception
        console.log(e)
      }
      
      let topicList = [`cs_isw/frontend/${mac}/data`]
      console.log(topicList)
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
    switchOpen(data,index){
      console.log(data);
      let id = this.deviceId;
      let postVal = data.value==1?0:1;
      this.$http({
        url:`/api/devices/${id}/write_attr/`,
        method:'post',
        data:{
          key:data.key,
          val:postVal
        }
      }).then(res=>{
        if(res.statusCode == 200){
          this.baseProps[index].value = postVal;
          uni.showToast({
            title: res.data.msg,
            icon:'none',
          });
          // this.getLastState(id);
        }
      })
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
        url:`/pages/equipment/switchLog?id=${this.deviceId}`
      })
    },
    goSetting(){
      uni.navigateTo({
        url:`/pages/equipment/switchSetting?id=${this.deviceId}`
      })
    },
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
      display: flex;
      align-items: center;
      justify-content: center;
      .box{
        width: 674rpx;
        height: 656rpx;
        padding: 16rpx;
        box-shadow: 0rpx 4rpx 4rpx 2rpx rgba(112,112,112,1);
        border-radius: 38rpx 38rpx 38rpx 38rpx;
        background: #FFFFFF;
        .innerbox{
          height: 100%;
          border-radius: 38rpx 38rpx 38rpx 38rpx;
          border: 2rpx solid #c9c9c9;
          display: flex;
          justify-content: space-around;
          align-items: center;
          text-align: center;
          align-content: center;
          flex-wrap: wrap;
          .item{
            height: 250rpx;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            .btn{
              width: 164rpx;
              height: 164rpx;
              background-size: 100% 100%;
            }
            .on0{
              background-image: url('../../static/switch/on1.png');
            }
            .on1{
              background-image: url('../../static/switch/on2.png');
            }
            .on2{
              background-image: url('../../static/switch/on3.png');
            }
            .off0{
              background-image: url('../../static/switch/off1.png');
            }
            .off1{
              background-image: url('../../static/switch/off2.png');
            }
            .off2{
              background-image: url('../../static/switch/off3.png');
            }
            .txt{
              width: 164rpx;
              height: 164rpx;
              line-height: 164rpx;
              
              border-radius: 50%;
              background-image: radial-gradient( circle closest-side, #F5F1F1 10%, #F8F8F8 70%, #ededed 100%,);
              font-size: 80rpx;
              font-weight: bold;
              color: #23D642;
              text-shadow: 0rpx 6rpx 6rpx rgba(0,0,0,0.39);
            }
          }
        }
      }
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
</style>
