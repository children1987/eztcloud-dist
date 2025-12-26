<template>
  <view>
    <u-page-title>
      <view class="select">
        <u-goback />
      </view>
    </u-page-title>

    <u-page-content>
      <view class="privacyAgreement">
        隐私协议
      </view>
      <view class="updata-date">
        <text>更新日期</text>
        <text>【2022/11/11】</text>
      </view>
      <view class="effect-date">
        <text>生效日期</text>
        <text>【2022/11/11】</text>
      </view>

    </u-page-content>

  </view>
</template>

<script>
export default {
  data() {
    return {};
  },
};
</script>

<style lang="scss">
.select {
  width: 200rpx;
}
.privacyAgreement {
  height: 86rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  math-style: 28rpx;
  font-size: 32rpx;
  font-family: Source Han Sans CN-Light, Source Han Sans CN;
  font-weight: 300;
  color: rgba(0, 0, 0, 0.85);
}
.updata-date {
  height: 86rpx;
  display: flex;
  padding-left: 70rpx;
  padding-right: 70rpx;
  align-items: center;
  background-color: #fff;
  math-style: 28rpx;
  font-size: 32rpx;
  font-family: Source Han Sans CN-Light, Source Han Sans CN;
  font-weight: 300;
  color: rgba(0, 0, 0, 0.85);
}
.effect-date {
  height: 86rpx;
  display: flex;
  align-items: center;
  background-color: #fff;
  math-style: 28rpx;
  padding-left: 70rpx;
  padding-right: 70rpx;
  font-size: 32rpx;
  font-family: Source Han Sans CN-Light, Source Han Sans CN;
  font-weight: 300;
  color: rgba(0, 0, 0, 0.85);
}
</style>
