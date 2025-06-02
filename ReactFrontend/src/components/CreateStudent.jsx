import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/api";
import {
  TextField,
  Button,
  IconButton,
  InputAdornment,
  MenuItem
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";

const CreateStudent = () => {
  const [formData, setFormData] = useState({
    fullName: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "student", // default
    category: ""
  });

  const [categories, setCategories] = useState([]); // Load categories if dynamic
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // You can fetch categories from backend if needed
    setCategories(["Python", "JavaScript", "AI", "Full Stack"]);
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      setError("No authentication token found. Please log in again.");
      return;
    }

    // Prepare payload
    const payload = {
      full_name: formData.fullName,
      username: formData.username, // May be empty, backend handles fallback
      email: formData.email,
      password: formData.password,
      role: formData.role,
      category: formData.category
    };

    API.post("/students/create/", payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    })
      .then(() => {
        alert("Student created and email sent.");
        navigate("/admin");
      })
      .catch((err) => {
        console.error("Error creating student", err);
        setError(
          "Failed to create student. Please check the inputs or try again."
        );
      });
  };

  return (
    <div style={{ maxWidth: 400, margin: "auto" }}>
      <h2>Create Student</h2>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Full Name"
          name="fullName"
          value={formData.fullName}
          onChange={handleChange}
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Username (optional)"
          name="username"
          value={formData.username}
          onChange={handleChange}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Password"
          name="password"
          type={showPassword ? "text" : "password"}
          value={formData.password}
          onChange={handleChange}
          required
          fullWidth
          margin="normal"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            )
          }}
        />
        <TextField
          label="Confirm Password"
          name="confirmPassword"
          type={showConfirmPassword ? "text" : "password"}
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          fullWidth
          margin="normal"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  edge="end"
                >
                  {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            )
          }}
        />
        <TextField
          label="Role"
          name="role"
          value={formData.role}
          onChange={handleChange}
          required
          select
          fullWidth
          margin="normal"
        >
          <MenuItem value="student">Student</MenuItem>
          <MenuItem value="subadmin">Sub-Admin</MenuItem>
          <MenuItem value="admin">Admin</MenuItem>
        </TextField>

        <TextField
          label="Category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          required
          select
          fullWidth
          margin="normal"
        >
          {categories.map((cat) => (
            <MenuItem key={cat} value={cat}>
              {cat}
            </MenuItem>
          ))}
        </TextField>

        {error && <p style={{ color: "red" }}>{error}</p>}
        <Button type="submit" variant="contained" color="primary" fullWidth>
          Create Student
        </Button>
      </form>
    </div>
  );
};

export default CreateStudent;
