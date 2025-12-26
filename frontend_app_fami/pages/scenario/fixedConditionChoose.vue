<template>
<view>
  <u-page-title>
    <view>
      <u-goback :titleText="title" />
    </view>
  </u-page-title>

  <u-page-content>
    <uni-forms ref="form" label-position="top" label-width="300rpx" style="flex:1" :model="formData" :rules="rules">
      <uni-forms-item :label="title + '条件:'" name="condition">
        <uni-data-select v-model="formData.condition" :localdata="conditions" placeholder="请选择条件"></uni-data-select>
      </uni-forms-item>
      <uni-forms-item :label="title + '数值'+ unit[title] + ':' " name="numb">
        <uni-easyinput v-model="formData.numb" type="number" placeholder="请输入数值" />
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
    this.title = query.type
    this.conditions = uni.getStorageSync('scene_conditions');
    console.log(this.conditions)
    if (query.editMode) {
      this.buttonText = '修改'
      let scenarioModel = uni.getStorageSync('scenarioModel')
      let obj = scenarioModel.cfg_info.conditions.find(item => item.c_type == 'weather' && item.key == this.keyMap[query.type])
      console.log(obj)
      this.$set(this.formData, 'condition', obj.condition)
      this.$set(this.formData, 'numb', obj.numb)
    }
    if (query.isEditMode) {
      this.isEditMode = query.isEditMode
    }

  },
  data() {
    return {
      buttonText: '下一步',
      keyMap: {
        '温度': 'temperature',
        '湿度': 'humidity',
        'PM2.5': 'pm2.5',
      },
      title: '',
      unit: {
        '温度': '(℃)',
        '湿度': '(%RH)',
        'PM2.5': '(um)',
      },
      conditions: [],
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
            errorMessage: '请输入数值',
          }]
        },
      }
    }
  },
  methods: {
    nextStep() {
      this.$refs.form.validate().then(res => {
        const scenarioModel = uni.getStorageSync('scenarioModel');

        let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
        // 改变全局场景对应参数
        let item = scenarioData.cfg_info.conditions.find(item => item.key == this.keyMap[this.title])
        if (item) {
          item.condition = this.formData.condition
          item.numb = this.formData.numb
        } else {
          scenarioData.cfg_info.conditions.push({
            c_type: "weather", // 室外天气
            key: this.keyMap[this.title],
            condition: this.formData.condition,
            numb: this.formData.numb,
          })
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
