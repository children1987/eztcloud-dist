<template>
<view class="page">
  <u-page-title>
    <u-goback />
  </u-page-title>
  <u-page-content>
    <web-view src="/static/user_agreement.html"/>
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
