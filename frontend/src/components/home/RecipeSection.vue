<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { productApi } from '../../api/products'

// 오늘의 레시피 — 식약처 레시피 DB(실제 사진·조리법)에서, 우리가 파는 재료와 겹치는 레시피를 받아온다.
// 각 재료는 실제 판매 상품에 매핑되어, 클릭하면 그 상품으로 연결된다. (하루 1회 서버 캐시)
const RECIPES = ref([])
const active = ref(0)
const cur = computed(() => RECIPES.value[active.value] || null)

// 메인 배너처럼 일정 시간마다 자동 전환(마우스 올리면 멈춤).
let timer = null
const AUTOPLAY = 4500
function go(i) { if (RECIPES.value.length) active.value = (i + RECIPES.value.length) % RECIPES.value.length }
function start() { stop(); if (RECIPES.value.length > 1) timer = setInterval(() => go(active.value + 1), AUTOPLAY) }
function stop() { if (timer) { clearInterval(timer); timer = null } }
function select(i) { go(i); start() } // 탭 클릭 시 그 레시피로 + 타이머 리셋

onMounted(async () => {
  try {
    const r = await productApi.recipes()
    RECIPES.value = Array.isArray(r) ? r : []
    start()
  } catch {
    RECIPES.value = []
  }
})
onBeforeUnmount(stop)
</script>

<template>
  <section class="sec" v-if="RECIPES.length" @mouseenter="stop" @mouseleave="start">
    <div class="sec-head">
      <div class="l">
        <h2>오늘의 레시피</h2>
        <p>판매 중인 제철 재료로 만드는 한 끼 — AI 추천</p>
      </div>
    </div>

    <div class="recipe-tabs">
      <button v-for="(r, i) in RECIPES" :key="i" class="rtab" :class="{ on: i === active }" @click="select(i)">{{ r.title }}</button>
    </div>

    <router-link class="rbanner" v-if="cur" :to="{ name: 'recipe-detail', params: { idx: active } }">
      <Transition name="rfade">
        <div class="rb-inner" :key="active">
          <img v-if="cur.image" :src="cur.image" class="rb-bg" alt="" aria-hidden="true" />
          <img v-if="cur.image" :src="cur.image" :alt="cur.title" class="rb-img" />
          <div class="grad"></div>
          <div class="rb-copy">
            <div class="rb-eye">{{ cur.eyebrow }}</div>
            <h3>{{ cur.title }}</h3>
            <span class="rb-cta">조리법·이미지 보기 ›</span>
          </div>
        </div>
      </Transition>
      <span class="ph-tag">레시피</span>
    </router-link>

    <div class="ring-row" v-if="cur">
      <span class="ring-label">관련 재료</span>
      <router-link
        v-for="(g, i) in cur.ingredients" :key="i" class="ring-chip"
        :to="g.productId ? { name: 'product-detail', params: { id: g.productId } } : { name: 'products', query: { keyword: g.label } }"
      >{{ g.label }}</router-link>
    </div>
  </section>
</template>

<style scoped>
.sec{ padding-top:46px; }
.sec-head{ margin-bottom:20px; }
.sec-head h2{ font-size:24px; font-weight:800; letter-spacing:-.025em; margin:0 0 5px; }
.sec-head p{ margin:0; color:var(--muted); font-size:14px; }

.recipe-tabs{ display:flex; gap:9px; overflow-x:auto; padding-bottom:4px; margin-bottom:20px; }
.rtab{ flex:none; padding:11px 20px; border-radius:999px; border:1.5px solid var(--line-2); background:#fff; font-size:15px; font-weight:600; color:var(--ink-2); white-space:nowrap; transition:.14s; }
.rtab:hover{ border-color:var(--leaf-300); background:var(--leaf-50); color:var(--leaf-700); }
.rtab.on{ background:#23281c; border-color:#23281c; color:#fff; }

.rbanner{ display:block; position:relative; border-radius:22px; overflow:hidden; aspect-ratio:1240/440; margin-bottom:18px; background:var(--leaf-700); transition:transform .15s; }
.rbanner:hover{ transform:translateY(-2px); }
.rb-cta{ display:inline-block; margin-top:14px; background:#fff; color:var(--leaf-700); font-weight:700; font-size:13.5px; padding:8px 15px; border-radius:999px; }
.rb-inner{ position:absolute; inset:0; }
/* 블러 배경 = 같은 사진을 흐리게 깔아 여백을 자연스럽게 채움(세련) */
.rb-bg{ position:absolute; inset:0; z-index:0; width:100%; height:100%; object-fit:cover; filter:blur(28px) brightness(.78); transform:scale(1.15); }
.rb-img{ position:absolute; inset:0; z-index:1; width:100%; height:100%; object-fit:contain; }
.grad{ position:absolute; inset:0; z-index:2; background:linear-gradient(180deg,rgba(20,24,14,0) 34%,rgba(20,24,14,.74) 100%); }
.rb-copy{ position:absolute; left:36px; bottom:34px; z-index:3; color:#fff; max-width:72%; }
.ph-tag{ position:absolute; top:14px; left:14px; z-index:5; background:rgba(28,34,21,.55); color:#fff; font-size:11.5px; font-weight:700; padding:5px 11px; border-radius:999px; }
/* 페이드 전환(자동 넘김 시 부드럽게 크로스페이드) */
.rfade-enter-active, .rfade-leave-active{ transition:opacity .6s ease; }
.rfade-enter-from, .rfade-leave-to{ opacity:0; }
.rb-eye{ font-size:14px; font-weight:500; letter-spacing:.03em; opacity:.86; margin-bottom:12px; font-style:italic; }
.rb-copy h3{ margin:0; font-size:clamp(22px,2.7vw,33px); font-weight:800; line-height:1.3; letter-spacing:-.02em; white-space:pre-line; text-shadow:0 2px 16px rgba(0,0,0,.32); }

.ring-row{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.ring-label{ font-size:13.5px; font-weight:700; color:var(--ink-2); }
.ring-chip{ font-size:13.5px; font-weight:600; color:var(--leaf-700); background:var(--leaf-50); padding:8px 14px; border-radius:999px; transition:.13s; }
.ring-chip:hover{ background:var(--leaf-100); }
</style>
