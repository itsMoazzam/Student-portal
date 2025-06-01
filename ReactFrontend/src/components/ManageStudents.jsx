import React, { useEffect, useState } from "react";
import API from "../api/api";
import { Button, TextField } from "@mui/material";
// import "../styles/ManageStudents.css";

const ManageStudents = () => {
  const [students, setStudents] = useState([]);
  const [editingStudent, setEditingStudent] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    marks: ""
  });

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = () => {
    API.get("/students/")
      .then((res) => setStudents(res.data))
      .catch((err) => console.error("Error fetching students", err));
  };

  const handleEdit = (student) => {
    setEditingStudent(student.id);
    setFormData({
      name: student.name,
      email: student.email,
      marks: student.marks || ""
    });
  };

  const handleDelete = (id) => {
    API.delete(`/students/${id}/`)
      .then(() => fetchStudents())
      .catch((err) => console.error("Error deleting student", err));
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleUpdate = (e) => {
    e.preventDefault();
    API.put(`/students/${editingStudent}/`, formData)
      .then(() => {
        setEditingStudent(null);
        fetchStudents();
      })
      .catch((err) => console.error("Error updating student", err));
  };

  return (
    <div className="manage-students">
      <h2>Manage Students</h2>
      {students.map((student) => (
        <div key={student.id} className="student-item">
          {editingStudent === student.id ? (
            <form onSubmit={handleUpdate}>
              <TextField
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
              <TextField
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
              <TextField
                label="Marks"
                name="marks"
                type="number"
                value={formData.marks}
                onChange={handleChange}
              />
              <Button type="submit" variant="contained" color="primary">
                Update
              </Button>
              <Button
                variant="outlined"
                onClick={() => setEditingStudent(null)}
              >
                Cancel
              </Button>
            </form>
          ) : (
            <>
              <p>
                <strong>{student.name}</strong> - {student.email} - Marks:{" "}
                {student.marks || "N/A"}
              </p>
              <Button variant="outlined" onClick={() => handleEdit(student)}>
                Edit
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={() => handleDelete(student.id)}
              >
                Delete
              </Button>
            </>
          )}
        </div>
      ))}
    </div>
  );
};

export default ManageStudents;
