import './navbar.css'
const Nav = () => {
  return (
    <div className="navbar">
      <a href="/#home" className="navbar-button">
        Home
      </a>
      <a href="/#about" className="navbar-button">
        About
      </a>
      <a href="/#solution" className="navbar-button">
        Solution
      </a>
      <a href="/#features" className="navbar-button">
        Features
      </a>
      <div className="navbar-dropdown">
        <button className="navbar-dropdown-button">Demos</button>
        <div className="navbar-dropdown-content">
          <a href="/demo">Segmentation Demo</a>
          <a href="/voice_demo">Voice Demo</a>
          <a href="/image_demo">Visual Demo</a>
        </div>
      </div>
    </div>
  )
}

export default Nav
