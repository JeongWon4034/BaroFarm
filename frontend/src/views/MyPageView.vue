<script setup>
import { ref, onMounted } from 'vue'
import { orderApi, reviewApi } from '../api/orders'
import { useAuthStore } from '../stores/auth'
import { won, thumbEmoji, dateOnly } from '../utils/format'
import StarRating from '../components/StarRating.vue'

const auth = useAuthStore()
const orders = ref([])
const loading = ref(true)
const error = ref('')

// 리뷰 작성 상태
const reviewing = ref(null) // orderId
const reviewRating = ref(5)
const reviewContent = ref('')
const reviewMsg = ref('')
const reviewDone = ref(new Set())

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    orders.value = await orderApi.myOrders()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function openReview(orderId) {
  reviewing.value = orderId
  reviewRating.value = 5
  reviewContent.value = ''
  reviewMsg.value = ''
}

async function submitReview(order) {
  reviewMsg.value = ''
  try {
    await reviewApi.create({ orderId: order.orderId, rating: reviewRating.value, content: reviewContent.value })
    reviewDone.value.add(order.orderId)
    reviewing.value = null
  } catch (e) {
    reviewMsg.value = e.message
  }
}
</script>

<template>
  <div>
    <div class="profile card">
      <span class="avatar">👤</span>
      <div>
        <strong class="uname">{{ auth.user?.name }}</strong>
        <span class="badge" style="margin-left:8px">{{ auth.user?.role === 'SELLER' ? '판매자' : '구매자' }}</span>
        <p class="muted email">{{ auth.user?.email }}</p>
      </div>
    </div>

    <h2 class="section-title">📦 구매 내역</h2>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>
    <div v-else-if="orders.length === 0" class="empty">
      <span class="emoji">🧾</span>아직 구매 내역이 없어요.
      <br /><router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 보러 가기</router-link>
    </div>

    <ul v-else class="orders">
      <li v-for="o in orders" :key="o.orderId" class="order card">
        <div class="order-main">
          <span class="thumb">{{ thumbEmoji({ name: o.productName }) }}</span>
          <div class="info">
            <strong class="pname">{{ o.productName }}</strong>
            <span class="muted sm">주문번호 #{{ o.orderId }} · {{ dateOnly(o.orderDate) }}</span>
          </div>
          <div class="right">
            <span class="status badge">{{ o.status || '결제완료' }}</span>
            <span class="qprice">{{ won(o.totalPrice) }} <span class="muted">/ {{ o.quantity }}개</span></span>
          </div>
        </div>

        <div class="order-actions">
          <span v-if="reviewDone.has(o.orderId)" class="done muted">✅ 리뷰 작성 완료</span>
          <button v-else-if="reviewing !== o.orderId" class="btn btn-outline sm-btn" @click="openReview(o.orderId)">✍️ 리뷰 작성</button>
        </div>

        <!-- 리뷰 폼 -->
        <div v-if="reviewing === o.orderId" class="review-form">
          <div class="rate-pick">
            <span class="muted">별점</span>
            <button v-for="n in 5" :key="n" class="star-btn" :class="{ on: n <= reviewRating }" @click="reviewRating = n">★</button>
            <span class="muted">{{ reviewRating }}점</span>
          </div>
          <textarea v-model="reviewContent" class="input" rows="2" placeholder="상품은 어떠셨나요?"></textarea>
          <p v-if="reviewMsg" class="err">{{ reviewMsg }}</p>
          <div class="form-actions">
            <button class="btn btn-outline sm-btn" @click="reviewing = null">취소</button>
            <button class="btn btn-primary sm-btn" @click="submitReview(o)">등록</button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.profile { display: flex; align-items: center; gap: 16px; padding: 20px; margin-bottom: 28px; }
.avatar { font-size: 40px; background: var(--color-primary-soft); border-radius: 50%; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; }
.uname { font-size: 18px; }
.email { margin: 4px 0 0; font-size: 14px; }

.section-title { font-size: 20px; margin-bottom: 16px; }
.orders { display: flex; flex-direction: column; gap: 12px; }
.order { padding: 16px; }
.order-main { display: flex; align-items: center; gap: 14px; }
.order .thumb { font-size: 34px; background: var(--color-primary-soft); border-radius: var(--radius-sm); width: 52px; text-align: center; padding: 6px 0; }
.order .info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.pname { font-size: 16px; }
.sm { font-size: 13px; }
.right { text-align: right; display: flex; flex-direction: column; gap: 6px; align-items: flex-end; }
.qprice { font-weight: 700; }

.order-actions { margin-top: 12px; }
.done { font-size: 14px; }
.sm-btn { padding: 8px 14px; font-size: 14px; }

.review-form { margin-top: 12px; border-top: 1px dashed var(--color-border); padding-top: 12px; }
.rate-pick { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.star-btn { border: none; background: transparent; font-size: 22px; color: #d6dade; padding: 0; }
.star-btn.on { color: var(--color-star); }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; }
.err { color: var(--color-accent-dark); font-size: 14px; }
</style>
