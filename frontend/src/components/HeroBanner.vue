<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// import.meta.glob으로 폴더 이미지 자동 수집 — 파일 추가/삭제하면 저장 후 자동 반영
const couponMods = import.meta.glob('../assets/coupon_banner/*.{png,jpg,jpeg,webp,PNG,JPG,JPEG,WEBP}', { eager: true })
const eventMods  = import.meta.glob('../assets/event_banner/*.{png,jpg,jpeg,webp,PNG,JPG,JPEG,WEBP}', { eager: true })

const slides = [
  ...Object.values(eventMods).map(m => m.default),
  ...Object.values(couponMods).map(m => m.default),
]

const idx = ref(0)
let timer = null
const AUTOPLAY = 3000

function go(i)  { idx.value = (i + slides.length) % slides.length }
function next() { go(idx.value + 1) }
function prev() { go(idx.value - 1) }
function start(){ stop(); timer = setInterval(next, AUTOPLAY) }
function stop()  { if (timer) { clearInterval(timer); timer = null } }

onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <section class="hero" @mouseenter="stop" @mouseleave="start">
    <div class="track" :style="{ transform: `translateX(-${idx * 100}%)` }">
      <div v-for="(src, i) in slides" :key="i" class="slide">
        <img :src="src" :alt="`배너 ${i + 1}`" class="banner-img" />
      </div>
    </div>

    <button class="nav prev" @click="prev" aria-label="이전">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m15 6-6 6 6 6"/></svg>
    </button>
    <button class="nav next" @click="next" aria-label="다음">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m9 6 6 6-6 6"/></svg>
    </button>

    <div class="dots">
      <button
        v-for="(_, i) in slides"
        :key="i"
        :class="{ on: i === idx }"
        @click="go(i)"
        :aria-label="`슬라이드 ${i + 1}`"
      ></button>
    </div>
    <span class="counter">{{ idx + 1 }} / {{ slides.length }}</span>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 30px;
  box-shadow: var(--shadow-md);
  background: #111;
  width: 100%;
  aspect-ratio: 16 / 5;
}

.track {
  display: flex;
  position: absolute;
  inset: 0;
  transition: transform .55s cubic-bezier(.4, .0, .2, 1);
}

.slide {
  flex: 0 0 100%;
  min-width: 100%;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 3;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, .35);
  color: #fff;
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: .15s;
  cursor: pointer;
}
.nav:hover { background: rgba(0, 0, 0, .6); }
.nav.prev  { left: 18px; }
.nav.next  { right: 18px; }

.dots {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: 20px;
  display: flex;
  gap: 8px;
  z-index: 3;
}
.dots button {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  border: none;
  padding: 0;
  background: rgba(255, 255, 255, .5);
  transition: .2s;
  cursor: pointer;
}
.dots button.on { width: 26px; background: #fff; }

.counter {
  position: absolute;
  right: 22px;
  bottom: 18px;
  z-index: 3;
  font-size: 12.5px;
  font-weight: 700;
  color: #fff;
  background: rgba(0, 0, 0, .35);
  padding: 5px 12px;
  border-radius: 999px;
}

@media (max-width: 760px) {
  .hero { aspect-ratio: 16 / 7; border-radius: 14px; }
}
</style>
