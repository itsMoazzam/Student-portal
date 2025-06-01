import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate
} from "react-router-dom";
import Login from "./pages/Login";
import AdminDashboard from "./pages/AdminDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import CertificatePage from "./pages/CertificatePage";
import { AuthProvider, useAuth } from "./context/AuthContext";
import "./App.css";
import UploadCertificate from "./components/UploadCertificate";
import StudentList from "./components/StudentList";
import CreateStudent from "./components/CreateStudent";
import ManageStudents from "./components/ManageStudents";
import BulkAddStudents from "./components/BulkAddStudents";

const PrivateRoute = ({ element, role }) => {
  const { user } = useAuth();
  console.log(element);
  if (!user) return <Navigate to="/login" />;
  if (user.role !== role) return <Navigate to="/login" />;
  return element;
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/admin/students" element={<StudentList />} />
          <Route path="/admin/create-student" element={<CreateStudent />} />
          <Route path="/admin/manage-students" element={<ManageStudents />} />
          <Route
            path="/admin/upload-certificate"
            element={<UploadCertificate />}
          />
          <Route path="/admin/student-categories" element={<StudentList />} />
          <Route
            path="/admin/bulk-add-students"
            element={<BulkAddStudents />}
          />
          <Route path="/admin/assign-task" element={<ManageStudents />} />
          <Route
            path="/admin/review-submissions"
            element={<UploadCertificate />}
          />
          <Route path="/admin/messages" element={<StudentList />} />
          <Route path="/admin/student-reports" element={<StudentDashboard />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/admin"
            element={<PrivateRoute element={<AdminDashboard />} role="admin" />}
          />
          <Route
            path="/student"
            element={
              <PrivateRoute element={<StudentDashboard />} role="student" />
            }
          />
          <Route
            path="/certificate"
            element={
              <PrivateRoute element={<CertificatePage />} role="student" />
            }
          />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
