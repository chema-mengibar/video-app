import { reactive } from 'vue';
import * as THREE from 'three';

export default class VisualsService {

  constructor() {


    this.scene = null;
    this.renderCallback = null;
    this.players = null;


  }

  getPosition(playerId) {
    const g = document.getElementById(playerId);
    const transform = g.getAttribute("transform");
    const match = transform.match(/translate\(([^,]+),\s*([^)]+)\)/);
    return { x: parseFloat(match[1]), y: parseFloat(match[2]) };
  }

  setScene(_scene, _callback, _players) {
    this.scene = _scene;
    this.renderCallback = _callback;
    this.players = _players;
  }

  svgToRink3D(svgPos) {
    const rinkWidth = 26;   // metros
    const rinkLength = 44;  // metros
    const svgWidth = 260;
    const svgHeight = 440;

    // Normaliza y centra
    const x3D = (svgPos.x / svgWidth) * rinkWidth - rinkWidth / 2;
    const z3D = (svgPos.y / svgHeight) * rinkLength - rinkLength / 2;

    return new THREE.Vector3(x3D, 0.3, z3D); // Y es altura, XZ es el plano del rink
  }




  line_rebound(p1_id, p2_id, band = 'left') {
    const from = this.getPosition(p1_id);
    const to = this.getPosition(p2_id);
    // const obstacle = this.getPosition(obstacle_id );

    const reboundX = band === 'left' ? 0 : 260; // 0 banda iquierda, 260 banda derecha
    const reboundY = from.y + (to.y - from.y) / 2; // mitad de camino hacia el destino

    const svg = document.getElementById("svg-data");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");

    // const distanceToObstacle = Math.hypot(obstacle.x - reboundX, obstacle.y - reboundY);

    // if (distanceToObstacle < 30) {
    //   // Si está muy cerca del defensor, subimos el rebote para esquivarlo
    //   console.log("Rebote cerca del defensor. Ajustando trayectoria...");
    //   reboundY -= 40;
    // }

    const d = `
      M ${from.x} ${from.y}
      L ${reboundX} ${reboundY}
      L ${to.x} ${to.y}
    `;

    path.setAttribute("d", d.trim());
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "#00ff00");
    path.setAttribute("stroke-width", "2");
    path.setAttribute("stroke-dasharray", "4,4"); // estilo de pase

    svg.appendChild(path);
  }

  line_direct(p1_id, p2_id,) {
    const coor1 = this.getPosition(p1_id);
    const coor2 = this.getPosition(p2_id);
    const svg = document.getElementById("svg-data");
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", coor1.x);
    line.setAttribute("y1", coor1.y);
    line.setAttribute("x2", coor2.x);
    line.setAttribute("y2", coor2.y);
    line.setAttribute("stroke", "#00ff00");
    line.setAttribute("stroke-width", "2");
    svg.appendChild(line);
  }


  draw3DLine(p1_id, p2_id) {

    const p1 = this.players[p1_id];
    const p2 = this.players[p2_id];

    const points = [
      new THREE.Vector3(p1.x, 0.1, p1.z),
      new THREE.Vector3(p2.x, 0.1, p2.z),
    ];

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ color: 0x00ff00 }); // verde fuerte

    const line = new THREE.Line(geometry, material);
    line.name = '___line' + Date.now();

    this.scene.add(line);
    this.renderCallback();
  }



  draw3DReboundLine(p1_id, p2_id, band = 'left') {

    const p1 = this.players[p1_id];
    const p2 = this.players[p2_id];

    const reboundY = band === 'left' ? 13 : -13; // 13 banda iquierda, -13 banda derecha
    const reboundX = p1.x + (p2.x - p1.x) / 2; // mitad de camino hacia el destino

    const points = [
      new THREE.Vector3(p1.x, 0.1, p1.z),
      new THREE.Vector3(reboundX, 0.1, reboundY),
      new THREE.Vector3(p2.x, 0.1, p2.z),
    ];

    points.forEach(p => {
      if (isNaN(p.x) || isNaN(p.y) || isNaN(p.z)) {
        console.error('Vector3 con NaN:', p);
      }
    });


    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ color: 0x00ff00 }); // verde fuerte

    const line = new THREE.Line(geometry, material);
    line.name = '___line' + Date.now();

    this.scene.add(line);
    this.renderCallback();
  }


  draw_lines(targetId) {

    try{
      const playerFirst = Object.entries(this.players).find(([k, o], index) => {
        return o.isFirst
      });
  
      if (!playerFirst || !targetId) { return }
  
      const playerFirstId = playerFirst[0];
  
      if (playerFirstId  === targetId) { return }
  
      this.line_rebound(playerFirstId, targetId, 'right')
      this.line_rebound(playerFirstId, targetId, 'left')
      this.line_direct(playerFirstId, targetId)
  
      this.draw3DReboundLine(playerFirstId, targetId, 'left')
      this.draw3DReboundLine(playerFirstId, targetId, 'right')
      this.draw3DLine(playerFirstId, targetId)
    } catch(e){
      console.error('[VisualsServices] draw_lines', e)
    }

    
  }


  clearSceneVisual() {
    const toRemove = [];

      const g = document.getElementById("svg-data");
      while (g.firstChild) {
          g.removeChild(g.firstChild);
      }

      this.scene.traverse((o) => {
          if (o.name && o.name.includes('___line')) {
              toRemove.push(o);
          }
      });

      toRemove.forEach((o) => {
          if (o.geometry) o.geometry.dispose();

          if (o.material) {
              if (Array.isArray(o.material)) {
                  o.material.forEach(m => m.dispose());
              } else {
                  o.material.dispose();
              }
          }

          this.scene.remove(o);
      });
  }




}