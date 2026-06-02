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
]
const CATEGORY_EMOJI = {
  vegetable: '🥬', fruit: '🍓', grain: '🌾', root: '🥔', mushroom: '🍄',
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
}
export function categoryLabel(code) {
  return CATEGORY_LABEL[code] || code || '기타'
}

export function dateOnly(value) {
  if (!value) return '-'
  return String(value).slice(0, 10)
}
