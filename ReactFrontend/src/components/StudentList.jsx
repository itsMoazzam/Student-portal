import React, { useEffect, useState } from "react";
import API from "../api/api";

const StudentList = () => {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    API.get("/students/")
      .then((res) => setStudents(res.data))

      .catch((err) => console.error("Error fetching students", err));
  }, []);

  return (
    <div className="student-list">
      <h2>Enroll Students</h2>
      <table
        border="1"
        cellPadding="10"
        style={{ borderCollapse: "collapse", width: "100%" }}
      >
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Degree Completed</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {students.map((student) => (
            <tr key={student.id}>
              <td>{student.id}</td>
              <td>{student.user.username}</td>
              <td>{student.user.email}</td>
              <td>{student.degree_completed ? "Yes" : "No"}</td>
              <td>{new Date(student.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StudentList;
