<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content class="pagebox">
    <view class="top">
      <view class="wall"></view>
      <view class="imgbox" @touchstart="touchstart" @touchmove="touchmove" @touchend="touchend">
        <view class="leftparg" ref="leftparg" :style="{width:`${ln}rpx`}">
          <view class="tagleft">
            <view class="cycle">
              <uni-icons :style="{opacity:ln==50?0:1}" type="back" size="8"></uni-icons>
              <uni-icons type="forward" size="8"></uni-icons>
            </view>
          </view>
        </view>
        <view class="rightpart" ref="rightpart" :style="{width:`${rn}rpx`}">
          <view class="tagright">
            <view class="cycle">
              <uni-icons type="back" size="4"></uni-icons>
              <uni-icons :style="{opacity:ln==50?0:1}" type="forward" size="4"></uni-icons>
            </view>
          </view>
        </view>
      </view>
      <view class="data">
        窗帘开度{{openRate}}%
      </view>
    </view>
    <view class="center">
      <view class="btnbox" >
        <view class="">
          <uni-icons :class="{disabled:openDisabled||ln==50}" class="item iconfont icon-a-zu2987" type="" size="30" @click="pressOpen"></uni-icons>
          <view class="">
            全开
          </view>
        </view>
        <view class="">
          <uni-icons :class="{disabled:stopDisabled}" class="item iconfont icon-tingzhi" type="" size="30" @click="pressStop"></uni-icons>
          <view class="">
            停止
          </view>
        </view>
        <view class="">
          <uni-icons :class="{disabled:closeDisabled||ln==375}" class="item iconfont icon-a-zu29871" type="" size="30" @click="pressClose"></uni-icons>
          <view class="">
            全关
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
      ln:375,
      rn:375,
      deviceId:'',
      openRate:0,//开度0-100
      fixdStartNum:0,
      startNum:0,
      openDisabled:false,
      closeDisabled:false,
      stopDisabled:false,
      interval:null,
      mqttClient:null,
    }
  },
  beforeDestroy() {
    this.unsubscribe();
    if(this.interval)clearInterval(this.interval);
  },
  onLoad(query) {
    this.deviceId = query.id;
    this.getDetail(query.id);
    let info = uni.getWindowInfo();
    // console.log(info)
  },
  methods: {
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
          this.subscription()
        }
      })
    },
    subscription(){
      let mac = this.detail.username;
      this.mqttClient = new this.$mqtt.mqttClient()
      let topicList = [`cs_isw/frontend/${mac}/data`]
      console.log(topicList)
      this.mqttClient.connect(topicList,(topic,msg)=>{
        console.log(topic,JSON.parse(msg.toString()),'推送数据')
        let msgData = JSON.parse(msg.toString());
        if(msgData&&msgData.open_rate){
          this.openRate = msgData.open_rate.value;
          this.ln = 375 - (3.25*(100-msgData.open_rate.value));
          this.rn = 375 - (3.25*(100-msgData.open_rate.value));
        }
        
      })
    },
    unsubscribe(){
      if(this.mqttClient)this.mqttClient.unsubscribe();
    },
    // 全开
    pressOpen(){
      if(this.openDisabled||this.ln ==50)return
      // if(this.stopDisabled)this.stopDisabled = false;
      this.closeDisabled = false;
      let id = this.deviceId;
      this.$http({
        url:`/api/devices/${id}/execute_service/`,
        method:'post',
        data:{
          service_key: "open",
        }
      }).then(res=>{
        if(res.statusCode == 200){
          uni.showToast({
            title: res.data.msg,
            icon:'none',
          });
        }
      })
      this.openDisabled = true;
      if(this.interval)clearInterval(this.interval);
      this.interval = setInterval(()=>{
        if(this.ln<=50){
          this.ln=50;
          this.rn=50;
          this.openRate = 0;
          clearInterval(this.interval)
          this.openDisabled = false;
          return
        }else{
          this.ln-=7;
          this.rn-=7;
        }
      },40)
    },
    //全关
    pressClose(){
      if(this.closeDisabled||this.ln==375)return
      // if(this.stopDisabled)this.stopDisabled = false;
      this.openDisabled = false;
      let id = this.deviceId;
      this.$http({
        url:`/api/devices/${id}/execute_service/`,
        method:'post',
        data:{
          service_key: "close",
        }
      }).then(res=>{
        if(res.statusCode == 200){
          uni.showToast({
            title: res.data.msg,
            icon:'none',
          });
        }
      })
      this.closeDisabled = true;
      if(this.interval)clearInterval(this.interval);
      this.interval = setInterval(()=>{
        if(this.ln>=375){
          this.ln=375;
          this.rn=375;
          this.openRate = 100;
          clearInterval(this.interval);
          this.closeDisabled = false;
          return
        }else{
          this.ln+=7;
          this.rn+=7;
        }
      },40)
    },
    //停止
    pressStop(){
      // if(this.stopDisabled)return
      clearInterval(this.interval)
      // this.stopDisabled = true;
      if(this.closeDisabled){
        this.closeDisabled = false;
      }
      if(this.openDisabled){
        this.openDisabled = false;
      }
      let id = this.deviceId;
      this.$http({
        url:`/api/devices/${id}/execute_service/`,
        method:'post',
        data:{
          service_key: "stop",
        }
      }).then(res=>{
        if(res.statusCode == 200){
          uni.showToast({
            title: res.data.msg,
            icon:'none',
          });
        }
      })
    },
    touchstart(e){
      if(this.interval)clearInterval(this.interval);
      // console.log(e)
      let x = e.changedTouches[0].pageX;
      this.startNum = x;
      this.fixdStartNum = x;
    },
    touchmove(e){
      // console.log(e)
      let x = e.changedTouches[0].pageX;
      let difference = this.startNum - x;
      let step = 7
      // console.log(x)
      // console.log(difference)
      
      if(difference<0){
        if(this.ln>375){
          this.ln=375;
        }else if(this.ln<=50){
          this.ln=50;
          this.rn=50;
        }else{
          this.ln-=step;
          this.rn-=step;
        }
      }else{
        if(this.ln>=375){
          this.ln=375;
        }else if(this.ln<50){
          this.ln=50;
          this.rn=50;
        }else{
          this.ln+=step;
          this.rn+=step;
        }
      }
      this.startNum = x;
    },
    touchend(e){
      // console.log(e)
      let x = e.changedTouches[0].pageX;
      let difference = this.fixdStartNum - x;
      let persent = Math.round((325-Math.abs(this.ln-50))*100/325);
      console.log(this.ln)
      console.log(persent)
      this.writeAttr( 100 - persent)
    },
    writeAttr(value){
      if(value == this.openRate)return
      this.openRate = value;
      let id = this.deviceId;
      this.$http({
        url:`/api/devices/${id}/write_attr/`,
        method:'post',
        data:{
          key: "open_rate",
          val: value
        }
      }).then(res=>{
        if(res.statusCode == 200){
          uni.showToast({
            title: res.data.msg,
            icon:'none',
          });
        }
      })
    },
    goLog(){
      uni.navigateTo({
        url:`/pages/equipment/curtainLog?id=${this.deviceId}`
      })
    },
    goSetting(){
      uni.navigateTo({
        url:`/pages/equipment/curtainSetting?id=${this.deviceId}`
      })
    },
    getLastState(id){
      this.$http({
        url:`/api/devices/${id}/get_last_report/`,
        method:'get',
        data:{}
      }).then(res=>{
        if(res.statusCode == 200){
          if(res.data.open_rate){
            this.openRate = res.data.open_rate.value;
            this.ln = 375-( 3.25*(100-res.data.open_rate.value));
            this.rn = 375-(3.25*(100-res.data.open_rate.value));
          }
        }
      })
    },
    toHomeDetile() {
      console.log(1111)
      uni.navigateTo({
        url: "/pages/homeDetile/homeDetile"
      })
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
      background: #FFFFFF;
      flex:1;
      .wall{
        height: 1.5%;
        background: #85CEFF;
        box-shadow: inset 0rpx 4rpx 2rpx 2rpx rgba(0,0,0,0.16);
      }
      .imgbox{
        height: 85%;
        position: relative;
        .leftparg,.rightpart{
          position: absolute;
          width: 375rpx;
          height: 90%;
          background-image: url('../../static/curtain/curtain.png');
          background-repeat: no-repeat;
          background-size: 100% 100%;
          top:0rpx;
        }
        .leftparg{
          left:2rpx;
        }
        .rightpart{
          right:2rpx;
        }
        .tagleft,.tagright{
          position: absolute;
          top: 50%;
          height: 18rpx;
          width: 100%;
        }
        .tagleft{
          background: linear-gradient(92deg, rgba(79,166,243,0) 0%, rgba(79,166,243,0.56) 55%, #4FA6F3 100%);
          right: 0rpx;
          .cycle{
            right: -20rpx;
          }
        }
        .tagright{
          background: linear-gradient(268deg, rgba(79,166,243,0) 0%, rgba(79,166,243,0.56) 55%, #4FA6F3 100%);
          left: 0rpx;
          .cycle{
           left: -20rpx; 
          }
        }
        .cycle{
          width: 36rpx;
          text-align: center;
          height: 36rpx;
          line-height: 36rpx;
          border: 2rpx solid #58ACF4;
          background: #FFFFFF;
          position: absolute;
          border-radius: 50%;
          font-size: 12rpx;
          overflow: hidden;
          top:-12rpx;
        }
      }
      .data{
        height: 10%;
        font-size: 28rpx;
        text-align: center;
        color: rgba(0,0,0,0.5);
        // display: flex;
        // justify-content: center;
        // align-items: center;
      }
    }
    .center{
      padding: 26rpx 16rpx;
      .btnbox{
        height: 208rpx;
        width: 100%;
        box-sizing: border-box;
        padding: 0px 40rpx;
        background: #FFFFFF;
        box-shadow: 0rpx 2rpx 4rpx 2rpx rgba(223,223,223,1);
        border-radius: 16rpx 16rpx 16rpx 16rpx;
        display: flex;
        align-items: center;
        justify-content: space-around;
        text-align: center;
        .item{
          display: inline-block;
          width: 94rpx;
          height: 94rpx;
          line-height: 94rpx;
          color:#fff!important;
          background: #48A9FC;
          border-radius: 50%;
          &.disabled{
            background: #c3c3c3;
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
