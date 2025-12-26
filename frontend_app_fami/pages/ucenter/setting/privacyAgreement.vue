<template>
<view class="page">
  <u-page-title>
    <u-goback />
  </u-page-title>
  <u-page-content>
    <web-view src="/static/privacy_policy.html"/>
  </u-page-content>
  
</view>
</template>

<script>
export default {
  data() {
    return {
      extraIcon: {
        color: '#4cd964',
        size: '22',
        type: 'gear-filled'
      }
    }
  },
  onLoad() {

  },
  methods: {
    getData(){
      this.$http({
          url: '/api-token-auth/',
          method: 'get',
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
          }
        })
    }
  }
}
</script>

<style lang="scss" scoped>
  .page{
    margin-top:10rpx;
    text-align: center;
    font-size: 32rpx;
    line-height: 1.6;
    ::v-deep .slotContent{
      background-color: #fff;
      text-align: left;
    }
    .tc{
      text-align: center;
    }
  }
</style>
