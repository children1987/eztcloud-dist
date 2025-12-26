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
      <!-- 添加 -->
      <uni-icons type="plus" class="icons" size="26" v-if="!isEditMode" @click="add" />
      <!-- 全选 -->
      <text class="iconfont icon-quanxuan " :style="selectedList.length == dataList.length ? 'color: #22be49' : '' "
 v-if="isEditMode" @click="selection"></text>
    </view>
  </u-page-title>
  <!-- <uni-nav-bar shadow left-icon="left" right-icon="compose" title="组织管理" leftText="" @clickLeft="goBack" @clickRight="goEdit" /> -->
  <u-page-content>
    <view class="page-content">
      <view class="" style="margin-right: 500rpx;">
        <picker style="border:none;" class="picker" @change="searchOrgChange" :value="searchOrgIndex" :range="orgArray" range-key="name">
          <view class="uni-input">
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
          <view class="item-left">
            <view class="title">{{item.name}}</view>
            <view class="content">设备数量：{{item.device_count}}</view>
          </view>
          <view class="item-right">
            <u-is-select v-if="isEditMode" :select="isSelect(item)" @click.native="clickOnRadio(item,index)" />
            <text v-else>
              <!-- <text v-if="active && item.id == active.id" style="color:#49A6FDFF;" >默认组织</text> -->
            </text>
          </view>
        </u-list-item>
      </view>
      <!-- bottom handle area-->
      <view class="b-button-box" v-if="isEditMode">
        <view class="b-button-item" v-if="(selectedList.length == 1)" @click="edit">
          <text class="iconfont icon-zhongmingming"></text>
          重命名
        </view>

        <view class="b-button-item" v-if="selectedList.length" @click="batchDelete">
          <text class="iconfont icon-shanchu"></text>
          删除
        </view>
      </view>
    </view>
  </u-page-content>
  <!-- edit -->
  <u-dialog ref="dialog" @confirm="formChange">
    <uni-forms ref="form" :rules="form" label-width="160rpx" label-align="right">
      <uni-forms-item label="所属组织">
        <picker class="picker" @change="bindOrgChange" :value="orgIndex" :range="orgArray" range-key="name">
          <view class="uni-input">
            <text class="right-text"> {{ orgIndex == null ? '请选择' : orgArray[orgIndex].name }}</text>
            <uni-icons type="bottom" size="10" class="row-bottom"></uni-icons>
          </view>
        </picker>
      </uni-forms-item>
      <uni-forms-item label="单元名称" name="name">
        <uni-easyinput v-model="form.name" placeholder="请输入" />
      </uni-forms-item>
    </uni-forms>
  </u-dialog>
</view>
</template>

<script>
export default {
  data() {
    return {
      search: {
        org: ''
      },
      pageOptios: {
        page: 1,
        page_size: 10,
      },
      next: false,
      active: {},
      isEditMode: false, // 是否编辑模式
      selectedList: [], // 已选中
      form: {
        org_id: '',
        name: ''
      },
      dataList: [],
      orgIndex: null,
      searchOrgIndex: null,
      orgArray: [],
      userInfo:{},
    }
  },
  onLoad() {
    this.getUserInfo();
    this.onSearch(true);
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
    getOrg() {
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
    searchOrgChange(e) {
      let index = e.detail.value;
      this.searchOrgIndex = index;
      this.search.org = this.orgArray[index].id;
      this.onSearch(true);
    },
    bindOrgChange(e) {
      let index = e.detail.value;
      this.orgIndex = index;
      this.form.org_id = this.orgArray[index].id;
    },
    onSearch(init = false) {
      if (init) {
        this.pageOptios.page = 1;
      }
      this.$http({
        url: '/api/org_units/',
        data: {
          org: this.search.org,
          ...this.pageOptios
        },
        method: 'get',
      }).then(res => {
        if (res.statusCode == 200) {
          let list = res.data.results.map(item => {
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
    batchDelete() {
      let ids = this.selectedList.map(item => item.id);
      this.$http({
        url: '/api/org_units/batch_delete/',
        method: 'post',
        data: {
          id_list: ids
        }
      }).then(res => {
        // console.log(res)
        if (res.statusCode == 200) {
          this.confirmEditor();
          this.onSearch(true);
        }
      })
    },
    async formChange() {
      let id = this.active.id;
      let result;

      if (id) {
        result = await this.$http({
          url: `/api/org_units/${id}/`,
          data: {
            ...this.form
          },
          method: 'patch',
        })
        this.confirmEditor();
      } else {
        result = await this.$http({
          url: `/api/org_units/`,
          data: {
            ...this.form
          },
          method: 'post',
        })
      }
      console.log(result)
      if (result.statusCode == 200 || result.statusCode == 201) {
        uni.showToast({
          title: result.data.msg || '操作成功',
          icon: 'none',
        });
        this.onSearch(true)
      }
    },
    edit() {
      console.log(this.active)
      this.form.name = this.active.name;
      this.form.org_id = this.active.org.id;
      this.$refs.dialog.open();
      if (this.active.org) {
        this.orgIndex = this.orgArray.findIndex(item => item.id == this.active.org.id);
      } else {
        this.orgIndex = null;
      }
    },
    add() {
      this.active = {};
      this.form.name = '';
      this.form.org_id = '';
      this.$refs.dialog.open();
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

  // margin-top:10rpx;
  .boxbody {
    display: flex;
    align-items: center;
    padding: 25rpx 0rpx;

    .title {
      color: #000000CC;
      font-size: 30rpx;
      width: 200rpx;
    }

    .content {
      color: #00000080;
      margin-left: 30rpx;
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
  // flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0rpx;

  .title {}

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
  flex: 0.7;
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

.picker {
  height: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;

  .uni-input {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    height: 72rpx;
    justify-content: space-between;
    align-items: center;
    padding: 0rpx 20rpx;

    .right-text {
      color: #999;
      font-size: 12px;
    }
  }
}


</style>
