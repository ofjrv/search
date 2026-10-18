// 분류 순서 (목록에 없는 분류는 맨 뒤에 가나다순)
const CATEGORY_ORDER = ['곤충', '새', '포유류', '양서류', '파충류', '물고기', '작은 동물', '식물']

function categoryRank(category) {
  const i = CATEGORY_ORDER.indexOf(category)
  return i === -1 ? CATEGORY_ORDER.length : i
}

// 생물 목록을 분류별로 묶고, 분류 안에서는 가나다순
function groupByCategory(creatures) {
  const groups = new Map()
  for (const c of creatures) {
    const key = c.category || '기타'
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(c)
  }
  return [...groups.entries()]
    .sort(([a], [b]) => categoryRank(a) - categoryRank(b) || a.localeCompare(b, 'ko'))
    .map(([category, items]) => [category, items.sort((a, b) => a.name.localeCompare(b.name, 'ko'))])
}

export default function CreatureButtons({ creatures, status, selectedId, onSelect, onRetry }) {
  if (status === 'loading') {
    return <p className="message chips-message">생물 목록을 불러오는 중이에요…</p>
  }

  if (status === 'error') {
    return (
      <div className="message message-warn chips-message">
        <p className="chips-error-text">잠시 후 다시 시도해 주세요</p>
        <button type="button" className="retry-button" onClick={onRetry}>
          다시 시도
        </button>
      </div>
    )
  }

  return (
    <nav className="chips" aria-label="생물 목록">
      {groupByCategory(creatures).map(([category, items]) => (
        <section key={category} className="chip-group">
          <h2 className="chip-group-title">{category}</h2>
          <div className="chip-list">
            {items.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`chip${c.id === selectedId ? ' chip-selected' : ''}`}
                aria-pressed={c.id === selectedId}
                onClick={() => onSelect(c)}
              >
                {c.name}
              </button>
            ))}
          </div>
        </section>
      ))}
    </nav>
  )
}
