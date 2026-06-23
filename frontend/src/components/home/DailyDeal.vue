<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { won, thumbEmoji } from '../../utils/format'

// 일일특가 — 목록에서 할인율이 가장 높은 상품 1개를 prop으로 받아 크게 노출.
const props = defineProps({ product: { type: Object, default: null } })
const emit = defineEmits(['add'])
const router = useRouter()

// 오늘 자정까지 남은 시간 카운트다운 (매일 밤 12시 리셋).
const cd = ref('00:00:00')
let timer = null
function tick() {
  const now = new Date()
  const midnight = new Date(now)
  midnight.setHours(24, 0, 0, 0) // 다음 자정(내일 00:00)
  const diff = Math.max(0, Math.floor((midnight - now) / 1000))
  const pad = (n) => String(n).padStart(2, '0')
  cd.value = `${pad(Math.floor(diff / 3600))}:${pad(Math.floor((diff % 3600) / 60))}:${pad(diff % 60)}`
}
onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onBeforeUnmount(() => timer && clearInterval(timer))

function goDetail() {
  if (props.product) router.push({ name: 'product-detail', params: { id: props.product.productId } })
}
function add() {
  if (props.product) emit('add', props.product)
}
</script>

<template>
  <section v-if="product" class="daily">
    <div class="daily-head">
      <h2 class="daily-t">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 18.6 5 21.4l1.4-6.8L1.3 9.9l6.9-.8L12 2Z"/></svg>일일특가
      </h2>
      <div class="daily-cd">
        <span class="cdic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span>
        <span class="num">{{ cd }}</span>
      </div>
      <p class="daily-sub">망설이면 늦어요</p>
    </div>

    <div class="daily-card" @click="goDetail">
      <div class="dc-img" :class="'t-' + product.category"><span class="emoji">{{ thumbEmoji(product) }}</span></div>
      <div class="dc-info">
        <h3 class="dc-name">{{ product.name }}</h3>
        <div class="price">
          <span v-if="(product.discountRate ?? 0) > 0" class="pct">{{ product.discountRate }}%</span>
          <span class="now">{{ won(product.discountedPrice ?? product.price) }}</span>
          <span v-if="(product.discountRate ?? 0) > 0" class="was">{{ won(product.price) }}</span>
        </div>
        <div v-if="product.reviewCount" class="rev">후기 {{ product.reviewCount }}개</div>
        <button class="dc-buy" @click.stop="add">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h2.2l2 13.4a1.5 1.5 0 0 0 1.5 1.3h9.7a1.5 1.5 0 0 0 1.5-1.2L21 7H5.5"/><circle cx="9" cy="21" r="1.3"/><circle cx="18" cy="21" r="1.3"/></svg>
          담기
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.daily{ padding-top:46px; }
.daily-head{ display:flex; align-items:center; gap:16px; margin-bottom:20px; flex-wrap:wrap; }
.daily-t{ display:flex; align-items:center; gap:9px; font-size:24px; font-weight:800; letter-spacing:-.02em; margin:0; }
.daily-t svg{ width:24px; height:24px; color:var(--gold); }
.daily-cd{ display:flex; align-items:center; gap:9px; }
.daily-cd .cdic{ width:32px; height:32px; border-radius:50%; background:#efe9ff; color:#6b2fb3; display:flex; align-items:center; justify-content:center; }
.daily-cd .cdic svg{ width:18px; height:18px; }
.daily-cd .num{ font-size:24px; font-weight:800; font-variant-numeric:tabular-nums; color:#5b41c4; }
.daily-sub{ color:var(--faint); font-size:14px; margin:0; }

.daily-card{ display:grid; grid-template-columns:1.12fr 1fr; background:var(--paper); border:1px solid var(--line); border-radius:22px; overflow:hidden; box-shadow:var(--shadow-sm); transition:box-shadow .2s, transform .2s; cursor:pointer; }
.daily-card:hover{ box-shadow:var(--shadow-lg); transform:translateY(-3px); }
.dc-img{ position:relative; aspect-ratio:4/3; background:#f4f5f3; display:flex; align-items:center; justify-content:center; }
.dc-img .emoji{ font-size:96px; }
.t-vegetable, .t-root, .t-mushroom{ background:#eef6e6; }
.t-fruit{ background:#fbf2e6; } .t-seafood{ background:#eaf2f7; } .t-meat{ background:#f8eeeb; } .t-grain{ background:#f6f1e3; }
.dc-info{ padding:38px 42px; display:flex; flex-direction:column; justify-content:center; }
.dc-name{ font-size:25px; font-weight:800; letter-spacing:-.02em; line-height:1.32; margin:0 0 18px; }
.dc-info .price{ display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; margin:0 0 12px; }
.dc-info .price .pct{ color:var(--deal); font-weight:800; font-size:22px; }
.dc-info .price .now{ font-weight:800; font-size:29px; letter-spacing:-.02em; }
.dc-info .price .was{ color:var(--faint); text-decoration:line-through; font-size:15px; }
.rev{ font-size:13.5px; color:var(--faint); margin-bottom:24px; }
.dc-buy{ align-self:flex-start; display:inline-flex; align-items:center; gap:8px; height:48px; padding:0 26px; border-radius:12px; border:1.5px solid var(--line-2); background:#fff; font-weight:700; font-size:15px; color:var(--ink); transition:.15s; }
.dc-buy:hover{ border-color:var(--leaf-500); background:var(--leaf-50); color:var(--leaf-700); }
.dc-buy svg{ width:18px; height:18px; }

@media (max-width:780px){ .daily-card{ grid-template-columns:1fr; } .dc-info{ padding:26px 24px; } }
</style>
