import { useEffect, useRef, useState } from 'react'
import { fetchAllCreatures, searchCreatures } from './api'
import CreatureButtons from './CreatureButtons'
import CreatureCard from './CreatureCard'

export default function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null) // null: 아직 검색 안 함
  const [searched, setSearched] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)
  const lastRequest = useRef(0)
  const resultsRef = useRef(null)

  // 검색창 아래 생물 버튼 목록 (API에서 받은 보이는 생물 전부)
  const [creatures, setCreatures] = useState([])
  const [listStatus, setListStatus] = useState('loading') // loading | ready | error
  const [selectedId, setSelectedId] = useState(null)

  const scrollToResults = useRef(false)

  function loadCreatures() {
    fetchAllCreatures().then(
      (data) => {
        setCreatures(data)
        setListStatus('ready')
      },
      () => setListStatus('error'),
    )
  }

  function retryLoad() {
    setListStatus('loading')
    loadCreatures()
  }

  useEffect(() => {
    loadCreatures()
  }, [])

  // 버튼으로 고른 카드가 화면에 보이도록 (카드가 그려진 뒤에 이동)
  useEffect(() => {
    if (!scrollToResults.current) return
    scrollToResults.current = false
    resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [results])

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
      // 이름이 정확히 맞으면 그 버튼을 선택 표시
      setSelectedId(data.find((c) => c.name === q.replace(/\s+/g, ''))?.id ?? null)
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

  // 버튼을 누르면 이미 받은 목록에서 바로 그 생물 카드를 보여 줌
  function handleSelect(creature) {
    lastRequest.current++ // 진행 중인 검색 결과는 무시
    setLoading(false)
    setError(false)
    setQuery(creature.name)
    setSearched(creature.name)
    setResults([creature])
    setSelectedId(creature.id)
    scrollToResults.current = true
  }

  return (
    <main className="page">
      <header className="hero">
        <h1 className="title">
          <span aria-hidden="true">🔍</span> 먹이 관계 알아보기
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

      <section className="results" aria-live="polite" ref={resultsRef}>
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

      <CreatureButtons
        creatures={creatures}
        status={listStatus}
        selectedId={selectedId}
        onSelect={handleSelect}
        onRetry={retryLoad}
      />
    </main>
  )
}
