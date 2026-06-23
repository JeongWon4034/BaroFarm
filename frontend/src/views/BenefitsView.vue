<script setup>
// 정적 배너 화면 — API 의존 없음. 배너 이미지는 준비되면 .bnr 안에 <img src="..."> 로 채운다.
// 챌린지 이벤트 배너는 챌린지 목록으로 연결.
const FILTERS = ['전체', '이벤트', '쿠폰', '공지']
import { ref } from 'vue'
const activeFilter = ref('전체')
</script>

<template>
  <div class="benefits container">
    <div class="pg-head">
      <h1>혜택 및 공지</h1>
      <p>진행 중인 이벤트와 쿠폰, 공지사항을 한눈에 확인하세요</p>
    </div>

    <div class="filterbar">
      <button
        v-for="f in FILTERS" :key="f"
        class="fchip" :class="{ on: activeFilter === f }"
        @click="activeFilter = f"
      >{{ f }}</button>
    </div>

    <div class="bnr-stack">
      <!-- 메인 이벤트 = 챌린지 연결 -->
      <div class="lbl"><span class="t">챌린지 이벤트</span><span class="pill event">CHALLENGE</span></div>
      <div class="bnr bnr-main">
        <span class="ph-tag">사용자 챌린지 배너</span>
        <router-link :to="{ name: 'challenges' }" class="bnr-cta">챌린지 참여하기
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </router-link>
      </div>

      <!-- 이벤트 2-up -->
      <div class="bnr-row">
        <div class="bnr bnr-half"><span class="ph-tag">이벤트 A</span></div>
        <div class="bnr bnr-half"><span class="ph-tag">이벤트 B</span></div>
      </div>

      <!-- 쿠폰: 길쭉한 배너 3개 -->
      <div class="lbl"><span class="t">쿠폰 혜택</span><span class="pill coupon">COUPON</span></div>
      <div class="bnr bnr-long"><span class="ph-tag">쿠폰 배너 1</span></div>
      <div class="bnr bnr-long"><span class="ph-tag">쿠폰 배너 2</span></div>
      <div class="bnr bnr-long"><span class="ph-tag">쿠폰 배너 3</span></div>

      <!-- 공지 -->
      <div class="lbl"><span class="t">공지사항</span><span class="pill notice">NOTICE</span></div>
      <div class="bnr bnr-strip"><span class="ph-tag">공지 배너 1</span></div>
      <div class="bnr bnr-strip"><span class="ph-tag">공지 배너 2</span></div>
    </div>
  </div>
</template>

<style scoped>
.benefits{ padding-top:36px; padding-bottom:70px; }
.pg-head h1{ margin:0 0 7px; font-size:30px; font-weight:800; letter-spacing:-.03em; }
.pg-head p{ margin:0; color:var(--muted); font-size:14.5px; }

.filterbar{ display:flex; gap:8px; padding:22px 0 28px; overflow-x:auto; }
.fchip{ flex:none; padding:10px 18px; border-radius:999px; border:1.5px solid var(--line); background:#fff; font-size:14.5px; font-weight:600; color:var(--ink-2); white-space:nowrap; transition:.14s; }
.fchip:hover{ border-color:var(--leaf-300); background:var(--leaf-50); color:var(--leaf-700); }
.fchip.on{ background:var(--leaf-600); border-color:var(--leaf-600); color:#fff; }

.bnr-stack{ display:flex; flex-direction:column; gap:20px; }
.lbl{ display:flex; align-items:center; gap:9px; margin:14px 0 -4px; }
.lbl:first-child{ margin-top:0; }
.lbl .t{ font-size:18px; font-weight:800; letter-spacing:-.02em; }
.lbl .pill{ font-size:11.5px; font-weight:700; padding:4px 10px; border-radius:999px; background:var(--leaf-50); color:var(--leaf-700); }
.lbl .pill.event{ background:var(--deal-soft); color:var(--deal); }
.lbl .pill.coupon{ background:#efe9ff; color:#6b2fb3; }
.lbl .pill.notice{ background:#f1f1ea; color:var(--muted); }

/* 배너 슬롯 — 준비되면 안에 <img style="width:100%;height:100%;object-fit:cover"> 삽입 */
.bnr{ position:relative; border-radius:20px; overflow:hidden; border:1px solid var(--line);
  background:linear-gradient(135deg,#eef4ef,#dcefe4); display:flex; align-items:center; justify-content:center; }
.bnr-main{ aspect-ratio:1240/300; }
.bnr-long{ aspect-ratio:1240/210; }
.bnr-strip{ aspect-ratio:1240/150; }
.bnr-row{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.bnr-half{ aspect-ratio:610/280; }
.ph-tag{ position:absolute; top:14px; left:14px; z-index:2; background:rgba(28,34,21,.55); color:#fff; font-size:11.5px; font-weight:700; padding:5px 11px; border-radius:999px; }
.bnr > .ph-tag + :empty, .bnr::after{ }
.bnr:not(:has(img))::before{ content:"배너 이미지"; color:var(--leaf-600); font-weight:600; font-size:14px; }
.bnr-cta{ position:absolute; right:18px; bottom:18px; z-index:3; display:inline-flex; align-items:center; gap:7px; background:#fff; color:var(--leaf-700); font-weight:700; font-size:14px; padding:11px 18px; border-radius:999px; box-shadow:var(--shadow-md); transition:.15s; }
.bnr-cta:hover{ transform:translateY(-2px); box-shadow:var(--shadow-lg); }
.bnr-cta svg{ width:16px; height:16px; }

@media (max-width:780px){ .bnr-row{ grid-template-columns:1fr; } }
</style>
