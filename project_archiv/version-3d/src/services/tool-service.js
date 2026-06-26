import { reactive } from 'vue';
import * as THREE from 'three';
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import Games from './tool/Games'

const bgColor = '#444444'

export default class ToolService {

    scene = new THREE.Scene();
    loader = new GLTFLoader();

    camera = null
    renderer = null

    cameraTop = null
    rendererTop = null

    flow = {
        gameCursor: 0,
        crono: 5,
        cronoLimit: 5,
        firstCoords: null,
        pt: null,
        controlsMain: null,
        initialRotation: null
    }

    games = [];

    constructor( visualsService ) {
        this._data = reactive({
            state: '', // loading, loaded
            team: ''
        })

        this.visualsService  = visualsService
        this.games  = this.helper_shuffle(Games)
    }

    get team() {
        return this._data.team
    }

    get players() {
        if(this.games.length === 0){return null}
        return this.games[this.flow.gameCursor].players
    }

    get game() {
        if(this.games.length === 0){return null}
        return this.games[this.flow.gameCursor]
    }

    helper_shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1)); // índice aleatorio entre 0 e i
            [array[i], array[j]] = [array[j], array[i]];   // intercambio
        }
        const t =  [...array];
        console.log(t)
        return t;
    }
    

    renderCallbak(){
        this.renderer.render(this.scene, this.camera);
    }

    flow_prepare() {
        const _ = this;

        const camConfig = {
            fov: 75,
            aspect: window.innerWidth / window.innerHeight,
            aspect: 1.5,
            near: 0.1,
            far: 1000.0
        };

        this.camera = this.cameraBuilder(camConfig);
        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('main-frame').appendChild(this.renderer.domElement);
        this.scene.add(this.camera);
        this.scene.background = new THREE.Color(bgColor);

        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
     
        this.flow.controls = new FirstPersonControls(this.camera, this.renderer.domElement);
        this.flow.controls.lookSpeed = 0.1;
        this.flow.controls.movementSpeed = 5;
        this.flow.controls.lookVertical = false;

        // Bind
        this.flow_animate = this.flow_animate.bind(this)
        this.renderCallbak = this.renderCallbak.bind(this)
        this.onDocumentKeyDown = this.onDocumentKeyDown.bind(this)

        // Load
        this.loader.load('rink.glb', function (gltf) {

            const model = gltf.scene;
            const box = new THREE.Box3().setFromObject(model);
            const size = new THREE.Vector3();
            box.getSize(size); // → dimensiones: ancho, alto, profundidad
            const center = new THREE.Vector3();
            box.getCenter(center); // → centro del modelo
            
            // console.log('Tamaño del modelo:', size);
            // console.log('Centro del modelo:', center);  // Object { x: 0, y: 0.75, z: 0 }
            // console.log('Mínimo:', box.min);
            // console.log('Máximo:', box.max);

            _.flow_init_scene()
            _.scene.add(gltf.scene);
            _.step_bridge_visual();
            _.step_set_assets()
            _.step_set_control()
            _.display()
        }, undefined, function (error) {
            console.error('>>>>>>>>', error);
        });
    }


    flow_init_scene() {
        const _ = this;
        setTimeout(() => {
            this.addLight();
            // this.addGrid();
            _.renderer.render(_.scene, _.camera);
            this.flow_animate();
            document.addEventListener('keydown', this.onDocumentKeyDown, false);
        }, 0)
    }


    flow_animate() {

        this.scene.traverse((child) => {
            if (child.isMesh && child.geometry?.type === 'PlaneGeometry') {
                child.lookAt(this.camera.position);
            }
        });

        requestAnimationFrame(this.flow_animate)
        this.renderer.render(this.scene, this.camera)
    }

    step_set_control() {
        const slider = document.getElementById('cam-slider');
        slider.addEventListener('input', (event) => {
            const angleDeg = Number(event.target.value);
            const angleRad = THREE.MathUtils.degToRad(angleDeg); // conversión
            this.camera.rotation.y = angleRad;
        });
    }


    step_set_assets() {
        const _ = this;
        const imagesList = [1, 2]

        let targetCoords = null;

        const targets = {
            neutral: null,
            home: null,
            guest: null,
        };

        // rink-floor,   rink-wall, rink-center, rink-goal-2, rink-goal-1
        this.scene.traverse(o => {

            // rink-goal-1 guest, rink-goal-2 home
            // console.log(o.name)
            if (o.name === 'rink-center') {
            
                targets.neutral= {
                    x: o.position.x,
                    z: o.position.z,
                    team: 'neutral'
                }

            }else if( o.name === 'rink-goal-1' ){
                targets.guest = {
                    x: o.position.x,
                    z: o.position.z,
                }
            }
            else if( o.name === 'rink-goal-2' ){
                targets.home = {
                    x: o.position.x,
                    z: o.position.z,
                }
            }
            else if (o.name === 'rink-floor') {
                const m = new THREE.MeshStandardMaterial({ color: '#5CACFB', side: THREE.DoubleSide })
                o.material = m;
                o.receiveShadow = true;
                o.castShadow = true;
            }
            else if (o.name === 'rink-wall') {

                const m = new THREE.MeshStandardMaterial({ color: '#336699', side: THREE.DoubleSide })
                o.material = m;
            }
            else if (o.name === 'rink-wall-1') {
                const m = new THREE.MeshStandardMaterial({ color: '#ffffff', side: THREE.DoubleSide })
                o.material = m;
                o.needsUpdate = true;
            }
            else if (o.name === 'rink-wall-2') {
                const m = new THREE.MeshStandardMaterial({ color: '#ff0000', side: THREE.DoubleSide })
                o.material = m;
                o.needsUpdate = true;
            }

        });


        this.step_build_toprink();

        Object.keys(_.players).forEach(playerKey => {

            const playerData = _.players[playerKey];
            const team = playerKey.includes('-h-') ? `home` : `guest`;

            if (playerData.isFirst) {
            
                this._data.team = team;

                _.camera.position.set(playerData.x, 1, playerData.z);
                this.flow.firstCoords = _.camera.position.clone();
                this.flow.controls.object.position.set(playerData.x, 1, playerData.z);

                const geometry = new THREE.CircleGeometry(0.3, 32);
                const material = new THREE.MeshBasicMaterial({ color: 0xff0000, side: THREE.DoubleSide });
                const circle = new THREE.Mesh(geometry, material);
                circle.position.set(playerData.x, 0.1, playerData.z);
                circle.rotation.set(Math.PI / 2, 0, 0);
                circle.name = '___' + playerKey

                this.scene.add(circle);

                if(team === 'home'){
                    targetCoords = targets.guest
                }else{
                    targetCoords = targets.home
                }

                if (targetCoords) {
                    const pt = new THREE.Vector3(targetCoords.x, 1, targetCoords.z)
                    _.camera.lookAt(pt);

                    this.flow.initialRotation = _.camera.rotation.clone();
                    this.flow.controls.target = pt;
                    this.flow.pt = this.flow.controls.target.clone();
                    this.centerFirst()

                }
            } else {

                const index = Math.floor(Math.random() * imagesList.length);
                const imageNum = imagesList[index];
                const idxImagePlayerRef = playerKey.includes('goalie') ? 'g' : imageNum;
                const imageName = playerKey.includes('-h-') ? `h${idxImagePlayerRef}` : `g${idxImagePlayerRef}`;

                const loaderImage = new THREE.TextureLoader();
                loaderImage.load(`/${imageName}.png`, (texture) => {
                    texture.encoding = THREE.sRGBEncoding;
                    const material = new THREE.MeshLambertMaterial({
                        alphaTest: 0.5,
                        map: texture,
                        transparent: true,
                        side: THREE.DoubleSide,
                    });
                    const geometry = new THREE.PlaneGeometry(2, 2);
                    const plane = new THREE.Mesh(geometry, material);
                    plane.position.set(playerData.x, 0.92, playerData.z);
                    plane.lookAt(this.camera.position); // Siempre mirando a la cámara
                    plane.castShadow = true;
                    plane.receiveShadow = true;
                    plane.name = '___' + playerKey
                    this.scene.add(plane);
                });
            }
            this.helper_addCircle({x:playerData.x,  z: playerData.z}, team, playerKey);
        })
    }



    helper_coordToPx(x, z) {
        const rinkWidthPx = 260;   // ancho (eje Z)
        const rinkHeightPx = 440;  // alto (eje X)

        const rinkUnitsX = 44;     // unidades eje X (vertical)
        const rinkUnitsZ = 26;     // unidades eje Z (horizontal)

        const scaleX = rinkHeightPx / rinkUnitsX;  // px por unidad eje X (vertical)
        const scaleZ = rinkWidthPx / rinkUnitsZ;   // px por unidad eje Z (horizontal)

        // Rotar 180° (invertir x y z)
        const xRot = -x;
        const zRot = -z;

        const left = (zRot + rinkUnitsZ / 2) * scaleZ;

        // Espejo vertical (invertimos el top)
        const top = rinkHeightPx - (xRot + rinkUnitsX / 2) * scaleX;

        return { left, top };
      }


    step_build_toprink(){
        Object.keys(this.players).forEach(playerKey => {
            const playerData = this.players[playerKey];
            const r = this.helper_coordToPx(playerData.x, playerData.z);
            const playerDom = document.getElementById(playerKey); 
            playerDom.setAttribute('transform', `translate(${r.left}, ${r.top})`);
            playerDom.setAttribute('data-is-first', playerData.isFirst);
        });
    }

    step_load_game() {
        this.clearScene();
        if (this.flow.gameCursor < Games.length - 1) {
            this.flow.gameCursor += 1;
        } else {
            this.flow.gameCursor = 0;
        }

        this.step_bridge_visual();
        this.step_set_assets();
        this.display();
    }

    step_bridge_visual(){
        this.visualsService.setScene(this.scene, this.renderCallbak, this.players);
    }




    clearScene() {
        const toRemove = [];

        const g = document.getElementById("svg-data");
        while (g.firstChild) {
            g.removeChild(g.firstChild);
        }

        this.scene.traverse((o) => {
            if (o.name && o.name.includes('___')) {
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


    cameraBuilder(camConfig) {
        return new THREE.PerspectiveCamera(camConfig.fov, camConfig.aspect, camConfig.near, camConfig.far);
    }

    addLight() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 2);
        this.scene.add(ambientLight);

        const light = new THREE.DirectionalLight(0xffffff, .7);
        light.position.set(-22, 50, -13)
        light.intensity = 2;
        light.castShadow = true;
        light.target.position.set(0, 0, 0);
        light.shadow.mapSize.width = 2048;
        light.shadow.mapSize.height = 2048;
        light.shadow.camera.near = 1;
        light.shadow.camera.far = 100;
        light.shadow.camera.left = -20;
        light.shadow.camera.right = 20;
        light.shadow.camera.top = 20;
        light.shadow.camera.bottom = -20;
        this.scene.add(light)
    }

    addGrid() {
        const axesHelper = new THREE.AxesHelper(5);
        this.scene.add(axesHelper);
        const size = 46;       // Tamaño total del grid en metros (40x40)
        const divisions = size / 2;  // Para que cada casilla mida 2 metros (40/2 = 20)
        const color = 0x4f4f4e;
        const gridHelper = new THREE.GridHelper(size, divisions, color, color);
        gridHelper.position.set(-1, 0, 5);
        this.scene.add(gridHelper);
    }

    display() {
        const displayConatiner = document.getElementById('display');
        displayConatiner.innerHTML = 'Scene: ' + this.game.id;
    }


    // Actions

    onDocumentKeyDown(event) {
        if (!this.camera) { return; }

        event = event || window.event;
        const keycode = event.keyCode;

        console.log(keycode);

        switch (keycode) {
            case 96:
                this.centerFirst()
                break;
            case 37:
                this.rotate('left')
                break;
            case 38:
                this.moveCam('front')
                break;
            case 40:
                this.moveCam('back')
                break;
            case 39:
                this.rotate('right')
                break;
            case 96:
                this.step_load_game();
                break;
        }
    }

    moveCam(direction = 'left') {
        let x = this.camera.position.x;
        let z = this.camera.position.z;

        if (direction === 'back') {
            x += 0.1
        }
        else if (direction === 'front') {
            x -= 0.1
        }
        else if (direction === 'left') {
            z += 0.1
        }
        else if (direction === 'right') {
            z -= 0.1
        }

        const pt = this.flow.controls.target
        this.camera.position.set(x, this.camera.position.y, z);
        this.camera.lookAt(pt);
    }

    rotate(direction = 'left'){
        const slider = document.getElementById('cam-slider');
        const value = parseInt(slider.value,10);
        let angleDeg = value;
        const dif = 40;
         if (direction === 'left') {
            angleDeg += dif
        }
        else {
            angleDeg -= dif
        }
        const angleRad = THREE.MathUtils.degToRad(angleDeg); // conversión
        this.camera.rotation.y = angleRad;
        document.getElementById('cam-slider').value = angleDeg;
    }


    fullScreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        setTimeout(() => {

            this.renderer.setSize(window.innerWidth, window.innerHeight);
        }, 1000)
    }


    // Helpers

    raw(obj) {
        return JSON.parse(JSON.stringify(obj))
    }


    centerFirst() {
        // // CASE: FirstPerson controls
        this.camera.rotation.copy(this.flow.initialRotation);
        const cameraPos = this.camera.position;
        const target = new THREE.Vector3(this.flow.pt.x, cameraPos.y, this.flow.pt.z);
        const dir = new THREE.Vector3().subVectors(cameraPos, target);
        const angleRad = Math.atan2(dir.x, dir.z); // atan2 da el ángulo desde Z
        const angleDeg = THREE.MathUtils.radToDeg(angleRad);
        document.getElementById('cam-slider').value = angleDeg;
    }

    nextGame() {
        this.step_load_game()
    }


    helper_addCircle({x,z}, teamKey, playerKey){
        const radius = 1.80; // en metros
        const segments = 32;

        const circleGeometry = new THREE.CircleGeometry(radius, segments);

        const color = teamKey === 'home' ? 0xff0000 : 0xffffff
        const circleMaterial = new THREE.MeshBasicMaterial({ color, 
            transparent: true,
            opacity: 0.5,
            depthWrite: false,
            blending: THREE.NormalBlending, 
        }); 
        const circle = new THREE.Mesh(circleGeometry, circleMaterial);

        // Opcional: girar para que esté sobre el suelo
        circle.rotation.x = -Math.PI / 2;
        circle.position.set(x, 0.05, z);
        circle.name = '___circle' + playerKey

        // Añadir a la escena
        this.scene.add(circle);
    }

    helper_metersToPixels(meters, svgSize, realSize) {
        return (meters * svgSize) / realSize;
    }

    helper_pixelsToMeters(pixels, svgSize, realSize) {
        return (pixels * realSize) / svgSize;
    }

    helper_distancia(a, b) {
        const dx = b.x - a.x;
        const dz = b.z - a.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

}