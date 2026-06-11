<script setup>
import { ref, computed, onMounted } from 'vue'
import { followApi } from '../api/follow'
import { useFollowStore } from '../stores/follow'

const follow = useFollowStore()
const all = ref([])
const loading = ref(true)
const error = ref('')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    all.value = (await followApi.following()) || []
    follow.ids = all.value.map((s) => s.sellerId)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const sellers = computed(() => all.value.filter((s) => follow.isFollowing(s.sellerId)))
const unfollowError = ref('')

async function unfollow(sellerId) {
  unfollowError.value = ''
  try {
    await follow.toggle(sellerId)
  } catch (e) {
    unfollowError.value = e.message || '팔로우 취소에 실패했어요. 다시 시도해주세요.'
  }
}
</script>

<template>
  <div>
    <h1 class="title">👥 팔로우한 판매자</h1>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>
    <div v-else-if="sellers.length === 0" class="empty">
      <span class="emoji">🧑‍🌾</span>아직 팔로우한 판매자가 없어요.<br />
      <router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 둘러보기</router-link>
    </div>

    <p v-if="unfollowError" class="err">{{ unfollowError }}</p>
    <ul v-else-if="sellers.length" class="seller-list">
      <li v-for="s in sellers" :key="s.sellerId" class="seller-row card">
        <div class="avatar">🏡</div>
        <div class="info">
          <span class="name">{{ s.name }}</span>
          <span class="meta muted">팔로워 {{ s.followerCount }} · 상품 {{ s.productCount }}</span>
        </div>
        <button class="btn btn-outline btn-sm" @click="unfollow(s.sellerId)">팔로잉 ✓</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.title { font-size: 24px; margin-bottom: 18px; }
.seller-list { display: flex; flex-direction: column; gap: 12px; }
.seller-row { display: flex; align-items: center; gap: 14px; padding: 14px 16px; }
.avatar { font-size: 34px; width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; background: var(--color-primary-soft); border-radius: 50%; }
.info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.info .name { font-weight: 700; font-size: 16px; }
.info .meta { font-size: 13px; }
.btn-sm { padding: 8px 14px; font-size: 14px; }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 0 0 12px; }
</style>
