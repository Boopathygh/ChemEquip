import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const Login = ({ onLogin }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState(''); // Only for signup
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        // Basic Auth implementation
        const auth = btoa(`${username}:${password}`);
        try {
            await axios.get(`${API_BASE_URL}/history/`, {
                headers: { 'Authorization': `Basic ${auth}` }
            });
            onLogin(username, password);
        } catch (err) {
            setError("Invalid credentials");
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await axios.post(`${API_BASE_URL}/register/`, {
                username, password, email
            });
            setSuccess("Account created! Please login.");
            setIsLogin(true); // Switch to login view
            setUsername('');
            setPassword('');
            setEmail('');
        } catch (err) {
            setError(err.response?.data?.error || "Registration failed");
        }
    };

    return (
        <div className="auth-container">
            <div className="card" style={{ maxWidth: '450px', width: '90%' }}>
                <h2 style={{ color: 'var(--primary-blue)', textAlign: 'center', marginBottom: '20px' }}>
                    {isLogin ? "ChemEquip Login" : "Create New Account"}
                </h2>

                {error && <div style={{ background: '#ffdddd', color: 'red', padding: '10px', borderRadius: '4px', marginBottom: '15px', textAlign: 'center' }}>{error}</div>}
                {success && <div style={{ background: '#ddffdd', color: 'green', padding: '10px', borderRadius: '4px', marginBottom: '15px', textAlign: 'center' }}>{success}</div>}

                <form onSubmit={isLogin ? handleLogin : handleRegister}>
                    <div>
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="Enter username"
                        />
                    </div>

                    {!isLogin && (
                        <div>
                            <label>Email (Optional)</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="Enter email"
                            />
                        </div>
                    )}

                    <div>
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Enter password"
                        />
                    </div>

                    <button type="submit" className="btn" style={{ width: '100%', marginTop: '10px', fontWeight: 'bold' }}>
                        {isLogin ? "Login" : "Sign Up"}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
                    {isLogin ? "Don't have an account?" : "Already have an account?"} <span
                        onClick={() => { setIsLogin(!isLogin); setError(''); setSuccess(''); }}
                        style={{ color: 'var(--primary-blue)', fontWeight: 'bold', cursor: 'pointer', textDecoration: 'underline' }}
                    >
                        {isLogin ? "Create one" : "Login"}
                    </span>
                </p>
            </div>
        </div>
    );
};

export default Login;
