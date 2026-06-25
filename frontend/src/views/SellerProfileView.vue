<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ name: '', intro: '', phone: '', profileImage: '' })
const saving = ref(false)
const msg = ref('')
const ok = ref(false)

onMounted(() => {
  const u = auth.user || {}
  form.value = {
    name: u.name || '',
    intro: u.intro || '',
    phone: u.phone || '',
    profileImage: u.profileImage || '',
  }
})

function onPickImage(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 1024 * 1024) {
    msg.value = '이미지는 1MB 이하만 가능해요.'
    ok.value = false
    e.target.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => { form.value.profileImage = reader.result }
  reader.readAsDataURL(file)
}

function clearImage() {
  form.value.profileImage = ''
}

async function save() {
  msg.value = ''
  ok.value = false
  if (!form.value.name.trim()) {
    msg.value = '농장명(판매자명)을 입력하세요.'
    return
  }
  saving.value = true
  try {
    await auth.updateProfile({
      name: form.value.name.trim(),
      intro: form.value.intro.trim() || null,
      phone: form.value.phone.trim() || null,
      profileImage: form.value.profileImage || null,
    })
    ok.value = true
    msg.value = '내 정보를 저장했어요.'
  } catch (e) {
    ok.value = false
    msg.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="seller-profile">
    <div class="head">
      <h1>🧑‍🌾 내 정보 수정</h1>
      <p class="muted">구매자에게 보이는 농장명·소개·연락처와 대표 이미지를 관리하세요.</p>
    </div>

    <div class="card form-card">
      <!-- 대표 이미지 -->
      <div class="img-row">
        <div class="ava-wrap">
          <span v-if="!form.profileImage" class="ava">🧑‍🌾</span>
          <img v-else :src="form.profileImage" class="ava-img" alt="대표 이미지" />
        </div>
        <div class="img-actions">
          <label class="btn btn-outline file-btn">
            이미지 변경
            <input type="file" accept="image/*" @change="onPickImage" hidden />
          </label>
          <button v-if="form.profileImage" type="button" class="btn btn-ghost" @click="clearImage">제거</button>
          <p class="hint">JPG·PNG, 1MB 이하</p>
        </div>
      </div>

      <!-- 필드 -->
      <label class="fld">
        <span>농장명 / 판매자명 <em>*</em></span>
        <input v-model="form.name" class="input" placeholder="예: 평창 고랭지 농원" maxlength="50" />
      </label>

      <label class="fld">
        <span>한 줄 소개</span>
        <input v-model="form.intro" class="input" placeholder="농장을 한 줄로 소개해주세요" maxlength="200" />
      </label>

      <label class="fld">
        <span>연락처</span>
        <input v-model="form.phone" class="input" placeholder="010-0000-0000" maxlength="20" />
      </label>

      <label class="fld">
        <span>이메일 (로그인 ID)</span>
        <input :value="auth.user?.email" class="input" disabled />
        <small class="ro-note">이메일은 변경할 수 없어요.</small>
      </label>

      <p v-if="msg" class="msg" :class="ok ? 'msg-ok' : 'msg-err'">{{ msg }}</p>

      <div class="actions">
        <button class="btn btn-outline" @click="router.push({ name: 'seller-center' })">판매자 센터로</button>
        <button class="btn btn-primary" :disabled="saving" @click="save">{{ saving ? '저장 중…' : '저장' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.seller-profile { max-width: 620px; padding-bottom: 40px; }
.head { margin-bottom: 18px; }
.head h1 { font-size: 23px; font-weight: 800; letter-spacing: -.02em; margin: 0 0 5px; }
.head .muted { color: var(--muted); font-size: 14px; margin: 0; }

.form-card { padding: 24px; display: flex; flex-direction: column; gap: 18px; }

.img-row { display: flex; align-items: center; gap: 18px; }
.ava-wrap { width: 76px; height: 76px; flex: none; border-radius: 18px; overflow: hidden;
  background: var(--leaf-50); display: flex; align-items: center; justify-content: center; border: 1px solid var(--line); }
.ava { font-size: 34px; }
.ava-img { width: 100%; height: 100%; object-fit: cover; }
.img-actions { display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
.file-btn { cursor: pointer; }
.hint { margin: 0; font-size: 12px; color: var(--muted); }

.fld { display: flex; flex-direction: column; gap: 7px; }
.fld > span { font-size: 13.5px; font-weight: 700; color: var(--ink); }
.fld em { color: var(--deal); font-style: normal; }
.input { width: 100%; padding: 11px 13px; border: 1px solid var(--line); border-radius: 10px;
  font-size: 14px; background: var(--paper); color: var(--ink); }
.input:focus { outline: none; border-color: var(--leaf-400); }
.input:disabled { background: var(--bg-2, #f4f6f4); color: var(--muted); }
.ro-note { font-size: 12px; color: var(--muted); }

.msg { margin: 0; font-size: 13.5px; font-weight: 600; padding: 10px 13px; border-radius: 10px; }
.msg-ok { background: var(--leaf-50); color: var(--leaf-700); }
.msg-err { background: #fdecec; color: #c0392b; }

.actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 4px; }
.btn-ghost { background: transparent; color: var(--muted); border: 1px solid var(--line); }
</style>
