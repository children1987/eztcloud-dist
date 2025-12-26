<template>
  <view class="page">
    <u-page-title>
      <view class="title-left">
        <!-- 确认 -->
        <text class="iconfont icon-wancheng" v-if="isEditMode" @click="confirmEditor"></text>
        <u-goback v-else />
      </view>
      <view class="title-center">
        <text v-if="isEditMode">已选择{{selectedList.length}}项</text>
      </view>
      <view class="right">
        <!-- 全选 -->
        <text class="iconfont icon-quanxuan" :style="selectedList.length == dataList.length ? 'color: #22be49' : '' "
 v-if="isEditMode" @click="selection"></text>
      </view>
    </u-page-title>

    <u-page-content>
      <view class="page-content">
        <view class="list" :style="isEditMode?'margin-bottom: 170rpx;':'margin-bottom: 20rpx;'">
          <u-list-item v-for="(item, index) in dataList" :key="item.id" @longtap.native="onLongPress(item,index)">
            <view class="item-left">
              <text class="bold-text">{{item.name}}</text>
              <text class="no-bold-text">地址：{{item.fullAddress}}</text>
            </view>
            <view class="item-right">
              <u-is-select v-if="isEditMode" :select="isSelect(item)" @click.native="clickOnRadio(item,index)" />
              <!-- <switch v-else :checked="!item" @change.stop="switchChange(item,index)" style="transform:scale(0.7)" /> -->
              <text v-else>
                <text v-if="active && item.id == defaultOrgId" style="color:#49A6FDFF;">默认组织</text>
              </text>
            </view>
          </u-list-item>
        </view>
        <!-- bottom handle area-->
        <view class="b-button-box" v-if="isEditMode">
          <view class="b-button-item" v-if="(selectedList.length == 1)" @click="setToDefault">
            <text class="iconfont icon-shoucang-moren"></text>
            设为默认组织
          </view>

          <view class="b-button-item" v-if="(selectedList.length == 1)" @click="edit">
            <text class="iconfont icon-dizhi"></text>
            修改地址
          </view>
        </view>
      </view>
    </u-page-content>

    <!-- edit -->
    <u-dialog ref="dialog" @confirm="formChange">
      <uni-forms ref="form" :rules="form" label-width="180rpx" label-align="right">
        <uni-forms-item label="地区" name="area"  style="align-items: center;">
          {{form.area}}
        </uni-forms-item>
        <uni-forms-item label="详细地址" name="address">
          <uni-easyinput v-model="form.address" placeholder="请输入" />
        </uni-forms-item>
      </uni-forms>
    </u-dialog>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        defaultOrgId:'',
        pageOptios: {
          page: 1,
          page_size: 10,
        },
        next: false,
        dataList: [],
        isEditMode: false, // 是否编辑模式
        selectedList: [], // 已选中
        form: {
          address: ""
        },
        active: {
          id: 1,
        },
      }
    },
    onLoad() {
      this.onSearch(true);
      let userInfo = uni.getStorageSync('userInfo')
      if(userInfo&&userInfo.default_org){
        this.defaultOrgId = userInfo.default_org.id;
      }
      console.log(userInfo)
    },
    onReachBottom() {
      if (this.next) {
        this.pageOptios.page++;
        this.onSearch(false);
      }
    },
    methods: {
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
      onSearch(init = false) {
        if (init) {
          this.pageOptios.page = 1;
        }
        this.$http({
          // url:'/api/orgs/'+this.$util.toUrl({
          //   ...this.pageOptios
          // }),
          url: '/api/orgs/',
          data: {
            ...this.pageOptios
          },
          method: 'get',
        }).then(res => {
          if (res.statusCode == 200) {
            let list = res.data.results.map(item=>{
              return {
                ...item,
                fullAddress:item.city.full_name.replace(/\s*/g,"")+item.address
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
      edit() {
        console.log(this.active)
        this.form.area = this.active.city.full_name.replace(/\s*/g,"");
        this.form.address = this.active.address;
        this.$refs.dialog.open();
      },
      setToDefault() {
        let id = this.active.id;
        console.log(id)
        this.$http({
          url:`/api/users/set_default_org/`,
          method:'post',
          data:{
            org_id:id
          }
        }).then(res=>{
          console.log(res)
          if(res.statusCode == 200 ||res.statusCode == 201){
            uni.showToast({
              title: res.data.msg||'设置成功',
              icon:'none',
            });
            this.defaultOrgId = id;
            this.updateUser();
          }
        })
      },
      formChange() {
        let id = this.active.id;
        this.$http({
          url: `/api/orgs/${id}/`,
          data: {
            ...this.form
          },
          method: 'patch',
        }).then(res => {
          if (res.statusCode == 200) {
            uni.showToast({
              title: '修改成功',
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
        let select = this.selectedList.find(item => item.id == data.id)
        if (select) {
          // 不能用index直接删, selectedList用户操作选取,乱序
          this.selectedList.forEach((item, i) => {
            if (select.id == item.id) {
              this.selectedList.splice(i, 1);
              if (this.selectedList.length == 1) {
                this.setAc(this.selectedList[0])
              }
            }
          })
        } else {
          this.selectedList.push(data);
          this.setAc(data)
        }
      },

      setAc(data) {
        this.active = data;
      },
    }
  }
</script>

<style lang="scss" scoped>
  .page {
    .title-center {
      flex: 1;
      text-align: center;
      color: $mainTitle;
    }

    // margin-top:10rpx;
    .boxbody {
      display: flex;
      align-items: center;

      .left {
        flex: 1;

        .title {
          color: #000000CC;
          font-size: 30rpx;
        }

        .content {
          color: #00000080;
          margin-top: 20rpx;
        }
      }

      .right {}
    }
  }

  .item-left {
    flex: 1;
    display: flex;
    flex-direction: column;

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
</style>
