<template>
<view>
  <u-page-title>
    <view>
      <u-goback :titleText="title" />
    </view>
  </u-page-title>

  <u-page-content>
    <view class="listBox">
      <view @click="navigateTo(item)" class="attributeItem" v-for=" item in services" :key="item.name">
        <view :style="key == item.key ? 'font-weight: 600' : '' "> {{item.name}} </view>
        <uni-icons style="margin-left: 30rpx;" type="right" size="18"></uni-icons>
      </view>
    </view>
  </u-page-content>
</view>
</template>

<script>
export default {
  onLoad(query) {
    this.services = uni.getStorageSync('services').services
    this.title = uni.getStorageSync('services').title + '动作'
    if (query.type && query.key) {
      this.actionIndex = query.actionIndex
      this.key = query.key
      this.type = query.type
      let item = this.services.find(i => i.key == query.key)
      if (item.input_data) {
        this.navigateTo(item)
      } else {
        this.secondaryMode = 'secondaryMode'
      }

    }
  },
  data() {
    return {
      title: '',
      services: [],
      type: '',
      key: '',
      secondaryMode: '',
      actionIndex: ''
    }
  },
  methods: {
    navigateTo(data) {
      // 分为两类 input_data 和 直接动作

      if (data.input_data) {
        if (this.secondaryMode == 'secondaryMode') {
          uni.navigateTo({
            url: `/pages/scenario/actionItem?item=${JSON.stringify(data)}&actionIndex=${this.actionIndex}`
          })
        } else {
          uni.navigateTo({
            url: `/pages/scenario/actionItem?item=${JSON.stringify(data)}&type=${this.type}&actionIndex=${this.actionIndex}`
          })
        }
      } else {
        const scenarioModel = uni.getStorageSync('scenarioModel');
        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        let item = scenarioData.scene_devices_data.find(device => device.action_msg.key == data.key)
        if (this.secondaryMode == 'secondaryMode') {
          let obj = {
            device_id: uni.getStorageSync('services').id,
            device_name: uni.getStorageSync('services').title,
            device_log: uni.getStorageSync('services').log,
            action_msg: {
              key: data.key,
              name: data.name
            }
          }
          scenarioData.scene_devices_data[this.actionIndex] = obj
          uni.setStorageSync('scenarioModel', scenarioData);
          uni.navigateTo({
            url: `/pages/scenario/details/details?type=editMode&actionIndex=${this.actionIndex}`
          })

        } else {
          // if (item) {
            // item.device_id = uni.getStorageSync('services').id
            // item.device_name = uni.getStorageSync('services').title
            // item.device_log = uni.getStorageSync('services').log
          // } else {
            let obj = {
              device_id: uni.getStorageSync('services').id,
              device_name: uni.getStorageSync('services').title,
              device_log: uni.getStorageSync('services').log,
              action_msg: {
                key: data.key,
                name: data.name
              }
            }
            scenarioData.scene_devices_data.push(obj)
          // }
          uni.setStorageSync('scenarioModel', scenarioData);
          uni.navigateTo({
            url: `/pages/scenario/details/details?type=editMode`
          })
        }

      }
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

.attributeItem {
  display: flex;
  justify-content: space-between;
  padding: 16rpx;
}
</style>
