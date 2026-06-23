<script setup>
import { ref, computed } from 'vue'
// 이타닉 레시피 — 탭 + 긴 배너 + 관련 재료(검색 연결). 정적 에디토리얼.
const RECIPES = [
  { tab: '등갈비 구이', eyebrow: "Inside Grocer's Kitchen", title: '도축 +5일 풍미를 더한\n등갈비 구이 with 매콤 마늘 소스', ing: ['등갈비', '그린페퍼', '아스파라거스'] },
  { tab: '오리고기카모난반', eyebrow: "Inside Grocer's Kitchen", title: '겉은 바삭 속은 촉촉\n오리고기 카모난반 소바', ing: ['훈제오리', '메밀소바면', '쪽파'] },
  { tab: '연어메밀면샐러드', eyebrow: "Inside Grocer's Kitchen", title: '노르웨이산 생연어로\n상큼한 연어 메밀면 샐러드', ing: ['생연어', '메밀면', '채소믹스'] },
  { tab: '목살 스테이크', eyebrow: "Inside Grocer's Kitchen", title: '두툼하게 구워낸\n저온숙성 목살 스테이크', ing: ['목살', '통후추', '방울토마토'] },
]
const active = ref(0)
const cur = computed(() => RECIPES[active.value])
</script>

<template>
  <section class="sec">
    <div class="sec-head">
      <div class="l">
        <h2>이타닉 레시피</h2>
        <p>피크타임 식재료로 특별하게</p>
      </div>
    </div>

    <div class="recipe-tabs">
      <button v-for="(r, i) in RECIPES" :key="i" class="rtab" :class="{ on: i === active }" @click="active = i">{{ r.tab }}</button>
    </div>

    <div class="rbanner">
      <span class="ph-tag">레시피 배너</span>
      <div class="grad"></div>
      <div class="rb-copy">
        <div class="rb-eye">{{ cur.eyebrow }}</div>
        <h3>{{ cur.title }}</h3>
      </div>
    </div>

    <div class="ring-row">
      <span class="ring-label">관련 재료</span>
      <router-link
        v-for="(g, i) in cur.ing" :key="i"
        class="ring-chip" :to="{ name: 'products', query: { keyword: g } }"
      >{{ g }}</router-link>
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

.rbanner{ position:relative; border-radius:22px; overflow:hidden; aspect-ratio:1240/440; margin-bottom:18px; background:linear-gradient(135deg,#cfe0d4,#b6d3c0); }
.ph-tag{ position:absolute; top:14px; left:14px; z-index:3; background:rgba(28,34,21,.55); color:#fff; font-size:11.5px; font-weight:700; padding:5px 11px; border-radius:999px; }
.grad{ position:absolute; inset:0; z-index:1; background:linear-gradient(180deg,rgba(20,24,14,0) 34%,rgba(20,24,14,.74) 100%); }
.rb-copy{ position:absolute; left:36px; bottom:34px; z-index:2; color:#fff; max-width:72%; }
.rb-eye{ font-size:14px; font-weight:500; letter-spacing:.03em; opacity:.86; margin-bottom:12px; font-style:italic; }
.rb-copy h3{ margin:0; font-size:clamp(22px,2.7vw,33px); font-weight:800; line-height:1.3; letter-spacing:-.02em; white-space:pre-line; text-shadow:0 2px 16px rgba(0,0,0,.32); }

.ring-row{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.ring-label{ font-size:13.5px; font-weight:700; color:var(--ink-2); }
.ring-chip{ font-size:13.5px; font-weight:600; color:var(--leaf-700); background:var(--leaf-50); padding:8px 14px; border-radius:999px; transition:.13s; }
.ring-chip:hover{ background:var(--leaf-100); }
</style>
