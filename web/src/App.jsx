import React, { useState } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [auth, setAuth] = useState(null); // stores bas64 encoded auth string

  const handleLogin = (username, password) => {
    setAuth(btoa(`${username}:${password}`));
  };

  return (
    <div className="App">
      {!auth ? <Login onLogin={handleLogin} /> : <Dashboard auth={auth} />}
    </div>
  );
}

export default App;
