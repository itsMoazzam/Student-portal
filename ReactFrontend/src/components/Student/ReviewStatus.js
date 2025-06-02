// components/ReviewStatus.js
import React, { useEffect, useState } from "react";
import axios from "axios";

function ReviewStatus() {
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    axios
      .get("/api/student/reviews/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("studentToken")}`
        }
      })
      .then((res) => {
        setReviews(res.data);
      });
  }, []);

  return (
    <div>
      <h2>Task Review Status</h2>
      <ul>
        {reviews.map((r, index) => (
          <li key={index}>
            Task: {r.taskTitle} - Status: {r.status} - Feedback: {r.feedback}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ReviewStatus;
