/**
 * CyberRacer Game Engine
 * Three.js based 3D racing visualization
 */

class GameEngine {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.car = null;
        this.carSpeed = 0;
        this.carRotation = 0;
        this.carPosition = { x: 0, z: 0 };
        
        this.carModels = [];
        this.currentCarIndex = 0;
        
        this.initialized = false;
    }

    async initialize() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a2a4a);
        this.scene.fog = new THREE.Fog(0x1a2a4a, 100, 1000);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth * 0.65 / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 3, 8);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        const canvas = document.getElementById('three-canvas');
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(window.innerWidth * 0.65, window.innerHeight - 100);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x00ff88, 0.5);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 10);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);

        // Track
        this.createTrack();

        // Load car models
        await this.loadCarModels();

        // Animation loop
        this.animate();

        this.initialized = true;
    }

    createTrack() {
        // Road plane
        const roadGeometry = new THREE.PlaneGeometry(20, 100);
        const roadMaterial = new THREE.MeshStandardMaterial({
            color: 0x222222,
            metalness: 0.3,
            roughness: 0.8
        });
        const road = new THREE.Mesh(roadGeometry, roadMaterial);
        road.rotation.x = -Math.PI / 2;
        road.castShadow = true;
        road.receiveShadow = true;
        this.scene.add(road);

        // Road markings
        const markingGeometry = new THREE.PlaneGeometry(0.5, 100);
        const markingMaterial = new THREE.MeshStandardMaterial({
            color: 0xffff00,
            emissive: 0xffff00,
            emissiveIntensity: 0.5
        });
        const marking = new THREE.Mesh(markingGeometry, markingMaterial);
        marking.rotation.x = -Math.PI / 2;
        marking.position.z = 0;
        marking.position.y = 0.01;
        this.scene.add(marking);

        // Side walls
        const wallGeometry = new THREE.BoxGeometry(1, 5, 100);
        const wallMaterial = new THREE.MeshStandardMaterial({
            color: 0x00ff88,
            emissive: 0x00ff88,
            emissiveIntensity: 0.2
        });

        const leftWall = new THREE.Mesh(wallGeometry, wallMaterial);
        leftWall.position.x = -11;
        leftWall.position.y = 2;
        this.scene.add(leftWall);

        const rightWall = new THREE.Mesh(wallGeometry, wallMaterial);
        rightWall.position.x = 11;
        rightWall.position.y = 2;
        this.scene.add(rightWall);
    }

    async loadCarModels() {
        // Wait for GLTFLoader to be available
        if (!window.GLTFLoader && !THREE.GLTFLoader) {
            console.error('GLTFLoader not loaded. Models will not render.');
            return;
        }

        const loader = new (window.GLTFLoader || THREE.GLTFLoader)();
        const carFiles = [
            '../assets/carred.glb',
            '../assets/carblue.glb',
            '../assets/cargreen.glb',
            '../assets/caryellow.glb',
            '../assets/carwhite.glb',
            '../assets/carblack.glb'
        ];

        for (const file of carFiles) {
            try {
                const gltf = await new Promise((resolve, reject) => {
                    loader.load(file, resolve, undefined, reject);
                });

                const model = gltf.scene;
                model.scale.set(0.1, 0.1, 0.1);
                model.castShadow = true;
                model.receiveShadow = true;

                // Hide initially
                model.visible = false;
                this.scene.add(model);
                this.carModels.push(model);
            } catch (error) {
                console.warn(`Failed to load ${file}:`, error);
            }
        }

        if (this.carModels.length > 0) {
            this.car = this.carModels[0];
            this.car.visible = true;
        }
    }

    updateFromGesture(gestureData) {
        if (!this.car) return;

        const gesture = gestureData.gesture;
        const maxSpeed = 0.5;
        const acceleration = 0.02;

        // Update speed based on gesture
        if (gesture === 'OPEN_PALM') {
            this.carSpeed = Math.min(this.carSpeed + acceleration, maxSpeed);
        } else if (gesture === 'FIST') {
            this.carSpeed = Math.max(this.carSpeed - acceleration * 2, -maxSpeed * 0.5);
        } else {
            // Friction
            this.carSpeed *= 0.95;
        }

        // Update rotation based on gesture
        if (gesture === 'POINT') {
            this.carRotation += 0.05;
        } else if (gesture === 'THUMBS_UP') {
            this.carRotation -= 0.05;
        }

        // Update position
        this.carPosition.x += Math.sin(this.carRotation) * this.carSpeed;
        this.carPosition.z += Math.cos(this.carRotation) * this.carSpeed;

        // Boundary collision
        if (this.carPosition.x > 8) this.carPosition.x = 8;
        if (this.carPosition.x < -8) this.carPosition.x = -8;

        // Update car transform
        this.car.position.x = this.carPosition.x;
        this.car.position.z = this.carPosition.z;
        this.car.rotation.y = this.carRotation;

        // Update camera to follow car
        const cameraDistance = 8;
        this.camera.position.x = this.carPosition.x + Math.sin(this.carRotation + Math.PI) * cameraDistance;
        this.camera.position.z = this.carPosition.z + Math.cos(this.carRotation + Math.PI) * cameraDistance;
        this.camera.position.y = 4;
        this.camera.lookAt(
            this.carPosition.x,
            0.5,
            this.carPosition.z
        );
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    getCarState() {
        return {
            speed: this.carSpeed,
            position: { ...this.carPosition },
            rotation: this.carRotation
        };
    }

    switchCar(index) {
        if (index < 0 || index >= this.carModels.length) return;

        if (this.car) {
            this.car.visible = false;
        }

        this.currentCarIndex = index;
        this.car = this.carModels[index];
        this.car.visible = true;
    }
}

const gameEngine = new GameEngine();
export { gameEngine };
