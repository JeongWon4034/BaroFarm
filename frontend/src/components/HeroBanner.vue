<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// 메인 상단 히어로 캐러셀 — 켤리식 큰 배너. 슬라이드는 데이터로만 관리해 추가/수정 쉬움.
const slides = [
  {
    eyebrow: '오늘의 마감임박',
    title: '산지에서 식탁까지,\n버려질 뻔한 신선식품을 제값에',
    sub: '농가도 식탁도 알뜰하게 — 폐기 직전 신선식품을 합리적인 가격으로',
    cta: '마감임박 특가 보기', to: { name: 'deals' }, emoji: '🥬',
    bg: 'linear-gradient(120deg, #0e4a2e 0%, #176b42 55%, #2a8a5a 100%)',
  },
  {
    eyebrow: '폐기 절감 챌린지',
    title: '한 끼의 선택이\n지구를 살립니다',
    sub: '마감임박 상품을 구매해 음식물 폐기를 줄이고 배지도 모아보세요',
    cta: '챌린지 참여하기', to: { name: 'challenges' }, emoji: '🌱',
    bg: 'linear-gradient(120deg, #123f2c 0%, #1f6b48 60%, #3a8f63 100%)',
  },
  {
    eyebrow: '산지직송 신선식품',
    title: '오늘 수확해\n내일 도착하는 신선함',
    sub: '중간 유통 없이 산지에서 바로 — 채소·과일·수산·축산 모두',
    cta: '신선식품 보러가기', to: { name: 'products' }, emoji: '🧺',
    bg: 'linear-gradient(120deg, #0f4632 0%, #1a6b4a 55%, #2f8a5e 100%)',
  },
]

const idx = ref(0)
let timer = null
const AUTOPLAY = 5000

function go(i) { idx.value = (i + slides.length) % slides.length }
function next() { go(idx.value + 1) }
function prev() { go(idx.value - 1) }

function start() { stop(); timer = setInterval(next, AUTOPLAY) }
function stop() { if (timer) { clearInterval(timer); timer = null } }

onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <section class="hero" @mouseenter="stop" @mouseleave="start">
    <div class="track" :style="{ transform: `translateX(-${idx * 100}%)` }">
      <div v-for="(s, i) in slides" :key="i" class="slide" :style="{ background: s.bg }">
        <div class="copy">
          <span class="eyebrow">{{ s.eyebrow }}</span>
          <h2>{{ s.title }}</h2>
          <p>{{ s.sub }}</p>
          <router-link :to="s.to" class="cta">
            {{ s.cta }}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </router-link>
        </div>
        <div class="art" aria-hidden="true">{{ s.emoji }}</div>
      </div>
    </div>

    <button class="nav prev" @click="prev" aria-label="이전">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m15 6-6 6 6 6"/></svg>
    </button>
    <button class="nav next" @click="next" aria-label="다음">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m9 6 6 6-6 6"/></svg>
    </button>

    <div class="dots">
      <button v-for="(s, i) in slides" :key="i" :class="{ on: i === idx }" @click="go(i)" :aria-label="`슬라이드 ${i + 1}`"></button>
    </div>
    <span class="counter">{{ idx + 1 }} / {{ slides.length }}</span>
  </section>
</template>

<style scoped>
.hero{
  position:relative; border-radius:20px; overflow:hidden;
  margin-bottom:30px; box-shadow:var(--shadow-md);
  height:360px;
}
.track{ display:flex; height:100%; transition:transform .55s cubic-bezier(.4,.0,.2,1); }
.slide{
  position:relative; min-width:100%; height:100%;
  display:flex; align-items:center; padding:0 60px; color:#fff;
}
.copy{ max-width:560px; z-index:2; }
.eyebrow{
  display:inline-block; font-size:13px; font-weight:700; letter-spacing:.04em;
  padding:5px 12px; border-radius:999px; margin-bottom:18px;
  background:rgba(255,255,255,.16); backdrop-filter:blur(4px);
}
.copy h2{
  font-size:38px; font-weight:800; line-height:1.25; letter-spacing:-.02em;
  margin:0 0 14px; white-space:pre-line; text-shadow:0 2px 18px rgba(0,0,0,.18);
}
.copy p{ font-size:16px; line-height:1.6; opacity:.92; margin:0 0 26px; max-width:440px; }
.cta{
  display:inline-flex; align-items:center; gap:8px;
  background:#fff; color:var(--leaf-700); font-weight:800; font-size:15px;
  padding:13px 24px; border-radius:999px; transition:.16s;
  box-shadow:0 8px 22px rgba(0,0,0,.18);
}
.cta:hover{ transform:translateY(-2px); box-shadow:0 12px 28px rgba(0,0,0,.24); }
.art{
  position:absolute; right:56px; bottom:-12px; font-size:230px; line-height:1;
  opacity:.9; filter:drop-shadow(0 24px 34px rgba(0,0,0,.28)); user-select:none;
}

.nav{
  position:absolute; top:50%; transform:translateY(-50%); z-index:3;
  width:44px; height:44px; border-radius:50%; border:none;
  background:rgba(255,255,255,.22); color:#fff; backdrop-filter:blur(4px);
  display:flex; align-items:center; justify-content:center; transition:.15s;
}
.nav:hover{ background:rgba(255,255,255,.4); }
.nav.prev{ left:18px; } .nav.next{ right:18px; }

.dots{ position:absolute; left:60px; bottom:26px; display:flex; gap:8px; z-index:3; }
.dots button{
  width:9px; height:9px; border-radius:999px; border:none; padding:0;
  background:rgba(255,255,255,.45); transition:.2s; cursor:pointer;
}
.dots button.on{ width:26px; background:#fff; }
.counter{
  position:absolute; right:22px; bottom:22px; z-index:3;
  font-size:12.5px; font-weight:700; color:#fff;
  background:rgba(0,0,0,.25); padding:5px 12px; border-radius:999px;
}

@media (max-width:760px){
  .hero{ height:300px; }
  .slide{ padding:0 30px; }
  .copy h2{ font-size:27px; }
  .copy p{ font-size:14px; }
  .art{ font-size:150px; right:14px; opacity:.55; }
  .dots{ left:30px; }
}
</style>
