<template>
  <view>
    <u-page-title>
      <view class="select">
        <u-goback />
      </view>
    </u-page-title>

    <u-page-content>
      <view class="unit-list">
        <text class="unit-title">生产一区</text>
        <text class="unit-number">设备数:5</text>
        <checkbox-group @change="radioChange" @click="openPopup">
          <label>
            <checkbox value="radio1" color="#0fb42b" />
          </label>
        </checkbox-group>
      </view>
      <uni-popup ref="popup" type="dialog" background-color="#ffffff">
        <view class="form">
          <uni-forms ref="form">
            <uni-forms-item label="单元名称:" name="oldPass" labelWidth="72px" class="form-item">
              <uni-easyinput type="text" placeholder="请输入" />
            </uni-forms-item>
          </uni-forms>
        </view>
        <view class="button">
          <button size="mini" class="left-button" @click="passwordCancel">取消</button>
          <button size="mini" class="right-button" @click="passwordChange">确认</button>
        </view>
      </uni-popup>
      <view class="bottom-edit">
        <view class="edit col-center">
          <text>重命名</text>
          <uni-icons type="more" size="20"></uni-icons>
        </view>
        <view class="delete col-center">
          <text>删除</text>
          <uni-icons type="trash" size="20"></uni-icons>
        </view>
      </view>
    </u-page-content>
  </view>
</template>

<script>
export default {
  data() {
    return {};
  },
  methods: {
    radioChange(e) {
      // console.log(e.detail.value);
    },
    openPopup() {
      this.$refs.popup.open("center");
    },
  },
};
</script>

<style lang="scss">
.select {
  width: 200rpx;
}
.unit-list {
  height: 140rpx;
  background: #ffffff;
  box-shadow: 0rpx 2rpx 4rpx 2rpx #dfdfdf;
  border-radius: 16rpx 16rpx 16rpx 16rpx;
  display: flex;
  align-items: center;
  justify-content: space-around;

  .unit-title {
    font-size: 32rpx;
    font-family: Source Han Sans CN-Light, Source Han Sans CN;
    font-weight: 300;
    color: rgba(0, 0, 0, 0.8);
  }
  .unit-number {
    font-size: 28rpx;
    font-family: Source Han Sans CN-Light, Source Han Sans CN;
    font-weight: 300;
    color: rgba(0, 0, 0, 0.8);
  }
}
.bottom-edit {
  width: calc(100% - 32rpx);
  background: #ffffff;
  position: fixed;
  bottom: var(--status-bar-height);
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 30rpx;
  padding-bottom: 30rpx;
  .col-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
	font-size: 28rpx;
	font-family: Source Han Sans CN-Light, Source Han Sans CN;
	font-weight: 300;
	color: rgba(0,0,0,0.8);
  }
  .edit {
    padding-right: 24rpx;
  }
  .delete {
    padding-left: 24rpx;
  }
}
.button {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 68rpx;
  .left-button {
    margin: 0;
    margin-right: 16rpx;
    width: 160rpx;
    font-weight: 400;
    color: rgba(0, 0, 0, 0.85);
  }
  .right-button {
    margin: 0;
    margin-left: 16rpx;
    width: 160rpx;
    background: linear-gradient(180deg, #48a9fd 0%, #5785fe 100%);
    font-weight: 400;
    color: #ffffff;
  }
}
.form {
  .form-item {
    padding-top: 60rpx;
  }
}
</style>
