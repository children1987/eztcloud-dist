<template>
<view class="page"> 
  <u-page-title>
    <u-goback />
  </u-page-title>
  <u-page-content>
    <view class="content">
      <uni-list>
        <uni-list-item 
          :rightText="detail.org&&detail.org.name"
          title="所属组织" >
          <template v-slot:header>
            <view class="iconbox">
              <text class="iconfont icon-zuzhijigou"></text>
            </view>
          </template>
        </uni-list-item>
        <uni-list-item
          title="所属单元"
          clickable
          @click="onClick({handleType:'unit'})"
          :rightText="detail.unit&&detail.unit.name"
          showArrow  >
          <template v-slot:header>
              <view class="iconbox">
                <text class="iconfont icon-icon-p_gongchangdanyuan"></text>
              </view>
            </template>
          </uni-list-item>
        <uni-list-item 
          title="网关"
          :rightText="detail.com_gateway&&detail.com_gateway.code">
          <template v-slot:header>
              <view class="iconbox">
                <text class="iconfont icon-wangguanshezhi"></text>
              </view>
            </template>
          </uni-list-item>
        <uni-list-item
          title="设备名称"
          clickable
          :rightText="detail.name"
          @click="onClick({handleType:'name'})"
          showArrow  >
          <template v-slot:header>
              <view class="iconbox">
                <text class="iconfont icon-zhongmingming"></text>
              </view>
            </template>
          </uni-list-item>
        
        <uni-list-item
          title="安装位置"
          clickable
          :rightText="detail.location"
          @click="onClick({handleType:'location'})"
          showArrow  >
          <template v-slot:header>
            <view class="iconbox">
              <text class="iconfont icon-weizhi"></text>
            </view>
          </template>
        </uni-list-item>
      </uni-list>  
    </view>
  </u-page-content>
  <!-- edit -->
  <u-dialog ref="dialog" @confirm="formChange" @cancel="formCancel">
    <uni-forms ref="form" :rules="form" label-width="160rpx" label-align="right">
      <uni-forms-item label="所属单元" v-if="handleType=='unit'">
        <picker class="picker" @change="bindUnitChange" :value="unitIndex" :range="unitArray" range-key="name">
            <view  class="uni-input">
                <text class="right-text"> {{ unitIndex == null ? '请选择' : unitArray[unitIndex].name }}</text>
                <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
            </view>
        </picker>
      </uni-forms-item>
      <uni-forms-item label="设备名称" name="name" v-if="handleType=='name'">
        <uni-easyinput v-model="form.name" placeholder="请输入" />
      </uni-forms-item>
      <uni-forms-item label="安装位置" name="location" v-if="handleType=='location'">
        <uni-easyinput v-model="form.location" placeholder="请输入" />
      </uni-forms-item>
    </uni-forms>
  </u-dialog>
</view>
</template>

<script>
export default {
  data() {
    return {
      deviceId:'',
      detail:{},
      form: {
        unit_id:'',
        name:'',
        location:'',
      },
      unitIndex:null,
      unitArray:[],
      handleType:'',//name，unit，location
    }
  },
  onLoad(query) {
    this.deviceId = query.id;
    this.getDetail(query.id);
    this.getUnit(query.id);
  },
  methods: {
    getUserInfo(){
      this.userInfo = uni.getStorageSync('userInfo')||{};
      console.log(this.userInfo);
    },
    onClick(e) {
      console.log('执行click事件', e)
      this.handleType = e.handleType;
      if(this.detail.unit){
        this.unitIndex = this.unitArray.findIndex(item=>item.id == this.detail.unit.id);
      }else{
        this.unitIndex = null;
      }
      this.$refs.dialog.open();
    },
    formCancel(){
      // this.handleType = ''
    },
    async formChange(){
      let id = this.deviceId;
      let result ;
      result = await this.$http({
        url: `/api/devices/${id}/`,
        data: {
          ...this.form
        },
        method: 'patch',
      })
      console.log(result)
      if (result.statusCode == 200 ||result.statusCode == 201) {
        uni.showToast({
          title: result.data.msg||'操作成功',
          icon:'none',
        });
        this.getDetail(id);
      }
    },
    bindUnitChange(e){
      let index = e.detail.value;
      this.unitIndex = index;
      this.form.unit_id = this.unitArray[index].id;
    },
    getDetail(id){
      this.$http({
        url: `/api/devices/${id}/`,
        method: 'get',
      }).then(res=>{
        if (res.statusCode == 200) {
          this.detail = res.data;
          this.form = {
            unit_id:res.data.unit?res.data.unit.id:'',
            name:res.data.name||'',
            location:res.data.location||'',
          }
        }
      })
    },
    getUnit(id){
      this.$http({
        url: '/api/devices/get_optional_org_units/',
        method: 'get',
        data:{
          device_id:id
        }
      }).then(res => {
        // console.log(res)
        if(res.statusCode == 200)this.unitArray = res.data;
      })
    },
  }
}
</script>

<style lang="scss" scoped>
  .page{
    ::v-deep .uni-list-item__content{
      justify-content: center;
    }
    .content{
      margin: 30rpx -16rpx 0px;
    }
    .iconbox{
      margin-right: 9px;
      display: flex;
      flex-direction: row;
      align-items: center;
    }
  }
  .picker{
    height: 100%;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    .uni-input{
      display: flex;
      width: 100%;
      box-sizing: border-box;
      height: 72rpx;
      justify-content: space-between;
      align-items: center;
      padding: 0rpx 20rpx;
      .right-text{
        color: #999;
        font-size: 12px;
      }
    }
  }
</style>
