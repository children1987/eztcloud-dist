<template>
<view>
  <view class="img">
    <image src="../../static/login/wulianwang.png" mode="scaleToFill" class="top-image" />
  </view>
  <view class="login-title">EasyCloud物联网平台</view>
  <view class="login-form">
    <uni-forms ref="form" class="form" :rules="rules" :modelValue="form">
      <uni-forms-item name="username">
        <uni-easyinput placeholder="登录" v-model="form.username" />
      </uni-forms-item>
      <uni-forms-item name="password">
        <uni-easyinput placeholder="密码" type="password" v-model="form.password" />
      </uni-forms-item>
    </uni-forms>
  </view>
  <view class="login-button">
    <button class="button" @click="login">立即登录</button>
  </view>
  <!-- <view class="tourist-login">游客登陆</view> -->
  <view class="agreement">
    <radio-group>
      <label @click="radioChange">
        <radio value="1" :checked="agree" disabled />
        <text>我已阅读</text>
        <text>《用户协议》</text>和
        <text>《隐私政策》</text>
      </label>
    </radio-group>
  </view>
  <u-dialog ref="popup" @confirm="dialogChange">
    <view class="dialogBox">
      <view class="dialogTitle">
        用户协议和隐私政策
      </view>
      <view class="dialogP">
        用户协议和隐私政策请您务必审慎阅读、充
        分理解“用户协议“和“隐私协议”各条款，包括但不限于：
        为了向您提供智能设备信息、消息通知等服务,
        我们需要收集您的设备信息、操作日志等个人信息。您可阅读
        <text @click="navigateTo('/pages/ucenter/setting/userAgreement')">《用户协议》</text> 和<text @click="navigateTo('/pages/ucenter/setting/privacyAgreement')">《隐私政策》</text> 了解详细信息。
      </view>
      <view class="dialogP">
        如您同意,请点击“确认”开始接受我们的服务。
      </view>
    </view>
  </u-dialog>
</view>
</template>

<script>
export default {
  data() {
    return {
      agree: false,
      form: {
        username: "",
        password: ""
      },
      rules: {
        username: {
          rules: [{
            required: true,
            errorMessage: '请输入账号',
          }, ]
        },
        password: {
          rules: [{
            required: true,
            errorMessage: '请输入密码',
          }, ]
        }
      }
    };
  },
  methods: {

    // 选中
    radioChange() {
      this.$refs.popup.open()
    },
    dialogChange() {
      this.agree = !this.agree;
    },
    // 跳转
    navigateTo(url) {
      uni.navigateTo({
        url
      })
    },
    login() {
      this.$refs.form.validate().then(res => {
        if (!this.agree) {
          uni.showToast({
            title: '请先阅读用户协议和隐私政策',
            icon: 'none',
          });
          this.radioChange()
          return
        }
        this.$http({
          url: '/api-token-auth/',
          method: 'post',
          data: {
            ...res
          }
        }).then(res => {
          console.log(res)
          if (res.statusCode == 200) {
            uni.setStorageSync('token', res.data.token);
            uni.setStorageSync('userInfo', res.data.user);
            uni.switchTab({
              url: '/pages/index/index',
            });
          }else{
            uni.showToast({
              title: res.data.msg,
              icon: 'none',
            });
          }
        })
      }).catch(err => {
        console.log('表单错误信息：', err);
      })
    }
  }
};
</script>

<style lang="scss">
page {
  background: linear-gradient(135deg, #68cffe 0%, #4249fb 100%, #3036ef 100%);
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.img {
  width: 100%;
  height: 352rpx;
  text-align: center;
  margin-top: 160rpx;

  .top-image {
    width: 340rpx;
    height: 352rpx;
    transform: translateY(60rpx);
  }
}

.login-title {
  font-size: 40rpx;
  font-weight: 500;
  color: #ffffff;
  text-align: center;
  margin-top: 116rpx;
  transform: translateY(-20rpx);
}

.login-form {
  width: 100%;
  margin-top: 40rpx;

  .form {
    width: 60%;
    text-align: center;
    margin: 0 auto;
  }
}

.login-button {
  .button {
    background: #5eb5ff;
    width: 60%;
    font-size: 32rpx;
    font-weight: 400;
    color: #ffffff;
  }
}

.tourist-login {
  text-align: center;
  font-size: 12px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 60rpx;
}

.agreement {
  font-size: 12px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  text-align: center;
  position: fixed;
  bottom: 20rpx;
  right: 0;
  left: 0;

  ::v-deep .uni-radio-input {
    width: 24rpx;
    height: 24rpx;
  }
}

.dialogBox {
  padding: 30rpx;

  .dialogTitle {
    color: #000;
    font-weight: 600;
    font-size: 32rpx;
    text-align: center;
    margin-bottom: 30rpx;
  }

  .dialogP {
    text-indent: 4ch;
    line-height: 1.7;

    text {
      color: $mainColor;
    }
  }
}
</style>
