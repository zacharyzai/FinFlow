<template>
  <div class="landing" :class="{ loading: isLoading }">
    <!-- Transparent navbar -->
    <nav class="navbar">
      <span class="navbar__brand">FinFlow</span>
      <router-link class="navbar__cta" to="/login">Sign Up / Log In</router-link>
    </nav>

    <main>
      <!-- Intro: full-height hero image -->
      <section class="block block--intro">
        <figure class="media">
          <img class="media__image" src="/images/12.svg" alt="FinFlow hero" />
        </figure>
      </section>

      <!-- Sticky grid scroll section -->
      <section class="block block--main" ref="blockMain">
        <div class="block__wrapper" ref="blockWrapper">
          <div class="content" ref="content">
            <h2 class="content__title" ref="contentTitle">Your finances, reimagined.</h2>
            <p class="content__description" ref="contentDescription">
              AI-powered insights for smarter spending.
            </p>
            <div class="content__buttons" ref="contentButtons">
              <router-link class="btn btn--outline" to="/login">Log In</router-link>
              <router-link class="btn btn--filled" to="/signup">Sign Up</router-link>
            </div>
          </div>
          <div class="gallery">
            <ul class="gallery__grid" ref="galleryGrid">
              <li v-for="img in galleryImages" :key="img.src" class="gallery__item">
                <img class="gallery__image" :src="img.src" :alt="img.alt" />
              </li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import imagesLoaded from 'imagesloaded'

gsap.registerPlugin(ScrollTrigger)

const isLoading = ref(true)

const galleryImages = Array.from({ length: 11 }, (_, i) => ({ src: `/images/${i + 1}.png`, alt: `Image ${i + 1}` }))

const blockMain = ref(null)
const blockWrapper = ref(null)
const content = ref(null)
const contentTitle = ref(null)
const contentDescription = ref(null)
const contentButtons = ref(null)
const galleryGrid = ref(null)

let lenis = null
let scrollTriggers = []
let titleOffsetY = 0
const numColumns = 3
let columns = []

function groupItemsByColumn(items) {
  const cols = Array.from({ length: numColumns }, () => [])
  items.forEach((item, i) => cols[i % numColumns].push(item))
  return cols
}

function initContent() {
  const desc = contentDescription.value
  const btns = contentButtons.value
  const title = contentTitle.value
  const cnt = content.value

  if (desc && btns) {
    gsap.set([desc, btns], { opacity: 0, pointerEvents: 'none' })
  }

  if (cnt && title) {
    const dy = (cnt.offsetHeight - title.offsetHeight) / 2
    titleOffsetY = (dy / cnt.offsetHeight) * 100
    gsap.set(title, { yPercent: titleOffsetY })
  }
}

function gridRevealTimeline(grid) {
  const timeline = gsap.timeline()
  const wh = window.innerHeight
  const dy = wh - (wh - grid.offsetHeight) / 2

  columns.forEach((column, colIndex) => {
    const fromTop = colIndex % 2 === 0
    timeline.from(
      column,
      {
        y: dy * (fromTop ? -1 : 1),
        stagger: { each: 0.06, from: fromTop ? 'end' : 'start' },
        ease: 'power1.inOut',
      },
      'grid-reveal',
    )
  })

  return timeline
}

function gridZoomTimeline(grid) {
  const timeline = gsap.timeline({ defaults: { duration: 1, ease: 'power3.inOut' } })

  timeline.to(grid, { scale: 2.05 })
  timeline.to(columns[0], { xPercent: -40 }, '<')
  timeline.to(columns[2], { xPercent: 40 }, '<')
  timeline.to(
    columns[1],
    {
      yPercent: (index) => (index < Math.floor(columns[1].length / 2) ? -1 : 1) * 40,
      duration: 0.5,
      ease: 'power1.inOut',
    },
    '-=0.5',
  )

  return timeline
}

function toggleContent(isVisible) {
  const title = contentTitle.value
  const desc = contentDescription.value
  const btns = contentButtons.value
  if (!title || !desc || !btns) return

  gsap
    .timeline({ defaults: { overwrite: true } })
    .to(title, {
      yPercent: isVisible ? 0 : titleOffsetY,
      duration: 0.7,
      ease: 'power2.inOut',
    })
    .to(
      [desc, btns],
      {
        opacity: isVisible ? 1 : 0,
        duration: 0.4,
        ease: `power1.${isVisible ? 'inOut' : 'out'}`,
        pointerEvents: isVisible ? 'all' : 'none',
      },
      isVisible ? '-=90%' : '<',
    )
}

function addParallaxOnScroll() {
  const block = blockMain.value
  const wrapper = blockWrapper.value
  if (!block || !wrapper) return

  const st = gsap.from(wrapper, {
    yPercent: -100,
    ease: 'none',
    scrollTrigger: {
      trigger: block,
      start: 'top bottom',
      end: 'top top',
      scrub: true,
    },
  })
  scrollTriggers.push(st)
}

function animateTitleOnScroll() {
  const block = blockMain.value
  const title = contentTitle.value
  if (!block || !title) return

  const st = gsap.from(title, {
    opacity: 0,
    duration: 0.7,
    ease: 'power1.out',
    scrollTrigger: {
      trigger: block,
      start: 'top 57%',
      toggleActions: 'play none none reset',
    },
  })
  scrollTriggers.push(st)
}

function animateGridOnScroll() {
  const block = blockMain.value
  const grid = galleryGrid.value
  if (!block || !grid) return

  const timeline = gsap.timeline({
    scrollTrigger: {
      trigger: block,
      start: 'top 25%',
      end: 'bottom bottom',
      scrub: true,
    },
  })

  timeline
    .add(gridRevealTimeline(grid))
    .add(gridZoomTimeline(grid), '-=0.6')
    .add(() => toggleContent(timeline.scrollTrigger.direction === 1), '-=0.32')

  scrollTriggers.push(timeline)
}

function initSmoothScrolling() {
  lenis = new Lenis({ lerp: 0.08, wheelMultiplier: 1.4 })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add((time) => lenis.raf(time * 1000))
  gsap.ticker.lagSmoothing(0)
}

function init() {
  const grid = galleryGrid.value
  if (!grid) return

  const items = Array.from(grid.querySelectorAll('.gallery__item'))
  columns = groupItemsByColumn(items)

  initContent()
  addParallaxOnScroll()
  animateTitleOnScroll()
  animateGridOnScroll()
}

onMounted(() => {
  new Promise((resolve) => {
    imagesLoaded(document.querySelectorAll('img'), { background: true }, resolve)
  }).then(() => {
    isLoading.value = false
    initSmoothScrolling()
    init()
  })
})

onUnmounted(() => {
  scrollTriggers.forEach((st) => {
    if (st?.scrollTrigger) st.scrollTrigger.kill()
    else if (st?.kill) st.kill()
  })
  ScrollTrigger.getAll().forEach((t) => t.kill())
  if (lenis) {
    lenis.destroy()
    lenis = null
  }
  gsap.ticker.remove((time) => lenis?.raf(time * 1000))
})
</script>

<style scoped>
.landing {
  --font-primary: 'Inter', Arial, sans-serif;
  --font-secondary: 'Georgia', Times, serif;
  --color-text: #0d0d0d;
  --color-bg: #ffffff;
  --color-accent: #1a1a2e;
  --color-btn-fill: #1a1a2e;
  --color-btn-fill-text: #ffffff;
}

/* ---------- Navbar ---------- */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 40px;
  background: transparent;
  pointer-events: none;
}

.navbar__cta {
  pointer-events: all;
  font-family: 'Urbanist', var(--font-primary);
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-decoration: none;
  color: var(--color-text);
  transition: opacity 0.2s;
}

.navbar__cta:hover {
  opacity: 0.5;
}

.navbar__brand {
  font-family: 'Urbanist', var(--font-secondary);
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--color-text);
}

/* Loading overlay */
.landing.loading::before,
.landing.loading::after {
  content: '';
  position: fixed;
  z-index: 10000;
}
.landing.loading::before {
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--color-bg);
}
.landing.loading::after {
  top: 50%;
  left: 50%;
  width: 100px;
  height: 1px;
  margin: 0 0 0 -50px;
  background: var(--color-text);
  animation: loaderAnim 1.5s ease-in-out infinite alternate forwards;
}

@keyframes loaderAnim {
  0% { transform: scaleX(0); transform-origin: 0% 50%; }
  50% { transform: scaleX(1); transform-origin: 0% 50%; }
  50.1% { transform: scaleX(1); transform-origin: 100% 50%; }
  100% { transform: scaleX(0); transform-origin: 100% 50%; }
}

/* Global resets scoped to landing */
.landing * {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.landing {
  font-family: var(--font-primary);
  font-size: 16px;
  background-color: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
}

/* Hide scrollbar */
:global(html) {
  scrollbar-width: none;
}
:global(html::-webkit-scrollbar) {
  display: none;
}

/* Images */
.landing img,
.landing svg {
  display: block;
  width: 100%;
  height: auto;
}

ul {
  list-style: none;
}

/* ---------- Block intro ---------- */
.block--intro {
  position: relative;
  z-index: 1;
}

.media {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
}

.media__image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  background-color: #f0f0f0;
}

/* ---------- Block main ---------- */
.block--main {
  height: 425vh;
}

.block__wrapper {
  position: sticky;
  top: 0;
  padding: 0 24px;
  will-change: transform;
  overflow: hidden;
}

.content {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  text-align: center;
  z-index: 1;
}

.content__title {
  font-family: var(--font-secondary);
  font-size: clamp(2.5rem, 7.2vw, 6.5rem);
  line-height: 1.15;
  letter-spacing: -0.02em;
  max-width: 800px;
  color: var(--color-text);
}

.content__description {
  max-width: 420px;
  margin-top: 20px;
  font-size: 0.875rem;
  line-height: 1.5;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #555;
}

.content__buttons {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

/* ---------- Buttons ---------- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 32px;
  font-family: 'Urbanist', var(--font-primary);
  font-size: 0.875rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  text-decoration: none;
  border-radius: 999px;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.btn--outline {
  border: 1.5px solid var(--color-accent);
  color: var(--color-accent);
  background: transparent;
}
.btn--outline:hover {
  background: var(--color-accent);
  color: #fff;
}

.btn--filled {
  border: 1.5px solid var(--color-btn-fill);
  background: var(--color-btn-fill);
  color: var(--color-btn-fill-text);
}
.btn--filled:hover {
  background: #2d2d4e;
  border-color: #2d2d4e;
}

/* ---------- Gallery ---------- */
.gallery {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate3d(-50%, -50%, 0);
  width: min(736px, 90vw);
}

.gallery__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  column-gap: 20px;
  row-gap: 24px;
  will-change: transform;
}

.gallery__item {
  width: 100%;
  aspect-ratio: 1;
  will-change: transform;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.gallery__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
