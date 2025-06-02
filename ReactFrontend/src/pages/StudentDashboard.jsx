import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Box, Button, Tooltip, Typography, Paper, Stack } from "@mui/material";
import LogoutIcon from "@mui/icons-material/Logout";
import AssignmentIcon from "@mui/icons-material/Assignment";
import ChatIcon from "@mui/icons-material/Chat";
import PublicIcon from "@mui/icons-material/Public";
import SchoolIcon from "@mui/icons-material/School";

const StudentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (!user) return null;

  return (
    <Box sx={{ padding: 4, backgroundColor: "#f0f4f8", minHeight: "100vh" }}>
      <Paper elevation={4} sx={{ padding: 4, borderRadius: 3 }}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          mb={4}
        >
          <Typography variant="h4" color="primary">
            Student Dashboard
          </Typography>
          <Tooltip title="Logout">
            <Button
              variant="outlined"
              color="error"
              onClick={handleLogout}
              startIcon={<LogoutIcon />}
            >
              Logout
            </Button>
          </Tooltip>
        </Stack>

        <Typography variant="subtitle1" mb={3}>
          Welcome, <strong>{user.username}</strong>
        </Typography>

        <Stack
          spacing={2}
          direction={{ xs: "column", sm: "row" }}
          flexWrap="wrap"
        >
          <Tooltip title="View and manage your assigned tasks">
            <Button
              variant="contained"
              color="primary"
              startIcon={<AssignmentIcon />}
              onClick={() => navigate("/student/tasks")}
            >
              View Tasks
            </Button>
          </Tooltip>

          <Tooltip title="Chat with your admin and view messages">
            <Button
              variant="contained"
              color="secondary"
              startIcon={<ChatIcon />}
              onClick={() => navigate("/student/chat")}
            >
              Chat with Admin
            </Button>
          </Tooltip>

          <Tooltip title="View your public portfolio">
            <Button
              variant="contained"
              color="success"
              startIcon={<PublicIcon />}
              onClick={() => navigate("/student/portfolio")}
            >
              View Portfolio
            </Button>
          </Tooltip>

          {user.status === "completed" && (
            <Tooltip title="Your certificate is available to download">
              <Button
                variant="contained"
                color="info"
                startIcon={<SchoolIcon />}
                onClick={() => navigate("/certificate")}
              >
                View Certificate
              </Button>
            </Tooltip>
          )}
        </Stack>
      </Paper>
    </Box>
  );
};

export default StudentDashboard;
