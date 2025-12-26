<template>
<view class="timelineBox">
  <view class="top">
    <view class="startDate">
      <uni-dateformat :date="currentday" format="MM月dd日"></uni-dateformat>
    </view>
    <uni-datetime-picker type="date" :clear-icon="false" v-model="startDate" @change="dateChange" placeholder="选择开始日期" />
  </view>
  <view v-if="!deviceLog.length" class="empty">
    暂无数据
  </view>
  <scroll-view class="logbox" @scrolltolower="toBottom" scroll-y @scroll="scroll">
    
    <view  class="item" v-for="(item,index) in deviceLog" :key='index'>
      <view class="left">
        <view class="line"></view>
        <view class="point"></view>
      </view>
      <view class="right">
        <view class="lef">
          <view class="">
            {{item.title}}
          </view>
          <view class="">
            <uni-dateformat :date="item.time" format="hh:mm"></uni-dateformat>
          </view>
        </view>
        <view class="rig">
          {{item.content}}
        </view>
      </view>
    </view>
  </scroll-view>
</view>

</template>

<script>
export default {
  props:{
    deviceLog:{
      type:Array,
      default:()=>[
        // {
        //   title:'手动|张三',
        //   content:'开度0%',
        //   time:'2021/12/13 12:10:20',
        //   state:'1'
        // }
      ]
    }
  },
  watch:{
    deviceLog:{
      immediate:true,
      handler(newVal,oldVal){
        console.log(newVal)
        if(newVal.length&&!this.hasInit){
          this.currentday = newVal[0].time;
          this.hasInit = true;
        }
      },
    }
  },
  data(){
    return{
      currentday:Date.now(),
      startDate:'',
      oldIndex:0,
      hasInit:false,
    }
  },
  methods:{
    scroll(e){
      let index = Math.floor(e.detail.scrollTop/80);
      if(index!= this.oldIndex){
        this.currentday = this.deviceLog[index].time;
        this.oldIndex = index;
      }
    },
    toBottom(e){
      console.log(e)
      this.$emit('toBottom')
    },
    dateChange(data){
      // console.log(data)
      this.$emit('dateChange',data)
    },
  }
}
</script>

<style lang="scss" scoped>
.timelineBox{
  height: 100%;
  display: flex;
  flex-direction: column;
  .empty{
    margin: 100rpx 0rpx;
    text-align: center;
  }
  .top{
    padding: 10rpx;
   display: flex;
   justify-content: space-between;
   align-items: center;
   z-index: 100;
   .startDate{
     width: 138rpx;
     height: 52rpx;
     border-radius: 8rpx;
     line-height: 52rpx;
     text-align: center;
     font-size: 28rpx;
     color: #fff;
     background: linear-gradient(180deg, #47ABFC 0%, #5B81FE 100%);
   }
   ::v-deep .uni-date{
        width: 276rpx;
        flex: none;
    }
  }
  .logbox{
    flex:1;
    overflow: auto;
    // overflow: hidden;
    .item{
      display: flex;
      width: 100%;
      height: 80px;
      .left{
        width: 100rpx;
        text-align: center;
        position: relative;
        .line{
          z-index: 1;
          position: absolute;
          top: -5px;
          bottom:5px;
          left: 50rpx;
          width: 4rpx;
          background-color: #00000040;
        }
        .point{
          z-index: 2;
          position: absolute;
          bottom: 5px;
          left:34rpx;
          width: 38rpx;
          height: 38rpx;
          border-radius: 50%;
          background: #0FB42B;
        }
      }
      .right{
        flex:1;
        display: flex;
        padding-top: 90rpx;
        .lef{
          width: 160rpx;
        }
        .rig{
          flex:1;
        }
      }
    }
  }
}
</style>
