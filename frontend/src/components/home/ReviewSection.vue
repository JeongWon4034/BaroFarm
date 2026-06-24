<script setup>
// 생생 대표 후기 — 샘플(에디토리얼). 사이트 전역 대표후기 API가 생기면 props/fetch로 교체.
// (현재 백엔드는 상품별 reviews 만 제공 → 홈 대표후기는 정적 샘플로 둠)
const REVIEWS = [
  { name: '이서연', prod: '국산 딸기 500g', stars: 5, text: '산지직송이라 그런지 알이 꽉꽉하고 당도가 달라요. 아이가 한 판을 다 비웠어요!' },
  { name: '정민재', prod: '제주 흑돼지 목살 100g', stars: 5, text: '마감임박이라 반신반의했는데 신선도 전혀 문제없고 가격꿀… 재구매 확정입니다.' },
  { name: '한영자', prod: '친환경 표고버섯 300g', stars: 4, text: '버섯 향이 진하고 두툼두툼해요. 다음엔 더 많이 주문하려고요.' },
]
</script>

<template>
  <section class="sec">
    <div class="sec-head">
      <div class="l">
        <h2>생생 대표 후기</h2>
        <p>바로팜을 먼저 맛본 이웃들의 진짜 후기</p>
      </div>
    </div>
    <div class="review-grid">
      <article v-for="(r, i) in REVIEWS" :key="i" class="review">
        <div class="rvimg"><span class="ph-tag">후기 사진 {{ i + 1 }}</span></div>
        <div class="rvbody">
          <div class="rvstars">
            <svg v-for="n in 5" :key="n" viewBox="0 0 24 24" :style="{ color: n <= r.stars ? 'var(--star)' : 'var(--line-2)' }" fill="currentColor"><path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 18.6 5 21.4l1.4-6.8L1.3 9.9l6.9-.8L12 2Z"/></svg>
          </div>
          <p class="rvtext">“{{ r.text }}”</p>
          <div class="rvmeta">
            <span class="av">{{ r.name.charAt(0) }}</span>
            <span class="who"><b>{{ r.name }}</b><span>{{ r.prod }}</span></span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.sec{ padding-top:46px; }
.sec-head{ margin-bottom:20px; }
.sec-head h2{ font-size:24px; font-weight:800; letter-spacing:-.025em; margin:0 0 5px; }
.sec-head p{ margin:0; color:var(--muted); font-size:14px; }
.review-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.review{ display:flex; flex-direction:column; border-radius:20px; overflow:hidden; border:1px solid var(--line); background:var(--paper); box-shadow:var(--shadow-sm); transition:transform .2s, box-shadow .2s; }
.review:hover{ transform:translateY(-4px); box-shadow:var(--shadow-lg); }
.rvimg{ position:relative; aspect-ratio:16/10; background:linear-gradient(135deg,#eef4ef,#dcefe4); }
.ph-tag{ position:absolute; top:12px; left:12px; background:rgba(28,34,21,.55); color:#fff; font-size:11.5px; font-weight:700; padding:5px 11px; border-radius:999px; }
.rvbody{ padding:17px 18px 19px; display:flex; flex-direction:column; gap:11px; }
.rvstars{ display:flex; gap:2px; }
.rvstars svg{ width:16px; height:16px; }
.rvtext{ margin:0; font-size:14.5px; line-height:1.55; color:var(--ink-2); font-weight:500; letter-spacing:-.01em; }
.rvmeta{ display:flex; align-items:center; gap:10px; margin-top:2px; padding-top:13px; border-top:1px solid var(--line); }
.av{ width:34px; height:34px; border-radius:50%; background:var(--leaf-100); color:var(--leaf-700); display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:800; flex:none; }
.who{ display:flex; flex-direction:column; gap:1px; line-height:1.3; }
.who b{ font-size:13.5px; font-weight:700; }
.who span{ font-size:12px; color:var(--muted); }
@media (max-width:780px){ .review-grid{ grid-template-columns:1fr; } }
</style>
