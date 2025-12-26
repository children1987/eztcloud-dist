<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
  methods:{
    
  }
}
</script>

<style lang="scss">
@import url('./static/icon_font/iconfont.css');
/*每个页面公共css */
page {
  // background: url('./static/global/appbg.jpg') 100% 100% no-repeat fixed;
  font-size: $contentWordsSize;
  color: $contentWords;
  background-color: $pageBackground;
  font-family: PingFang, YaHei, Arial, Tahoma;
  .uni-icons{
    color: $contentWords !important;
  }
  .iconfont{
    color: #333;
    font-size: 50rpx;
    font-weight: 500;
  }
}
</style>
