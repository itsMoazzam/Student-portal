import React, { useState, useEffect } from "react";
import { TextField, Button, MenuItem, Box, Typography } from "@mui/material";
import API from "../../api/api"; // Adjust the import path as necessary

const CategorizeStudent = () => {
  const [studentId, setStudentId] = useState("");
  const [categories, setCategories] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState("");

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await API.get("/categories/", {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCategories(response.data);
      } catch (error) {
        console.error("Error loading categories", error);
      }
    };

    fetchCategories();
  }, []);

  const handleCategorize = async () => {
    try {
      const token = localStorage.getItem("token");
      await API.patch(
        `/students/${studentId}/categorize/`,
        { category_id: selectedCategoryId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("Student categorized.");
      setStudentId("");
      setSelectedCategoryId("");
    } catch (error) {
      alert("Failed to categorize student.");
      console.error(error);
    }
  };

  return (
    <Box sx={{ maxWidth: 500, mx: "auto", mt: 5 }}>
      <Typography variant="h5" gutterBottom>
        Categorize Student
      </Typography>
      <TextField
        label="Student ID"
        fullWidth
        margin="normal"
        value={studentId}
        onChange={(e) => setStudentId(e.target.value)}
      />
      <TextField
        select
        label="Select Category"
        fullWidth
        margin="normal"
        value={selectedCategoryId}
        onChange={(e) => setSelectedCategoryId(e.target.value)}
      >
        {categories.map((cat) => (
          <MenuItem key={cat.id} value={cat.id}>
            {cat.name}
          </MenuItem>
        ))}
      </TextField>
      <Button variant="contained" onClick={handleCategorize}>
        Assign Category
      </Button>
    </Box>
  );
};

export default CategorizeStudent;
