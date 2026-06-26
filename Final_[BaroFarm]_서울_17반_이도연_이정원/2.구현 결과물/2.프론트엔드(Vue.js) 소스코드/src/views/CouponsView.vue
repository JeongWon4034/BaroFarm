<script setup>
import { ref, onMounted } from 'vue'
import { couponApi } from '../api/coupons'
import { dateOnly } from '../utils/format'

const coupons = ref([])
const loading = ref(true)

onMounted(async () => {
  coupons.value = (await couponApi.myCoupons().catch(() => [])) || []
  loading.value = false
})

const statusLabel = (s) => ({ ISSUED: '사용 가능', USED: '사용 완료', EXPIRED: '만료' }[s] || s)
</script>

<template>
  <div>
    <h1 class="title">🎟️ 내 쿠폰</h1>
    <p class="muted sub">챌린지를 완료하면 다음 구매에 쓸 추가 할인 쿠폰을 받아요.</p>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="!coupons.length" class="empty">
      <span class="emoji">🎟️</span>아직 받은 쿠폰이 없어요.<br />
      <router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'challenges' }">챌린지 도전하기</router-link>
    </div>

    <ul v-else class="cp-list">
      <li v-for="c in coupons" :key="c.couponId" class="cp card" :class="{ dim: c.status !== 'ISSUED' }">
        <div class="cp-rate">{{ c.discountRate }}<small>%</small></div>
        <div class="cp-info">
          <div class="cp-from">{{ c.sourceChallengeTitle || '챌린지 보상' }} 쿠폰</div>
          <div class="cp-meta muted">
            <template v-if="c.status === 'ISSUED' && c.expiresAt">~{{ dateOnly(c.expiresAt) }}까지</template>
            <template v-else>{{ statusLabel(c.status) }}</template>
          </div>
        </div>
        <span class="cp-status" :class="c.status.toLowerCase()">{{ statusLabel(c.status) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.title { font-size: 24px; margin-bottom: 6px; }
.sub { margin: 0 0 20px; }
.cp-list { display: flex; flex-direction: column; gap: 12px; }
.cp { display: flex; align-items: center; gap: 18px; padding: 16px 20px; }
.cp.dim { opacity: .5; }
.cp-rate { font-size: 28px; font-weight: 800; color: var(--deal); min-width: 70px; }
.cp-rate small { font-size: 16px; }
.cp-info { flex: 1; min-width: 0; }
.cp-from { font-weight: 700; font-size: 15px; }
.cp-meta { font-size: 13px; margin-top: 2px; }
.cp-status { font-size: 12px; font-weight: 700; padding: 4px 11px; border-radius: 999px; white-space: nowrap; }
.cp-status.issued { background: var(--leaf-50); color: var(--leaf-700); }
.cp-status.used, .cp-status.expired { background: #eef1f3; color: #6b7280; }
.empty { text-align: center; color: var(--muted); padding: 60px 20px; }
.empty .emoji { display: block; font-size: 40px; margin-bottom: 12px; }
</style>
