import SceneDummy from './scenes/scene-dummy.json'
import Scene0 from './scenes/scene-0.json'
import Scene1 from './scenes/scene-1.json'
import Scene2 from './scenes/scene-2.json'
import Scene3 from './scenes/scene-3.json'
import Scene4 from './scenes/scene-4.json'
import Scene6 from './scenes/scene-6.json'
import Scene7 from './scenes/scene-7.json'
import Scene8 from './scenes/scene-8.json'


const scenes = [
    // SceneDummy, 
    Scene8,
    Scene7,
    Scene4,
    Scene0,
    Scene1,
    Scene2,
    Scene3,
    Scene6
].map(sceneJson => {

    const players = {};
    sceneJson.assets.forEach(assetItem => {
        players[assetItem.name] = {
            x: parseFloat(assetItem.loc.x),
            z: parseFloat(assetItem.loc.z),
            isFirst: sceneJson.meta.first === assetItem.name
        }
    })

    return {
        id: sceneJson.meta.name,
        "limits": {
            "x": 22.5,
            "z": 13.5
        },
        players: players
    }
})

export default scenes;


/*
"player-g-goalie",      "x": -20.09,     "z": 0.05
"player-h-goalie", "x": 20.09,        "z": -0.05


@PROMPT

tengo un rink de hockey patines en linea en 3d, las coordenadas de las desde el centro 0,0,0 son: 22.0  y 13.0. es decir
el rectangulo tiene los vertices en :
-22.0, -13.0
-22.0, 13.0
22.0, -13.0
22.0, 13.0



reparte la posicion de 8 jugadores, 4 por equipo , por el campo en una situacion real de juego.
 el portero va aparte, es decir solo la posicion de  son 2 defensas y 2 delanteros, que pueden estar adelantados, haberse quedado atras, desmarcarse, etc..
dame para cada jugador un json :

 {
    "name": "player-g-1",
    "loc": {
        "x": 7.08,
        "z": -2.84
    }
},

donde en el nombre aparece  -g- , -h- : home o guest y el numero de jugador:
1,2,3,4

elige a uno de los jugadores para la accion, es decir, el que tiene el puck, y cual seria la mejor decision que hacer: retroceder, tirar, pasar , avanzar
dame el nombre del jugador que has elegido, y un breve frase de la solucion.

dame una breve descripcion de la situacion del juego, quien ataca, defiende, etc.. en una frase


*/

