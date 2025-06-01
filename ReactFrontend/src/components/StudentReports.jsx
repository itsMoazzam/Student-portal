import React, { useState } from "react";
import axios from "axios";

const StudentReports = () => {
  const [studentId, setStudentId] = useState("");

  const handleGenerateReport = async () => {
    try {
      const response = await axios.get(`/api/generate-report/${studentId}/`, {
        responseType: "blob"
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${studentId}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error(error);
      alert("Error generating report");
    }
  };

  return (
    <div className="container">
      <h2>Generate Student Report</h2>
      <input
        type="text"
        placeholder="Student ID"
        onChange={(e) => setStudentId(e.target.value)}
      />
      <button onClick={handleGenerateReport}>Generate Report</button>
    </div>
  );
};

export default StudentReports;
