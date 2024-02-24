import './navbar.css';
const Nav = () => {
  return (
    <div className="navbar">
      <a href="#home" className="navbar-button">
        Home
      </a>
      <a href="#about" className="navbar-button">
        About
        </a>
      <a href="#solution" className="navbar-button">
        Solution
        </a>
      <a href="#features" className="navbar-button">
        Features
      </a>
      <a href="#contact" className="navbar-button">
        Contact
        </a>
    </div>
  );
};

export default Nav;
