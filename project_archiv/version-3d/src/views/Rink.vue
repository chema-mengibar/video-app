

<script>

import SvgRink from '../components/SvgRink.vue'

export default {
  name: "Rink",
  inject: ["$services"],
  data: () => ({
    t: {},
    data: null,
    model:{
      targetPlayerId: ''
    }
  }),
  methods: {
    centerFirst: function () {
      this.$services.toolService.centerFirst();
    },
    nextGame: function () {
      this.$services.toolService.nextGame();
    },
    load: function () {
      const _ = this;
      this.$services.toolService.flow_prepare();
    },
  },
  created() {
    const _ = this;
    _.t = this.$services.localeService.D();
  },
  components:{
    SvgRink
  },
  mounted() {
    this.$nextTick();
    this.load();
  },
};
</script>

<style  lang="scss">
@import "../styles/media";

#app {
  position: relative;
}

.info-panel {
  position: absolute;
  top: 10px;
  right: 10px;
}

.toolbar {
  padding: 20px;
  position: absolute;
  top: 0;
  left: 0;
  right:0;
  margin:0 auto;
  display: flex;
  background-color: rgba(0, 0, 0, 0.1);
  width: calc(100vw - 400px);
  display: flex;
  gap: 20px;
  z-index:200;
}

.tool {
  &.full {
    flex: 1;
  }

  input {
    width: 100%;
  }

  button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    &:hover {
      background-color: #0056b3;
    }
  }
}

.team-wrapper {
  border: 1px solid rgba(255, 255, 255, 0.5);
  padding: 3px 11px;
  border-radius: 5px;
  display: flex;
  gap: 7px;
  align-items: center;

  .team {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    &[data-team="home"] {
      background-color: red;
    }
    &[data-team="guest"] {
      background-color: white;
    }
  }
}

.top-rink {
  position: absolute;
  top: 0;
  left: 0;
  padding: 5px;
  z-index:3000;


  svg{
    width:200px;
    height:auto;
  }
  
}

.controls {
  position: absolute;
  z-index: 100;
  width: 100vw;
  height: 100vh;
  top: 0;
  left: 0;

  .control {
    position: absolute;
    width: 200px;
    height: 200px;
    //background-color: rgba(255, 56, 30, 0.589);


    $colorLine : 1px solid rgba(255, 0, 0, 0.5);

    &.cl {
      top: 0;
      left: 0;
      margin: auto 0;
      bottom: 0;
       height: 100vh;
       border-right: $colorLine;
    }
    &.cr {
      top: 0;
      right: 0;
      margin: auto 0;
      bottom: 0;
       height: 100vh;
              border-left:  $colorLine;
    }
    &.bc {
      bottom: 0;
      left: 0;
      right: 0;
      margin: 0 auto;
      width: calc(100vw - 420px);
             border-top:  $colorLine;
    }
  }
}
</style>

<template>
  <div id="main-frame"></div>

  <div class="top-rink">
    <div class="line tl"></div>
    <div class="line tr"></div>
    <div class="line bl"></div>
    <div class="line br"></div>
    <div id="top-rink" class="players-wrapper">
      <SvgRink />
    </div>
  </div>

  <div class="info-panel">
    <div class="team-wrapper" :data-team="$services.toolService.team">
      <div class="team" :data-team="$services.toolService.team"></div>
      {{ $services.toolService.team }}
    </div>
    <div id="display"></div>
  </div>

  <div class="toolbar">
   <div class="tool">
      <button v-on:click="$services.visualsService.clearSceneVisual()">VX</button>
      <button v-on:click="$services.toolService.fullScreen()">F</button>
      <button v-on:click="$services.visualsService.draw_lines(model.targetPlayerId)">D</button>

       <select v-model="model.targetPlayerId" >
        <option value="player-h-1">H 1</option>
        <option value="player-h-2">H 2</option>
        <option value="player-h-3">H 3</option>
        <option value="player-h-4">H 4</option>

        <option value="player-g-1">G 1</option>
        <option value="player-g-2">G 2</option>
        <option value="player-g-3">G 3</option>
        <option value="player-g-4">G 4</option>
      </select>

    </div>
    <div class="tool full">
      <input type="range" id="cam-slider" min="-240" max="240" value="0" />
    </div>
    <div class="tool"><button v-on:click="nextGame()">N</button></div>
  </div>

  <div id="controls" className="controls">
    <div id="control-l"   v-on:click="$services.toolService.rotate('left')" className="control cl"></div>
    <div id="control-r" v-on:click="$services.toolService.rotate('right')"  className="control cr"></div>
    <div id="control-b"  v-on:click="$services.toolService.centerFirst()" className="control bc"></div>
  </div>
</template>