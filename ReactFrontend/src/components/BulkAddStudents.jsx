import React, { useState } from "react";
import axios from "axios";
import { Button, Tooltip, Typography } from "@mui/material";

const BulkAddStudents = () => {
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || file.type !== "text/csv") {
      alert("Please upload a valid CSV file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("/api/bulk-upload-students/", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      alert("Students added successfully");
    } catch (error) {
      alert("Failed to add students");
      console.error(error);
    }
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "40px auto",
        padding: "20px",
        border: "1px solid #ccc",
        borderRadius: "10px"
      }}
    >
      <Typography variant="h5" gutterBottom>
        Bulk Add Students
      </Typography>

      <form onSubmit={handleSubmit}>
        <Tooltip title="Upload a CSV file with username and email columns">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ marginBottom: "20px" }}
          />
        </Tooltip>
        <br />
        <Button type="submit" variant="contained" color="primary">
          Upload CSV
        </Button>
      </form>
    </div>
  );
};

export default BulkAddStudents;
