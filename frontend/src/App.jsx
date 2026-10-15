import { useRef, useState } from 'react'
import { searchCreatures } from './api'
import CreatureCard from './CreatureCard'

// 검색창 아래 빠른 검색 버튼
const QUICK_NAMES = ['메뚜기', '개구리', '뱀', '매', '참새']

export default function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null) // null: 아직 검색 안 함
  const [searched, setSearched] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)
  const lastRequest = useRef(0)

  async function runSearch(text) {
    const q = text.trim()
    if (!q) return
    const id = ++lastRequest.current
    setLoading(true)
    setError(false)
    try {
      const data = await searchCreatures(q)
      // 빠르게 여러 번 누르면 마지막 검색 결과만 반영
      if (id !== lastRequest.current) return
      setResults(data)
      setSearched(q)
    } catch {
      if (id !== lastRequest.current) return
      setError(true)
      setResults(null)
    } finally {
      if (id === lastRequest.current) setLoading(false)
    }
  }

  function handleSubmit(e) {
    e.preventDefault() // 엔터 키도 여기로 옴
    runSearch(query)
  }

  function handleQuick(name) {
    setQuery(name)
    runSearch(name)
  }

  return (
    <main className="page">
      <header className="hero">
        <h1 className="title">
          <span aria-hidden="true">🔍</span> 먹이를 찾아라
        </h1>
        <p className="subtitle">궁금한 생물 이름을 써 보세요!</p>
      </header>

      <form className="search" onSubmit={handleSubmit} role="search">
        <input
          className="search-input"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="예: 메뚜기"
          aria-label="생물 이름"
          enterKeyHint="search"
          autoComplete="off"
        />
        <button className="search-button" type="submit" disabled={loading}>
          찾기
        </button>
      </form>

      <div className="quick" aria-label="빠른 검색">
        {QUICK_NAMES.map((name) => (
          <button key={name} type="button" className="quick-button" onClick={() => handleQuick(name)}>
            {name}
          </button>
        ))}
      </div>

      <section className="results" aria-live="polite">
        {loading && <p className="message">찾고 있어요…</p>}

        {!loading && error && (
          <p className="message message-warn">
            지금은 찾을 수 없어요. 선생님께 알려 주세요!
          </p>
        )}

        {!loading && !error && results && results.length === 0 && (
          <p className="message message-warn">
            <strong>‘{searched}’</strong>
            <br />
            아직 없는 생물이에요. 선생님께 알려 주세요!
          </p>
        )}

        {!loading &&
          !error &&
          results?.map((c) => <CreatureCard key={c.id} creature={c} />)}
      </section>
    </main>
  )
}
