<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { challengeApi } from '../api/challenges'
import { useAuthStore } from '../stores/auth'
import { dateOnly, challengeStatus } from '../utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const challenge = ref(null)
const my = ref(null)
const loading = ref(true)
const error = ref('')
const joining = ref(false)
const msg = ref('')

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    challenge.value = await challengeApi.detail(route.params.id)
    if (auth.isLoggedIn) {
      const list = await challengeApi.myChallenges().catch(() => [])
      my.value = list.find((c) => c.challengeId === Number(route.params.id)) || null
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const status = computed(() => challengeStatus(challenge.value || {}, my.value))
const pct = computed(() => {
  if (!my.value || !challenge.value) return 0
  return Math.min(100, Math.round((my.value.progress / challenge.value.goalCount) * 100))
})

async function join() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  joining.value = true
  msg.value = ''
  try {
    await challengeApi.join(challenge.value.challengeId)
    await load()
  } catch (e) {
    msg.value = e.message
  } finally {
    joining.value = false
  }
}
</script>

<template>
  <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
  <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>

  <div v-else-if="challenge">
    <router-link :to="{ name: 'challenges' }" class="back muted">← 챌린지 목록으로</router-link>

    <div class="card hero">
      <div class="badge-emoji">{{ challenge.badgeEmoji }}</div>
      <h1 class="title">{{ challenge.title }}</h1>
      <p class="desc">{{ challenge.description }}</p>
      <p class="goal muted sm">목표: 마감임박 상품 <strong>{{ challenge.goalCount }}개</strong> 구매 · 기간 {{ challenge.periodDays }}일</p>
    </div>

    <!-- 내 진행 상황 / 달성 로그 (증빙) -->
    <div v-if="my" class="card progress-card" :class="{ dim: status.key === 'EXPIRED' }">
      <div class="sec-row">
        <h2 class="sec">내 진행 상황</h2>
        <span class="st-badge" :class="status.cls">
          {{ status.emoji }} {{ status.label }}
          <span v-if="status.key === 'ONGOING'" class="dday">· {{ status.dday }}</span>
        </span>
      </div>

      <!-- 달성 -->
      <template v-if="status.key === 'COMPLETED'">
        <div class="done-banner">🏅 달성 완료!</div>
        <p class="log muted sm">달성일: {{ dateOnly(my.completedAt) }} · 참여일: {{ dateOnly(my.joinedAt) }} · {{ challenge.badgeEmoji }} 뱃지 획득</p>
      </template>

      <!-- 기간 만료 -->
      <template v-else-if="status.key === 'EXPIRED'">
        <div class="bar"><div class="bar-fill fill-expired" :style="{ width: pct + '%' }" /></div>
        <p class="prog">{{ my.progress }} / {{ challenge.goalCount }} <span class="muted sm">· 목표 미달성</span></p>
        <p class="hint muted sm">참여일 {{ dateOnly(my.joinedAt) }} 기준 {{ challenge.periodDays }}일이 지나 종료된 챌린지예요. 다음 챌린지에 다시 도전해보세요.</p>
      </template>

      <!-- 진행 중 -->
      <template v-else>
        <div class="bar"><div class="bar-fill" :style="{ width: pct + '%' }" /></div>
        <p class="prog">{{ my.progress }} / {{ challenge.goalCount }} <span class="muted sm">({{ pct }}%)</span></p>
        <p class="hint muted sm">마감임박(떨이) 상품을 구매하면 진행도가 올라갑니다. 남은 기간 <strong>{{ status.dday }}</strong>.</p>
      </template>
    </div>

    <div v-else class="join-row">
      <p v-if="msg" class="err">{{ msg }}</p>
      <button class="btn btn-primary" :disabled="joining" @click="join">
        {{ joining ? '참여 중…' : '🚀 이 챌린지 도전하기' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 16px; font-size: 14px; }
.hero { padding: 28px; text-align: center; }
.badge-emoji { font-size: 64px; line-height: 1; margin-bottom: 10px; }
.title { font-size: 24px; margin: 0 0 8px; }
.desc { font-size: 15px; line-height: 1.6; color: #4a5560; margin: 0 0 10px; }
.goal { margin: 0; }
.sm { font-size: 13px; }

.progress-card { margin-top: 18px; padding: 20px; }
.progress-card.dim { opacity: 0.78; }
.sec-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 14px; }
.sec { font-size: 16px; margin: 0; }
.st-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 700;
  padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
.st-badge .dday { font-weight: 800; }
.st-ongoing { background: var(--color-primary-soft); color: var(--color-primary-dark); }
.st-expired { background: #f0f0f0; color: #888; }
.st-done { background: #fff4d6; color: #b8860b; }
.done-banner { color: var(--color-primary-dark); font-weight: 800; font-size: 20px; }
.log { margin: 10px 0 0; }
.bar { height: 12px; background: var(--color-bg); border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--color-primary); transition: width 0.3s ease; }
.bar-fill.fill-expired { background: var(--color-muted); }
.prog { font-size: 18px; font-weight: 700; margin: 10px 0 4px; }
.hint { margin: 0; }

.join-row { margin-top: 20px; text-align: center; }
.join-row .btn { padding: 14px 28px; font-size: 16px; }
.err { color: var(--color-accent-dark); font-size: 14px; margin-bottom: 10px; }
</style>
