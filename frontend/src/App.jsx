import { useState } from "react";

function App() {
  const [title, setTitle] = useState("");
  const [provider, setProvider] = useState("zoom");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [createdMeeting, setCreatedMeeting] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setCreatedMeeting(null);

    try {
      const res = await fetch("/api/meetings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          provider,
          meeting_url: meetingUrl,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setCreatedMeeting(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      <h1>Meeting Participation Analyzer</h1>
      <p>Paste a meeting link and start tracking (dummy step for now).</p>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          Title
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Weekly sync"
            required
            style={{ width: "100%", padding: 8 }}
          />
        </label>

        <label>
          Provider
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            style={{ width: "100%", padding: 8 }}
          >
            <option value="zoom">Zoom</option>
            <option value="gmeet">Google Meet</option>
            <option value="teams">Microsoft Teams</option>
          </select>
        </label>

        <label>
          Meeting URL
          <input
            type="url"
            value={meetingUrl}
            onChange={(e) => setMeetingUrl(e.target.value)}
            placeholder="https://zoom.us/j/123..."
            required
            style={{ width: "100%", padding: 8 }}
          />
        </label>

        <button type="submit" style={{ padding: 10, fontWeight: "bold", cursor: "pointer" }}>
          Start Tracking (Mock)
        </button>
      </form>

      {error && (
        <p style={{ color: "red", marginTop: 16 }}>
          Error: {error}
        </p>
      )}

      {createdMeeting && (
        <div style={{ marginTop: 24, padding: 16, border: "1px solid #ccc", borderRadius: 8 }}>
          <h2>Meeting Created</h2>
          <p><strong>ID:</strong> {createdMeeting.id}</p>
          <p><strong>Title:</strong> {createdMeeting.title}</p>
          <p><strong>Provider:</strong> {createdMeeting.provider}</p>
          <p><strong>Status:</strong> {createdMeeting.status}</p>
          <p><strong>Recall Bot ID:</strong> {createdMeeting.recall_bot_id || "pending / unknown"}</p>
        </div>
      )}

    </div>
  );
}

export default App;
