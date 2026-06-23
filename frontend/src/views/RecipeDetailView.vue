<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { productApi } from '../api/products'

const route = useRoute()
const recipe = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    // 첫 호출은 AI 이미지 생성으로 십수 초 걸릴 수 있음(그날 이후엔 캐시).
    recipe.value = await productApi.recipeDetail(route.params.idx)
  } catch (e) {
    error.value = e?.message || '레시피를 불러오지 못했어요.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="rd">
    <router-link :to="{ name: 'products' }" class="back">← 홈으로</router-link>

    <div v-if="loading" class="empty">
      <span class="spin"></span>
      <p>AI가 레시피 이미지와 조리법을 만들고 있어요…<br /><small>처음 한 번만 시간이 걸려요</small></p>
    </div>

    <div v-else-if="error || !recipe" class="empty"><span class="emoji">⚠️</span>{{ error || '레시피가 없어요.' }}</div>

    <template v-else>
      <!-- 이미지(AI 생성) 또는 그라데이션 폴백 -->
      <div class="hero" :class="{ ph: !recipe.image }">
        <img v-if="recipe.image" :src="recipe.image" :alt="recipe.title" />
        <div class="hero-copy">
          <span class="eye">{{ recipe.eyebrow }}</span>
          <h1>{{ recipe.title }}</h1>
        </div>
      </div>

      <!-- 재료(실제 판매 상품 링크) -->
      <section class="block">
        <h2>재료</h2>
        <div class="ings">
          <router-link
            v-for="(g, i) in recipe.ingredients" :key="i" class="chip"
            :to="g.productId ? { name: 'product-detail', params: { id: g.productId } } : { name: 'products', query: { keyword: g.label } }"
          >{{ g.label }}<span v-if="g.productId" class="buy">담으러 가기 ›</span></router-link>
        </div>
      </section>

      <!-- 조리법 -->
      <section class="block" v-if="recipe.steps?.length">
        <h2>조리법</h2>
        <ol class="steps">
          <li v-for="(s, i) in recipe.steps" :key="i"><span class="no">{{ i + 1 }}</span><p>{{ s }}</p></li>
        </ol>
      </section>
      <p v-else class="muted">조리법을 불러오지 못했어요. (AI 미연결 시 재료만 표시)</p>
    </template>
  </div>
</template>

<style scoped>
.rd{ max-width:860px; margin:0 auto; }
.back{ display:inline-block; margin-bottom:18px; font-size:14px; font-weight:600; color:var(--muted); }
.back:hover{ color:var(--leaf-700); }

.empty{ text-align:center; padding:80px 20px; color:var(--muted); }
.empty .emoji{ font-size:42px; display:block; margin-bottom:12px; }
.empty small{ color:var(--faint); font-size:12.5px; }
.spin{ width:34px; height:34px; border-radius:50%; border:3px solid var(--leaf-100); border-top-color:var(--leaf-600);
  display:inline-block; margin-bottom:16px; animation:sp .8s linear infinite; }
@keyframes sp{ to{ transform:rotate(360deg); } }

.hero{ position:relative; border-radius:22px; overflow:hidden; aspect-ratio:16/10; margin-bottom:28px; background:#000; }
.hero.ph{ background:linear-gradient(135deg,#cfe0d4,#b6d3c0); }
.hero img{ width:100%; height:100%; object-fit:cover; display:block; }
.hero-copy{ position:absolute; left:0; right:0; bottom:0; padding:30px 32px; color:#fff;
  background:linear-gradient(180deg,rgba(20,24,14,0),rgba(20,24,14,.78)); }
.hero-copy .eye{ font-size:13.5px; font-weight:500; font-style:italic; opacity:.9; }
.hero-copy h1{ margin:8px 0 0; font-size:clamp(24px,3.4vw,36px); font-weight:800; letter-spacing:-.02em; line-height:1.25; white-space:pre-line; }

.block{ margin-bottom:30px; }
.block h2{ font-size:18px; font-weight:800; margin:0 0 14px; color:var(--ink); }
.ings{ display:flex; gap:10px; flex-wrap:wrap; }
.chip{ display:inline-flex; align-items:center; gap:7px; font-size:14px; font-weight:600; color:var(--leaf-700);
  background:var(--leaf-50); padding:10px 15px; border-radius:999px; transition:.13s; }
.chip:hover{ background:var(--leaf-100); }
.chip .buy{ font-size:12px; color:var(--leaf-600); font-weight:700; }

.steps{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:14px; }
.steps li{ display:flex; gap:14px; align-items:flex-start; }
.steps .no{ flex:none; width:28px; height:28px; border-radius:50%; background:var(--leaf-600); color:#fff;
  font-size:14px; font-weight:800; display:flex; align-items:center; justify-content:center; }
.steps p{ margin:2px 0 0; font-size:15.5px; line-height:1.55; color:var(--ink-2); }
.muted{ color:var(--muted); }
</style>
