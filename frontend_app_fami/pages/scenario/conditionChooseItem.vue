<template>
<view>
  <u-page-title>
    <view>
      <u-goback :titleText="title" :showGoBack="buttonText == '修改'?'false':'true'" />
    </view>
  </u-page-title>

  <u-page-content>
    <uni-forms ref="form" label-position="top" label-width="300rpx" style="flex:1" :model="formData" :rules="rules">
      <view class="float" v-if="condition_info.type != 'select'">
        <uni-forms-item :label="title + '条件:'" name="condition">
          <uni-data-select v-model="formData.condition" :localdata="objToArr(condition_info.conditions)" placeholder="请选择条件"></uni-data-select>
        </uni-forms-item>
        <uni-forms-item :label="title  + (this.query.data_specs?`(${this.query.data_specs.unit})`:'')" name="numb">

          <uni-easyinput v-if="!is_slide" v-model="formData.numb" type="number" placeholder="请输入数值" />

          <view v-else class="slider-wraper">
            <pp-slider :min="query.data_specs.min" :max="query.data_specs.max" :vertical="false" :show-value="true" :value="formData.numb || 0" :block-size="20" :disabled="false" @changing="changing" />
          </view>

        </uni-forms-item>
      </view>
      <view class="select" v-if="condition_info.type == 'select'">
        <uni-forms-item :label="title " name="condition" v-show="false">
          <uni-data-select v-model="formData.condition" :localdata="objToArr(condition_info.conditions)" placeholder="请选择"></uni-data-select>
        </uni-forms-item>
        <uni-forms-item :label="title" name="numb">
          <uni-data-select v-model="formData.numb" :localdata="objToArr(condition_info.choices)" placeholder="请选择"></uni-data-select>
        </uni-forms-item>
      </view>
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
    this.query = obj
    console.log(obj)
    this.key = obj.key
    this.title = obj.name
    this.is_slide = obj.condition_info.is_slide
    this.condition_info = obj.condition_info
    if (this.condition_info.type == 'select') {
      this.formData.condition = '=='
      this.rules.numb.rules[0].errorMessage = '请选择'
    } else {
      this.formData.condition = ''
      this.rules.numb.rules[0].errorMessage = '请输入'
    }

    if (query.type) {
      this.buttonText = '修改'
      let scenarioModel = uni.getStorageSync('scenarioModel')
      let device = scenarioModel.cfg_info.conditions.find(item => item.c_type == 'device' && item.key == obj.key)
      this.$set(this.formData, 'condition', device.condition)
      this.$set(this.formData, 'numb', device.numb)
    }
    if (query.isEditMode) {
      this.isEditMode = query.isEditMode
    }

  },
  data() {
    return {
      condition_info: {},
      is_slide: false,
      isEditMode: '',
      buttonText: '下一步',
      key: '',
      title: '',
      formData: {
        condition: '',
        numb: ''
      },
      rules: {
        condition: {
          rules: [{
            required: true,
            errorMessage: '请选择条件',
          }]
        },
        numb: {
          rules: [{
            required: true,
            errorMessage: '必选项',
          }]
        },
      }
    }
  },
  methods: {
    changing(val) {
      this.formData.numb = val
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
        const scenarioModel = uni.getStorageSync('scenarioModel');
        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        let item = scenarioData.cfg_info.conditions.find(item => item.key == this.key && item.c_type == 'device')
        // 找到条件列表下设备 属性是否存在, 存在则修改, 不存在则添加
        console.log(uni.getStorageSync('properties').id)
        if (item) {
          item.condition = this.formData.condition
          item.numb = this.formData.numb
          if (this.query.condition_info.type == 'select') {
            item.numb_name = this.objToArr(this.query.condition_info.choices).find(item => item.value == res.numb).text
          }
        } else {
          let obj = {
            c_type: "device",
            device_id: uni.getStorageSync('properties').id,
            device_name: uni.getStorageSync('properties').title,
            device_logo: uni.getStorageSync('properties').logo,
            key: this.key,
            key_name: this.query.name,
            condition: res.condition,
            numb: res.numb,
            type: this.query.condition_info.type
          }
          if (this.query.condition_info.type == 'select') {
            obj.numb_name = this.objToArr(this.query.condition_info.choices).find(item => item.value == res.numb).text
          }
          scenarioData.cfg_info.conditions.push(obj)
        }
        uni.setStorageSync('scenarioModel', scenarioData);

        if (this.buttonText == '修改' || this.isEditMode) {
          uni.navigateTo({
            url: `/pages/scenario/details/details?type=editMode`
          })
        } else {
          uni.navigateTo({
            // url: `/pages/scenario/selectEquipment`
            url: `/pages/scenario/details/details?type=editMode`
          })
        }
      }).catch(err => {
        console.log(err)
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
