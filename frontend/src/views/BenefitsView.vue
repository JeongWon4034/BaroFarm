<script setup>
import { ref } from 'vue'

// import.meta.glob — 폴더 이미지 자동 수집. 파일 추가/삭제/교체 시 저장 후 자동 반영.
const challengeMods = import.meta.glob('../assets/challenge_banner/*.{png,jpg,jpeg,webp,PNG,JPG,JPEG,WEBP}', { eager: true })
const couponMods    = import.meta.glob('../assets/coupon_banner/*.{png,jpg,jpeg,webp,PNG,JPG,JPEG,WEBP}', { eager: true })
const eventMods     = import.meta.glob('../assets/event_banner/*.{png,jpg,jpeg,webp,PNG,JPG,JPEG,WEBP}', { eager: true })

const challengeImages = Object.values(challengeMods).map(m => m.default)
const couponImages    = Object.values(couponMods).map(m => m.default)
const eventImages     = Object.values(eventMods).map(m => m.default)

const FILTERS = ['전체', '챌린지', '쿠폰', '이벤트']
const activeFilter = ref('전체')

const showChallenge = () => activeFilter.value === '전체' || activeFilter.value === '챌린지'
const showCoupon    = () => activeFilter.value === '전체' || activeFilter.value === '쿠폰'
const showEvent     = () => activeFilter.value === '전체' || activeFilter.value === '이벤트'
</script>

<template>
  <div class="benefits container">
    <div class="pg-head">
      <h1>혜택 및 공지</h1>
      <p>진행 중인 이벤트와 쿠폰 혜택을 한눈에 확인하세요</p>
    </div>

    <div class="filterbar">
      <button
        v-for="f in FILTERS" :key="f"
        class="fchip" :class="{ on: activeFilter === f }"
        @click="activeFilter = f"
      >{{ f }}</button>
    </div>

    <div class="bnr-stack">

      <!-- 챌린지 이벤트 -->
      <template v-if="showChallenge()">
        <div class="lbl">
          <span class="t">챌린지 이벤트</span>
          <span class="pill challenge">CHALLENGE</span>
        </div>
        <div v-for="src in challengeImages" :key="src" class="bnr-item">
          <img :src="src" alt="챌린지 배너" />
        </div>
      </template>

      <!-- 쿠폰 혜택 -->
      <template v-if="showCoupon()">
        <div class="lbl">
          <span class="t">쿠폰 혜택</span>
          <span class="pill coupon">COUPON</span>
        </div>
        <div v-for="src in couponImages" :key="src" class="bnr-item">
          <img :src="src" alt="쿠폰 배너" />
        </div>
      </template>

      <!-- 이벤트 -->
      <template v-if="showEvent()">
        <div class="lbl">
          <span class="t">이벤트</span>
          <span class="pill event">EVENT</span>
        </div>
        <div v-for="src in eventImages" :key="src" class="bnr-item">
          <img :src="src" alt="이벤트 배너" />
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
.benefits { padding-top: 36px; padding-bottom: 70px; }
.pg-head h1 { margin: 0 0 7px; font-size: 30px; font-weight: 800; letter-spacing: -.03em; }
.pg-head p  { margin: 0; color: var(--muted); font-size: 14.5px; }

.filterbar { display: flex; gap: 8px; padding: 22px 0 28px; overflow-x: auto; }
.fchip {
  flex: none; padding: 10px 18px; border-radius: 999px;
  border: 1.5px solid var(--line); background: #fff;
  font-size: 14.5px; font-weight: 600; color: var(--ink-2);
  white-space: nowrap; transition: .14s;
}
.fchip:hover { border-color: var(--leaf-300); background: var(--leaf-50); color: var(--leaf-700); }
.fchip.on    { background: var(--leaf-600); border-color: var(--leaf-600); color: #fff; }

.bnr-stack { display: flex; flex-direction: column; gap: 16px; }

.lbl { display: flex; align-items: center; gap: 9px; margin: 14px 0 -4px; }
.lbl .t    { font-size: 18px; font-weight: 800; letter-spacing: -.02em; }
.lbl .pill { font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 999px; }
.lbl .pill.challenge { background: #e6f4ea; color: #1a6b42; }
.lbl .pill.event     { background: var(--deal-soft); color: var(--deal); }
.lbl .pill.coupon    { background: #efe9ff; color: #6b2fb3; }

.bnr-item {
  width: 100%;
  aspect-ratio: 5 / 2;   /* 모든 이미지 동일 비율 고정 */
  border-radius: 12px;
  overflow: hidden;
}
.bnr-item img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;      /* 비율 맞게 중앙 크롭 */
  object-position: center;
}
</style>
