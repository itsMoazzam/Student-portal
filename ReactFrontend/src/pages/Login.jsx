import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/api";
import { jwtDecode } from "jwt-decode";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import { RiLockPasswordFill } from "react-icons/ri";
import { FaUser } from "react-icons/fa";
import "../components/css/login.css"; // Ensure you have the correct path to your CSS file

const LoginPage = () => {
  const navigate = useNavigate();
  useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      setError("Please enter both username and password");
      return;
    }

    try {
      const response = await API.post("/token/", {
        username,
        password
      });
      console.log(response.data.access);
      const token = response.data.access;

      // Save token to localStorage and set Authorization header
      localStorage.setItem("token", token);
      API.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      // Decode the token to get user role
      const decoded = jwtDecode(token);
      const role = decoded.is_staff ? "admin" : "student";

      // Optional: log info
      console.log("Decoded JWT:", decoded);
      console.log("User role:", role);

      // Navigate based on role
      navigate(`/${role}`);
    } catch (error) {
      console.error("Login failed", error);
      setError("Invalid credentials");
    }
  };

  return (
    <main>
      <div className="glass-container">
        <div className="glass-form">
          <h1 className="glass-heading">Welcome Back</h1>
          <div className="input-group">
            <FaUser className="input-icon" />
            <input
              type="text"
              autoComplete="off"
              spellCheck="false"
              autoCorrect="off"
              autoCapitalize="off"
              placeholder="Username or Email"
              className="glass-input with-icon "
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div className="input-group">
            <RiLockPasswordFill className="input-icon" />
            <input
              type={showPassword ? "text" : "password"}
              autoComplete="off"
              spellCheck="false"
              autoCorrect="off"
              autoCapitalize="off"
              placeholder="Password"
              className="glass-input with-icon "
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
          <button className="glass-btn" onClick={handleLogin}>
            Login
          </button>
          <div className="glass-error-container">
            <pre
              className="glass-error"
              style={{ visibility: error ? "visible" : "hidden" }}
            >
              {error || " "}
            </pre>
          </div>
        </div>
      </div>
    </main>
  );
};

export default LoginPage;
