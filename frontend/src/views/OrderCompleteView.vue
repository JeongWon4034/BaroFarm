<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { orderApi } from '../api/orders'
import { won } from '../utils/format'

const route = useRoute()
const orders = ref([])
const loading = ref(true)

const total = computed(() => orders.value.reduce((s, o) => s + (o.totalPrice || 0), 0))

onMounted(async () => {
  const ids = String(route.query.ids || '').split(',').filter(Boolean)
  const results = await Promise.all(ids.map((id) => orderApi.detail(id).catch(() => null)))
  orders.value = results.filter(Boolean)
  loading.value = false
})
</script>

<template>
  <div class="wrap">
    <div class="check">✅</div>
    <h1>주문이 완료되었습니다!</h1>
    <p class="muted">신선한 상품을 산지에서 바로 보내드릴게요. 🚚</p>

    <div v-if="loading" class="muted" style="margin:24px">불러오는 중…</div>
    <div v-else class="receipt card">
      <ul>
        <li v-for="o in orders" :key="o.orderId" class="line">
          <span>{{ o.productName }} <span class="muted">× {{ o.quantity }}</span></span>
          <span class="price">{{ won(o.totalPrice) }}</span>
        </li>
      </ul>
      <hr class="divider" />
      <div class="line total"><span>총 결제 금액</span><span class="price">{{ won(total) }}</span></div>
    </div>

    <div class="actions">
      <router-link class="btn btn-outline" :to="{ name: 'products' }">계속 쇼핑하기</router-link>
      <router-link class="btn btn-primary" :to="{ name: 'mypage' }">주문 내역 보기</router-link>
    </div>
  </div>
</template>

<style scoped>
.wrap { max-width: 520px; margin: 24px auto; text-align: center; }
.check { font-size: 64px; }
h1 { font-size: 24px; margin: 8px 0; }
.receipt { padding: 20px; text-align: left; margin: 24px 0; }
.line { display: flex; justify-content: space-between; padding: 8px 0; font-size: 15px; }
.divider { border: none; border-top: 1px solid var(--color-border); margin: 10px 0; }
.total { font-weight: 700; font-size: 17px; }
.actions { display: flex; gap: 12px; justify-content: center; }
</style>
