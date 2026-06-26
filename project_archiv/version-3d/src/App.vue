<script>
export default {
  inject: ['$services'],
  data: ()=>( {
      t: {},
  }),
  created(){
    this.t = this.$services.localeService.D();
  },
}
</script>

<style lang="scss">
  @import "./App.scss";
</style>

<template>
  <router-view />
</template>