// components/StudentChat.js
import React, { useState, useEffect } from "react";
import axios from "axios";

function StudentChat() {
  const [messages, setMessages] = useState([]);
  const [msg, setMsg] = useState("");

  const fetchMessages = async () => {
    const res = await axios.get("/api/student/messages/", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("studentToken")}`
      }
    });
    setMessages(res.data);
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const sendMessage = async () => {
    await axios.post(
      "/api/student/messages/",
      { message: msg },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("studentToken")}`
        }
      }
    );
    setMsg("");
    fetchMessages();
  };

  const downloadHistory = () => {
    window.open("/api/student/messages/download", "_blank");
  };

  return (
    <div>
      <h2>Chat with Admin</h2>
      <div className="chat-box">
        {messages.map((m, i) => (
          <div key={i}>
            <strong>{m.sender}</strong>: {m.text}
          </div>
        ))}
      </div>
      <input
        value={msg}
        onChange={(e) => setMsg(e.target.value)}
        placeholder="Type a message"
      />
      <button onClick={sendMessage}>Send</button>
      <button onClick={downloadHistory}>Download Chat History</button>
    </div>
  );
}

export default StudentChat;
