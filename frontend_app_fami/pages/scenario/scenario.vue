<template>
<view>
  <u-page-title>
    <view class="title-left">
      <view class="select" v-if="!isEditMode">
        <uni-data-select v-model="orgValue" :localdata="orgList" :clear="false" @change="orgChange"></uni-data-select>
      </view>
      <!-- 确认 -->
      <text class="iconfont icon-wancheng" v-if="isEditMode" @click="confirmEditor"></text>
    </view>
    <view class="title-center">
      <text v-if="isEditMode">已选择{{selectedList.length}}项</text>
    </view>
    <view class="right">
      <!-- 添加 -->
      <uni-icons type="plus" size="26" class="icons" v-if="!isEditMode" @click="newScene" />
      <!-- 全选 -->
      <text class="iconfont icon-quanxuan" :style="selectedList.length == dataList.length ? 'color: #22be49' : '' " v-if="isEditMode" @click="selection"></text>
    </view>
  </u-page-title>

  <u-page-content>
    <view @click="newScene"  class="noData" v-if="dataList.length === 0">
      <view>该组织下暂无场景</view>
      <view>点击创建新的场景</view>
    </view>
    <view v-else class="page-content">
      <view class="list" :style="isEditMode ? 'margin-bottom: 170rpx;' : 'margin-bottom: 20rpx;'">
        <u-list-item v-for="(item, index) in dataList" :key="item.id" @longtap.native="onLongPress(item,index)">
          <view class="item-left" @click="toDetail(item)">
            <view class="bold-text">{{item.name}}</view>
            <!-- <text class="no-bold-text">{{item.description}}</text> -->
            <view style="padding-top: 20rpx; display: flex; align-items: center;">
              <image class="tImage" :src="tImageMap(item)" mode="aspectFit" />
              <uni-icons style="margin: 0rpx 10rpx;" type="right" size="18"></uni-icons>
              <image v-for="d in item.scene_devices" :key="d.id" class="tImage" :src="dImageMap(d.device)" mode="aspectFit" />
            </view>
          </view>
          <view class="item-right">
            <u-is-select v-if="isEditMode" :select="isSelect(item)" @click.native="clickOnRadio(item,index)" />
            <switch v-else :checked="item.is_active" @change.stop="switchChange(item,index)" style="transform:scale(0.7)" />
          </view>
        </u-list-item>
      </view>
      <view class="b-button-box" v-if="isEditMode">
        <view class="b-button-item" v-if="(selectedList.length == 1)" @click="rename">
          <text class="iconfont icon-zhongmingming"></text>
          重命名
        </view>
        <view class="b-button-item" v-if="selectedList.length" @click="batchDelete">
          <text class="iconfont icon-shanchu" @click="batchDelete"></text>
          删除
        </view>
      </view>
    </view>
  </u-page-content>

  <!-- edit -->
  <!-- 新弹出框 -->
  <u-dialog ref="popup" @confirm="formChange">
    <uni-forms ref="form" :rules="form" label-width="140rpx" label-align="right">
      <uni-forms-item label="名称：" name="name">
        <uni-easyinput v-model="form.name" placeholder="请输入" />
      </uni-forms-item>
    </uni-forms>
  </u-dialog>
</view>
</template>

<script>
export default {
  onShow() {

  },
  data() {
    return {
      orgValue: '',
      orgList:[],
      isEditMode: false, // 是否编辑模式
      selectedList: [], // 已选中
      dataList: [],
      form: {
        name: ""
      },
      orgs: [],
      org: {
        city: {}
      }
    };
  },
  onLoad() {
    this.org =  uni.getStorageSync('org') || {}
  },
  onShow() {
    this.orgValue = uni.getStorageSync('org').id
    this.getList()
    this.getOrg()
    this.getConditions()
  },
  methods: {
    getOrg() {
      this.$http({
        url: '/api/orgs/get_all/',
        method: 'get',
      }).then(res => {
        // console.log(res)
        if (res.statusCode == 200) {
          this.orgList = res.data.map(item => {
            return {
              value: item.id,
              text: item.name
            }
          });
          this.orgs = res.data
          let org = this.orgs.find(item => this.orgValue == item.id)
          this.org = org
          uni.setStorageSync('org', org);
        }
      })
    },
    orgChange(data) {
      console.log(data)
      this.orgValue = data;
      let org = this.orgs.find(item => data == item.id)
      this.org = org
      uni.setStorageSync('org', org);
      this.getList()
    },
    // 条件图片映射
    tImageMap(item) {
      let obj = item.cfg_info.conditions[0]
      if (obj.c_type == 'device') {
        return obj.device_logo
      } else if (obj.c_type == 'timing') {
        return 'https://i.52112.com/icon/jpg/256/20190820/54343/2433537.jpg'
      } else if (obj.c_type == 'weather') {
        let map = {
          'temperature': '/static/equipment/wendu.png',
          'humidity': '/static/equipment/shidu.png',
          'pm2.5': '/static/equipment/pm.png'
        }
        return map[obj.key]
      } else {
        return '/static/dbs.png'
      }
    },

    // 条件图片映射
    dImageMap(item) {
      if (item.logo) {
        return item.logo
      } else {
        return '/static/dbs.png'
      }
    },

    // 全局获取数据存储
    getConditions() {
      this.$http({
        url: '/api/const_data?data_type=scene_conditions',
        method: 'get',
        data: {}
      }).then(res => {
        if (res.statusCode == 200) {
          uni.setStorageSync('scene_conditions', res.data);
        }
      })
    },
    // 新增场景
    newScene() {
      let org = uni.getStorageSync('org')
      let scenarioData = {
        'name': '场景',
        'description': '',
        'is_active': true,
        'org_id': org.id,
        'cfg_info': {
          "effect_time": {
            end_time: "23:59:00",
            exec_date: "",
            exec_days: [],
            start_time: "00:00:00",
            timing_type: "everyday"
          }, // 生效时间
          "relation": "and", // or "or" 条件逻辑（如果同事满足时, 如果任一满足时）
          "conditions": [] // 条件
        },
        'scene_devices_data': [], // 设备动作
      }
      uni.setStorageSync('scenarioModel', scenarioData)
      this.navigateTo('/pages/scenario/details/details?type=editMode')
    },
    // 重命名
    rename() {
      let item = this.selectedList[0]
      item.org_id = item.org.id
      item.scene_devices_data = item.scene_devices.map(i => {
        return {
          "device_id": i.device.id,
          "device_name": i.device.name,
          "action_msg": i.action_msg
        }
      })
      uni.setStorageSync('scenarioModel', item)
      this.form.name = uni.getStorageSync('scenarioModel').name
      this.$refs.popup.open();
    },
    // 获取场景列表
    getList() {
      this.$http({
        url: '/api/scenes/',
        data: {
          org: this.orgValue
        },
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          this.dataList = res.data.results
        } else {
          uni.showToast({
            title: res.data.msg,
            icon: 'none',
          });
        }
      })
    },
    // 跳转
    navigateTo(url) {
      uni.navigateTo({
        url
      })
    },
    // 跳转详情
    toDetail(item) {
      if (this.isEditMode) return
      item.org_id = item.org.id
      item.scene_devices_data = item.scene_devices.map(i => {
        return {
          "device_id": i.device.id,
          "device_name": i.device.name,
          "action_msg": i.action_msg
        }
      })

      uni.setStorageSync('scenarioModel', item)
      uni.navigateTo({
        url: `/pages/scenario/details/details`
      })
    },
    // 编辑提交
    formChange() {
      this.form.name
      let scenarioData = uni.getStorageSync('scenarioModel');
      scenarioData.name = this.form.name
      this.$http({
        url: `/api/scenes/${scenarioData.id}/`,
        data: scenarioData,
        method: 'patch',
      }).then(res => {
        if (res.statusCode == 200) {
          this.getList()
          this.isEditMode = false
        } else {
          uni.showToast({
            title: res.data.msg,
            icon: 'none',
          });
        }
      })

    },
    // 批量删除
    batchDelete() {
      let id_list = this.selectedList.map(item => item.id)
      this.$http({
        url: `/api/scenes/batch_delete/`,
        data: {
          id_list
        },
        method: 'post',
      }).then(res => {
        if (res.statusCode == 200) {
          this.getList()
          this.isEditMode = false
          if (res.data.msg) {
            uni.showToast({
              title: res.data.msg,
              icon: 'success',
            });
          }
        } else {
          uni.showToast({
            title: res.data.msg,
            icon: 'none',
          });
        }
      })
    },
    // 确认编辑
    confirmEditor() {
      this.isEditMode = false
      this.selectedList = []
    },
    // 长按
    onLongPress(item) {
      this.selectedList = []
      this.selectedList.push(item)
      this.isEditMode = true
    },
    // 判断是否已选中
    isSelect(data) {
      let select = this.selectedList.find(item => item.id == data.id)
      return !!select
    },
    // 全选/反选
    selection() {
      if (this.selectedList.length == this.dataList.length) {
        this.selectedList = []
      } else {
        this.selectedList = JSON.parse(JSON.stringify(this.dataList))
      }
    },
    // 单选
    clickOnRadio(data) {
      let select = this.selectedList.find(item => item.id == data.id)
      if (select) {
        // 不能用index直接删, selectedList用户操作选取,乱序
        this.selectedList.forEach((item, i) => {
          if (select.id == item.id) {
            this.selectedList.splice(i, 1);
          }
        })
      } else {
        this.selectedList.push(data);
      }
    },
    // 场景开关Change
    switchChange(item, index) {
      this.$http({
        url: `/api/scenes/${item.id}/switch_status/`,
        data: {},
        method: 'post',
      }).then(res => {
        if (res.statusCode == 200) {
          this.getList()
          if (res.data.msg) {
            uni.showToast({
              title: res.data.msg,
              icon: res.data.result,
            });
          }
        } else {
          uni.showToast({
            title: res.data.msg,
            icon: 'none',
          });
        }
      })
    }

  }
};
</script>

<style lang="scss" scoped>
.select {
  width: 260rpx;

  ::v-deep .uni-select__input-text {
    font-size: $textInputSize;
    color: $mainTitle;
  }

  ::v-deep .uni-select {
    border: none !important;
  }

}
.title-center {
  flex: 1;
  text-align: center;
  font-size: 34rpx;
  color: $mainTitle;
}

.item-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .bold-text {
    font-size: $contentWordsSize;
    font-weight: 400;
    color: $mainTitle;
    margin: 20rpx 0;
    font-weight: 600;

    width: 100%;
    box-sizing: border-box;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .no-bold-text {
    padding-top: 28rpx;
    font-size: $contentWordsSize;
    font-weight: 300;
  }
}

.item-right {}

.page-content {
  display: flex;
  flex-direction: column;
  height: 100%;

  .list {
    flex: 1;
    overflow-y: auto;
  }

  .b-button-box {
    height: 150rpx;
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: space-evenly;
    background-color: $backgroundColor;
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;

    .b-button-item {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
  }
}

.pop {
  ::v-deep .uni-popup__wrapper {
    border-radius: 12rpx;
    overflow: hidden;
  }

  .form {
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

.icons {
  color: $mainColor !important;
}

.tImage {
  width: 50rpx;
  height: 50rpx;
  border-radius: 50%;
  margin-right: 10rpx;
}
.noData{
  position: absolute;
  top: 50%;
  left: 50%;
  text-align: center;
  color: #4da7fc;
  transform: translate(-50%, -50%);
  text-decoration:underline
}
</style>
