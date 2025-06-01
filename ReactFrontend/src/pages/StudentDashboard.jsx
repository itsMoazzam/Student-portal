import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
// import "";

const StudentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="student-dashboard">
      <div className="header">
        <h2>Student Dashboard</h2>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>
      <div className="student-info">
        <p>
          <strong>Name:</strong> {user.name}
        </p>
        <p>
          <strong>Email:</strong> {user.email}
        </p>
        <p>
          <strong>Status:</strong> {user.status}
        </p>
      </div>
      {user.status === "completed" && (
        <div className="certificate-link">
          <button onClick={() => navigate("/certificate")}>
            View Certificate
          </button>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
