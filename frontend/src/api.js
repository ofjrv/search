import axios from 'axios'

// 백엔드 주소 (끝의 / 는 제거)
const baseURL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

const api = axios.create({ baseURL, timeout: 10000 })

// 이름·별칭으로 생물 검색
export async function searchCreatures(q) {
  const { data } = await api.get('/api/creatures/', { params: { q } })
  return data
}
