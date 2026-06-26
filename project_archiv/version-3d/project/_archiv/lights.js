       // // Luz puntual para dar calidez y profundidad
        // const pointLight = new THREE.PointLight(0xffffff, 1, 100);
        // pointLight.position.set(5, 10, 5);
        // pointLight.castShadow = true;
        // this.scene.add(pointLight);
        // const pointLight_helper = new THREE.PointLightHelper(pointLight, 5, 0xff0000); // tamaño y color del helper
        // this.scene.add(pointLight_helper);



                // Luz direccional simulando luces del techo
                const dirLight = new THREE.DirectionalLight(0xffffff, 1);
                dirLight.position.set(10, 20, 10);
                dirLight.castShadow = true;
                dirLight.shadow.mapSize.width = 2048;
                dirLight.shadow.mapSize.height = 2048;
                dirLight.shadow.camera.near = 1;
                dirLight.shadow.camera.far = 50;
                this.scene.add(dirLight);