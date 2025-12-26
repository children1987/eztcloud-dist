<template>
  <!-- 弹出框 -->
  <uni-popup ref="popup" type="dialog" background-color="#ffffff" class="pop">
    <view class="popbody">
      <slot ></slot>
    </view>
    <slot name='foot'>
      <view class="button">
        <button v-if="showCancelButton" size="mini" class="left-button" @click="cancel">{{cancelButtonText}}</button>
        <button v-if="showConfirmButton" size="mini" type="primary" class="right-button" @click="confirm">{{confirmButtonText}}</button>
      </view>
    </slot>
  </uni-popup>
</template>

<script>
export default {
  props:{
    showCancelButton:{
      type: Boolean,
      default: true
    },
    showConfirmButton:{
      type: Boolean,
      default: true
    },
    cancelButtonText:{
      type: String,
      default: '取消'
    },
    confirmButtonText:{
      type: String,
      default: '确认'
    },
  },
  methods:{
    //打开
    open(){
      this.$refs.popup.open('center');
      this.$emit('open')
    },
    // 取消/关闭
    cancel() {
      this.$refs.popup.close();
      this.$emit('cancel')
    },
    //确认
    confirm(){
      this.$refs.popup.close();
      this.$emit('confirm')
    }
  }
}
</script>

<style lang="scss" scoped>
.pop {
  ::v-deep .uni-popup__wrapper {
    border-radius: 12rpx;
    overflow: hidden;
  }

  .popbody {
    padding: 30rpx;
    width: 620rpx;
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
}
</style>
