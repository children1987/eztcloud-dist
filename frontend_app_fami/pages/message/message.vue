<template>
  <view>
    <u-page-title>
      <view class="select">
        <u-goback />
      </view>
    </u-page-title>

    <u-page-content>
      <view class="message-top">
        <view class="icon-area">
          <view class="icon-number">
            <view class="badge badgeOne">0</view>
            <view class="icon-text">
              故障
            </view>
          </view>
          <view class="icon-number">
            <view class="badge badgeTwo">{{dataList.length}}</view>
            <view class="icon-text">
              告警
            </view>
          </view>
          <view class="icon-number">
            <view class="badge badgeThree">0</view>
            <view class="icon-text">
              信息
            </view>
          </view>
        </view>
      </view>
      <view class="message-main">
        <view class="top-title">
          今天
        </view>
        <view class="main-card" v-for="item in dataList" :key="item.id">
          <view class="card-top">
            <template v-if="item.event_type=='warning'">
              <text class="warning-icon"></text>
              <text class="title-tips">告警</text>
            </template>
            <template v-else-if="item.event_type=='info'">
              <text class="info-icon"></text>
              <text class="title-tips">信息</text>
            </template>
            <template v-else>
              <text class="error-icon"></text>
              <text class="title-tips">故障</text>
            </template>
            <text class="title-years">{{item.timestamp}}</text>
          </view>
          <view class="card-bottom">
            <text class="title-detail">{{item.device.name}}{{item.content}}</text>
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
      dataList:[],
      pageOptios: {
        page: 1,
        page_size: 10,
      },
      next: false,
    };
  },
  onLoad() {
    this.onSearch(true);
  },
  onReachBottom() {
    if (this.next) {
      this.pageOptios.page++;
      this.onSearch(false);
    }
  },
  methods:{
    onSearch(init = false) {
      if (init) {
        this.pageOptios.page = 1;
      }
      this.$http({
        url: '/api/event_records/',
        data: {
          ...this.pageOptios
        },
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          let list = res.data.results.map(item=>{
            return {
              ...item,
            }
          });
          if (init) {
            this.dataList = list;
          } else {
            if (list && list.length) {
              this.dataList = this.dataList.concat(list);
            }
          }
          if (res.data.next) {
            this.next = true;
          } else {
            this.next = false;
          }
        }
      })
    },
  }
};
</script>

<style lang="scss">
.select {
  width: 200rpx;
}
.message-top {
  height: 204rpx;
  background-color: #fff;
  // margin: 16rpx;
  box-shadow: 0rpx 2rpx 4rpx 2rpx #dfdfdf;
  border-radius: 16rpx 16rpx 16rpx 16rpx;
  .icon-area {
    display: flex;
    height: 100%;
    .icon-number {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      .badge {
        width: 88rpx;
        height: 88rpx;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
      }
      .badgeOne {
        background-image: url("../../static/message/1.png");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 100% 100%;
      }
      .badgeTwo {
        background-image: url("../../static/message/2.png");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 100% 100%;
      }
      .badgeThree {
        background-image: url("../../static/message/3.png");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 100% 100%;
      }
      .icon-text {
        font-size: 32rpx;
        font-weight: 300;
        color: rgba(0, 0, 0, 0.8);
        padding-top: 20rpx;
      }
    }
  }
}
.message-main {
  .top-title {
    font-size: 28rpx;
    font-weight: 400;
    color: #000000;
    padding: 16rpx;
  }
  .main-card {
    // margin-left: 16rpx;
    // margin-right: 16rpx;
    margin-bottom: 16rpx;
    height: 140rpx;
    background: #ffffff;
    box-shadow: 0rpx 2rpx 4rpx 2rpx #dfdfdf;
    border-radius: 16rpx 16rpx 16rpx 16rpx;
    display: flex;
    flex-direction: column;
    justify-content: center;
    .card-top {
      padding-left: 16rpx;
      padding-right: 16rpx;
      .warning-icon {
        width: 24rpx;
        height: 24rpx;
        background: #f6a561;
        border-radius: 50%;
        display: inline-block;
      }
      .info-icon {
        width: 24rpx;
        height: 24rpx;
        background: #22ADFFFF;
        border-radius: 50%;
        display: inline-block;
      }
      .error-icon {
        width: 24rpx;
        height: 24rpx;
        background: #FA4611FF;
        border-radius: 50%;
        display: inline-block;
      }
      .title-tips {
        font-size: 28rpx;
        font-weight: 400;
        color: rgba(0, 0, 0, 0.8);
        padding-left: 8rpx;
      }
      .title-years {
        font-size: 28rpx;
        font-weight: 300;
        color: rgba(0, 0, 0, 0.8);
        padding-left: 8rpx;
      }
    }
    .card-bottom {
      padding-left: 16rpx;
      padding-right: 16rpx;
      .title-detail {
        font-size: 28rpx;
        font-weight: 300;
        color: rgba(0, 0, 0, 0.8);
      }
    }
  }
}
</style>
