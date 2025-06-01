import React, { useState } from "react";
import { TextField, Button, Box } from "@mui/material";
import API from "../api/api";

const GeneratePDFReport = () => {
  const [studentId, setStudentId] = useState("");

  const handleGenerate = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await API.get(
        `/students/${studentId}/generate-report/`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: "blob" // Important for file download
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${studentId}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch {
      alert("Failed to generate report.");
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
      <Button variant="contained" onClick={handleGenerate}>
        Generate PDF Report
      </Button>
    </Box>
  );
};

export default GeneratePDFReport;
