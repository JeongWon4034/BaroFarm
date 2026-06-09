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

// 프로필 편집
const editing = ref(false)
const savingProfile = ref(false)
const profileMsg = ref('')
const pform = ref({ name: '', intro: '', phone: '', profileImage: '' })

function openProfileEdit() {
  const u = auth.user || {}
  pform.value = { name: u.name || '', intro: u.intro || '', phone: u.phone || '', profileImage: u.profileImage || '' }
  profileMsg.value = ''
  editing.value = true
}
function onPickImage(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 1024 * 1024) { profileMsg.value = '이미지는 1MB 이하만 가능해요.'; e.target.value = ''; return }
  const reader = new FileReader()
  reader.onload = () => { pform.value.profileImage = reader.result }
  reader.readAsDataURL(file)
}
async function saveProfile() {
  profileMsg.value = ''
  if (!pform.value.name.trim()) { profileMsg.value = '이름을 입력하세요.'; return }
  savingProfile.value = true
  try {
    await auth.updateProfile({
      name: pform.value.name.trim(),
      intro: pform.value.intro.trim() || null,
      phone: pform.value.phone.trim() || null,
      profileImage: pform.value.profileImage || null,
    })
    editing.value = false
  } catch (e) {
    profileMsg.value = e.message
  } finally {
    savingProfile.value = false
  }
}

// 리뷰 작성 상태
const reviewing = ref(null) // orderId
const reviewRating = ref(5)
const reviewContent = ref('')
const reviewMsg = ref('')

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
    const review = await reviewApi.create({ orderId: order.orderId, rating: reviewRating.value, content: reviewContent.value })
    order.reviewId = review.reviewId // DB 기준 상태로 즉시 반영(리로드해도 유지)
    reviewing.value = null
  } catch (e) {
    reviewMsg.value = e.message
  }
}
</script>

<template>
  <div>
    <div class="profile card">
      <span v-if="!auth.user?.profileImage" class="avatar">👤</span>
      <img v-else :src="auth.user.profileImage" class="avatar-img" alt="프로필" />
      <div class="pinfo">
        <strong class="uname">{{ auth.user?.name }}</strong>
        <span class="badge" style="margin-left:8px">{{ auth.user?.role === 'SELLER' ? '판매자' : '구매자' }}</span>
        <p class="muted email">{{ auth.user?.email }}</p>
        <p v-if="auth.user?.intro" class="intro">{{ auth.user.intro }}</p>
        <p v-if="auth.user?.phone" class="muted phone">📞 {{ auth.user.phone }}</p>
      </div>
      <button class="btn btn-outline sm-btn" @click="openProfileEdit">✏️ 편집</button>
    </div>

    <!-- 프로필 편집 -->
    <div v-if="editing" class="card edit-card">
      <h3 class="edit-title">프로필 편집</h3>
      <div class="edit-grid">
        <div class="img-pick">
          <span v-if="!pform.profileImage" class="avatar">👤</span>
          <img v-else :src="pform.profileImage" class="avatar-img" alt="미리보기" />
          <label class="btn btn-outline sm-btn file-btn">
            이미지 선택<input type="file" accept="image/*" @change="onPickImage" hidden />
          </label>
        </div>
        <div class="fields">
          <label class="fld"><span>이름</span><input v-model="pform.name" class="input" /></label>
          <label class="fld"><span>소개</span><input v-model="pform.intro" class="input" placeholder="한 줄 소개" /></label>
          <label class="fld"><span>전화번호</span><input v-model="pform.phone" class="input" placeholder="010-0000-0000" /></label>
        </div>
      </div>
      <p v-if="profileMsg" class="err">{{ profileMsg }}</p>
      <div class="edit-actions">
        <button class="btn btn-outline" @click="editing = false">취소</button>
        <button class="btn btn-primary" :disabled="savingProfile" @click="saveProfile">{{ savingProfile ? '저장 중…' : '저장' }}</button>
      </div>
    </div>

    <div class="orders-head">
      <h2 class="section-title">📦 구매 내역</h2>
      <router-link v-if="orders.length" class="btn btn-outline sm-btn" :to="{ name: 'purchase-insights' }">📊 내 구매 분석</router-link>
    </div>

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
          <span v-if="o.reviewId" class="done muted">✅ 리뷰 작성 완료</span>
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
.profile { display: flex; align-items: center; gap: 16px; padding: 20px; margin-bottom: 16px; }
.avatar { font-size: 40px; background: var(--color-primary-soft); border-radius: 50%; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.avatar-img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.pinfo { flex: 1; }
.uname { font-size: 18px; }
.email { margin: 4px 0 0; font-size: 14px; }
.intro { margin: 6px 0 0; font-size: 14px; color: var(--color-text); }
.phone { margin: 4px 0 0; font-size: 13px; }

.edit-card { padding: 20px; margin-bottom: 28px; }
.edit-title { font-size: 16px; margin: 0 0 16px; }
.edit-grid { display: flex; gap: 20px; align-items: flex-start; }
.img-pick { display: flex; flex-direction: column; gap: 8px; align-items: center; }
.file-btn { cursor: pointer; }
.fields { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.fld { display: flex; flex-direction: column; gap: 5px; font-size: 13px; font-weight: 600; color: var(--color-muted); }
.fld .input { font-weight: 500; color: var(--color-text); }
.edit-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
@media (max-width: 560px) { .edit-grid { flex-direction: column; align-items: stretch; } }

.section-title { font-size: 20px; margin-bottom: 16px; }
.orders-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.orders-head .section-title { margin-bottom: 0; }
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
