export default function LoadingSpinner({ size = 40, text = '' }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: '16px', padding: '2rem'
    }}>
      <div style={{
        width: size, height: size,
        border: `3px solid rgba(229,9,20,0.2)`,
        borderTopColor: 'var(--accent-primary)',
        borderRadius: '50%',
        animation: 'spinAnim 0.8s linear infinite'
      }} />
      {text && <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{text}</p>}
    </div>
  )
}
