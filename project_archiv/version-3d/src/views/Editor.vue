

<script>
import SvgRink from "../components/SvgRink.vue";

export default {
  name: "Editor",
  inject: ["$services"],
  data: () => ({
    t: {},
    data: {},
    selectedGame: null,

    defaultModel: {
      ["player-h-1"]: { x: 0.5, z: -0 },
      ["player-h-2"]: { x: 0.5, z: 6.9 },
      ["player-h-3"]: { x: 0.5, z: -6.6 },
      ["player-h-4"]: { x: 7.8, z: 0 },
      ["player-h-goalie"]: { x: 19.5, z: 0 },

      ["player-g-1"]: { x: -0.5, z: 0 },
      ["player-g-2"]: { x: -0.5, z: 6.9 },
      ["player-g-3"]: { x: -0.5, z: -6.6 },
      ["player-g-4"]: { x: -7.8, z: 0 },
      ["player-g-goalie"]: { x: -19.5, z: 0 },
    },
    model: {
      ["player-h-1"]: { x: 0.5, z: -0 },
      ["player-h-2"]: { x: 0.5, z: 6.9 },
      ["player-h-3"]: { x: 0.5, z: -6.6 },
      ["player-h-4"]: { x: 7.8, z: 0 },
      ["player-h-goalie"]: { x: 19.5, z: 0 },

      ["player-g-1"]: { x: -0.5, z: 0 },
      ["player-g-2"]: { x: -0.5, z: 6.9 },
      ["player-g-3"]: { x: -0.5, z: -6.6 },
      ["player-g-4"]: { x: -7.8, z: 0 },
      ["player-g-goalie"]: { x: -19.5, z: 0 },
    },
  }),
  methods: {
    mapData: function () {
      const data = {
        meta: {
          name: "",
          first: "",
        },
        assets: [],
      };

      Object.entries(this.model).forEach(([k, o], idx) => {
        const obj = {
          name: k,
          loc: {
            x: parseFloat(o.x),
            z: parseFloat(o.z),
          },
        };

        data.assets.push(obj);
      });

      return data;
    },
    handleSelectChange: function () {
      if (this.selectedGame === -1) {
        this.model = this.defaultModel;
        return;
      }

      if (this.selectedGame >= this.$services.editorService.games.length) {
        this.model = this.defaultModel;
        this.selectedGame = -1;
        return;
      }

      const game = this.$services.editorService.getGameByIdex(
        this.selectedGame
      );

      if (game) {
        Object.entries(game.players).forEach(([playerKey, o], idx) => {
          this.model[playerKey] = {
            x: parseFloat(o.x),
            z: parseFloat(o.z),
          };
        });
      }
    },
    render: function () {
      console.log(">>>>>>>>>");
      Object.entries(this.model).forEach(([playerKey, o], idx) => {
        console.log(o.x, o.z);
        const playerDom = document.getElementById(playerKey);
        const { left, top } = this.$services.toolService.helper_coordToPx(
          o.x,
          o.z
        );
        playerDom.setAttribute("transform", `translate(${left}, ${top})`);

        playerDom.addEventListener("dragend", () => {
          playerDom.style.opacity = "1";
          console.log(">>>>>>>>>");
        });
      });
    },
  },
  created() {
    const _ = this;
    _.t = this.$services.localeService.D();
  },
  components: {
    SvgRink,
  },
  computed: {
    modelEntries() {
      return Object.keys(this.model);
    },
  },
  mounted() {
    this.$nextTick();
    this.render();
  },

  watch: {
    model: {
      handler(curr, prev) {
        this.render();
      },
      deep: true,
    },
  },
};
</script>

<style  lang="scss">
@import "../styles/media";

#app {
  position: relative;
}

.editor {
  height: 100%;
  display: flex;

  .mirror {
    transform: rotate(180deg);
  }

  .rink {
    flex: 1;
    padding: 20px;

    svg {
      width: 100%;
      height: auto;
      max-height: 100%;
    }
  }

  .panel {
    flex: 1;
    padding: 20px;
    width: 400px;
    overflow: auto;
  }

  .console {
    flex: 1;
    padding: 20px;
    overflow: auto;
  }

  .block {
    margin: 10px 0;
    display: flex;
    flex-direction: column;

    &[data-team="home"] {
      input {
        margin-left: 20px;
        accent-color: #ff0000;
      }
    }

    &[data-team="guest"] {
      input {
        margin-left: 20px;
        accent-color: #070bff;
      }
    }

    label {
      margin-bottom: 10px;
    }

    input {
      margin-left: 20px;
    }
  }
}
</style>

<template>
  <div class="editor">
    <div class="rink">
      <SvgRink />
    </div>

    <div class="panel">
      <select v-model="selectedGame" @change="handleSelectChange">
        <option :value="-1">new</option>
        <option
          v-for="(game, idx) in $services.editorService.games"
          :key="game.id"
          :value="idx"
        >
          {{ game.id }} 
        </option>
      </select>
      <p>Seleccionaste: {{ selectedGame }}</p>

      <div
        :data-team="key.includes('-h') ? 'home' : 'guest'"
        class="block"
        v-for="key in modelEntries"
        :key="key"
      >
        <label>{{ key.replace("player-", "").replace("-", " ") }}</label>
        <input
          type="range"
          min="-22.0"
          max="22.0"
          step="0.1"
          v-model="model[key].x"
        />
        <input
          class="mirror"
          type="range"
          min="-13.0"
          max="13.0"
          step="0.1"
          v-model="model[key].z"
        />
      </div>
    </div>
    <pre class="console">{{ JSON.stringify(mapData(), null, 4) }} </pre>
  </div>
</template>


