import React, { useState } from "react";
import { TextField, Button, Box } from "@mui/material";
import API from "../api/api";

const MarkDegreeCompleted = () => {
  const [studentId, setStudentId] = useState("");

  const handleMarkCompleted = async () => {
    try {
      const token = localStorage.getItem("token");
      await API.post(
        `/students/${studentId}/mark-completed/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("Degree marked as completed.");
    } catch (err) {
      console.error(err);
      alert("Failed to mark degree completed.");
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
      <Button variant="contained" onClick={handleMarkCompleted}>
        Mark as Completed
      </Button>
    </Box>
  );
};

export default MarkDegreeCompleted;
