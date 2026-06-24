<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

// 바로팜 AI 로딩 — 개인화 문구 + 시뮬레이션 진행바.
// 실제 측정값이 아니라 '예상 진행' 애니메이션(92%까지 점근, 응답 오면 부모가 언마운트).
const props = defineProps({
  name: { type: String, default: '' },          // 사용자 이름
  title: { type: String, default: 'AI 리포트' }, // 예: '구매 리포트'
})

const pct = ref(6)
let timer = null

// 산지→분석→정리 단계 문구를 진행률에 따라 바꿔 체감 진행감을 준다.
const STAGES = [
  '신선한 데이터를 산지에서 모으는 중',
  '소비 패턴을 꼼꼼히 살펴보는 중',
  '리포트를 정성껏 담는 중',
]
const stage = computed(() => STAGES[Math.min(STAGES.length - 1, Math.floor(pct.value / 33))])

onMounted(() => {
  timer = setInterval(() => {
    // 처음엔 빠르게, 92%에 가까울수록 느리게(점근).
    if (pct.value < 92) pct.value = Math.min(92, pct.value + Math.max(0.5, (92 - pct.value) * 0.05))
  }, 110)
})
onBeforeUnmount(() => timer && clearInterval(timer))
</script>

<template>
  <div class="ail">
    <div class="badge">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 21V11" />
        <path d="M12 11C12 7 15 4 20 4c0 4-3 7-8 7Z" />
        <path d="M12 13.5C12 10.5 9 8 4.5 8c0 3.5 3 6 7.5 5.5Z" />
      </svg>
    </div>

    <h3 class="ail-t">
      <template v-if="name"><b>{{ name }}</b>님의 </template>{{ title }}를 만들고 있어요
    </h3>
    <p class="ail-sub">{{ stage }}…</p>

    <div class="ail-bar"><div class="ail-fill" :style="{ width: pct + '%' }"></div></div>
    <span class="ail-pct">{{ Math.round(pct) }}%</span>
  </div>
</template>

<style scoped>
.ail{ text-align:center; padding:60px 20px; max-width:440px; margin:0 auto; }

.badge{
  width:66px; height:66px; margin:0 auto 18px; border-radius:20px;
  background:var(--leaf-50); color:var(--leaf-600);
  display:flex; align-items:center; justify-content:center;
  box-shadow:var(--shadow-sm); animation:bob 1.7s ease-in-out infinite;
}
.badge svg{ width:34px; height:34px; }
@keyframes bob{ 0%,100%{ transform:translateY(0) } 50%{ transform:translateY(-6px) } }

.ail-t{ font-size:18px; font-weight:800; color:var(--ink); margin:0 0 6px; letter-spacing:-.02em; }
.ail-t b{ color:var(--leaf-700); }
.ail-sub{ font-size:13.5px; color:var(--muted); margin:0 0 22px; }

.ail-bar{ height:10px; border-radius:999px; background:var(--leaf-50); overflow:hidden; }
.ail-fill{
  height:100%; border-radius:999px; position:relative;
  background:linear-gradient(90deg, var(--leaf-500), var(--leaf-600));
  transition:width .25s ease;
}
/* 진행 중임을 보여주는 은은한 흐름(shimmer) */
.ail-fill::after{
  content:""; position:absolute; inset:0;
  background:linear-gradient(90deg, transparent, rgba(255,255,255,.45), transparent);
  animation:sh 1.3s linear infinite;
}
@keyframes sh{ from{ transform:translateX(-100%) } to{ transform:translateX(100%) } }

.ail-pct{ display:inline-block; margin-top:11px; font-size:13px; font-weight:800; color:var(--leaf-700); }
</style>
