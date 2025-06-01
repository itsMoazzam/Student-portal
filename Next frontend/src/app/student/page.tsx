'use client';

import StudentHeader from '@/components/StudentHeader';
import { useEffect, useState } from 'react';
import api from '@/utils/api';
import './styles.css'

interface StudentProfile {
  id: number;
  name: string;
  email: string;
  degreeCompleted: boolean;
  certificateUrl: string | null;
}

export default function StudentDashboard() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/dashboard/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setProfile(response.data);
    } catch {
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  return (
    <div>
      <StudentHeader />
      <main className="dashboard-main">
        <h2 className="dashboard-heading">Student Dashboard</h2>
        <p className="dashboard-subtext">View profile and academic status.</p>

        {loading && <p>Loading profile...</p>}
        {error && <p className="error-text">{error}</p>}
        {profile && (
          <div className="profile-card">
            <p><strong>Name:</strong> {profile.name}</p>
            <p><strong>Email:</strong> {profile.email}</p>
            <p><strong>Degree Status:</strong> {profile.degreeCompleted ? 'Completed' : 'In Progress'}</p>
            {profile.degreeCompleted && profile.certificateUrl ? (
              <div className="certificate-section">
                <p className="certificate-label"><strong>Certificate:</strong></p>
                <a
                  href={profile.certificateUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="certificate-button"
                >
                  View Certificate
                </a>
              </div>
            ) : (
              <p className="certificate-unavailable">Certificate not available yet.</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
