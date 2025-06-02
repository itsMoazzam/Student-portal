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
import CategorizeStudent from "./components/category/CategorizeStudent";
import TaskPanel from "./components/Student/TaskPanel";
import ChatPanel from "./components/Student/StudentChat";
import PortfolioPage from "./components/Student/PortfolioManager";
import AssignTask from "./components/AssignTask";
import AddCategory from "./components/category/AddCategory";

const PrivateRoute = ({ element, role }) => {
  const { user } = useAuth();
  console.log(user);
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
          <Route
            path="/admin/students"
            element={<PrivateRoute element={<StudentList />} role="admin" />}
          />
          <Route
            path="/admin/create-student"
            element={<PrivateRoute element={<CreateStudent />} role="admin" />}
          />
          <Route
            path="/admin/manage-students"
            element={<PrivateRoute element={<ManageStudents />} role="admin" />}
          />

          <Route
            path="/admin/messages"
            element={<PrivateRoute element={<StudentList />} role="admin" />}
          />
          <Route path="/certificate" element={<CertificatePage />} />
          <Route
            path="/admin/student-categories"
            element={
              <PrivateRoute element={<CategorizeStudent />} role="admin" />
            }
          />
          <Route
            path="/admin/upload-certificate"
            element={
              <PrivateRoute element={<UploadCertificate />} role="admin" />
            }
          />
          <Route
            path="/admin/bulk-add-students"
            element={
              <PrivateRoute element={<BulkAddStudents />} role="admin" />
            }
          />
          <Route
            path="/admin/add-category"
            element={<PrivateRoute element={<AddCategory />} role="admin" />}
          />
          <Route
            path="/admin/assign-task"
            element={<PrivateRoute element={<AssignTask />} role="admin" />}
          />
          <Route
            path="/admin/review-submissions"
            element={<UploadCertificate />}
          />
          <Route path="/admin/student-reports" element={<StudentList />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/admin"
            element={<PrivateRoute element={<AdminDashboard />} role="admin" />}
          />

          <Route
            path="/student"
            element={
              <PrivateRoute
                role="student"
                element={<StudentDashboard />}
              ></PrivateRoute>
            }
          />
          <Route path="/student/tasks" element={<TaskPanel />} />
          <Route path="/student/chat" element={<ChatPanel />} />
          <Route path="/student/portfolio" element={<PortfolioPage />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
