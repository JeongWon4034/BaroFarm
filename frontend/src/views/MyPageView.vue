<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { orderApi, reviewApi } from '../api/orders'
import { useAuthStore } from '../stores/auth'
import { won, thumbEmoji, dateOnly, orderStatusMeta } from '../utils/format'
import StarRating from '../components/StarRating.vue'

const router = useRouter()
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
  if (!pform.value.name.trim()) { profileMsg.value = '닉네임을 입력하세요.'; return }
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

// 회원 탈퇴
const withdrawing = ref(false)
const withdrawPassword = ref('')
const withdrawMsg = ref('')
const withdrawLoading = ref(false)

async function submitWithdraw() {
  withdrawMsg.value = ''
  if (!withdrawPassword.value) { withdrawMsg.value = '비밀번호를 입력하세요.'; return }
  withdrawLoading.value = true
  try {
    await auth.deactivate(withdrawPassword.value)
    router.push({ name: 'login' })
  } catch (e) {
    withdrawMsg.value = e.code === 'WRONG_PASSWORD' ? '비밀번호가 올바르지 않습니다.' : e.message
  } finally {
    withdrawLoading.value = false
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
  if (!reviewContent.value.trim()) { reviewMsg.value = '리뷰 내용을 입력해주세요.'; return }
  if (reviewContent.value.trim().length < 5) { reviewMsg.value = '리뷰는 5자 이상 입력해주세요.'; return }
  try {
    const review = await reviewApi.create({ orderId: order.orderId, rating: reviewRating.value, content: reviewContent.value.trim() })
    order.reviewId = review.reviewId // DB 기준 상태로 즉시 반영(리로드해도 유지)
    reviewing.value = null
  } catch (e) {
    reviewMsg.value = e.code === 'DUPLICATE_REVIEW' ? '이미 리뷰를 작성한 주문입니다.' : e.message
  }
}
</script>

<template>
  <div class="mypage">
    <div class="my-grid">
      <!-- 사이드 -->
      <aside class="my-side">
        <div class="profile">
          <div class="ava-wrap" @click="!editing && openProfileEdit()">
            <span v-if="!auth.user?.profileImage" class="ava">{{ auth.user?.role === 'SELLER' ? '🧑‍🌾' : '👤' }}</span>
            <img v-else :src="auth.user.profileImage" class="ava-img" alt="프로필" />
          </div>
          <div class="p-name">{{ auth.user?.name }}</div>
          <div class="grade">{{ auth.user?.role === 'SELLER' ? '🌾 판매 농가' : '🌿 절약러' }}</div>
          <p class="p-email">{{ auth.user?.email }}</p>
          <p v-if="auth.user?.intro" class="p-intro">{{ auth.user.intro }}</p>
          <p v-if="auth.user?.phone" class="p-phone">📞 {{ auth.user.phone }}</p>
          <button v-if="!editing" class="btn btn-outline edit-btn" @click="openProfileEdit">✏️ 프로필 편집</button>
        </div>

        <div class="panel">
          <div class="my-menu">
            <a class="on">🧾 주문 내역</a>
            <router-link :to="{ name: 'wishlist' }">❤️ 찜한 상품</router-link>
            <router-link :to="{ name: 'following' }">👥 팔로잉 농가</router-link>
            <router-link :to="{ name: 'challenges' }">🏆 절약 챌린지</router-link>
            <router-link :to="{ name: 'purchase-insights' }">📊 내 구매 분석</router-link>
            <template v-if="auth.isSeller">
              <span class="menu-sep"></span>
              <router-link :to="{ name: 'seller-dashboard' }">📉 폐기 대시보드</router-link>
              <router-link :to="{ name: 'seller-products' }">📦 내 상품 관리</router-link>
            </template>
          </div>
        </div>
      </aside>

      <!-- 본문 -->
      <div class="my-main">
        <!-- 프로필 편집 -->
        <div v-if="editing" class="edit-card">
          <h3 class="edit-title">✏️ 프로필 편집</h3>
          <div class="edit-row">
            <div class="img-pick">
              <span v-if="!pform.profileImage" class="ava">👤</span>
              <img v-else :src="pform.profileImage" class="ava-img" alt="미리보기" />
              <label class="btn btn-outline file-btn">이미지 변경<input type="file" accept="image/*" @change="onPickImage" hidden /></label>
            </div>
            <div class="fields">
              <label class="fld"><span>닉네임</span><input v-model="pform.name" class="input" placeholder="닉네임" /></label>
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

        <div class="sec-title">
          <h2>📦 구매 내역</h2>
          <router-link v-if="orders.length" :to="{ name: 'purchase-insights' }">📊 내 구매 분석 →</router-link>
        </div>

        <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
        <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>
        <div v-else-if="orders.length === 0" class="empty">
          <span class="emoji">🧾</span>아직 구매 내역이 없어요.
          <br /><router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 보러 가기</router-link>
        </div>

        <ul v-else class="orders">
          <li v-for="o in orders" :key="o.orderId" class="order-card">
            <div class="order-top">
              <div class="date">{{ dateOnly(o.orderDate) }} <small>주문 #{{ o.orderId }}</small></div>
              <span class="status" :class="orderStatusMeta(o.status).cls">{{ orderStatusMeta(o.status).label }}</span>
            </div>
            <div class="order-prod">
              <div class="ci-tile">{{ thumbEmoji({ name: o.productName }) }}</div>
              <div class="op-info">
                <div class="nm">{{ o.productName }}</div>
                <div class="q">수량 {{ o.quantity }}개</div>
              </div>
              <div class="p">{{ won(o.totalPrice) }}</div>
            </div>

            <div class="order-actions">
              <span v-if="o.reviewId" class="done">✅ 리뷰 작성 완료</span>
              <button v-else-if="o.status === 'COMPLETED' && reviewing !== o.orderId" class="btn btn-outline" @click="openReview(o.orderId)">✍️ 리뷰 작성</button>
              <span v-else-if="o.status !== 'COMPLETED'" class="await muted">🚚 배송 완료 후 리뷰를 작성할 수 있어요</span>
            </div>

            <!-- 리뷰 폼 -->
            <div v-if="reviewing === o.orderId" class="review-form">
              <div class="rate-pick">
                <span class="rp-label">별점</span>
                <button v-for="n in 5" :key="n" class="star-btn" :class="{ on: n <= reviewRating }" @click="reviewRating = n">★</button>
                <span class="rp-val">{{ reviewRating }}점</span>
              </div>
              <textarea v-model="reviewContent" class="input" rows="2" placeholder="상품은 어떠셨나요?"></textarea>
              <p v-if="reviewMsg" class="err">{{ reviewMsg }}</p>
              <div class="form-actions">
                <button class="btn btn-outline" @click="reviewing = null">취소</button>
                <button class="btn btn-primary" @click="submitReview(o)">등록</button>
              </div>
            </div>
          </li>
        </ul>

        <!-- 회원 탈퇴 -->
        <div class="withdraw-section">
          <button v-if="!withdrawing" class="withdraw-btn" @click="withdrawing = true">👋 회원 탈퇴</button>
          <div v-else class="withdraw-card">
            <h3 class="withdraw-title">⚠️ 회원 탈퇴</h3>
            <p class="withdraw-desc">탈퇴하면 계정이 비활성화되고 복구할 수 없습니다.<br />비밀번호를 입력해 본인 확인 후 탈퇴하세요.</p>
            <input v-model="withdrawPassword" type="password" class="input" placeholder="현재 비밀번호 입력" />
            <p v-if="withdrawMsg" class="err">{{ withdrawMsg }}</p>
            <div class="withdraw-actions">
              <button class="btn btn-outline" @click="withdrawing = false; withdrawPassword = ''; withdrawMsg = ''">취소</button>
              <button class="btn btn-danger" :disabled="withdrawLoading" @click="submitWithdraw">{{ withdrawLoading ? '처리 중…' : '탈퇴 확인' }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mypage { padding: 4px 0 40px; }
.my-grid { display: grid; grid-template-columns: 260px 1fr; gap: 30px; align-items: start; }

/* 사이드 */
.my-side { position: sticky; top: 130px; display: flex; flex-direction: column; gap: 16px; }
.profile { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 24px 22px; text-align: center; box-shadow: var(--shadow-sm); }
.ava-wrap { cursor: pointer; width: 72px; margin: 0 auto 12px; }
.ava { width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(150deg, var(--leaf-400), var(--leaf-600)); display: flex; align-items: center; justify-content: center; font-size: 32px; box-shadow: var(--shadow-sm); }
.ava-img { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; box-shadow: var(--shadow-sm); }
.p-name { font-size: 18px; font-weight: 800; }
.grade { display: inline-block; margin-top: 7px; font-size: 12px; font-weight: 700; color: var(--leaf-700); background: var(--leaf-50); padding: 3px 11px; border-radius: 999px; }
.p-email { color: var(--muted); font-size: 13px; margin: 10px 0 0; word-break: break-all; }
.p-intro { color: var(--ink-2); font-size: 13.5px; margin: 8px 0 0; }
.p-phone { color: var(--muted); font-size: 12.5px; margin: 4px 0 0; }
.edit-btn { width: 100%; margin-top: 16px; padding: 9px; font-size: 13.5px; }

.panel { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 12px; box-shadow: var(--shadow-sm); }
.my-menu { display: flex; flex-direction: column; gap: 2px; }
.my-menu a { display: flex; align-items: center; gap: 10px; padding: 11px 13px; border-radius: 10px; font-size: 14.5px; font-weight: 600; color: var(--ink-2); transition: .13s; }
.my-menu a.on { background: var(--leaf-100); color: var(--leaf-700); }
.my-menu a:not(.on):hover { background: var(--leaf-50); }
.menu-sep { height: 1px; background: var(--line); margin: 6px 4px; }

/* 본문 */
.edit-card { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 22px; box-shadow: var(--shadow-sm); margin-bottom: 22px; }
.edit-title { font-size: 16px; font-weight: 800; margin: 0 0 18px; }
.edit-row { display: flex; gap: 20px; align-items: flex-start; }
.img-pick { display: flex; flex-direction: column; gap: 8px; align-items: center; }
.img-pick .ava, .img-pick .ava-img { width: 64px; height: 64px; font-size: 28px; }
.file-btn { cursor: pointer; padding: 7px 12px; font-size: 12.5px; }
.fields { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.fld { display: flex; flex-direction: column; gap: 5px; font-size: 13px; font-weight: 600; color: var(--muted); }
.fld .input { font-weight: 500; color: var(--ink); }
.edit-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }

.sec-title { display: flex; align-items: center; justify-content: space-between; margin: 0 0 16px; }
.sec-title h2 { font-size: 20px; font-weight: 800; letter-spacing: -.02em; margin: 0; }
.sec-title a { font-size: 13px; color: var(--muted); }
.sec-title a:hover { color: var(--leaf-700); }

.orders { display: flex; flex-direction: column; gap: 14px; list-style: none; margin: 0; padding: 0; }
.order-card { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 18px; box-shadow: var(--shadow-sm); }
.order-top { display: flex; align-items: center; justify-content: space-between; padding-bottom: 14px; border-bottom: 1px solid var(--line); margin-bottom: 14px; }
.order-top .date { font-weight: 700; font-size: 14.5px; }
.order-top .date small { color: var(--muted); font-weight: 500; margin-left: 8px; font-size: 12.5px; }
.order-top .status { font-size: 12.5px; font-weight: 700; color: var(--leaf-700); background: var(--leaf-50); padding: 4px 11px; border-radius: 999px; }
.order-top .status.st-pending { color: #b76e00; background: #fef3e2; }
.order-top .status.st-confirmed { color: #1a56b8; background: #e7f0ff; }
.order-top .status.st-shipping { color: #5b3cc4; background: #eae6ff; }
.order-top .status.st-completed { color: var(--leaf-700); background: var(--leaf-50); }
.order-actions .await { font-size: 12.5px; }
.order-prod { display: grid; grid-template-columns: 52px 1fr auto; gap: 12px; align-items: center; }
.ci-tile { width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 27px; background: radial-gradient(circle at 50% 36%, var(--leaf-50), var(--leaf-100)); }
.op-info .nm { font-weight: 700; font-size: 15px; }
.op-info .q { font-size: 12.5px; color: var(--muted); margin-top: 2px; }
.order-prod .p { font-weight: 800; }

.order-actions { margin-top: 16px; }
.order-actions .btn { padding: 9px 16px; font-size: 13.5px; }
.done { font-size: 14px; color: var(--muted); }

.review-form { margin-top: 14px; border-top: 1px dashed var(--line-2); padding-top: 14px; }
.rate-pick { display: flex; align-items: center; gap: 6px; margin-bottom: 10px; }
.rp-label, .rp-val { color: var(--muted); font-size: 13.5px; }
.star-btn { border: none; background: transparent; font-size: 22px; color: #d6dade; padding: 0; line-height: 1; }
.star-btn.on { color: var(--star); }
.review-form .input { resize: vertical; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 10px; }
.form-actions .btn { padding: 8px 16px; font-size: 13.5px; }
.err { color: var(--deal); font-size: 13.5px; margin: 8px 0 0; }

.withdraw-section { margin-top: 40px; padding-top: 22px; border-top: 1px solid var(--line); }
.withdraw-btn { color: var(--muted); font-size: 14px; font-weight: 600; padding: 9px 16px; border: 1px solid var(--line); border-radius: var(--r-btn); background: #fff; cursor: pointer; transition: .15s; }
.withdraw-btn:hover { border-color: #e5a0a0; color: #c0392b; }
.withdraw-card { background: #fff; border: 1px solid #f5c6c6; border-radius: 16px; padding: 20px; }
.withdraw-title { font-size: 16px; margin: 0 0 8px; color: #c0392b; }
.withdraw-desc { color: var(--muted); font-size: 13px; margin: 0 0 14px; line-height: 1.6; }
.withdraw-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }

@media (max-width: 900px) {
  .my-grid { grid-template-columns: 1fr; }
  .my-side { position: static; }
}
</style>
