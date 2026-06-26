<script setup>
// 이타닉 가든 PICK — MD 큐레이션(에디토리얼). 정적 콘텐츠라 백엔드 불필요.
// 각 카드는 검색/둘러보기로 연결. 이미지는 .pimg 에 <img> 넣으면 채워짐.
const PICKS = [
  { tag: '이달의 산지', t: '강원 고랭지 채소 꾸러미', d: '해발 800m 평창에서 아침에 수확한 잎채소 모둠', kw: '채소', img: '/seed-images/pick1.jpg' },
  { tag: '제철 한정', t: '완도 활전복 특선', d: '5년 물질 해녀가 직접 채취한 당일 활전복', kw: '전복', img: '/seed-images/pick2.jpg' },
  { tag: '농가 직송', t: '성주 참외 첫물', d: '당도 13brix 이상만 골라 담은 올해 첫 참외', kw: '참외', img: '/seed-images/pick3.jpg' },
]
</script>

<template>
  <section class="sec">
    <div class="sec-head">
      <div class="l">
        <h2>이타닉 가든 PICK</h2>
      </div>
    </div>
    <div class="pick-grid">
      <router-link
        v-for="(p, i) in PICKS" :key="i"
        class="pick" :to="{ name: 'products', query: { keyword: p.kw } }"
      >
        <div class="pimg">
          <img :src="p.img" :alt="p.t" loading="lazy" />
          <span class="ph-tag">PICK {{ i + 1 }}</span>
        </div>
        <div class="pbody">
          <span class="ptag">{{ p.tag }}</span>
          <h3>{{ p.t }}</h3>
          <p>{{ p.d }}</p>
        </div>
      </router-link>
    </div>
  </section>
</template>

<style scoped>
.sec{ padding-top:46px; }
.sec-head{ margin-bottom:20px; }
.sec-head h2{ font-size:24px; font-weight:800; letter-spacing:-.025em; margin:0 0 5px; }
.sec-head p{ margin:0; color:var(--muted); font-size:14px; }
.pick-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.pick{ display:flex; flex-direction:column; border-radius:20px; overflow:hidden; border:1px solid var(--line); background:var(--paper); box-shadow:var(--shadow-sm); transition:transform .2s, box-shadow .2s; }
.pick:hover{ transform:translateY(-4px); box-shadow:var(--shadow-lg); }
.pimg{ position:relative; aspect-ratio:16/10; background:linear-gradient(135deg,#eef4ef,#dcefe4); overflow:hidden; }
.pimg img{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.ph-tag{ position:absolute; top:12px; left:12px; background:rgba(28,34,21,.55); color:#fff; font-size:11.5px; font-weight:700; padding:5px 11px; border-radius:999px; }
.pbody{ padding:17px 18px 19px; }
.ptag{ display:inline-block; font-size:11.5px; font-weight:700; color:var(--leaf-700); background:var(--leaf-50); padding:4px 10px; border-radius:7px; margin-bottom:10px; }
.pbody h3{ margin:0 0 7px; font-size:18px; font-weight:800; letter-spacing:-.02em; line-height:1.3; color:var(--ink); }
.pbody p{ margin:0; font-size:13.5px; color:var(--muted); line-height:1.5; }
@media (max-width:780px){ .pick-grid{ grid-template-columns:1fr; } }
</style>
