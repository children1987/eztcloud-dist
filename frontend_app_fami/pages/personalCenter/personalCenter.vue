<template>
  <view>
    <u-page-title>
      <view class="select">
        <u-goback />
      </view>
    </u-page-title>
    <u-page-content>
      <view class="personal">
        <!-- <view class="avatar-area">
          <image src="" mode="aspectFit" class="avatar-img"></image>
          <uni-icons type="forward" size="16"></uni-icons>
        </view> -->
        <view class="account">
          <text class="account-left">当前账号</text>
          <text class="account-right">15236968956</text>
        </view>
        <view class="account">
          <text class="account-left">姓名</text>
          <text class="account-right">张伟</text>
        </view>
      </view>
    </u-page-content>

  </view>
</template>

<script>
export default {
  data() {
    return {};
  },
  methods: {},
};
</script>

<style lang="scss">
.select {
  width: 200rpx;
}
.personal {
  background-color: #fff;
  height: 336rpx;
  // padding-left: 52rpx;
  // padding-right: 24rpx;
}
.avatar-area {
  height: 120rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  .avatar-img {
    background-color: red;
    width: 82rpx;
    height: 82rpx;
    border-radius: 52rpx 52rpx 52rpx 52rpx;
    background: linear-gradient(180deg, #46adfc 0%, #5983fe 100%);
  }
}
.account {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 84rpx;
  .account-left {
    height: 34rpx;
    font-size: 32rpx;
    font-family: Source Han Sans CN-Light, Source Han Sans CN;
    font-weight: 300;
    color: rgba(0, 0, 0, 0.8);

    .account-right {
      height: 28rpx;
      font-size: 28rpx;
      font-family: Source Han Sans CN-Light, Source Han Sans CN;
      font-weight: 300;
      color: rgba(0, 0, 0, 0.5);
    }
  }
}
</style>
