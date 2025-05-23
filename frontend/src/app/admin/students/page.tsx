'use client';

import AdminHeader from '@/components/AdminHeader';
import { useEffect, useState } from 'react';
import api from '@/utils/api';
import '../styles.css'

interface Student {
  id: number;
  name: string;
  email: string;
  degreeCompleted: boolean;
}

export default function StudentList() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStudents = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/students/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setStudents(response.data);
    } catch {
      setError('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  return (
    <div>
      <AdminHeader />
      <main className="main-section">
        <h2 className="stu-heading">Student Management</h2>
        {loading && <p>Loading students...</p>}
        {error && <p className="err">{error}</p>}
        {!loading && !error && (
        <table className="student-table">
  <thead>
    <tr className="header-row">
      <th>ID</th>
      <th>Name</th>
      <th>Email</th>
      <th>Degree Completed</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {students.map((student) => (
      <tr key={student.id} className="body-row">
        <td>{student.id}</td>
        <td>{student.name}</td>
        <td>{student.email}</td>
        <td>{student.degreeCompleted ? 'Yes' : 'No'}</td>
        <td className="action-buttons">
          <button className="btn edit">Edit</button>
          <button className="btn delete">Delete</button>
          {!student.degreeCompleted && (
            <button className="btn complete">Mark Completed</button>
          )}
        </td>
      </tr>
    ))}
  </tbody>
</table>

        )}
      </main>
    </div>
  );
}
