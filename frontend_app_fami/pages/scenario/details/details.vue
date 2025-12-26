<template>
<view>
  <u-page-title>
    <view class="title-left" style="overflow: hidden;width: 80%;">
      <!-- 确认 -->
      <text class="iconfont icon-wancheng" v-if="isEditMode && scenarioData.id" @click="confirmEditor"></text>
      <view class="goback" v-if="!isEditMode || !scenarioData.id">
        <uni-icons type="left" size="20" @click="goBack"></uni-icons>
        <text class="scenarioName">{{scenarioData.name}}</text>
      </view>
    </view>

    <view class="title-center">

    </view>

    <view class="right">
      <!-- 编辑 -->
      <text class="iconfont icon-xiugai icons" v-if="!isEditMode" @click="isEditMode = true"></text>
      <uni-icons @click="toScenario" color="#333 !important" type="close" size="30" v-if="isEditMode"></uni-icons>
    </view>
  </u-page-title>

  <u-page-content>
    <view class="page-content">
      <!-- Render Area -->
      <view class="renderArea" :style="isEditMode ? 'margin-bottom: 120rpx' : 'margin-bottom: 20rpx'">
        <u-list-item>
          <view style="flex: 1">
            <view class="row-box">
              <view class="row-left">
                <text class="iconfont icon-caidan"></text>如果
              </view>
              <text v-if="isEditMode" class="continue_to_add" @click="navigateTo('/pages/scenario/sceneSeting?type=isEditMode')">{{scenarioData.cfg_info.conditions.length?'继续添加条件':'添加条件'}}</text>
            </view>
            <view class="row-box" style="color:#000; font-weight: 600; padding-left: 70rpx;" @click="openRelation">
              {{relation=='and'?'同时满足所有条件':'满足任意条件'}}
              <uni-icons style="margin-left: 30rpx; font-weight: 400;" v-if="isEditMode" type="right" size="18"></uni-icons>
            </view>
            <view @click="conditionsChange(item)" v-for="(item , index) in scenarioData.cfg_info.conditions" :key="item.c_type+item.key">
              <view class="row-box" v-if="item.c_type != 'device'">
                <view class="row-left">
                  <text v-if="isEditMode" class="iconfont icon-jianshao" @click.stop="delCondition(index)"></text>
                  {{ item.c_type == 'timing'?item.exec_time: mapSceneConditions(item.condition) + ' ' +  item.numb}}
                </view>
                <text>
                  {{ item.c_type == 'timing'?'定时': item.c_type== 'device'?'设备':conditionsKeyMap[item.key]}}
                  <uni-icons style="margin-left: 30rpx;" v-if="isEditMode" type="right" size="18"></uni-icons>
                </text>
              </view>
              <view class="row-box" v-if="item.c_type == 'device'">
                <view class="row-left" v-if="item.type == 'float' || item.type == 'int'">
                  <text v-if="isEditMode" class="iconfont icon-jianshao" @click.stop="delCondition(index)"></text>
                  {{ item.key_name }} {{ item.c_type == 'timing'?item.exec_time: mapSceneConditions(item.condition) + ' ' +  item.numb}}
                </view>
                <view class="row-left" v-if="item.type == 'select'">
                  <text v-if="isEditMode" class="iconfont icon-jianshao" @click.stop="delCondition(index)"></text>
                  {{item.key_name}} {{ item.numb_name}}
                </view>
                <text>
                  {{ item.device_name}}
                  <uni-icons style="margin-left: 30rpx;" v-if="isEditMode" type="right" size="18"></uni-icons>
                </text>
              </view>
            </view>
            <view class="line" style="margin-bottom: 20rpx"></view>
            <view class="row-box">
              <view class="row-left">
                <text class="iconfont icon-quchuli"></text>就执行
              </view>
              <text v-if="isEditMode" class="continue_to_add" @click="navigateTo('/pages/scenario/selectEquipment')"> {{scene_devices_data.length?'继续添加设备':'添加设备'}}</text>
            </view>
            <view class="row-box" @click="actionToModify(item,index)" v-for="(item, index) in scene_devices_data" :key="index">
              <view class="row-left">
                <text v-if="isEditMode" class="iconfont icon-jianshao" @click.stop="delDevice(index)"></text>
                <image :src="item.device_log || '/static/dbs.png'" class="image" mode="aspectFit" />
                <view class="textBox">
                  <view class="name">
                    {{item.device_name}}
                  </view>
                  <view class="parameter">
                    {{item.action_msg.name}}
                    <text v-if="item.action_msg.input_data">
                      <text v-for="service in item.action_msg.input_data" :key="service.key">
                        {{ service.name }} {{ service.value }}
                      </text>
                    </text>
                  </view>
                </view>
              </view>
              <view class="row-left">
                <uni-icons v-if="isEditMode" type="right" size="18"></uni-icons>
              </view>

            </view>
          </view>
        </u-list-item>

        <u-list-item v-if="isEditMode" @click.native="effectiveTime" class="effectiveTimePeriod">
          <view class="icon-time-box">
            <!-- <text class="iconfont icon-shijian"></text>  -->
            <text class="title">生效时间段</text>
          </view>
          <view class="icon-time-box">
            {{ timing_type_map[timing_type] }} {{ timeDisplayMap() }}
            <uni-icons type="right" size="20"></uni-icons>
          </view>
        </u-list-item>

        <u-list-item v-if="!isEditMode" @click.native="toCheckEffectTime" class="effectiveTimePeriod">
          <view class="icon-time-box">
            <text class="title">生效时间段</text>
          </view>
          <view class="icon-time-box">
            {{ timing_type_map[timing_type] }} {{ timeDisplayMap() }}
            <uni-icons type="right" size="20"></uni-icons>
          </view>
        </u-list-item>
      </view>

      <view class="effect-time-button" v-if="isEditMode" @click="onSave">
        {{scenarioData.id?'保存':'创建'}}
      </view>
    </view>
  </u-page-content>
  <!-- 弹出 条件  时间 -->
  <uni-popup ref="popupTime" type="bottom">
    <view class="timeBox">
      <view class="confirmButtonBox">
        <view class="buttonItem" @click="$refs.popupTime.close()">取消</view>
        <view class="buttonItem" style="color:#50c3ff" @click="confirmTime">确定</view>
      </view>
      <u-time @change="changeTime" :times="conditionsTimeList" />
    </view>
  </uni-popup>
  <!-- 条件关系 -->
  <u-and-or ref="andOr" :relation="relation" @selection="refreshPage" />
   <!-- 新弹出框 -->
   <u-dialog ref="scenarName" @confirm="scenesSave('name')">
    <uni-forms ref="form" label-width="140rpx" label-align="right">
      <uni-forms-item label="名称：" name="name">
        <uni-easyinput v-model="scenarName" placeholder="请输入场景名称" />
      </uni-forms-item>
    </uni-forms>
  </u-dialog>
</view>
</template>

<script>
export default {
  data() {
    return {
      scenarName:'',
      timing_type: null,
      relation: '',
      actionIndex: 0,
      editModeType: 'editMode',
      isEditMode: false, // 是否编辑模式
      scenarioData: {
        name: ''
      },
      conditions: [],
      scene_conditions: [],
      conditionsKeyMap: {
        'temperature': '温度',
        'humidity': '湿度',
        'pm2.5': 'PM2.5',
      },
      conditionsTimeList: ['00', '00'],
      conditionsTime: '',
      effect_time: {},
      timing_type_map: {
        once: '单次',
        everyday: '每日',
        week: '每周',
        monthly: '每月',
        holiday: '法定节假日',
        workday: '法定工作日'
      },
    };
  },
  onLoad(query) {
    if (query.type == 'editMode') {
      this.isEditMode = true
      this.editModeType = query.type
    } else {
      this.editModeType = ''
    }

  },
  onShow() {
    this.scenarioData = uni.getStorageSync('scenarioModel')
    this.effect_time = this.scenarioData.cfg_info.effect_time
    this.timing_type = this.scenarioData.cfg_info.effect_time.timing_type || null
    this.scene_conditions = uni.getStorageSync('scene_conditions');
    this.conditions = JSON.parse(JSON.stringify(this.scenarioData)).cfg_info.conditions || []
    this.relation = JSON.parse(JSON.stringify(this.scenarioData)).cfg_info.relation
    this.scene_devices_data = JSON.parse(JSON.stringify(this.scenarioData)).scene_devices_data || []
  },
  
  methods: {
    // 时段显示映射
    timeDisplayMap(){
      let str = ''
      console.log(this.effect_time)
      if(this.effect_time.start_time && this.effect_time.end_time ){
        if(this.effect_time.start_time == '00:00:00' && this.effect_time.end_time == '23:59:00'){
          // 全天
          return 
        }
        if(this.effect_time.start_time > this.effect_time.end_time){
          str = `${this.effect_time.start_time}-${this.effect_time.end_time}(第二天)`
        }else{
          str = `${this.effect_time.start_time}-${this.effect_time.end_time}`
        }
      }
      return str
    },
    toScenario(){
      uni.switchTab({url:'/pages/scenario/scenario'})
    },
    // 点击保存按钮
    onSave(){
      if(!this.scene_devices_data.length){
        uni.showToast({
            title: '至少有一个执行设备',
            icon: 'error',
          });
        return 
      }
      if(!this.scenarioData.cfg_info.conditions.length){
        uni.showToast({
            title: '至少有一个条件',
            icon: 'error',
          });
        return 
      }
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      if(scenarioData.id){
        this.scenesSave()
      }else{
        this.scenarName = ''
        let arr = []
        scenarioData.cfg_info.conditions.forEach(t => {
          if(t.c_type == 'timing'){
            arr.push('定时')
          }
          if(t.c_type == 'weather'){
            let str = this.conditionsKeyMap[t.key]
            str+= this.mapSceneConditions(t.condition)
            str+=t.numb
            arr.push(str)
          }
          if(t.c_type == 'device'){
            let str = t.device_name
            if(t.type == 'select'){
              str+=t.key_name
              str+=t.numb_name
            }else{
              str+=t.key_name
              str+= this.mapSceneConditions(t.condition)
              str+=t.numb
            }
            arr.push(str)
          }
        });
        this.scenarName = arr.join('-')
        this.scenarName += '_'
        let arr2 = []
        scenarioData.scene_devices_data.forEach(d=>{
          let str = d.device_name
          str+=d.action_msg.name
          arr2.push(str)
        })
        this.scenarName += arr2.join('-')
        this.$refs.scenarName.open()
      }
    },
    // 保存
    scenesSave(type) {
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      if(type == 'name'){
        scenarioData.name = this.scenarName
      }
      this.$http({
        url: scenarioData.id ? `/api/scenes/${scenarioData.id}/` : '/api/scenes/',
        data: scenarioData,
        method: scenarioData.id ? 'patch' : 'post',
      }).then(res => {
        if (res.statusCode == 201 || res.statusCode == 200) {
          uni.switchTab({
            url: `/pages/scenario/scenario`
          })
        } else {
          uni.showToast({
            title: res.data.msg,
            icon: 'none',
          });
        }
      })
    },
    // 打开选择生效时间
    effectiveTime() {
      uni.navigateTo({
        url: `/pages/scenario/effectiveTime`
      })
    },
    // 打开回显生效时间
    toCheckEffectTime() {
      uni.navigateTo({
        url: `/pages/scenario/toCheckEffectTime`
      })
    },
    // 打开条件关系选择
    openRelation() {
      this.$refs.andOr.open()
    },
    // 删除条件
    delCondition(index) {
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      let arr = scenarioData.cfg_info.conditions
      arr.splice(index, 1)

      scenarioData.cfg_info.conditions = arr
      uni.setStorageSync('scenarioModel', scenarioData)
      this.refreshPage()
    },
    // 删除动作
    delDevice(index) {
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      let arr = scenarioData.scene_devices_data
      arr.splice(index, 1)
      scenarioData.scene_devices_data = arr
      uni.setStorageSync('scenarioModel', scenarioData)
      this.refreshPage()
    },
    // 设备作为条件修改
    deviceNavigateTo(item, key) {
      let obj = {
        id: item.id,
        title: item.name,
        logo: item.logo || item.product.logo,
        properties: item.product.cfg_info.properties.filter(attribute => attribute.condition_info)
      }
      uni.setStorageSync('properties', obj)
      uni.navigateTo({
        url: `/pages/scenario/conditionChoose?type=editMode&key=${key}`
      })
    },
    // 动作修改
    actionNavigateTo(item, key) {
      let obj = {
        id: item.id,
        log: item.log || item.product.log || '',
        title: item.name,
        services: item.product.cfg_info.services.filter(attribute => attribute.scene_action)
      }
      uni.setStorageSync('services', obj)
      uni.navigateTo({
        url: `/pages/scenario/equipmentMovement?type=editMode&key=${key}&actionIndex=${this.actionIndex}`
      })
    },
    // 获取设备详情
    geDevices(item, type) {
      this.$http({
        url: `/api/devices/${item.device_id}/`,
        data: {},
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          if (type == 'action') {
            this.actionNavigateTo(res.data, item.action_msg.key)
          } else {
            this.deviceNavigateTo(res.data, item.key)
          }
        }
      })
    },
    // 固定条件映射
    mapSceneConditions(key) {
      let obj = this.scene_conditions.find(item => key == item.value)
      return obj.text
    },
    // 确认编辑
    confirmEditor() {
      let scenarioData = uni.getStorageSync('scenarioModel');
      this.$http({
        url: `/api/scenes/${scenarioData.id}/`,
        data: scenarioData,
        method: 'patch',
      }).then(res => {
        if (res.statusCode == 200) {
          this.isEditMode = false
        } else {
          uni.showToast({
            title: res.data.msg,
            icon: 'none',
          });
        }
      })
    },
    // 返回上一层
    goBack() {
      uni.navigateBack()
    },
    // 跳转
    navigateTo(url) {
      uni.navigateTo({
        url
      })
    },
    // 动作修改
    actionToModify(item, index) {
      this.actionIndex = index
      this.geDevices(item, 'action')
    },
    // 条件修改 业务分类
    conditionsChange(item) {
      if (item.c_type == 'timing') {
        item.exec_time.split(':')
        let times = item.exec_time.split(':')
        this.conditionsTimeList = [times[0], times[1]]
        this.openPopupTime(item.exec_time)
      }
      if (item.c_type == 'weather') {
        this.navigateTo(`/pages/scenario/fixedConditionChoose?type=${this.conditionsKeyMap[item.key]}&editMode=editMode`)
      }
      if (item.c_type == 'device') {
        this.geDevices(item)
      }
    },
    // 弹出 条件  时间选择
    openPopupTime(time) {
      this.conditionsTime = time || '00:00:00'
      this.$refs.popupTime.open('bottom')
    },
    // 修改定时
    changeTime(time) {
      this.conditionsTime = `${time[0]}:${time[1]}:00`
    },
    // 修改 storageSync 刷新页面
    refreshPage() {
      this.scenarioData = uni.getStorageSync('scenarioModel')
      this.scene_conditions = uni.getStorageSync('scene_conditions');
      this.conditions = JSON.parse(JSON.stringify(this.scenarioData)).cfg_info.conditions || []
      this.relation = JSON.parse(JSON.stringify(this.scenarioData)).cfg_info.relation
      this.scene_devices_data = JSON.parse(JSON.stringify(this.scenarioData)).scene_devices_data || []
    },
    // 修改定时确认
    confirmTime() {
      this.$refs.popupTime.close()
      const scenarioModel = uni.getStorageSync('scenarioModel');
      let scenarioData = JSON.parse(JSON.stringify(scenarioModel))
      // 改变全局场景对应参数
      let item = scenarioData.cfg_info.conditions.find(item => item.c_type == 'timing')
      if (item) {
        item.exec_time = this.conditionsTime
      } else {
        scenarioData.cfg_info.conditions.push({
          c_type: "timing",
          exec_time: this.conditionsTime
        })
      }
      uni.setStorageSync('scenarioModel', scenarioData);
      this.refreshPage()
    },
  }
};
</script>

<style lang="scss" scoped>
.title-center {
  flex: 1;
  text-align: center;
  color: $mainTitle;
}

.icon-xiugai {
  font-size: 30rpx;
  font-weight: 600;
}

.goback {
  display: flex;
  align-items: center;

  text {
    font-size: 28rpx;
    color: #000;
    margin-left: 10rpx;
  }
}

.page-content {
  display: flex;
  flex-direction: column;
  height: 100%;

  .renderArea {
    flex: 1;
    overflow-y: auto;
  }

}

.row-box {
  @include flex-box;
  padding: 16rpx;

  .image {
    width: 80rpx;
    height: 80rpx;
  }

  .row-left {
    display: flex;
    align-items: center;

    .iconfont {
      font-size: 30rpx;
    }
  }

  .continue_to_add {
    color: $mainColor;
  }
}

.icon-jianshao {
  color: rgb(255, 38, 0);
  margin-right: 30rpx;
  font-weight: 600;
}

.line {
  @include divider;
}

.textBox {
  width: 360rpx;
  margin: 0 30rpx;

  .name {
    @include overflow-text;
    font-size: 32rpx;
    color: $mainTitle;
    line-height: 1.5;
  }

  .parameter {
    font-size: 26rpx;
    @include overflow-text;
  }

}

.effect-time-button {
  @include button;
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 20rpx;
}

.timeBox {
  background-color: $backgroundColor;
  transform: translateY(30rpx);

  .confirmButtonBox {
    display: flex;
    padding: 16rpx 10rpx 0 10rpx;
    display: flex;
    justify-content: space-between;

    .buttonItem {
      padding: 10rpx;
    }
  }
}

.icon-time-box {
  display: flex;
  align-items: center;
}
.icons{
  color: $mainColor !important;
}
.scenarioName{
  display: inline-block;
  white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.effectiveTimePeriod{
  background-color: #fff;
  min-height: 100rpx;
  border-radius: 30rpx;
  margin-top: 20rpx;
  padding: 20rpx 40rpx;
  margin-top: 100rpx;
  .title{
    font-size: 30rpx;
    color: #333;
    font-weight: 600;
  }
}
</style>
