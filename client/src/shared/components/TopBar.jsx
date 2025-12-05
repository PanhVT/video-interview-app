import { useEffect, useState } from 'react'
import sunIcon from '../../assets/sun.png'
import moonIcon from '../../assets/moon.png'
import logoImg from '../../assets/cat_logo.png'

export default function TopBar({ className = '' }) {
  const [theme, setTheme] = useState(() => (
    typeof window !== 'undefined' ? (localStorage.getItem('theme') || 'light') : 'light'
  ))

  useEffect(() => {
    document.body.classList.toggle('theme-dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  return (
    <div className={`topbar ${className}`.trim()}>
      <div className="logo">
        <img src={logoImg} alt="SnapQ logo" className="logo-img" />
        SnapCat
      </div>
      <div className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
        <img src={theme === 'dark' ? sunIcon : moonIcon} alt="theme toggle" />
      </div>
    </div>
  )
}

