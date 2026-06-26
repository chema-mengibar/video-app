 let b;

        this.scene.traverse(o => {
            // dist-1
            // dist-2


            // if(o.name.includes('dummy')){
            //   let parent = o.parent;
            //     parent.remove( o );
            //    console.log(parent)

            //   // const selectedObject = _.scene.getObjectByName(o.name);
            //   //  _.scene.remove( parent );
            //   // console.log(selectedObject)
            // }

           


            if (o.name.includes('player-')) {


                // if (!o.name.includes('goalie')) {
                //     o.position.x = _.players[o.name].x;
                //     o.position.z = _.players[o.name].z;
                //     // o.rotation.y = 4.5;
                // }

                o.children.forEach((child, idx) => {

                    o.visible = false;

                    console.log(o.position)

                    const loaderImage = new THREE.TextureLoader();
                    loaderImage.load('/b.png', (texture) => {
                        const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
                        const sprite = new THREE.Sprite(material);
                        sprite.scale.set(1.4, 1.8, 1);
                        sprite.position.set(
                            o.position.x,
                            o.position.y + .8,
                            o.position.z);
                        this.scene.add(sprite);
                    });

             

                    if (o.name === 'player-g-1') {
                        b = o
                    }

                    // // player color: home or guest
                    // let color = o.name.includes('-h') ? '#ff0000' : '#0000ff'
                    // let opacity = 1;

                    // if (o.name === 'player-h-0') {
                    //     color = '#b32d93'
                    // }

                    // // basis circle in player
                    // if (idx === 1) {
                    //     color = o.name.includes('-h') ? '#880000' : '#000088'
                    //     if (o.name === 'player-h-0') {
                    //         color = '#ff9ce8'
                    //     }
                    //     opacity = 0.8;
                    // }

                    // // numbers
                    // if (idx > 1) {
                    //     color = '#000000'

                    //     opacity = 1;
                    // }

                    // const m = new THREE.MeshBasicMaterial({ color: color })
                    // m.side = THREE.DoubleSide;
                    // m.side = THREE.DoubleSide;
                    // m.opacity = opacity;
                    // m.transparent = true;
                    // m.needsUpdate = true;
                    // child.material = m;





                })

       

                if (o.name === 'player-h-0') {
                    _.camera.position.x = _.players[o.name].x;
                    _.camera.position.z = _.players[o.name].z;
                    _.camera.position.y = 1;

                    const pt = new THREE.Vector3(b.position.x, 1.7, o.position.z)
                    _.camera.lookAt(pt);

                }
            }
        })