import React, { useState } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";
import API from "../../api/api";

const AddCategory = () => {
  const [name, setName] = useState("");

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("token");
      await API.post(
        "/categories/",
        { name },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      alert("Category added");
      setName("");
    } catch (error) {
      alert("Error adding category");
      console.error(error);
    }
  };

  return (
    <Box sx={{ maxWidth: 400, mx: "auto", mt: 5 }}>
      <Typography variant="h5" gutterBottom>
        Add New Category
      </Typography>
      <TextField
        label="Category Name"
        fullWidth
        margin="normal"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <Button variant="contained" onClick={handleSubmit}>
        Add Category
      </Button>
    </Box>
  );
};

export default AddCategory;
