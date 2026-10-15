// 분류별 배지 색 (없으면 기본색)
const BADGE_COLORS = {
  곤충: 'badge-green',
  식물: 'badge-leaf',
  포유류: 'badge-orange',
  새: 'badge-sky',
  '작은 동물': 'badge-purple',
  양서류: 'badge-teal',
  물고기: 'badge-blue',
  파충류: 'badge-brown',
}

export default function CreatureCard({ creature }) {
  const { name, category, description, food, source_org, source_url } = creature
  // 먹이가 "X"이면 식물
  const isPlant = food.trim().toUpperCase() === 'X'

  return (
    <article className="card">
      <div className="card-head">
        <h2 className="card-name">{name}</h2>
        <span className={`badge ${BADGE_COLORS[category] || 'badge-default'}`}>{category}</span>
      </div>

      <p className="card-desc">{description}</p>

      <p className="card-food">
        <span aria-hidden="true">🍽️</span> <strong>먹이:</strong>{' '}
        {isPlant ? '식물은 스스로 양분을 만들어요' : food}
      </p>

      {source_org && (
        <p className="card-source">
          출처:{' '}
          {source_url ? (
            <a href={source_url} target="_blank" rel="noopener noreferrer">
              {source_org}
            </a>
          ) : (
            source_org
          )}
        </p>
      )}
    </article>
  )
}
