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
      <!-- <text class="iconfont icon-xiugai" v-if="!isEditMode" @click="add"></text> -->
      <uni-icons class="icons" type="plus" size="26" v-if="!isEditMode" @click="add"/>
      <!-- 全选 -->
      <text class="iconfont icon-quanxuan" :style="selectedList.length == dataList.length ? 'color: #22be49' : '' "
 v-if="isEditMode" @click="selection"></text>
    </view>
    <view class="search">
      <view class="left">
        <uni-easyinput v-model="search" placeholder="请输入" />
      </view>
      <button class="mini-btn" type="primary" size="mini" style="margin-left: 20rpx;" @click="onSearch">搜索</button>
    </view>
  </u-page-title>
  <u-page-content>
    <view class="page-content" >
      <view class="list" :style="isEditMode?'margin-bottom: 170rpx;':'margin-bottom: 20rpx;'">
        <view style="display: flex;align-items: center;" v-for="(item, index) in dataList" :key="item.id" @longtap.native="onLongPress(item,index)">
          <view class="item-left" >
            <!-- <uni-forms label-width="150rpx" label-align="right">
              <uni-forms-item label="用户姓名:" style="align-items: center;">
                {{item.nickname}}
              </uni-forms-item>
              <uni-forms-item label="账号:" style="align-items: center;">
                {{item.username}}
              </uni-forms-item>
              <uni-forms-item label="创建时间:" style="align-items: center;">
                {{item.date_joined}}
              </uni-forms-item>
            </uni-forms> -->
            <image :src="item.avatar?item.avatar:'../../../static/user.png'" />
            <view class="user_name">{{item.nickname}}</view>
            <view class="user_mobile">{{item.mobile}}</view>
            
          </view>
          <view class="item-right">
            <u-is-select v-if="isEditMode" :select="isSelect(item)" @click.native="clickOnRadio(item,index)" />
          </view>
        </view>              
      </view>
      <!-- bottom handle area-->
      <view class="b-button-box" v-if="isEditMode">
        <view class="b-button-item" v-if="(selectedList.length == 1)" @click="edit">
          <text class="iconfont icon-zhongmingming"></text>
          修改
        </view>
        <view class="b-button-item" v-if="selectedList.length" @click="batchDelete">
          <text class="iconfont icon-shanchu" ></text>
          删除
        </view>
      </view>
    </view>
  </u-page-content>
  <!-- edit -->
  <u-dialog ref="dialog" @confirm="formChange">
    <uni-forms ref="form" :rules="form" label-width="150rpx" label-align="right">
      <uni-forms-item label="用户姓名:" name="nickname" >
        <uni-easyinput  trim="all" v-model="form.nickname" placeholder="请输入" ></uni-easyinput>
      </uni-forms-item>
      <uni-forms-item label="手机号:"  style="align-items: center;">
        <text v-if="userInfo.id != active.id">{{active.mobile}}</text>
        <uni-easyinput v-if="userInfo.id == active.id"  trim="all" v-model="active.mobile" placeholder="请输入" ></uni-easyinput>
      </uni-forms-item>
      <!-- <uni-forms-item label="关联组织" name="org_id">
        <picker  class="picker" @change="bindEditOrgChange" :value="editOrgIndex" :range="orgArray" range-key="name">
            <view  class="uni-input">
                <text class="right-text"> {{ editOrgIndex==null ? '请选择' : orgArray[editOrgIndex].name }}</text>
                <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
            </view>
        </picker>
      </uni-forms-item> -->
      <uni-forms-item label="新密码:" name="password">
        <uni-easyinput v-model="form.password" type="password" placeholder="请输入" />
      </uni-forms-item>
      <uni-forms-item label="确认密码:" name="password2">
        <uni-easyinput v-model="form.password2" type="password" placeholder="请输入" />
      </uni-forms-item>
    </uni-forms>
  </u-dialog>
  <!-- add -->
  <u-dialog ref="addDialog" @confirm="addFormChange">
    <uni-forms ref="form" :rules="addForm" label-width="150rpx" label-align="right">
      <uni-forms-item label="用户姓名" name="nickname" >
        <uni-easyinput  trim="all" v-model="addForm.nickname" placeholder="请输入" ></uni-easyinput>
      </uni-forms-item>
      <uni-forms-item label="手机号" name="mobile" style="margin-bottom: 0rpx;">
        <uni-easyinput  trim="all" v-model="addForm.mobile" placeholder="请输入" ></uni-easyinput>
      </uni-forms-item>
      <view style="padding: 20rpx 0rpx 20rpx 140rpx;">
        <!-- <text style="color: #48A7FDFF;">获取验证码</text> -->
        <u-sms ref="sms"  @click.native="getSms"/>
      </view>
      <uni-forms-item label="验证码" name="sms">
        <uni-easyinput  trim="all" v-model="addForm.sms" placeholder="请输入" ></uni-easyinput>
      </uni-forms-item>
      <uni-forms-item label="关联组织" name="org_id">
        <!-- <view class="picker" @tap="show = true">
          {{info || "请选择"}}
          <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
        </view> -->
        <picker  class="picker" @change="bindOrgChange" :value="orgIndex" :range="orgArray" range-key="name">
            <view  class="uni-input">
                <text class="right-text"> {{ orgIndex==null ? '请选择' : orgArray[orgIndex].name }}</text>
                <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
            </view>
        </picker>
      </uni-forms-item>
      <uni-forms-item label="登录密码" name="password">
        <uni-easyinput v-model="addForm.password" type="password" placeholder="请输入" />
      </uni-forms-item>
      <uni-forms-item label="确认密码" name="password2">
        <uni-easyinput v-model="addForm.password2" type="password" placeholder="请输入" />
      </uni-forms-item>
    </uni-forms>
  </u-dialog>
  <u-multiple-select
    v-model="show"
    :data="orgArray"
    label-name="name"
    value-name="id"
    :default-selected="defaultSelected"
    @confirm="confirm"
    @cancel="cancel"
  ></u-multiple-select>
</view>
</template>

<script>
export default {
  data() {
    return {
      userInfo:{id: null},
      pageOptios: {
        page: 1,
        page_size: 10,
      },
      next: false,
      search:'',
      dataList:[],
      active:{},
      isEditMode: false, // 是否编辑模式
      selectedList: [], // 已选中
      form: {
        nickname:'',
        sms:'',
        org_id:'',
        password:'',
        password2:'',
      },
      addForm: {
        nickname:'',
        mobile:'',
        sms:'',
        org_id:'',
        password:'',
        password2:'',
      },
      orgIndex:null,
      editOrgIndex:null,
      orgArray:[],
      
      show: false, //是否显示 - 双向绑定
      info: "",
      defaultSelected: ["3", "5"], //默认选中项
    }
  },
  onLoad() {
    this.userInfo = uni.getStorageSync('userInfo')||{id:null};
    this.onSearch(true);
    this.getOrg();
  },
  onReachBottom() {
    if (this.next) {
      this.pageOptios.page++;
      this.onSearch(false);
    }
  },
  methods: {
    getSms(){
      let mobile = this.addForm.mobile;
      console.log(mobile)
      if(mobile){
        this.$refs.sms.getSms({mobile});
      }
    },
    cancel(){},
    confirm(data) {
      console.log(data);
      this.info = data.map((el) => el.name).join(",");
    },
    
    
    getOrg(){
      this.$http({
        url: '/api/users/get_my_orgs/',
        method: 'get',
      }).then(res => {
        console.log(res)
        if(res.statusCode == 200)this.orgArray = res.data;
      })
    },
    bindEditOrgChange(e){
      let index = e.detail.value;
      this.editOrgIndex = index;
      this.form.org_id = this.orgArray[index].id;
    },
    bindOrgChange(e){
      console.log(e)
      let index = e.detail.value;
      this.orgIndex = index;
      this.addForm.org_id = this.orgArray[index].id;
    },
    batchDelete(){
      let ids = this.selectedList.map(item=>item.id);
      this.$http({
        url: '/api/users/batch_delete/',
        method: 'post',
        data:{
          id_list:ids
        }
      }).then(res => {
        // console.log(res)
        if(res.statusCode == 200){
           this.confirmEditor();
           this.onSearch(true);
        }
      })
    },
    async addFormChange(){
      let verifyMobilOrg = await this.$http({
        url:'/api/users/verify_sms_code/',
        method:'post',
        data:{
          verify_type:'register',
          mobile:this.addForm.mobile,
          code:this.addForm.sms
        }
      })
      if(verifyMobilOrg.data.result == 'error'){
        uni.showToast({
          title: verifyMobilOrg.data.msg,
          icon:'none',
        });
        return
      }
      this.$http({
        url: `/api/users/`,
        data: {
          username:this.addForm.mobile,
          ...this.addForm
        },
        method: 'post',
      }).then(res=>{
        if (res.statusCode == 200 ||res.statusCode == 201) {
          uni.showToast({
            title: res.data.msg||'操作成功',
            icon:'none',
          });
          this.onSearch(true)
        }
      })
    },
    formChange(){
      let id = this.active.id;
      this.form.mobile  = this.active.mobile
      this.$http({
        url: `/api/users/${id}/`,
        data: {
          ...this.form

        },
        method: 'patch',
      }).then(res=>{
        if (res.statusCode == 200 ||res.statusCode == 201) {
          uni.showToast({
            title: res.data.msg||'操作成功',
            icon:'none',
          });
          this.confirmEditor();
          this.onSearch(true)
        }
      })
    },
    edit(){
      console.log(this.active)
      this.form.nickname = this.active.nickname;
      this.form.org_id = this.active.org?this.active.org.id:'';
      this.form.password  = '';
      this.form.password2  = '';
      this.$refs.dialog.open();
      if(this.active.org){
        this.editOrgIndex = this.orgArray.findIndex(item=>item.id == this.active.org.id);
      }else{
        this.editOrgIndex = null;
      }
      
    },
    add(){
      this.addForm.nickname = '';
      this.addForm.mobile = '';
      this.addForm.org_id = '';
      this.addForm.password  = '';
      this.$refs.addDialog.open();
      this.orgIndex = null;
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
    onSearch(init = false) {
      if (init) {
        this.pageOptios.page = 1;
      }
      this.$http({
        url: '/api/users/',
        data: {
          search:this.search,
          orgs: uni.getStorageSync('org').id || '',
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
          console.log(list)
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
  }
}
</script>

<style lang="scss" scoped>
  .page{
    .search{
      width: 100%;
      display: flex;
      justify-content: center;
      padding: 20rpx;
      background-color: #fff;
      .left{
        flex:1;
      }
      .mini-btn{
        height: 72rpx;
        line-height: 72rpx;
      }
    }
    .boxbody{
      // padding: 25rpx 0rpx;
      ::v-deep .uni-forms-item{
        margin-bottom: 0rpx;
        .uni-forms-item__label{
          height: 26px;
        }
      }
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
    align-items: center;
    height: 120rpx;
    padding: 0 20rpx;
    ::v-deep .uni-forms-item{
      margin-bottom: 0rpx;
      .uni-forms-item__label{
        height: 26px;
      }
    }

    image{
      width: 80rpx;
      height: 80rpx;
      border-radius: 50%;
    }
    .user_name{
      padding: 0 20rpx;
      width: 120rpx;
    }
  
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
    box-sizing: border-box;
    padding-top: 90rpx;
  
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
