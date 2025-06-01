import React, { useState } from "react";
import { Button, Typography, Box } from "@mui/material";
import API from "../api/api";

const BulkUpload = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus("");
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      await API.post("/students/bulk-upload/", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      setStatus("Students uploaded successfully.");
    } catch (error) {
      console.error(error);
      setStatus("Upload failed.");
    }
  };

  return (
    <Box>
      <Typography variant="h6">Bulk Upload Students</Typography>
      <input type="file" onChange={handleFileChange} />
      <Button variant="contained" color="primary" onClick={handleUpload}>
        Upload
      </Button>
      <Typography color="secondary">{status}</Typography>
    </Box>
  );
};

export default BulkUpload;
