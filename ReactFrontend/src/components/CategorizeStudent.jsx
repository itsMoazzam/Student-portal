import React, { useState } from "react";
import { TextField, Button, Box } from "@mui/material";
import API from "../api/api";

const CategorizeStudent = () => {
  const [studentId, setStudentId] = useState("");
  const [category, setCategory] = useState("");

  const handleCategorize = async () => {
    try {
      const token = localStorage.getItem("token");
      await API.post(
        `/students/${studentId}/categorize/`,
        { category },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("Student categorized successfully.");
    } catch (err) {
      console.error(err);
      alert("Failed to categorize student.");
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
        label="Category"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button variant="contained" onClick={handleCategorize}>
        Categorize
      </Button>
    </Box>
  );
};

export default CategorizeStudent;
