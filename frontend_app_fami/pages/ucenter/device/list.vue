<template>
<view class="page">
  <u-page-title>
    <view class="title-left">
      <!-- 确认 -->
      <text class="iconfont icon-wancheng" v-if="isEditMode" @click="confirmEditor"></text>
      <u-goback v-else/>
    </view>
    <view class="title-center">
      <text v-if="isEditMode">已选择{{selectedList.length}}项</text>
    </view>
    <view class="right">
      <!-- 添加 -->
      <!-- <uni-icons type="plus" size="24" v-if="!isEditMode" @click="add"/> -->
      <!-- 全选 -->
      <!-- <text class="iconfont icon-quanxuan" v-if="isEditMode" @click="selection"></text> -->
    </view>
  </u-page-title>
  <u-page-content>
    <view class="page-content" >
      <view class="" style="margin-right: 500rpx;">
        <picker style="border:none;" class="picker" @change="searchOrgChange" :value="searchOrgIndex" :range="orgArray" range-key="name">
            <view  class="uni-input">
                <text class="right-text"> {{ searchOrgIndex == null ? '请选择' : orgArray[searchOrgIndex].name }}</text>
                <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
            </view>
        </picker>
      </view>
      <view v-if="!dataList.length" class="empty">
        暂无数据
      </view>
      <view class="list" :style="isEditMode?'margin-bottom: 170rpx;':'margin-bottom: 20rpx;'">
        <u-list-item v-for="(item, index) in dataList" :key="item.id" @longtap.native="onLongPress(item,index)">
          <view class="item-left" >
            <view class="left">
              <image style="width: 100rpx; height: 100rpx;" :src="item.logo || '/static/dbs.png'">
            </view>
            <view class="center">
              <view class="title">{{item.name}}</view>
              <view class="content">{{item.unit&&item.unit.name}}</view>
            </view>
            <view class="signal">
              <u-signal :signal="item.state" />
            </view>
          </view>
          <view class="item-right">
            <u-is-select v-if="isEditMode" :select="isSelect(item)" @click.native="clickOnRadio(item,index)" />
            <!-- <switch v-else :checked="!item" @change.stop="switchChange(item,index)" style="transform:scale(0.7)" /> -->
            <text v-else >
              <text v-if="active && item.id == mainDeviceId" style="color:#49A6FDFF;" >主设备</text>
            </text>
          </view>
        </u-list-item>              
      </view>
      <!-- bottom handle area-->
      <view class="b-button-box" v-if="isEditMode">
        <view class="b-button-item" v-if="(selectedList.length == 1)" @click="setToMain">
          <text class="iconfont icon-shoucang-moren"></text>
          设为主设备
        </view>
      
        <view class="b-button-item" v-if="(selectedList.length == 1)" @click="edit">
          <text class="iconfont icon-dizhi" ></text>
          修改设备
        </view>
      </view>
    </view>
  </u-page-content>
  <!-- edit -->
  <u-dialog ref="dialog" @confirm="formChange">
    <uni-forms ref="form" :rules="form" label-width="160rpx" label-align="right">
      <uni-forms-item label="设备名称" name="name">
        <uni-easyinput v-model="form.name" placeholder="请输入" />
      </uni-forms-item>
      <uni-forms-item label="所属单元" >
        <picker class="picker" @change="bindUnitChange" :value="unitIndex" :range="unitArray" range-key="name">
            <view  class="uni-input">
                <text class="right-text"> {{ unitIndex == null ? '请选择' : unitArray[unitIndex].name }}</text>
                <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
            </view>
        </picker>
      </uni-forms-item>
      <uni-forms-item label="安装位置" name="location">
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
      search:{
        org:''
      },
      pageOptios: {
        page: 1,
        page_size: 10,
      },
      next: false,
      active:{},
      dataList:[],
      form: {
        name:'',
        unit_id:'',
        location:''
      },
      isEditMode: false, // 是否编辑模式
      selectedList: [], // 已选中
      unitIndex:null,//所属单元
      unitArray: [],//所属单元选项
      mainDeviceId:'',
      searchOrgIndex:null,
      orgArray:[],
      userInfo:{},
    }
  },
  onLoad() {
    this.getUserInfo();
    this.onSearch(true);
    let userInfo = uni.getStorageSync('userInfo')
    if(userInfo&&userInfo.main_device){
      this.mainDeviceId = userInfo.main_device.id;
    }
  },
  mounted() {
    this.getOrg();
  },
  onReachBottom() {
    if (this.next) {
      this.pageOptios.page++;
      this.onSearch(false);
    }
  },
  methods: {
    getUserInfo() {
      let userInfo = uni.getStorageSync('userInfo');
      this.userInfo = userInfo;
      let default_org = userInfo.default_org;
      if (default_org) {
        this.search.org = default_org.id;
      }
    },
    searchOrgChange(e){
      let index = e.detail.value;
      this.searchOrgIndex = index;
      this.search.org = this.orgArray[index].id;
      this.onSearch(true);
    },
    getOrg(){
      this.$http({
        url: '/api/orgs/get_all/',
        method: 'get',
      }).then(res => {
        // console.log(res)
        if (res.statusCode == 200){
          this.orgArray = res.data;
          if(this.search.org){
            let index = res.data.findIndex(item=>item.id == this.search.org)
            this.searchOrgIndex = index;
          }
        } 
      })
    },
    updateUser(){
      let userInfo = uni.getStorageSync('userInfo');
      this.$http({
        url:`/api/users/${userInfo.id}/`
      }).then(res=>{
        if(res.statusCode == 200 ||res.statusCode == 201){
          uni.setStorageSync('userInfo',res.data);
        }
      })
    },
    getUnit(){
      this.$http({
        url: '/api/devices/get_optional_org_units/',
        method: 'get',
        data:{
          device_id:this.active.id
        }
      }).then(res => {
        // console.log(res)
        if(res.statusCode == 200)this.unitArray = res.data;
      })
    },
    bindUnitChange: function(e) {
      let index = e.detail.value;
      this.unitIndex = index;
      this.form.unit_id = this.unitArray[index].id;
    },
    setToMain(){
      let id = this.active.id;
      this.$http({
        url:`/api/orgs/set_main_device/`,
        method:'post',
        data:{
          device_id:id
        }
      }).then(res=>{
        console.log(res)
        if(res.statusCode == 200 ||res.statusCode == 201){
          uni.showToast({
            title: res.data.msg||'设置成功',
            icon:'none',
          });
          this.mainDeviceId = id;
          this.updateUser();
        }
      })
    },
    edit(){
      console.log(this.active)
      this.getUnit();
      this.form.name = this.active.name;
      this.form.unit_id = this.active.unit?this.active.unit.id:'';
      this.form.location = this.active.location;
      this.$refs.dialog.open();
      if(this.active.unit){
        this.unitIndex = this.unitArray.findIndex(item=>item.id == this.active.unit.id);
      }
    },
    add(){
      this.form.name = '';
      this.form.unit_id = '';
      this.form.location = '';
      this.unitIndex = null;
      this.$refs.dialog.open();
    },
    onSearch(init = false) {
      if (init) {
        this.pageOptios.page = 1;
      }
      this.$http({
        url: '/api/devices/',
        data: {
          org:this.search.org,
          ...this.pageOptios
        },
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          let list = res.data.results.map(item=>{
            return {
              ...item,
            }
          });
          if (init) {
            this.dataList = list;
          } else {
            if (list && list.length) {
              this.dataList = this.dataList.concat(list);
            }
          }
          if (res.data.next) {
            this.next = true;
          } else {
            this.next = false;
          }
        }
      })
    },
    formChange(){
      let id = this.active.id;
      this.$http({
        url: `/api/devices/${id}/`,
        data: {
          ...this.form
        },
        method: 'patch',
      }).then(res=>{
        console.log(res)
        if (res.statusCode == 200 ||res.statusCode == 201) {
          this.confirmEditor();
          uni.showToast({
            title: res.data.msg||'操作成功',
            icon:'none',
          });
          this.onSearch(true)          
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
      this.setAc(item)
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
      console.log(data)
      let select = this.selectedList.find(item => item.id == data.id)
      console.log(select)
      if (select) {
        // 不能用index直接删, selectedList用户操作选取,乱序
        this.selectedList.forEach((item, i) => {
          if (select.id == item.id) {
            this.selectedList.splice(i, 1);
            if(this.selectedList.length==1){
              this.setAc(this.selectedList[0])
            }
          }
        })
      } else {
        this.selectedList.push(data);
        this.setAc(data)
      }
    },
    setAc(data){
      this.active = data;
    },
  }
}
</script>

<style lang="scss" scoped>
  .page{
    .left{
    }
    .center{
      width: 200rpx;
      overflow: hidden;
      .title{
        color: #000000CC;
        font-size: 30rpx;
      }
      .content{
        color:#00000080;
        margin-top: 0rpx;
      }
    }
    .right{
      min-width: 80rpx;
    }
  }
  .title-center {
    flex: 1;
    text-align: center;
    color: $mainTitle;
  }
  .item-left {
    flex: 1;
    display: flex;
    // flex-direction: column;
    justify-content: space-between;
    align-items: center;
  
    .bold-text {
      font-size: $contentWordsSize;
      font-weight: 400;
      color: $mainTitle;
    }
  
    .no-bold-text {
      padding-top: 28rpx;
      font-size: $contentWordsSize;
      font-weight: 300;
    }
  }
  
  .item-right {
    min-width: 140rpx;
    text-align: right;
  }
  
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
