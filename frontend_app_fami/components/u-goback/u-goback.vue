<template>
  <!-- 返回加每页title -->
<view class="goback">
  <uni-icons v-if="showGoBack == 'true'" type="left" size="20"  @click="goBack"></uni-icons>
  <text>{{title}}</text>
</view>
</template>

<script>
import pagesJson from '@/pages.json'
export default{
  props:{
    titleText:{
      type: String,
      default: ''
    },
    showGoBack:{
      type: String,
      default: 'true'
    },
  },
  data(){
    return{
      title:''
    }
  },
  created(){
    let pages = getCurrentPages()
    let page = pages[pages.length - 1]
    this.title = pagesJson.pages.find(item=>item.path == page.route).style.navigationBarTitleText
    if(this.titleText){
      this.title = this.titleText
    }
  },
  methods:{
    goBack(){
      uni.navigateBack()
    }
  }
}

</script>

<style lang="scss" scoped>
.goback {
  display: flex;
  align-items: center;
  text{
    font-size: 28rpx;
    color: #000;
    margin-left: 10rpx;
  }
}
</style>
