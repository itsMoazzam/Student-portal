'use client';

import AdminHeader from '@/components/AdminHeader';
import { useRouter } from 'next/navigation';
import Button from '@mui/material/Button';

import './styles.css'

const AdminDashboard = () => {
  const router = useRouter();
  return (
    <div>
      <AdminHeader />
      <main className="main-section">
        <h2 className="stu-heading">Welcome, Admin</h2>
        <p className="admin-description">Manage students and certificates here.</p>

        <div className="admin-grid">
          {/* View All Students */}
          <div className="admin-card">
            <h3 className="card-title">All Students</h3>
            <p className="card-description">Browse and manage all registered students.</p>
            <Button
              onClick={() => router.push('/admin/students')}
              variant="contained"
              color="primary">
              View Students
            </Button>
          </div>

          {/* Create New Student */}
          <div className="admin-card">
            <h3 className="card-title">Create Student</h3>
            <p className="card-description">Add a new student to the system.</p>
            <Button
              onClick={() => router.push('/admin/create-student')}
              variant="contained"
              color="success">
              Add Student
            </Button>
          </div>

          {/* Degree Completion */}
          <div className="admin-card">
            <h3 className="card-title">Mark Degree Completed</h3>
            <p className="card-description">Update student status after graduation.</p>
            <Button
              onClick={() => router.push('/admin/complete-degree')}
              variant='contained'
              color='warning'

            >
              Mark Completed
            </Button>
          </div>

          {/* Upload Certificate */}
          <div className="admin-card">
            <h3 className="card-title">Upload Certificate</h3>
            <p className="card-description">Attach certificate to student profile.</p>
            <Button
              onClick={() => router.push('/admin/upload-certificate')}
              variant="contained"
              color="secondary"
            >
              Upload Now
            </Button>
          </div>
        </div>
      </main>

    </div>
  );
}


export default AdminDashboard;