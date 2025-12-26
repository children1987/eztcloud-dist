<template>
<view>
  <u-page-title>
    <view>
      <u-goback :titleText="title" />
    </view>
  </u-page-title>

  <u-page-content>
    <view class="listBox">
      <view @click="navigateTo(item)" class="attributeItem" v-for=" item in properties" :key="item.name">
        <view>{{item.name}}</view>
        <uni-icons style="margin-left: 30rpx;" type="right" size="18"></uni-icons>
      </view>
    </view>
  </u-page-content>
</view>
</template>

<script>
export default {
  onLoad(query) {
    this.properties = uni.getStorageSync('properties').properties
    this.title = uni.getStorageSync('properties').title
    if(query.type&&query.key){
      this.type = query.type
      let item = this.properties.find(i=> i.key == query.key)
      this.navigateTo(item)
    }
    if(query.isEditMode){
      this.isEditMode = query.isEditMode
    }
    
  },
  data() {
    return {
      title:'',
      properties:[],
      type:'',
      isEditMode:''
    }
  },
  methods: {
    navigateTo(item){
      uni.navigateTo({
        url: `/pages/scenario/conditionChooseItem?item=${JSON.stringify(item)}&type=${this.type}${this.isEditMode?'&isEditMode=isEditMode':''}`
      })
    }
  },
};
</script>

<style lang="scss" scoped>
.listBox {
  background-color: $backgroundColor;
  border-radius: 30rpx;
  padding: 30rpx;
  box-shadow: 0px 2px 2px 1px $shadow;
  margin-top: 30rpx;
  color: #000;
}
  .attributeItem{
    display: flex;
    justify-content: space-between;
    padding: 16rpx;
  }
</style>
