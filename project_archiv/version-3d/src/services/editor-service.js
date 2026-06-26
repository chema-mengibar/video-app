import { reactive } from 'vue';
import Games from './tool/Games'

export default class EditorService {

  constructor() {
    this._data = reactive({
      
    })

    this.gamesList  = Games.sort((a, b) => {
        const numA = parseInt(a.id.match(/\d+/)?.[0] ?? 0);
        const numB = parseInt(b.id.match(/\d+/)?.[0] ?? 0);
        return numA - numB;
    });
   
  }

  get games(){
    return this.gamesList;
  }

  getGameByIdex( idx ){
    return this.gamesList[idx];
  }
}