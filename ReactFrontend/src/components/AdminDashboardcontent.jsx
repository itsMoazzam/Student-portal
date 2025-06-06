import { useNavigate } from "react-router-dom";
import { Button, Grid } from "@mui/material";
import {
  Users,
  UserPlus,
  ListOrdered,
  Upload,
  UserCog,
  FolderPlus,
  ClipboardList,
  MessageCircle,
  FileText
} from "lucide-react";
import CategoryIcon from "@mui/icons-material/Category";

const AdminDashboardButtons = () => {
  const navigate = useNavigate();

  const buttons = [
    {
      label: "Student List",
      icon: <Users size={28} />,
      route: "/admin/students"
    },
    {
      label: "Create Student",
      icon: <UserPlus size={28} />,
      route: "/admin/create-student"
    },
    {
      label: "Manage Students",
      icon: <UserCog size={28} />,
      route: "/admin/manage-students"
    },
    {
      label: "Upload Certificate",
      icon: <Upload size={28} />,
      route: "/admin/upload-certificate"
    },
    {
      label: "Bulk Add Students",
      icon: <ListOrdered size={28} />,
      route: "/admin/bulk-add-students"
    },
    {
      label: "Student Categories",
      icon: <FolderPlus size={28} />,
      route: "/admin/student-categories"
    },
    {
      label: "Assign Task",
      icon: <ClipboardList size={28} />,
      route: "/admin/assign-task"
    },
    {
      label: "Review Submissions",
      icon: <ClipboardList size={28} />,
      route: "/admin/review-submissions"
    },
    {
      label: "Messaging System",
      icon: <MessageCircle size={28} />,
      route: "/admin/messages"
    },
    {
      label: "Add categories",
      icon: <CategoryIcon size={28} />,
      route: "/admin/add-category"
    },
    {
      label: "Reports & Certificates",
      icon: <FileText size={28} />,
      route: "/admin/student-reports"
    }
  ];

  return (
    <Grid container spacing={3} justifyContent="center">
      {buttons.map((btn, idx) => (
        <Grid item xs={12} key={idx}>
          <Button
            variant="contained"
            fullWidth
            onClick={() => navigate(btn.route)}
            style={{ flexDirection: "column", padding: "20px" }}
          >
            {btn.icon}
            {btn.label}
          </Button>
        </Grid>
      ))}
    </Grid>
  );
};

export default AdminDashboardButtons;
