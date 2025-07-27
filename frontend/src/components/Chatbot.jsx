import { useEffect, useRef, useState } from "react";
import { API } from "../api";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: "system", content: "Ask me to create/read/update/delete customers!" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  const recognitionRef = useRef(null);

  useEffect(() => {
    // Setup Web Speech API
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setListening(true);
      recognition.onend = () => setListening(false);
      recognition.onerror = (e) => {
        setListening(false);
        console.error("Speech recognition error:", e);
      };
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => (prev ? prev + " " + transcript : transcript));
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleMic = () => {
    if (!recognitionRef.current) {
      alert("Speech Recognition not supported in this browser.");
      return;
    }
    if (listening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    try {
      const { data } = await API.post("/chatbot", { message: input });
      setMessages((m) => [
        ...m,
        { role: "assistant", content: JSON.stringify(data.result, null, 2) },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Error: " + err.message },
      ]);
    } finally {
      setInput("");
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Gemini Chatbot (CRUD via ADK Tools)</h2>

      <div className="h-64 overflow-y-auto bg-gray-50 p-3 rounded border mb-3">
        {messages.map((m, idx) => (
          <div key={idx} className="mb-2">
            <span className="font-bold">
              {m.role === "user" ? "You" : m.role === "system" ? "System" : "Assistant"}:
            </span>
            <pre className="whitespace-pre-wrap break-words">
              {m.content}
            </pre>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <input
          className="input flex-1"
          placeholder='e.g. "Create a customer Jane, 98765, MG Road"'
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          className={`mic-btn ${listening ? "active" : ""}`}
          title={listening ? "Stop" : "Start"} onClick={toggleMic}
        >
          🎙️
        </button>
        <button className="btn" onClick={send} disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
