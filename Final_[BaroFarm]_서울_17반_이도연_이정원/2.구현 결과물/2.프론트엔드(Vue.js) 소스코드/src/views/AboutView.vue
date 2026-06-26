<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// 정적 소개 화면 — API 의존 없음. 스크롤 등장 + 숫자 카운트업만 동작.
const rootEl = ref(null)
let io = null
let statsIo = null

function countUp(el) {
  const to = parseFloat(el.dataset.to)
  const dec = parseInt(el.dataset.dec || '0', 10)
  const suffix = el.dataset.suffix || ''
  const dur = 1400
  const t0 = performance.now()
  function tick(now) {
    const p = Math.min(1, (now - t0) / dur)
    const e = 1 - Math.pow(1 - p, 3)
    const v = to * e
    el.textContent = (dec ? v.toFixed(dec) : Math.round(v).toLocaleString()) + suffix
    if (p < 1) requestAnimationFrame(tick)
    else el.textContent = (dec ? to.toFixed(dec) : Math.round(to).toLocaleString()) + suffix
  }
  requestAnimationFrame(tick)
}

onMounted(() => {
  const root = rootEl.value
  if (!root) return
  io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target) }
    })
  }, { threshold: 0.16, rootMargin: '0px 0px -8% 0px' })
  root.querySelectorAll('.reveal').forEach((el) => io.observe(el))

  statsIo = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) {
        en.target.querySelectorAll('.cup').forEach(countUp)
        statsIo.unobserve(en.target)
      }
    })
  }, { threshold: 0.4 })
  const statsEl = root.querySelector('.stats')
  if (statsEl) statsIo.observe(statsEl)
})
onBeforeUnmount(() => { io?.disconnect(); statsIo?.disconnect() })
</script>

<template>
  <div ref="rootEl" class="about">
    <!-- HERO -->
    <section class="ab-hero">
      <div class="container">
        <span class="eyebrow reveal">About BaroFarm</span>
        <h1 class="reveal d1">산지에서 식탁까지,<br><span class="hl">가장 짧은 거리.</span></h1>
        <p class="reveal d2">바로팜은 농가와 소비자를 직접 잇는 산지 직거래 마켓입니다.<br>갓 수확한 신선함을, 더 정직한 값에 만나요.</p>
        <router-link :to="{ name: 'products' }" class="ab-cta reveal d3">신선식품 둘러보기
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </router-link>
      </div>
    </section>

    <!-- MISSION -->
    <section class="mission">
      <div class="container">
        <span class="eyebrow reveal">우리가 하는 일</span>
        <p class="lead reveal d1">좋은 먹거리는<br><b>가장 가까운 거리</b>에서 옵니다.<br>바로팜은 그 거리를<br><b>농가와 식탁, 단 한 단계</b>로 줄입니다.</p>
      </div>
    </section>

    <!-- PROBLEM vs SOLUTION -->
    <section class="pvs">
      <div class="container pvs-grid">
        <div class="pcard old reveal">
          <div class="tag">기존 유통</div>
          <h3>여러 손을 거치는 사이<br>신선함은 줄어듭니다</h3>
          <div class="flow">
            <span class="node">산지</span><span class="arrow">›</span>
            <span class="node">도매</span><span class="arrow">›</span>
            <span class="node">중간상</span><span class="arrow">›</span>
            <span class="node">소매</span><span class="arrow">›</span>
            <span class="node">소비자</span>
          </div>
          <p>유통 단계가 길수록 도착은 늦고, 농가 몫은 줄고, 가격엔 거품이 낍니다.</p>
        </div>
        <div class="pcard new reveal d1">
          <div class="tag">바로팜</div>
          <h3>농가에서 식탁으로,<br>바로 잇습니다</h3>
          <div class="flow">
            <span class="node strong">산지 농가</span><span class="arrow">›</span>
            <span class="node strong">우리 식탁</span>
          </div>
          <p>중간 단계를 걷어내 더 신선하게, 농가에는 제값을, 소비자에게는 합리적인 가격을 드려요.</p>
        </div>
      </div>
    </section>

    <!-- VALUES -->
    <section class="values">
      <div class="container">
        <div class="sec-c">
          <span class="eyebrow reveal">바로팜이 지키는 것</span>
          <h2 class="reveal d1">세 가지 약속</h2>
          <p class="reveal d2">신선함과 신뢰, 정직한 가격을 타협하지 않아요</p>
        </div>
        <div class="vgrid">
          <div class="vcard reveal">
            <div class="vicon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21V11"/><path d="M12 11C12 7 15 4 20 4c0 4-3 7-8 7Z"/><path d="M12 13.5C12 10.5 9 8 4.5 8c0 3.5 3 6 7.5 5.5Z"/></svg></div>
            <h3>당일 수확 직송</h3>
            <p>아침에 수확한 제철 먹거리를 산지에서 바로 포장해 신선하게 보내드려요.</p>
          </div>
          <div class="vcard reveal d1">
            <div class="vicon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
            <h3>정직한 가격</h3>
            <p>불필요한 중간 마진을 걷어내, 농가도 소비자도 손해 보지 않는 합리적인 값을 만듭니다.</p>
          </div>
          <div class="vcard reveal d2">
            <div class="vicon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 4 5v6c0 5 3.4 8.5 8 10 4.6-1.5 8-5 8-10V5l-8-3Z"/><path d="m9 12 2 2 4-4"/></svg></div>
            <h3>산지 신뢰</h3>
            <p>모든 상품은 생산 농가가 실명으로 등록해요. 누가, 어디서 길렀는지 투명하게 확인할 수 있어요.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- STATS -->
    <section class="stats">
      <div class="container">
        <div class="sec-c">
          <span class="eyebrow light reveal">숫자로 보는 바로팜</span>
          <h2 class="reveal d1">농가도, 식탁도 함께 자랐어요</h2>
        </div>
        <div class="sgrid">
          <div class="scard reveal">
            <div class="num"><span class="cup" data-to="120">0</span><span class="u">+ 농가</span></div>
            <div class="lab">함께하는 계약 산지농가</div>
          </div>
          <div class="scard reveal d1">
            <div class="num"><span class="cup" data-to="38" data-suffix="만 건">0</span></div>
            <div class="lab">누적 산지 직거래</div>
          </div>
          <div class="scard reveal d2">
            <div class="num"><span class="cup" data-to="4.9" data-dec="1">0</span><span class="u">/ 5.0</span></div>
            <div class="lab">신선도 만족도</div>
          </div>
        </div>
      </div>
    </section>

    <!-- HOW -->
    <section class="how">
      <div class="container">
        <div class="sec-c">
          <span class="eyebrow reveal">이용 방식</span>
          <h2 class="reveal d1">주문부터 배송까지, 세 걸음</h2>
        </div>
        <div class="hgrid">
          <div class="hstep reveal">
            <div class="n">1</div>
            <h3>오늘의 신선식품 주문</h3>
            <p>산지에서 갓 올라온 제철 먹거리를 골라 담아요.</p>
          </div>
          <div class="hstep reveal d1">
            <div class="n">2</div>
            <h3>산지에서 바로 수확·포장</h3>
            <p>주문이 들어가면 농가가 그날 수확해 신선하게 포장해요.</p>
          </div>
          <div class="hstep reveal d2">
            <div class="n">3</div>
            <h3>산지에서 바로 배송</h3>
            <p>중간 유통 없이 산지에서 바로, 신선함 그대로 집까지 배송돼요.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- FINAL CTA -->
    <section class="final">
      <div class="container">
        <div class="final-card reveal">
          <h2>오늘 산지의 신선함,<br>바로 만나보세요</h2>
          <p>지금 바로팜에서 제철 먹거리를 둘러보세요.</p>
          <router-link :to="{ name: 'products' }" class="ab-cta">신선식품 둘러보기
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about :deep(section){ position:relative; }
.eyebrow{ display:inline-block; font-size:13px; font-weight:700; letter-spacing:.05em; color:var(--leaf-700); background:var(--leaf-50); padding:6px 14px; border-radius:999px; }
.eyebrow.light{ background:rgba(255,255,255,.16); color:#fff; }

/* hero */
.ab-hero{ padding:74px 0 64px; text-align:center; overflow:hidden;
  background:radial-gradient(120% 130% at 50% -10%, rgba(90,169,130,.30), transparent 56%), linear-gradient(180deg,var(--leaf-50),var(--cream) 78%);
  border-bottom:1px solid var(--leaf-100); }
.ab-hero h1{ font-size:clamp(34px,5vw,60px); line-height:1.12; letter-spacing:-.035em; font-weight:800; margin:18px auto 18px; color:var(--leaf-700); max-width:14ch; }
.ab-hero h1 .hl{ color:var(--leaf-500); white-space:nowrap; }
.ab-hero p{ font-size:clamp(16px,1.7vw,19px); color:var(--ink-2); max-width:540px; margin:0 auto 30px; line-height:1.6; }
.ab-cta{ display:inline-flex; align-items:center; gap:8px; background:var(--leaf-600); color:#fff; font-weight:700; font-size:16px; padding:15px 28px; border-radius:999px; box-shadow:0 10px 24px rgba(23,107,66,.28); transition:.16s; }
.ab-cta:hover{ background:var(--leaf-700); transform:translateY(-2px); box-shadow:0 14px 30px rgba(23,107,66,.34); }
.heroimg{ position:relative; max-width:980px; margin:54px auto 0; aspect-ratio:1240/420; border-radius:26px; overflow:hidden; border:1px solid var(--leaf-100); box-shadow:var(--shadow-lg); background:var(--leaf-50); display:flex; align-items:center; justify-content:center; }
.heroimg .ph{ color:var(--leaf-500); font-weight:600; font-size:15px; }

/* mission */
.mission{ padding:88px 0; text-align:center; }
.mission .lead{ font-size:clamp(24px,3vw,36px); font-weight:700; line-height:1.5; letter-spacing:-.02em; max-width:24ch; margin:18px auto 0; color:var(--ink); text-wrap:balance; }
.mission .lead b{ color:var(--leaf-700); font-weight:800; white-space:nowrap; }

/* problem vs solution */
.pvs{ padding:30px 0 90px; }
.pvs-grid{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }
.pcard{ border-radius:22px; padding:38px 36px; border:1px solid var(--line); background:var(--paper); }
.pcard.old{ background:#faf7f4; border-color:#eee3da; }
.pcard .tag{ font-size:13px; font-weight:700; letter-spacing:.02em; color:var(--muted); margin-bottom:16px; }
.pcard.new .tag{ color:var(--leaf-700); }
.pcard h3{ font-size:23px; font-weight:800; letter-spacing:-.02em; margin:0 0 18px; line-height:1.3; }
.flow{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.node{ font-size:13.5px; font-weight:600; color:var(--ink-2); background:#f1f1ea; padding:8px 13px; border-radius:9px; white-space:nowrap; }
.pcard.new .node{ background:var(--leaf-50); color:var(--leaf-700); }
.node.strong{ background:var(--leaf-600); color:#fff; }
.arrow{ color:var(--faint); font-weight:700; }
.pcard p{ margin:20px 0 0; color:var(--muted); font-size:14.5px; line-height:1.6; }

/* values */
.values{ padding:90px 0; background:var(--paper); border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
.sec-c{ text-align:center; margin-bottom:46px; }
.sec-c h2{ font-size:clamp(26px,3vw,36px); font-weight:800; letter-spacing:-.025em; margin:14px 0 10px; }
.sec-c p{ color:var(--muted); font-size:15.5px; margin:0; }
.vgrid{ display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
.vcard{ border:1px solid var(--line); border-radius:20px; padding:34px 30px; background:var(--cream); transition:transform .2s, box-shadow .2s; }
.vcard:hover{ transform:translateY(-4px); box-shadow:var(--shadow-md); }
.vicon{ width:54px; height:54px; border-radius:16px; background:var(--leaf-100); color:var(--leaf-700); display:flex; align-items:center; justify-content:center; margin-bottom:20px; }
.vicon svg{ width:27px; height:27px; }
.vcard h3{ font-size:20px; font-weight:800; letter-spacing:-.02em; margin:0 0 10px; }
.vcard p{ margin:0; color:var(--muted); font-size:14.5px; line-height:1.62; }

/* stats */
.stats{ padding:86px 0; background:linear-gradient(150deg,var(--leaf-700),var(--leaf-600) 60%,var(--leaf-500)); color:#fff; text-align:center; }
.stats .sec-c h2{ color:#fff; }
.sgrid{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; max-width:880px; margin:46px auto 0; }
.scard .num{ font-size:clamp(40px,5vw,58px); font-weight:800; letter-spacing:-.03em; line-height:1; font-variant-numeric:tabular-nums; }
.scard .num .u{ font-size:.5em; margin-left:3px; font-weight:700; }
.scard .lab{ margin-top:12px; font-size:14.5px; color:rgba(255,255,255,.82); font-weight:500; }

/* how */
.how{ padding:90px 0; }
.hgrid{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.hstep{ position:relative; padding:34px 30px; border:1px solid var(--line); border-radius:20px; background:var(--paper); }
.hstep .n{ width:38px; height:38px; border-radius:12px; background:var(--leaf-600); color:#fff; font-weight:800; font-size:17px; display:flex; align-items:center; justify-content:center; margin-bottom:18px; }
.hstep h3{ font-size:19px; font-weight:800; letter-spacing:-.02em; margin:0 0 9px; }
.hstep p{ margin:0; color:var(--muted); font-size:14.5px; line-height:1.6; }

/* final */
.final{ padding:0 0 100px; }
.final-card{ position:relative; overflow:hidden; border-radius:28px; padding:70px 40px; text-align:center;
  background:radial-gradient(120% 140% at 12% 12%, rgba(90,169,130,.30), transparent 55%), linear-gradient(140deg,var(--leaf-50),var(--leaf-100));
  border:1px solid var(--leaf-100); }
.final-card h2{ font-size:clamp(26px,3.4vw,40px); font-weight:800; letter-spacing:-.03em; margin:0 0 14px; color:var(--leaf-700); }
.final-card p{ font-size:16px; color:var(--ink-2); margin:0 0 28px; }

/* reveal — 기본은 보임. 모션 허용일 때만 hidden 에서 등장 (감속 모션/SSR 안전) */
@media (prefers-reduced-motion: no-preference){
  .reveal{ opacity:0; transform:translateY(20px); transition:opacity .7s cubic-bezier(.2,.7,.3,1), transform .7s cubic-bezier(.2,.7,.3,1); }
  .reveal.in{ opacity:1; transform:none; }
  .reveal.d1{ transition-delay:.08s; } .reveal.d2{ transition-delay:.16s; } .reveal.d3{ transition-delay:.24s; }
}

@media (max-width:880px){
  .pvs-grid, .vgrid, .sgrid, .hgrid{ grid-template-columns:1fr; }
}
</style>
