// 가격 포맷: 5800 → "₩5,800"
export function won(value) {
  if (value == null) return '-'
  return '₩' + Number(value).toLocaleString('ko-KR')
}

// 카테고리/상품명 기반 이모지 썸네일 (시드 thumbnailUrl이 더미라 설계처럼 이모지로 대체)
const NAME_EMOJI = [
  ['상추', '🥬'], ['배추', '🥬'], ['토마토', '🍅'], ['파프리카', '🫑'], ['피망', '🫑'],
  ['고추', '🌶️'], ['양파', '🧅'], ['마늘', '🧄'], ['당근', '🥕'], ['감자', '🥔'],
  ['고구마', '🍠'], ['옥수수', '🌽'], ['오이', '🥒'], ['브로콜리', '🥦'], ['버섯', '🍄'],
  ['딸기', '🍓'], ['사과', '🍎'], ['포도', '🍇'], ['수박', '🍉'], ['귤', '🍊'],
  ['바나나', '🍌'], ['복숭아', '🍑'], ['배', '🍐'], ['콩', '🫘'], ['쌀', '🌾'],
  ['오징어', '🦑'], ['새우', '🦐'], ['생선', '🐟'], ['한우', '🥩'], ['불고기', '🥩'], ['고기', '🥩'],
]
const CATEGORY_EMOJI = {
  vegetable: '🥬', fruit: '🍓', grain: '🌾', root: '🥔', mushroom: '🍄',
  seafood: '🐟', meat: '🥩',
}

export function thumbEmoji(product) {
  const name = product?.name || ''
  for (const [kw, emoji] of NAME_EMOJI) {
    if (name.includes(kw)) return emoji
  }
  return CATEGORY_EMOJI[product?.category] || '🥗'
}

// 카테고리 코드 → 한글 라벨
const CATEGORY_LABEL = {
  vegetable: '채소', fruit: '과일', grain: '곡물', root: '구근', mushroom: '버섯',
  seafood: '해산물', meat: '육류',
}
export function categoryLabel(code) {
  return CATEGORY_LABEL[code] || code || '기타'
}

export function dateOnly(value) {
  if (!value) return '-'
  return String(value).slice(0, 10)
}

// 유통기한 D-day 라벨: 0 → "오늘 마감", 1 → "D-1" …
export function dDayLabel(days) {
  if (days == null) return ''
  if (days < 0) return '마감'
  if (days === 0) return '오늘 마감'
  return 'D-' + days
}

// API 에러를 사용자에게 보여줄 일관된 한국어 메시지로 변환.
// 권한·인증·존재 실패는 백엔드 raw 문구 대신 코드 기준 통일 문구를 쓴다.
const ERROR_MESSAGE = {
  FORBIDDEN: '본인이 작성한 글·댓글만 수정하거나 삭제할 수 있어요.',
  UNAUTHORIZED: '로그인이 필요해요. 다시 로그인해 주세요.',
  TOKEN_INVALIDATED: '로그인이 만료됐어요. 다시 로그인해 주세요.',
  ACCOUNT_INACTIVE: '탈퇴하거나 비활성화된 계정이에요.',
  POST_NOT_FOUND: '이미 삭제되었거나 존재하지 않는 글이에요.',
  COMMENT_NOT_FOUND: '이미 삭제된 댓글이에요.',
  PARENT_COMMENT_NOT_FOUND: '답글을 달 댓글을 찾을 수 없어요. 이미 삭제되었을 수 있어요.',
  PARENT_POST_MISMATCH: '다른 게시글의 댓글에는 답글을 달 수 없어요.',
  DATA_INTEGRITY_VIOLATION: '관련 게시글이나 댓글이 변경·삭제되어 처리할 수 없어요. 새로고침 후 다시 시도해 주세요.',
}
export function apiMessage(e, fallback = '요청을 처리하지 못했어요.') {
  return ERROR_MESSAGE[e?.code] || e?.message || fallback
}

// 챌린지 참여 상태를 표시용으로 파생한다.
// 백엔드 status는 ONGOING/COMPLETED뿐이라, '기간 만료'는 joinedAt+periodDays를 현재시각과 비교해 프론트에서 계산.
//   COMPLETED                          → 달성
//   ONGOING & 기간 지남 & 미달성        → 만료(EXPIRED)
//   ONGOING & 기간 내                   → 진행 중(+ 남은 D-day)
const MS_PER_DAY = 86400000
export function challengeStatus(challenge, my) {
  if (!my) return { key: 'NONE' }
  if (my.status === 'COMPLETED') {
    return { key: 'COMPLETED', label: '달성 완료', emoji: '🏅', cls: 'st-done' }
  }
  const joined = new Date(my.joinedAt)
  const deadline = new Date(joined.getTime() + (challenge.periodDays || 0) * MS_PER_DAY)
  const daysLeft = Math.ceil((deadline.getTime() - Date.now()) / MS_PER_DAY)
  if (daysLeft < 0) {
    return { key: 'EXPIRED', label: '기간 만료', emoji: '⏰', cls: 'st-expired' }
  }
  return {
    key: 'ONGOING', label: '진행 중', emoji: '🟢', cls: 'st-ongoing',
    daysLeft, dday: daysLeft === 0 ? '오늘 마감' : `D-${daysLeft}`,
  }
}

// 폐기위험 등급 → 표시 메타 (라벨/뱃지 클래스)
const RISK_META = {
  HIGH: { label: '폐기 임박', cls: 'risk-high' },
  MEDIUM: { label: '서두르세요', cls: 'risk-medium' },
  LOW: { label: '여유', cls: 'risk-low' },
  EXPIRED: { label: '판매종료', cls: 'risk-expired' },
}
export function riskMeta(level) {
  return RISK_META[level] || RISK_META.LOW
}
