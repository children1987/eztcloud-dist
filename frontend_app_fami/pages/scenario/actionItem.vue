<template>
<view>
  <u-page-title>
    <view>
      <u-goback :titleText="title" :showGoBack="buttonText == '修改'?'false':'true'" />
    </view>
  </u-page-title>

  <u-page-content style="padding-top: 30rpx">
    <uni-forms ref="form" label-position="top" label-width="300rpx" style="flex:1" :model="formData" :rules="rules">
      <uni-forms-item :label="item.name + (item.data_specs&&item.data_specs.unit?`(${item.data_specs.unit})`:'')" :name="item.key" v-for="item in input_data" :key="item.key">
        <view v-if="item.data_type != 'select'">
          <uni-easyinput  v-if="!item.data_specs.is_slide" v-model="formData[item.key]" type="number" :placeholder="'请输入' + item.name" />
          <view v-if="item.data_specs.is_slide" class="slider-wraper">
            <pp-slider :min="item.data_specs.min" :max="item.data_specs.max" :vertical="false" :show-value="true" :value="formData[item.key] || 0" :block-size="20" :disabled="false" @changing="changing($event,item.key)" />
          </view>
        </view>
        <uni-data-select v-else v-model="formData[item.key]" :localdata="objToArr(item.choices)" :placeholder="'请选择' + item.name"></uni-data-select>
      </uni-forms-item>
    </uni-forms>

    <view class="next-button" @click="nextStep">
      {{ buttonText }}
    </view>
  </u-page-content>
</view>
</template>

<script>
export default {
  onLoad(query) {
    let obj = JSON.parse(query.item)
    console.log(obj)
    this.objItem = JSON.parse(JSON.stringify(obj))
    this.title = obj.name
    this.input_data = obj.input_data
    obj.input_data.forEach(item => {
      if (item.data_type == 'int' || item.data_type == 'float') {
        this.$set(
          this.rules,
          item.key, {
            rules: [{
                required: true,
                errorMessage: '请输入',
              },
              {
                validateFunction: function (rule, value, data, callback) {
                  if (value < item.data_specs.min || value > item.data_specs.max) {
                    return callback(`超出取值范围,取值范围是${item.data_specs.min}~${item.data_specs.max}`)
                  }
                  return true
                }
              }
            ]
          }
        )
      }else{
        this.$set(
          this.rules,
          item.key, {
            rules: [{
                required: true,
                errorMessage: item.data_type != 'select' ? '请输入' : '请选择',
              }
            ]
          }
        )
      }

    })
    if (query.type) {
      this.buttonText = '修改'
      let scenarioModel = uni.getStorageSync('scenarioModel')
      let services = uni.getStorageSync('services')
      let device = {}
      if (query.actionIndex) {
        this.actionIndex = query.actionIndex
        device = scenarioModel.scene_devices_data[this.actionIndex]
      } else {
        device = scenarioModel.scene_devices_data.find(item => {
          return item.device_id == services.id && item.action_msg.key == obj.key
        })
      }
      device.action_msg.input_data.forEach(item => {
        this.$set(this.formData, item.key, item.value)
      })
    }

  },
  data() {
    return {
      buttonText: '下一步',
      title: '',
      input_data: [],
      formData: {},
      rules: {},
      objItem: null,
      actionIndex: 'null'
    }
  },
  methods: {
    changing(val, key) {
      this.$set(this.formData, key, val)
    },
    // objToArr
    objToArr(obj) {
      let keys = Object.keys(obj)
      let arr = []
      keys.forEach(key => {
        arr.push({
          value: obj[key],
          text: key
        })
      })
      return arr || []
    },
    nextStep() {
      this.$refs.form.validate().then(res => {
        let input_data = this.input_data.map(item => {
          return {
            key: item.key,
            name: item.name,
            value: res[item.key]

          }
        })

        const scenarioModel = uni.getStorageSync('scenarioModel');
        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        let item = scenarioData.scene_devices_data.find(device => device.action_msg.key == this.objItem.key)
        if (this.actionIndex !== 'null') {
          let obj = {
            device_id: uni.getStorageSync('services').id,
            device_name: uni.getStorageSync('services').title,
            device_log: uni.getStorageSync('services').log,
            action_msg: {
              key: this.objItem.key,
              name: this.objItem.name,
              input_data
            }
          }
          scenarioData.scene_devices_data[this.actionIndex] = obj
        } else {
          // if (item) {
          // item.device_id = uni.getStorageSync('services').id
          // item.device_name = uni.getStorageSync('services').title
          // item.device_log = uni.getStorageSync('services').log
          // item.action_msg = {
          //   key: this.objItem.key,
          //   name: this.objItem.name,
          //   input_data
          // }
          // } else {
          let obj = {
            device_id: uni.getStorageSync('services').id,
            device_name: uni.getStorageSync('services').title,
            device_log: uni.getStorageSync('services').log,
            action_msg: {
              key: this.objItem.key,
              name: this.objItem.name,
              input_data
            }
          }
          scenarioData.scene_devices_data.push(obj)
          // }
        }

        uni.setStorageSync('scenarioModel', scenarioData);
        console.log(uni.getStorageSync('scenarioModel'))
        uni.navigateTo({
          url: `/pages/scenario/details/details?type=editMode`
        })

      }).catch(err => {

      })
    },
  },
};
</script>

<style lang="scss" scoped>
::v-deep .uni-select {
  background-color: #fff !important;
}

::v-deep .uni-forms-item {
  margin-bottom: 30rpx;
}

.next-button {
  @include button;
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 20rpx;
}
</style>
