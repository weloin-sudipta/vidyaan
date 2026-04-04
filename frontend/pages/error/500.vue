<template>
  <div class="min-h-screen bg-white flex items-center justify-center p-6 relative overflow-hidden font-sans">
    
    <div class="absolute inset-0 z-0 pointer-events-none">
      <div class="meltdown-gradient"></div>
    </div>

    <div class="relative z-10 w-full max-w-6xl flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
      
      <div class="w-full lg:w-1/2 h-[350px] md:h-[550px] relative">
        <div ref="threeContainer" class="w-full h-full cursor-wait"></div>
        
        <div class="absolute bottom-4 lg:bottom-12 left-1/2 -translate-x-1/2 lg:left-0 lg:translate-x-0 bg-red-500/10 backdrop-blur-xl border border-red-500/20 px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3">
           <span class="relative flex h-2 w-2">
             <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
             <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
           </span>
           <p class="text-[10px] font-black text-red-400 uppercase tracking-[0.2em]">
             CRITICAL: Logic Circuit Overload
           </p>
        </div>
      </div>

      <div class="w-full lg:w-1/2 text-center lg:text-left space-y-8">
        <div class="relative">
          <h1 class="text-8xl md:text-[12rem] font-black text-white/[0.03] absolute -top-10 lg:-top-24 left-0 lg:left-[-60px] select-none leading-none">
            500
          </h1>
          
          <span class="text-red-500 text-xs font-black uppercase tracking-[0.5em] block mb-4 relative z-10">
            Internal Server Error
          </span>
          
          <h2 class="text-4xl md:text-6xl font-black text-slate-400 leading-[1.1] relative z-10">
            Engine <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-purple-500">
              Overheated.
            </span>
          </h2>
          
          <p class="text-slate-400 font-medium mt-8 max-w-md mx-auto lg:mx-0 leading-relaxed text-sm md:text-base">
            Our servers are having a bit of a meltdown. Our engineers have been paged to cool things down. Please try refreshing in a moment.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row items-center gap-4 relative z-10">
          <button @click="handleRefresh" 
            class="w-full sm:w-auto px-10 py-4 bg-white text-slate-900 rounded-[1.5rem] font-black text-xs hover:bg-red-500 hover:text-white transition-all shadow-2xl shadow-red-500/20 flex items-center justify-center gap-3">
            <i class="fa fa-refresh text-[10px]"></i>
            <span>Re-check</span>
          </button>
          
          <NuxtLink to="/" 
            class="w-full sm:w-auto px-10 py-4 bg-slate-800 text-white border border-slate-700 rounded-[1.5rem] font-black text-xs hover:bg-slate-700 transition-all flex items-center justify-center gap-3">
            <i class="fa fa-home text-[10px]"></i>
            <span>Escape to Safety</span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const threeContainer = ref(null)
let scene, camera, renderer, sun, planetGroup
let mouseX = 0, mouseY = 0
let frame = 0

const handleRefresh = () => window.location.reload()

onMounted(() => {
  if (!threeContainer.value) return

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(75, threeContainer.value.clientWidth / threeContainer.value.clientHeight, 0.1, 1000)
  camera.position.z = 40

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(threeContainer.value.clientWidth, threeContainer.value.clientHeight)
  threeContainer.value.appendChild(renderer.domElement)

  // 1. The Glitching Sun
  const sunGeom = new THREE.SphereGeometry(7, 32, 32)
  const sunMat = new THREE.MeshPhongMaterial({ 
    color: 0x6366f1, 
    emissive: 0xff0000, // Red glow for error
    emissiveIntensity: 0.5,
    wireframe: true // Makes it look technical/broken
  })
  sun = new THREE.Mesh(sunGeom, sunMat)
  scene.add(sun)

  // 2. Eratic Planet
  planetGroup = new THREE.Group()
  const planetGeom = new THREE.SphereGeometry(2, 16, 16)
  const planetMat = new THREE.MeshPhongMaterial({ color: 0xa855f7 })
  const planet = new THREE.Mesh(planetGeom, planetMat)
  
  // Broken Ring
  const ringGeom = new THREE.TorusGeometry(5, 0.1, 8, 50)
  const ringMat = new THREE.MeshBasicMaterial({ color: 0xff3333, wireframe: true })
  const ring = new THREE.Mesh(ringGeom, ringMat)
  ring.rotation.x = Math.PI / 2
  planet.add(ring)

  planet.position.x = 18
  planetGroup.add(planet)
  scene.add(planetGroup)

  scene.add(new THREE.PointLight(0xff0000, 2, 50))
  scene.add(new THREE.AmbientLight(0x404040))

  const animate = () => {
    frame = requestAnimationFrame(animate)
    
    // Animate Meltdown
    sun.rotation.y += 0.01
    sun.scale.setScalar(1 + Math.sin(Date.now() * 0.01) * 0.05) // Pulsing
    
    planetGroup.rotation.y += 0.02 // Fast, erratic orbit
    planetGroup.rotation.z = Math.sin(Date.now() * 0.005) * 0.5 // Wobble

    // Mouse Interaction (Glitchy tilt)
    scene.rotation.x = mouseY * 0.2
    scene.rotation.y = mouseX * 0.2

    renderer.render(scene, camera)
  }
  animate()

  const onMouseMove = (e) => {
    mouseX = (e.clientX / window.innerWidth) * 2 - 1
    mouseY = (e.clientY / window.innerHeight) * 2 - 1
  }
  window.addEventListener('mousemove', onMouseMove)
})

onUnmounted(() => {
  cancelAnimationFrame(frame)
  window.removeEventListener('mousemove', null)
})
</script>

<style scoped>
.meltdown-gradient {
  position: absolute;
  width: 100%;
  height: 100%;
  background: transparent;
}

/* Red pulsing aura */
.meltdown-gradient::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 30%, rgba(239, 68, 68, 0.05) 0%, transparent 50%);
  animation: pulse-red 8s infinite alternate;
}

@keyframes pulse-red {
  0% { opacity: 0.3; }
  100% { opacity: 0.8; }
}
</style>