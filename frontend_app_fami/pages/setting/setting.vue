<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <view class="setting-list first-list">
      <view class="list-box" @click="openPopup">
        <text class="list-left">修改密码</text>
        <uni-icons type="forward" size="16"></uni-icons>
      </view>
      <uni-popup ref="popup" type="dialog" background-color="#ffffff">
        <view class="form">
          <uni-forms ref="form">
            <uni-forms-item label="手机号:" name="oldPass" labelWidth="72px">
              <uni-easyinput type="number" placeholder="请输入手机号" />
              <text class="code">获取验证码</text>
            </uni-forms-item>
            <uni-forms-item label="验证码:" name="oldPass" labelWidth="72px">
              <uni-easyinput type="text" placeholder="请输入验证码" />
            </uni-forms-item>
            <uni-forms-item label="新密码:" name="oldPass" labelWidth="72px">
              <uni-easyinput type="password" placeholder="请输入新密码" />
            </uni-forms-item>
            <uni-forms-item label="确认密码:" name="newPsd" labelWidth="72px">
              <uni-easyinput type="password" placeholder="请再次输入新密码" />
            </uni-forms-item>
          </uni-forms>
        </view>
        <view class="button">
          <button size="mini" class="left-button" @click="passwordCancel">取消</button>
          <button size="mini" class="right-button" @click="passwordChange">确认</button>
        </view>
      </uni-popup>

    </view>
    <view class="setting-list">
      <view class="list-box" @click="jumpUserAgreement">
        <text class="list-left">用户协议</text>
        <uni-icons type="forward" size="16"></uni-icons>
      </view>
    </view>
    <view class="setting-list">
      <view class="list-box" @click="jumpPrivacyAgreement">
        <text class="list-left">隐私协议</text>
        <uni-icons type="forward" size="16"></uni-icons>
      </view>
    </view>
    <view class="setting-list">
      <view class="list-box">
        <text class="list-left">账号注销</text>
        <view>
          <text class="account-text">400888</text>
          <uni-icons type="forward" size="16"></uni-icons>
        </view>
      </view>
    </view>
    <footer class="operation" style="margin-top: 10px">
      <text class="account" @click="changeAccount">切换账号</text>
      <text class="loginOut" @click="quitSoftware">退出软件</text>
    </footer>

  </u-page-content>

</view>
</template>

<script>
export default {
  data() {
    return {};
  },
  methods: {
    // 打开修改密码的弹框
    openPopup() {
      this.$refs.popup.open("center");
    },
    // 点击取消修改密码
    passwordCancel() {
      this.$refs.popup.close();
    },
    // 点击确定修改密码
    passwordChange() {
      // console.log('点击确认');
    },
    // 退出软件
    quitSoftware() {
      switch (uni.getSystemInfoSync().platform) {
        case "android":
          plus.runtime.quit();
          break;
        case "ios":
          plus.ios
            .import("UIApplication")
            .sharedApplication()
            .performSelector("exit");
          break;
      }
    },
    // 切换账号
    changeAccount() {
      uni.reLaunch({
        url: "/pages/login/login",
      });
    },
    // 跳转到用户协议
    jumpUserAgreement() {
      uni.navigateTo({
        url: "/pages/userAgreement/userAgreement",
      });
    },
    // 跳转到隐私协议
    jumpPrivacyAgreement() {
      uni.navigateTo({
        url: "/pages/privacyAgreement/privacyAgreement",
      });
    },
  },
};
</script>

<style lang="scss">
.select {
  width: 200rpx;
}

.first-list {
  margin-top: 16rpx;
}

.setting-list {
  height: 84rpx;
  background-color: #fff;

  // padding-left: 32rpx;
  // padding-right: 32rpx;
  .list-box {
    border-bottom: 2rpx solid rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 80rpx;

    .list-left {
      font-size: 32rpx;
      font-family: Source Han Sans CN-Light, Source Han Sans CN;
      font-weight: 300;
      color: rgba(0, 0, 0, 0.85);
    }

    .account-text {
      font-size: 28rpx;
      font-family: Source Han Sans CN-Light, Source Han Sans CN;
      font-weight: 300;
      color: rgba(0, 0, 0, 0.5);
    }
  }
}

.form {
  .code {
    font-size: 28rpx;
    font-family: Source Han Sans CN-Light, Source Han Sans CN;
    font-weight: 300;
    color: #48a7fd;
  }

  ::v-deep .uni-forms .uni-forms-item:first-child .uni-forms-item__content {
    display: flex;
    align-items: center;
  }

  ::v-deep .uni-easyinput {
    width: 320rpx;
  }
}

.button {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 68rpx;

  .left-button {
    margin: 0;
    margin-right: 16rpx;
    width: 160rpx;
    font-weight: 400;
    color: rgba(0, 0, 0, 0.85);
  }

  .right-button {
    margin: 0;
    margin-left: 16rpx;
    width: 160rpx;
    background: linear-gradient(180deg, #48a9fd 0%, #5785fe 100%);
    font-weight: 400;
    color: #ffffff;
  }
}

.operation {
  display: flex;
  flex-direction: column;
  align-items: center;

  :first-child {
    margin-bottom: 20rpx;
    width: 750rpx;
    background-color: #fff;
    text-align: center;
    height: 80rpx;
    line-height: 80rpx;
  }

  :last-child {
    width: 750rpx;
    background-color: #fff;
    text-align: center;
    height: 80rpx;
    line-height: 80rpx;
  }
}
</style>
