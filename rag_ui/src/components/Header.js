import React, { useState } from 'react';

const Header = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogin = () => {
    // TODO: Implement actual login logic
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    // TODO: Implement actual logout logic
    setIsLoggedIn(false);
    setShowDropdown(false);
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="app-title">
          <h1>Financial Analyst</h1>
        </div>
        <div className="user-section">
          {!isLoggedIn ? (
            <button className="user-icon-button" onClick={handleLogin}>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="currentColor" 
                className="user-icon"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
              </svg>
            </button>
          ) : (
            <div className="user-profile">
              <div 
                className="user-avatar" 
                onClick={() => setShowDropdown(!showDropdown)}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 24 24" 
                  fill="currentColor" 
                  className="user-icon"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>
              </div>
              {showDropdown && (
                <div className="dropdown-menu">
                  <div className="dropdown-item user-info">
                    <span>user@example.com</span>
                  </div>
                  <div className="dropdown-divider"></div>
                  <div 
                    className="dropdown-item"
                    onClick={handleLogout}
                  >
                    Logout
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 