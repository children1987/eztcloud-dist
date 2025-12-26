<template>
  <text style="color: #48A7FDFF;">
    {{!isClam?'获取验证码':num+'秒'}}
  </text>
</template>

<script>

export default {

  data() {
    return {
      isClam:false,
      num:0,
      timer:null
    }
  },
  props: {
    countdown: {
      type: Number,
      default:60,
    },
    url:{
      type:String,
      default:'/api/users/send_register_code/'
    }
  },
  methods: {
    setClam(){
      this.isClam = true;
      this.num = this.countdown;
      this.timer = setInterval(()=>{
        this.num--;
        if(this.num == 0){
          clearInterval(this.timer);
          this.isClam = false;
        }
      },1000)
    },
    getSms(data){
      if(this.isClam) return
      this.$http({
         url:this.url,
         method:'post',
         data
       }).then(res=>{
         if(res.statusCode == 200){
           uni.showToast({
             title: res.data.msg,
             icon:'none',
           });
           if(res.data.result != 'error'){
            this.setClam();
           }
         }
       })
   }

  }
}
</script>

<style lang="scss" scoped>

</style>
