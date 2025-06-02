// PortfolioManager.jsx
import { useEffect, useState } from "react";
import API from "../../api/api";

const PortfolioManager = () => {
  const [profile, setProfile] = useState({
    github: "",
    linkedin: "",
    is_public: false,
    is_approved: false
  });
  const [notification, setNotification] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await API.get("/student/profile/");
        setProfile(response.data);
      } catch (err) {
        console.error("Error fetching profile:", err);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async () => {
    try {
      await API.put("/student/profile/", profile);
      setNotification("Profile saved successfully!");
      setTimeout(() => setNotification(""), 3000);
    } catch (err) {
      console.error("Error saving profile:", err);
      setNotification("Error saving profile");
    }
  };

  const requestPublic = async () => {
    try {
      await API.post("/student/profile/request-public/");
      setNotification(
        "Public visibility requested. Waiting for admin approval."
      );
      setTimeout(() => setNotification(""), 5000);
      // Refresh profile
      const response = await API.get("/student/profile/");
      setProfile(response.data);
    } catch (err) {
      console.error("Error requesting public visibility:", err);
    }
  };

  return (
    <div className="portfolio-manager">
      <h2>Your Public Portfolio</h2>
      {notification && <div className="notification">{notification}</div>}

      <div className="form-group">
        <label>GitHub Profile URL</label>
        <input
          type="url"
          value={profile.github}
          onChange={(e) => setProfile({ ...profile, github: e.target.value })}
          placeholder="https://github.com/yourusername"
        />
      </div>

      <div className="form-group">
        <label>LinkedIn Profile URL</label>
        <input
          type="url"
          value={profile.linkedin}
          onChange={(e) => setProfile({ ...profile, linkedin: e.target.value })}
          placeholder="https://linkedin.com/in/yourusername"
        />
      </div>

      <div className="visibility-status">
        <p>
          Current Status:{" "}
          {profile.is_approved && profile.is_public
            ? "PUBLIC (Visible to everyone)"
            : profile.is_approved
            ? "READY (Approved but not public)"
            : "PRIVATE (Not approved)"}
        </p>
      </div>

      <div className="action-buttons">
        <button onClick={handleSave} className="save-btn">
          Save Changes
        </button>

        {!profile.is_public && profile.is_approved && (
          <button
            onClick={() => setProfile({ ...profile, is_public: true })}
            className="go-public-btn"
          >
            Go Public
          </button>
        )}

        {!profile.is_approved && (
          <button onClick={requestPublic} className="request-approval-btn">
            Request Admin Approval
          </button>
        )}
      </div>
    </div>
  );
};

export default PortfolioManager;
