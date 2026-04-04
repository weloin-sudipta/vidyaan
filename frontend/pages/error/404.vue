<template>
  <div class="min-h-screen bg-[#f8fafc] flex items-center justify-center p-6 relative overflow-hidden font-sans">
    
    <div class="absolute inset-0 z-0 pointer-events-none">
      <div class="mesh-gradient"></div>
    </div>

    <div class="relative z-10 w-full max-w-6xl flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
      
      <div class="w-full lg:w-1/2 h-[350px] md:h-[550px] relative">
        <div ref="threeContainer" class="w-full h-full cursor-grab active:cursor-grabbing"></div>
        
        <div class="absolute bottom-4 lg:bottom-12 left-1/2 -translate-x-1/2 lg:left-0 lg:translate-x-0 bg-white/60 backdrop-blur-xl border border-white px-6 py-3 rounded-2xl shadow-[0_20px_50px_rgba(79,70,229,0.15)] flex items-center gap-3">
           <span class="relative flex h-2 w-2">
             <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
             <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
           </span>
           <p class="text-[10px] font-black text-amber-700 uppercase tracking-[0.2em]">
             WARNING: You Lost in Space.
           </p>
        </div>
      </div>

      <div class="w-full lg:w-1/2 text-center lg:text-left space-y-8">
        <div class="relative">
          <h1 class="text-8xl md:text-[12rem] font-black text-slate-900/[0.03] absolute -top-10 lg:-top-24 left-0 lg:left-[-60px] select-none leading-none">
            {{ error?.statusCode || 404 }}
          </h1>
          
          <span class="text-indigo-500 text-xs font-black uppercase tracking-[0.5em] block mb-4 relative z-10">
            Navigation Interrupted
          </span>
          
          <h2 class="text-4xl md:text-6xl font-black text-slate-900 leading-[1.1] relative z-10">
            Lost in <br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600">
              Thought.
            </span>
          </h2>
          
          <p class="text-slate-500 font-medium mt-8 max-w-md mx-auto lg:mx-0 leading-relaxed text-sm md:text-base">
            {{ error?.message || "The page you're looking for is missing. It seems your request has dissolved into the digital void." }}
          </p>
        </div>

        <div class="flex flex-col sm:flex-row items-center gap-4 relative z-10">
          <NuxtLink to="/" 
            class="w-full sm:w-auto px-10 py-4 bg-slate-900 text-white rounded-[1.5rem] font-black text-xs hover:bg-indigo-600 hover:scale-105 transition-all shadow-2xl shadow-indigo-200 flex items-center justify-center gap-3">
            <i class="fa fa-th-large text-[10px]"></i>
            <span>Return to Dashboard</span>
          </NuxtLink>
          
          <button @click="goBack" 
            class="w-full sm:w-auto px-10 py-4 bg-white/60 backdrop-blur-md border-2 border-slate-100 text-slate-600 rounded-[1.5rem] font-black text-xs hover:border-indigo-400 hover:text-indigo-600 transition-all flex items-center justify-center gap-3">
            <i class="fa fa-redo text-[10px]"></i>
            <span>Try Again</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
// import { useError, clearError } from '#app'
// import { useRouter } from 'vue-router'

// const error = useError()
// const router = useRouter()

// const goBack = () => {
//   clearError()
//   router.back()
// }

const threeContainer = ref(null)
let scene, camera, renderer, solarSystemGroup, planetOrbitGroup
let mouseX = 0, mouseY = 0
let animationId
let handleMouseMove

onMounted(() => {
  if (!threeContainer.value) return

  scene = new THREE.Scene()

  camera = new THREE.PerspectiveCamera(
    75,
    threeContainer.value.clientWidth / threeContainer.value.clientHeight,
    0.1,
    1000
  )

  camera.position.set(0, 10, 35)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(
    threeContainer.value.clientWidth,
    threeContainer.value.clientHeight
  )

  renderer.setPixelRatio(window.devicePixelRatio)
  threeContainer.value.appendChild(renderer.domElement)

  solarSystemGroup = new THREE.Group()
  scene.add(solarSystemGroup)

  const sun = new THREE.Mesh(
    new THREE.SphereGeometry(6, 32, 16),
    new THREE.MeshPhongMaterial({
      color: 0x6366f1,
      emissive: 0x6366f1
    })
  )

  solarSystemGroup.add(sun)

  planetOrbitGroup = new THREE.Group()
  solarSystemGroup.add(planetOrbitGroup)

  const planet = new THREE.Mesh(
    new THREE.SphereGeometry(2.5, 32, 16),
    new THREE.MeshPhongMaterial({ color: 0xa855f7 })
  )

  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(5, 0.4, 16, 100),
    new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 0.8
    })
  )

  ring.rotation.x = Math.PI / 2
  planet.add(ring)

  planet.position.x = 20
  planetOrbitGroup.add(planet)

  scene.add(new THREE.DirectionalLight(0xffffff, 1.8))
  scene.add(new THREE.AmbientLight(0xffffff, 0.6))

  const animate = () => {
    animationId = requestAnimationFrame(animate)

    planetOrbitGroup.rotation.y += 0.005

    solarSystemGroup.rotation.x += (mouseY * 0.5 - solarSystemGroup.rotation.x) * 0.05
    solarSystemGroup.rotation.y += (mouseX * 0.5 - solarSystemGroup.rotation.y) * 0.05

    renderer.render(scene, camera)
  }

  animate()

  handleMouseMove = (event) => {
    mouseX = (event.clientX / window.innerWidth) * 2 - 1
    mouseY = -(event.clientY / window.innerHeight) * 2 + 1
  }

  window.addEventListener('mousemove', handleMouseMove)

  window.addEventListener('resize', () => {
    if (!threeContainer.value) return
    camera.aspect = threeContainer.value.clientWidth / threeContainer.value.clientHeight
    camera.updateProjectionMatrix()
    renderer.setSize(
      threeContainer.value.clientWidth,
      threeContainer.value.clientHeight
    )
  })
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)

  if (renderer) {
    renderer.dispose()
    renderer.forceContextLoss()
  }

  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
.mesh-gradient {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #f8fafc;
  background-image: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.1) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.08) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
  animation: mesh-breathing 20s ease infinite alternate;
}

@keyframes mesh-breathing {
  0% { transform: scale(1) translate(0, 0); }
  100% { transform: scale(1.05) translate(0.5%, 0.5%); }
}

.rounded-\[1\.5rem\] {
  border-radius: 1.5rem;
}

canvas {
  outline: none;
}
</style>