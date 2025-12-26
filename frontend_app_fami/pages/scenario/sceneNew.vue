<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <u-list-item>
      <uni-forms ref="form" label-position="top" style="flex:1" :model="formData" :rules="rules">
        <uni-forms-item label="所属组织:" name="orgName">
          <!-- <text class="code">郑州发电站</text> -->
          <uni-easyinput v-model="formData.orgName" disabled type="text" placeholder="请输入场景说明" />
        </uni-forms-item>
        <uni-forms-item label="场景名称:" name="name">
          <uni-easyinput v-model="formData.name" type="text" placeholder="请输入场景名称" />
        </uni-forms-item>
        <uni-forms-item label="场景说明:" name="instructions">
          <uni-easyinput v-model="formData.instructions" type="text" placeholder="请输入场景说明" />
        </uni-forms-item>
      </uni-forms>
    </u-list-item>
    <view class="next-button" @click="nextStep">
      下一步
    </view>
  </u-page-content>

</view>
</template>

<script>
export default {
  onLoad() {
    this.formData.orgName = uni.getStorageSync('org').name;
    this.formData.orgId = uni.getStorageSync('org').id;
  },
  data() {
    return {
      formData: {
        orgName: '组织名称',
        orgId: null,
        name: '',
        instructions: ''
      },
      rules: {
        // 对name字段进行必填验证
        name: {
          rules: [{
              required: true,
              errorMessage: '请输入场景名称',
            },
            {
              minLength: 2,
              maxLength: 12,
              errorMessage: '场景名称长度在 {minLength} 到 {maxLength} 个字符',
            }
          ]
        },
        instructions: {
          rules: [{
              required: true,
              errorMessage: '请输入场景说明',
            },
            {
              minLength: 2,
              maxLength: 30,
              errorMessage: '场景说明长度在 {minLength} 到 {maxLength} 个字符',
            }
          ]
        },
      }
    };
  },
  methods: {
    // 下一步
    nextStep() {
      this.$refs.form.validate().then(res => {
        let scenarioData = {
          'name': '',
          'description': '',
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
        scenarioData.name = res.name
        scenarioData.org_id = this.formData.orgId
        scenarioData.description = res.instructions
        uni.setStorageSync('scenarioModel', scenarioData);
        uni.navigateTo({
          url: '/pages/scenario/sceneSeting'
        })
      }).catch(err => {

      })
    },
  },
};
</script>

<style lang="scss" scoped>
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
