'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '@/utils/auth';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import './styles.css';

const LoginPage = () => {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    try {
      await login(username, password); // call login()
      // Redirect based on role
      const isAdmin = localStorage.getItem('isStaff') === 'true';
      const isSuperUser = localStorage.getItem('isSuperUser') === 'true';



      if (isAdmin || isSuperUser) {
        router.push('/admin');
      } else {
        router.push('/student');
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Login failed. Please try again.');
      }

      setTimeout(() => setError(''), 3000);
    }
  };

  return (
    <div className="glass-container">
      <div className="glass-form">
        <h1 className="glass-heading">Welcome Back</h1>

        <div className="input-group">
          <input
            type="text"
            placeholder="Username or Email"
            className="glass-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div className="input-group">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
            className="glass-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            className="password-toggle"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <label className="remember-me">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            Remember me
          </label>

          <button
            className="glass-link"
            style={{ background: 'none', border: 'none', padding: 0 }}
            onClick={() => router.push('/forgot-password')}
          >
            Forgot password?
          </button>
        </div>

        <button className="glass-btn" onClick={handleLogin}>
          Login
        </button>

        {error && <pre className="glass-error">{error}</pre>}
      </div>
    </div>
  );
};

export default LoginPage;
