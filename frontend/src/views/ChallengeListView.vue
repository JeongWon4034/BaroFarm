<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { challengeApi } from '../api/challenges'
import { useAuthStore } from '../stores/auth'
import { challengeStatus, dateOnly } from '../utils/format'

const router = useRouter()
const auth = useAuthStore()

const challenges = ref([])
const mine = ref({}) // challengeId -> UserChallenge
const loading = ref(true)
const error = ref('')
const joining = ref(null)
const msg = ref('')

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    challenges.value = await challengeApi.list()
    if (auth.isLoggedIn) {
      const my = await challengeApi.myChallenges().catch(() => [])
      mine.value = Object.fromEntries(my.map((c) => [c.challengeId, c]))
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 챌린지별 파생 상태(진행중/만료/달성) 맵: challengeId -> status
const statusMap = computed(() => {
  const m = {}
  for (const c of challenges.value) {
    const mc = mine.value[c.challengeId]
    if (mc) m[c.challengeId] = challengeStatus(c, mc)
  }
  return m
})
const ongoingCount = computed(() => Object.values(statusMap.value).filter((s) => s.key === 'ONGOING').length)
const completedCount = computed(() => Object.values(statusMap.value).filter((s) => s.key === 'COMPLETED').length)
const expiredCount = computed(() => Object.values(statusMap.value).filter((s) => s.key === 'EXPIRED').length)

function pct(c) {
  const m = mine.value[c.challengeId]
  if (!m) return 0
  return Math.min(100, Math.round((m.progress / c.goalCount) * 100))
}

async function join(c) {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: '/challenges' } })
    return
  }
  joining.value = c.challengeId
  msg.value = ''
  try {
    await challengeApi.join(c.challengeId)
    await load()
  } catch (e) {
    msg.value = e.message
  } finally {
    joining.value = null
  }
}
</script>

<template>
  <div>
    <div class="head">
      <h1>🏆 폐기 절감 챌린지</h1>
      <p class="muted sub">마감임박 상품을 구매할 때마다 진행도가 쌓여요. 음식물 폐기를 줄이고 뱃지를 모아보세요.</p>
    </div>

    <div v-if="auth.isLoggedIn" class="summary">
      진행 중 <strong>{{ ongoingCount }}</strong> · 달성 <strong>{{ completedCount }}</strong> · 만료 <strong>{{ expiredCount }}</strong>
    </div>

    <p v-if="msg" class="err">{{ msg }}</p>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>

    <div v-else class="grid">
      <div v-for="c in challenges" :key="c.challengeId" class="card ch-card">
        <div class="badge-emoji">{{ c.badgeEmoji }}</div>
        <div class="ch-body">
          <router-link :to="{ name: 'challenge-detail', params: { id: c.challengeId } }" class="ch-title">{{ c.title }}</router-link>
          <p class="ch-desc muted">{{ c.description }}</p>
          <p class="ch-goal muted sm">목표: 마감임박 상품 {{ c.goalCount }}개 구매 · {{ c.periodDays }}일</p>

          <template v-if="statusMap[c.challengeId]">
            <div class="st-badge" :class="statusMap[c.challengeId].cls">
              {{ statusMap[c.challengeId].emoji }} {{ statusMap[c.challengeId].label }}
              <span v-if="statusMap[c.challengeId].key === 'ONGOING'" class="dday">· {{ statusMap[c.challengeId].dday }}</span>
            </div>
            <template v-if="statusMap[c.challengeId].key !== 'COMPLETED'">
              <div class="bar"><div class="bar-fill" :class="{ 'fill-expired': statusMap[c.challengeId].key === 'EXPIRED' }" :style="{ width: pct(c) + '%' }" /></div>
              <div class="prog sm">
                {{ mine[c.challengeId].progress }} / {{ c.goalCount }}
                <span v-if="statusMap[c.challengeId].key === 'EXPIRED'" class="muted">· 목표 미달성</span>
              </div>
            </template>
            <p v-else class="prog sm muted">{{ dateOnly(mine[c.challengeId].completedAt) }} 달성 · {{ c.badgeEmoji }} 뱃지 획득</p>
          </template>
          <button v-else class="btn btn-primary sm-btn" :disabled="joining === c.challengeId" @click="join(c)">
            {{ joining === c.challengeId ? '참여 중…' : '도전하기' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.head { margin-bottom: 16px; }
.head h1 { font-size: 22px; margin: 0 0 6px; }
.sub { font-size: 14px; margin: 0; }
.summary { background: var(--color-primary-soft); border: 1px solid #cfe8d4; color: var(--color-primary-dark);
  border-radius: var(--radius-sm); padding: 10px 14px; font-size: 14px; margin-bottom: 18px; }
.summary strong { font-size: 16px; }
.err { color: var(--color-accent-dark); font-size: 14px; }

.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
@media (max-width: 720px) { .grid { grid-template-columns: 1fr; } }

.ch-card { display: flex; gap: 16px; padding: 18px; align-items: flex-start; }
.badge-emoji { font-size: 44px; line-height: 1; }
.ch-body { flex: 1; min-width: 0; }
.ch-title { font-size: 17px; font-weight: 700; color: var(--color-text); }
.ch-title:hover { color: var(--color-primary-dark); }
.ch-desc { font-size: 14px; line-height: 1.55; margin: 6px 0 8px; }
.ch-goal { margin: 0 0 12px; }
.sm { font-size: 13px; }

.bar { height: 8px; background: var(--color-bg); border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--color-primary); transition: width 0.3s ease; }
.bar-fill.fill-expired { background: var(--color-muted); }
.prog { margin-top: 6px; color: var(--color-muted); font-weight: 600; }
.sm-btn { padding: 8px 16px; font-size: 14px; }

/* 상태 배지(진행중/만료/달성) */
.st-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 700;
  padding: 4px 10px; border-radius: 999px; margin-bottom: 8px; }
.st-badge .dday { font-weight: 800; }
.st-ongoing { background: var(--color-primary-soft); color: var(--color-primary-dark); }
.st-expired { background: #f0f0f0; color: #888; }
.st-done { background: #fff4d6; color: #b8860b; }
/* 만료 카드는 전체를 차분하게 */
.ch-card:has(.st-expired) { opacity: 0.72; }
</style>
