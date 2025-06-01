import React, { useState } from "react";
import { TextField, Button, Box } from "@mui/material";
import API from "../api/api";

const UploadCertificate = () => {
  const [studentId, setStudentId] = useState("");
  const [certificate, setCertificate] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("certificate", certificate);

    try {
      const token = localStorage.getItem("token");
      await API.post(`/students/${studentId}/upload-certificate/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      alert("Certificate uploaded successfully.");
    } catch (error) {
      console.error(error);
      alert("Failed to upload certificate.");
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
      <input type="file" onChange={(e) => setCertificate(e.target.files[0])} />
      <Button variant="contained" onClick={handleUpload}>
        Upload Certificate
      </Button>
    </Box>
  );
};

export default UploadCertificate;
