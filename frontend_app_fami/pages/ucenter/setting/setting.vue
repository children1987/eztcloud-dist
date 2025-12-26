<template>
  <view class="page">
    <u-page-title>
      <u-goback />
    </u-page-title>
    <u-page-content>
      <uni-list style="margin: 30rpx -16rpx 0px;">
        <uni-list-item :border="false" showArrow title="修改密码" @click="changePwd" clickable />
        <uni-list-item :border="false" showArrow title="用户协议" to="/pages/ucenter/setting/userAgreement" @click="onClick" />
        <uni-list-item :border="false" showArrow title="隐私政策" to="/pages/ucenter/setting/privacyAgreement" @click="onClick" />
        <uni-list-item :border="false" showArrow title="账号注销" rightText="13816412014" @click="cancelAccount" clickable />
      </uni-list>
      <view class="btnbox btnmt" @click="switchUser">
        切换账号
      </view>
      <view class="btnbox" @click="exit">
        退出软件
      </view>
    </u-page-content>

    <!-- changepwd -->
    <u-dialog ref="dialog" @confirm="formChange">
      <uni-forms ref="form" :rules="passwordForm" label-width="160rpx" label-align="right">
        <uni-forms-item  label="手机号" name="phone" style="margin-bottom: 0rpx;">
          <uni-easyinput trim="all" v-model="passwordForm.phone" placeholder="请输入"></uni-easyinput>
        </uni-forms-item>
        <view style="padding: 20rpx 0rpx 20rpx 180rpx;">
          <!-- <text style="color: #48A7FDFF;">获取验证码</text> -->
          <u-sms ref="sms" url='/api/users/send_change_password_code/'  @click.native="getSms"/>
        </view>
        <uni-forms-item label="验证码" name="code">
          <uni-easyinput trim="all" v-model="passwordForm.code" placeholder="请输入"></uni-easyinput>
        </uni-forms-item>
        <uni-forms-item label="新密码" name="pwd">
          <uni-easyinput v-model="passwordForm.pwd" type="password" placeholder="请输入" />
        </uni-forms-item>
        <uni-forms-item label="确认密码" name="pwd2">
          <uni-easyinput v-model="passwordForm.pwd2" type="password" placeholder="请输入" />
        </uni-forms-item>
      </uni-forms>
    </u-dialog>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        passwordForm: {
          phone: '',
          code: '',
          pwd: '',
          pwd2: '',
        },
        userInfo: {

        }
      }
    },
    onLoad() {
      this.getUserInfo();
    },
    methods: {
      getSms(){
        let mobile = this.passwordForm.phone;
        if(mobile){
          this.$refs.sms.getSms({
            mobile,
            user_id:this.userInfo.id
          });
        }
      },
      getUserInfo(){
        let userInfo = uni.getStorageSync('userInfo')||{};
        this.userInfo = userInfo
        if(userInfo.mobile){
          this.passwordForm.phone = userInfo.mobile;
        }
      },
      async formChange() {
        if(this.passwordForm.pwd!=this.passwordForm.pwd2){
          uni.showToast({
            title: '新密码与确认密码不同，请检查',
            icon:'none',
          });
          return
        }
        let verifyMobilOrg = await this.$http({
          url:'/api/users/verify_sms_code/',
          method:'post',
          data:{
            verify_type:'change_password ',
            mobile:this.form.mobile,
            code:this.form.sms
          }
        })
        if(verifyMobilOrg.data.result == 'error'){
          uni.showToast({
            title: verifyMobilOrg.data.msg,
            icon:'none',
          });
          return
        }
        let data = {
          old_password:this.userInfo.mobile,
          new_password: this.passwordForm.pwd,
        };
        this.$http({
          url:'/api/users/change_password/',
          method:'post',
          data
        }).then(res=>{
          if(res.statusCode == 200){
            this.$refs.dialog.cancel();
            uni.showToast({
              title: '修改成功',
              icon:'none',
            });
          }
        })
      },
      switchUser() {
        uni.reLaunch({
          url: '/pages/login/login',
        });
      },
      exit() {
        switch (uni.getSystemInfoSync().platform) {
          case 'android':
            plus.runtime.quit();
            break;
          case 'ios':
            plus.ios
              .import('UIApplication')
              .sharedApplication()
              .performSelector('exit');
            break;
        }
      },
      changePwd(e) {
        console.log(e)
        this.$refs.dialog.open();
      },
      cancelAccount() {
        uni.makePhoneCall({
          phoneNumber:'13816412014'
        })
      },
      onClick(e) {
        // console.log('执行click事件', e.data)
        // uni.showToast({
        //   title: '点击反馈'
        // });
      },
    }
  }
</script>

<style lang="scss" scoped>
  .page {
    margin-top: 10rpx;
  }

  .pop {
    .form {
      padding: 40rpx 60rpx;
    }
  }

  .button {
    display: flex;
    justify-content: center;
    align-items: center;
    padding-bottom: 40rpx;

    .left-button {
      margin: 0;
      margin-right: 16rpx;
      width: 160rpx;
    }

    .right-button {
      margin: 0;
      margin-left: 16rpx;
      width: 160rpx;
    }
  }

  .btnbox {
    margin-top: 20rpx;
    background-color: #fff;
    height: 94rpx;
    line-height: 94rpx;
    text-align: center;
    font-size: 28rpx;
    color: #000000D9;
    box-shadow: 0px 2rpx 4rpx 2rpx rgba(223, 223, 223, 1);
    margin-left: -16rpx;
    margin-right: -16rpx;
  }

  .btnmt {
    margin-top: 50rpx;
  }
  ::v-deep .uni-list-item__content {
    justify-content: center;
    padding: 20rpx;
  }
</style>
