import { useEffect, useState } from 'react';
import StudentHeader from '@/components/StudentHeader';
import CertificateViewer from '@/components/CertificateViewer';
import api from '@/utils/api';
import '../styles.css'

const CertificatePage = () => {
  const [certificateUrl, setCertificateUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCertificate = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await api.get('/certificate/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setCertificateUrl(response.data.url);
      } catch {
        setError('Failed to load certificate.');
      } finally {
        setLoading(false);
      }
    };
    fetchCertificate();
  }, []);

  return (
    <div>
      <StudentHeader />
      <main className="dashboard-main">
        {loading && <p>Loading certificate...</p>}
        {error && <p className="error-text">{error}</p>}
        {!loading && !error && certificateUrl && (
          <CertificateViewer url={certificateUrl} />
        )}
      </main>
    </div>
  );
}


export default CertificatePage