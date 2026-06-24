import http from './http'

// 행동 로그 emit — 퍼널/AB/체류시간 분석의 원천 데이터를 백엔드(/events)로 보낸다.
// 원칙: fire-and-forget. 수집 실패가 사용자 흐름을 절대 막지 않는다(에러 삼킴).

// 세션 ID — 1회 방문 기준 키. 탭 단위(sessionStorage)로 1회 생성해 재사용.
function getSessionId() {
  let sid = sessionStorage.getItem('fg_session_id')
  if (!sid) {
    sid = 'sess_' + Math.random().toString(36).slice(2, 11) + Date.now().toString(36)
    sessionStorage.setItem('fg_session_id', sid)
  }
  return sid
}

function deviceType() {
  return window.innerWidth <= 768 ? 'MOBILE_WEB' : 'PC_WEB'
}

/**
 * 행동 이벤트 1건 전송.
 * @param {string} eventType  view_home | click_product | view_detail | click_checkout | complete_order
 * @param {object} [extra]    { productId, abTestGroup, stayDuration }
 */
export function track(eventType, extra = {}) {
  const payload = {
    sessionId: getSessionId(),
    eventType,
    deviceType: deviceType(),
    productId: extra.productId ?? null,
    abTestGroup: extra.abTestGroup ?? null,
    stayDuration: extra.stayDuration ?? null,
  }
  // 비동기 fire-and-forget — 응답을 기다리지 않고, 실패해도 조용히 무시
  http.post('/events', payload).catch(() => {})
}
