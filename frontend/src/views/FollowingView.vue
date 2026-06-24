<script setup>
import { ref, computed, onMounted } from 'vue'
import { followApi } from '../api/follow'
import { productApi } from '../api/products'
import { useFollowStore } from '../stores/follow'
import { useCartStore } from '../stores/cart'
import ProductCard from '../components/ProductCard.vue'

const follow = useFollowStore()
const cart = useCartStore()
const sellers = ref([]) // 팔로우한 판매자 목록
const products = ref([]) // 팔로우한 판매자들이 파는 상품
const loading = ref(true)
const error = ref('')
const selected = ref(null) // 선택된 판매자 id (null = 전체)
const unfollowError = ref('')
const toast = ref('')
let toastTimer

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    const list = (await followApi.following()) || []
    sellers.value = list
    follow.ids = list.map((s) => s.sellerId)
    if (list.length) {
      // 카탈로그가 작아 한 번에 받아 팔로우 판매자 것만 필터 (page는 0-인덱스)
      const res = await productApi.list({ page: 0, size: 500 })
      const all = res?.content ?? res ?? []
      const ids = new Set(list.map((s) => s.sellerId))
      products.value = all.filter((p) => ids.has(p.sellerId))
    } else {
      products.value = []
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 언팔로우 즉시 반영 — follow 스토어 기준으로 거름
const followed = computed(() => sellers.value.filter((s) => follow.isFollowing(s.sellerId)))
const selectedSeller = computed(() => sellers.value.find((s) => s.sellerId === selected.value) || null)
const productCountOf = (sellerId) => products.value.filter((p) => p.sellerId === sellerId).length

const visibleProducts = computed(() => {
  const base = products.value.filter((p) => follow.isFollowing(p.sellerId))
  return selected.value == null ? base : base.filter((p) => p.sellerId === selected.value)
})

async function unfollow(sellerId) {
  unfollowError.value = ''
  try {
    await follow.toggle(sellerId)
    if (selected.value === sellerId) selected.value = null // 필터 해제
  } catch (e) {
    unfollowError.value = e.message || '팔로우 취소에 실패했어요. 다시 시도해주세요.'
  }
}

function addToCart(product) {
  cart.add(product, 1)
  toast.value = `${product.name} · 장바구니에 담았어요`
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 1800)
}
</script>

<template>
  <div>
    <h1 class="title">👥 팔로잉</h1>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>
    <div v-else-if="followed.length === 0" class="empty">
      <span class="emoji">🧑‍🌾</span>아직 팔로우한 판매자가 없어요.<br />
      <router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 둘러보기</router-link>
    </div>

    <template v-else>
      <!-- 판매자 기준 필터 칩 -->
      <div class="chips">
        <button class="chip" :class="{ on: selected === null }" @click="selected = null">
          전체 <span class="cnt">{{ visibleProducts.length }}</span>
        </button>
        <button
          v-for="s in followed"
          :key="s.sellerId"
          class="chip"
          :class="{ on: selected === s.sellerId }"
          @click="selected = s.sellerId"
        >
          🏡 {{ s.name }} <span class="cnt">{{ productCountOf(s.sellerId) }}</span>
        </button>
      </div>

      <!-- 선택된 판매자 정보 + 언팔로우 -->
      <div v-if="selectedSeller" class="seller-bar card">
        <div class="avatar">🏡</div>
        <div class="info">
          <span class="name">{{ selectedSeller.name }}</span>
          <span class="meta muted">팔로워 {{ selectedSeller.followerCount }} · 상품 {{ productCountOf(selectedSeller.sellerId) }}</span>
        </div>
        <button class="btn btn-outline btn-sm" @click="unfollow(selectedSeller.sellerId)">팔로잉 ✓</button>
      </div>

      <p v-if="unfollowError" class="err">{{ unfollowError }}</p>

      <!-- 상품 그리드 -->
      <div v-if="visibleProducts.length" class="prod-grid">
        <ProductCard v-for="p in visibleProducts" :key="p.productId" :product="p" @add="addToCart" />
      </div>
      <div v-else class="empty sm">
        <span class="emoji">📦</span>
        {{ selected === null ? '팔로우한 판매자가 등록한 상품이 아직 없어요.' : '이 판매자가 등록한 상품이 아직 없어요.' }}
      </div>
    </template>

    <transition name="toast">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.title { font-size: 24px; margin-bottom: 18px; }

.chips { display: flex; flex-wrap: wrap; gap: 9px; margin-bottom: 18px; }
.chip {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 8px 14px; border-radius: 999px; border: 1px solid var(--line-2);
  background: #fff; color: var(--ink-2); font-size: 14px; font-weight: 600;
  cursor: pointer; transition: .14s;
}
.chip:hover { border-color: var(--leaf-300); color: var(--leaf-700); }
.chip.on { background: var(--leaf-600); border-color: var(--leaf-600); color: #fff; }
.chip .cnt {
  font-size: 12px; font-weight: 700; min-width: 18px; height: 18px; padding: 0 5px;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 9px; background: var(--leaf-50); color: var(--leaf-700);
}
.chip.on .cnt { background: rgba(255,255,255,.25); color: #fff; }

.seller-bar { display: flex; align-items: center; gap: 14px; padding: 13px 16px; margin-bottom: 16px; }
.seller-bar .avatar {
  font-size: 28px; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center;
  background: var(--leaf-50); border-radius: 50%;
}
.seller-bar .info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.seller-bar .info .name { font-weight: 700; font-size: 16px; }
.seller-bar .info .meta { font-size: 13px; }
.btn-sm { padding: 8px 14px; font-size: 14px; }

.prod-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 18px; }

.err { color: var(--deal); font-size: 14px; margin: 0 0 12px; }
.empty { text-align: center; color: var(--muted); padding: 60px 20px; }
.empty .emoji { display: block; font-size: 40px; margin-bottom: 12px; }
.empty.sm { padding: 40px 20px; }

.toast {
  position: fixed; left: 50%; bottom: 30px; transform: translateX(-50%);
  background: var(--ink); color: #fff; padding: 12px 20px; border-radius: 10px;
  font-size: 14px; font-weight: 600; box-shadow: var(--shadow-lg); z-index: 50;
}
.toast-enter-active, .toast-leave-active { transition: opacity .2s, transform .2s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }
</style>
