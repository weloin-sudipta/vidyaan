<template>
  <div class="min-h-screen bg-[#f8fafc] flex items-center justify-center p-6 relative overflow-hidden font-sans">
    
    <div class="absolute inset-0 z-0 opacity-[0.03] pointer-events-none" 
         style="background-image: radial-gradient(#6366f1 1px, transparent 1px); background-size: 30px 30px;">
    </div>

    <div class="relative z-10 w-full max-w-6xl flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
      
      <div class="w-full lg:w-1/2 h-[400px] md:h-[600px] relative">
        <div ref="threeContainer" class="w-full h-full"></div>
        
        <div class="absolute top-10 left-1/2 -translate-x-1/2 lg:left-10 lg:translate-x-0 bg-indigo-600 text-white px-4 py-2 rounded-full shadow-xl flex items-center gap-3">
           <i class="fa fa-cog fa-spin text-xs"></i>
           <p class="text-[9px] font-black uppercase tracking-[0.2em]">Optimization in Progress: 82%</p>
        </div>
      </div>

      <div class="w-full lg:w-1/2 text-center lg:text-left space-y-8">
        <div class="relative">
          <span class="text-indigo-500 text-xs font-black uppercase tracking-[0.5em] block mb-4 relative z-10">
            Scheduled Maintenance
          </span>
          
          <h2 class="text-4xl md:text-6xl font-black text-slate-900 leading-[1.1] relative z-10">
            Improving the <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-purple-600">
              Foundation.
            </span>
          </h2>
          
          <p class="text-slate-500 font-medium mt-8 max-w-md mx-auto lg:mx-0 leading-relaxed text-sm md:text-base">
            We're currently fine-tuning our servers to provide a faster and smoother experience for all Vidyaan students. We'll be back online shortly.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row items-center gap-4 relative z-10">
          <div class="px-8 py-4 bg-white border-2 border-slate-100 rounded-2xl flex items-center gap-4 shadow-sm">
            <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
              <i class="fa fa-clock-o"></i>
            </div>
            <div class="text-left">
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-wider">Estimated Back</p>
              <p class="text-sm font-bold text-slate-700">In 45 Minutes</p>
            </div>
          </div>
          
          <button @click="copySupportEmail"
            class="px-8 py-4 bg-slate-900 text-white rounded-2xl font-black text-xs hover:bg-indigo-600 transition-all flex items-center gap-3">
            <i class="fa fa-envelope-o"></i>
            <span>Contact Support</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const threeContainer = ref(null)
let scene, camera, renderer, parentGroup, scannerPlane
let frameId

onMounted(() => {
  if (!threeContainer.value) return

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(75, threeContainer.value.clientWidth / threeContainer.value.clientHeight, 0.1, 1000)
  camera.position.z = 40

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(threeContainer.value.clientWidth, threeContainer.value.clientHeight)
  threeContainer.value.appendChild(renderer.domElement)

  // 1. The "Foundational" Structure (Wireframe Octahedron)
  parentGroup = new THREE.Group()
  const geometry = new THREE.OctahedronGeometry(12, 1)
  const material = new THREE.MeshPhongMaterial({ 
    color: 0x6366f1, 
    wireframe: true, 
    transparent: true, 
    opacity: 0.5 
  })
  const structure = new THREE.Mesh(geometry, material)
  parentGroup.add(structure)

  // 2. Add some "floating data nodes" around it
  for (let i = 0; i < 8; i++) {
    const nodeGeom = new THREE.BoxGeometry(2, 2, 2)
    const nodeMat = new THREE.MeshPhongMaterial({ color: 0xa855f7, wireframe: true })
    const node = new THREE.Mesh(nodeGeom, nodeMat)
    
    node.position.set(
      Math.random() * 30 - 15,
      Math.random() * 30 - 15,
      Math.random() * 30 - 15
    )
    parentGroup.add(node)
  }

  scene.add(parentGroup)

  // 3. Scanning Laser Plane
  const laserGeom = new THREE.PlaneGeometry(50, 2)
  const laserMat = new THREE.MeshBasicMaterial({ 
    color: 0x6366f1, 
    transparent: true, 
    opacity: 0.3, 
    side: THREE.DoubleSide 
  })
  scannerPlane = new THREE.Mesh(laserGeom, laserMat)
  scene.add(scannerPlane)

  // Lighting
  const light = new THREE.PointLight(0x6366f1, 2, 100)
  light.position.set(10, 10, 20)
  scene.add(light)
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))

  const animate = () => {
    frameId = requestAnimationFrame(animate)
    
    parentGroup.rotation.y += 0.005
    parentGroup.rotation.z += 0.002
    
    // Scanner move up and down automatically
    scannerPlane.position.y = Math.sin(Date.now() * 0.002) * 20
    
    renderer.render(scene, camera)
  }
  animate()

  // Interactivity: Mouse movement tilts the structure
  const handleMouseMove = (e) => {
    const x = (e.clientX / window.innerWidth) - 0.5
    const y = (e.clientY / window.innerHeight) - 0.5
    parentGroup.rotation.x = y * 0.5
    parentGroup.rotation.y = x * 0.5
  }
  window.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  cancelAnimationFrame(frameId)
  window.removeEventListener('mousemove', null)
})
</script>

<style scoped>
/* Smooth Fade-in animation */
.lg\:w-1\/2 {
  animation: slideUp 1s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>