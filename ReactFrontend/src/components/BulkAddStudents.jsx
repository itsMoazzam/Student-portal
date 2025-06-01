import React, { useState } from "react";
import axios from "axios";

const BulkAddStudents = () => {
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("/api/bulk-upload-students/", formData);
      alert("Students added successfully");
    } catch (error) {
      alert("Failed to add students");
      console.error(error);
    }
  };

  return (
    <div className="container">
      <h2>Bulk Add Students</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit">Upload CSV</button>
      </form>
    </div>
  );
};

export default BulkAddStudents;
