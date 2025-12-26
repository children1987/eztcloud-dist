<template>
<view class="page">
  <u-page-title>
    <u-goback />
  </u-page-title>
  
  <u-page-content>
    <uni-list style="margin: 30rpx -16rpx 0px;">
      <!-- <uni-list-item
        :title="userInfo.nickname" 
        showArrow
        thumb-size="lg"  >
        <template v-slot:header>
          <view class="iconbox">
            <view class="avatar" v-if="userInfo.avatar">
              <img style="width: 112rpx;height: 112rpx;" :src="userInfo.avatar" alt="" srcset="">
            </view>
            <view class="avatar" v-else>
              {{userInfo.nickname}}
            </view>
          </view>
        </template>
      </uni-list-item> -->
      <uni-list-item title="当前账号(手机号)"  :rightText="userInfo.mobile" />  
      <uni-list-item title="姓名"  :rightText="userInfo.nickname" />  
    </uni-list>
  </u-page-content>
  
</view>
</template>

<script>
export default {
  data() {
    return {
      userInfo:{},
    }
  },
  onLoad() {
    this.getUserInfo();
  },
  methods: {
    getUserInfo(){
      this.userInfo = uni.getStorageSync('userInfo')||{};
    },
  }
}
</script>

<style lang="scss" scoped>
  .page{
    ::v-deep .uni-list-item__content{
      justify-content: center;
    }
    .iconbox{
      margin-right: 9px;
      display: flex;
      flex-direction: row;
      align-items: center;
    }
    .avatar{
      border-radius: 50%;
      overflow: hidden;
      background-image: linear-gradient(#46ADFC,#5983FE);
      width: 112rpx;
      height: 112rpx;
      line-height: 112rpx;
      font-size: 30rpx;
      text-align: center;
      color:#fff;
    }
  }
</style>
