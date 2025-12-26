<template>
<view class="page">
  <uni-list>
    <uni-list-item showArrow to="/pages/ucenter/personalCenter/personalCenter" @click="onClick" thumb-size="lg">
      <template v-slot:header>
        <view class="iconbox">
          <view class="avatar">
            <image style="width: 112rpx;height: 112rpx;" :src="userInfo.avatar?userInfo.avatar:src.t1" />
          </view>
          <!-- <view class="avatar" v-else>
            {{userInfo.nickname}}
          </view> -->
          <view class="userInfo">
            <view class="nickname">{{userInfo.nickname}}</view>
            <view class="default_org">{{userInfo.default_org.name}}</view>
          </view>
        </view>
      </template>
    </uni-list-item>
  </uni-list>

  <view class="content">
    <uni-list>
      <uni-list-item :border="false" showArrow to="/pages/ucenter/org/list" @click="onClick" title="组织管理">
        <template v-slot:header>
          <view class="iconbox">
            <text class="iconfont icon-zuzhijigou" style="font-size: 48rpx"></text>
          </view>
        </template>
      </uni-list-item>
      <uni-list-item :border="false" title="单元管理" :to="`/pages/ucenter/unit/list`" @click="onClick" showArrow>
        <template v-slot:header>
          <view class="iconbox">
            <text class="iconfont icon-icon-p_gongchangdanyuan" style="font-size: 50rpx"></text>
          </view>
        </template>
      </uni-list-item>
      <uni-list-item :border="false" title="设备管理" :to="`/pages/ucenter/device/list`" @click="onClick" showArrow>
        <template v-slot:header>
          <view class="iconbox">
            <text class="iconfont icon-ziyuanxhdpi" style="font-size: 44rpx"></text>
          </view>
        </template>
      </uni-list-item>
      <uni-list-item :border="false" title="用户管理" :to="`/pages/ucenter/user/list`" @click="onClick" showArrow>
        <template v-slot:header>
          <view class="iconbox">
            <text class="iconfont icon-yonghu" style="font-size: 50rpx"></text>
          </view>
        </template>
      </uni-list-item>
      <uni-list-item :border="false" title="消息中心" :to="`/pages/message/message`" @click="onClick" showArrow>
        <template v-slot:header>
          <view class="iconbox">
            <text class="iconfont icon-xiaoxi" style="font-size: 50rpx"></text>
          </view>
        </template>
      </uni-list-item>
      <uni-list-item :border="false" title="设置" :to="`./setting/setting`" @click="onClick" showArrow>
        <template v-slot:header>
          <view class="iconbox">
            <text class="iconfont icon-shezhi" style="font-size: 54rpx"></text>
          </view>
        </template>
      </uni-list-item>
    </uni-list>
  </view>
</view>
</template>

<script>
export default {
  data() {
    return {
      src: {
        t1: '/static/user.png'
      },
      userInfo: {

      }
    }
  },
  onLoad() {
    this.getUserInfo();
  },
  methods: {
    getUserInfo() {
      this.userInfo = uni.getStorageSync('userInfo') || {};
      console.log(this.userInfo);
    },
    onClick(e) {
      console.log('执行click事件', e.data)
      uni.showToast({
        title: '点击反馈'
      });
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
.page {
  margin-top: 80rpx;

  ::v-deep .uni-list-item__content {
    justify-content: center;
    padding: 20rpx;
  }

  .content {
    margin: 20rpx;
    border-radius: 20rpx;
    overflow: hidden;
  }

  .iconbox {
    margin-right: 9px;
    display: flex;
    flex-direction: row;
    align-items: center;

    .iconfont {
      color: $mainColor;
    }
  }

  .avatar {
    border-radius: 50%;
    overflow: hidden;
    background-image: linear-gradient(#46ADFC, #5983FE);
    width: 112rpx;
    height: 112rpx;
    line-height: 112rpx;
    font-size: 30rpx;
    text-align: center;
    color: #fff;
  }
}

.userInfo {
  position: relative;
  left: 20rpx;

  .nickname {
    color: #333;
  }

  .default_org {
    margin-top: 10rpx;
    font-size: 24rpx;
  }
}
</style>
