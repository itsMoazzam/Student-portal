import React from "react";
import { useNavigate } from "react-router-dom";
import { Button, AppBar, Toolbar, Typography, Box } from "@mui/material";
import { LogOut } from "lucide-react";
import AdminDashboardContent from "../components/AdminDashboardcontent";

const AdminDashboard = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="admin-dashboard">
      {/* Header */}
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Admin Dashboard
          </Typography>
          <Button color="inherit" startIcon={<LogOut />} onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      {/* Dashboard Content */}
      <Box padding={4}>
        <AdminDashboardContent />
      </Box>
    </div>
  );
};

export default AdminDashboard;
