// components/TaskPanel.js
import React, { useEffect, useState } from "react";
import axios from "axios";

function TaskPanel() {
  const [tasks, setTasks] = useState([]);
  // const [submissions, setSubmissions] = useState({});

  useEffect(() => {
    const fetchTasks = async () => {
      const res = await axios.get("/api/student/tasks/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("studentToken")}`
        }
      });
      setTasks(res.data);
    };
    fetchTasks();
  }, []);

  const handleSubmit = async (taskId) => {
    const githubLink = prompt("Enter your GitHub submission link:");
    if (!githubLink) return;

    await axios.post(
      `/api/student/submit-task/`,
      {
        taskId,
        githubLink
      },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("studentToken")}`
        }
      }
    );

    alert("Task submitted");
  };

  return (
    <div>
      <h2>Assigned Tasks</h2>
      {tasks.map((task) => (
        <div key={task.id} className="task-card">
          <h3>{task.title}</h3>
          <p>{task.description}</p>
          <p>Deadline: {task.deadline}</p>
          <button onClick={() => handleSubmit(task.id)}>
            Submit GitHub Link
          </button>
        </div>
      ))}
    </div>
  );
}

export default TaskPanel;
