import React, { useState } from "react";
import { TextField, Button, Box } from "@mui/material";
import API from "../api/api";

const AssignTask = () => {
  const [studentId, setStudentId] = useState("");
  const [task, setTask] = useState("");

  const handleAssign = async () => {
    try {
      const token = localStorage.getItem("token");
      await API.post(
        `/students/${studentId}/assign-task/`,
        { task },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("Task assigned successfully.");
    } catch {
      alert("Failed to assign task.");
    }
  };

  return (
    <Box>
      <TextField
        label="Student ID"
        value={studentId}
        onChange={(e) => setStudentId(e.target.value)}
        fullWidth
        margin="normal"
      />
      <TextField
        label="Task Description"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button variant="contained" onClick={handleAssign}>
        Assign Task
      </Button>
    </Box>
  );
};

export default AssignTask;
