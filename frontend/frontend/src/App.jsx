import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);


// file upload function
  const handleFileUpload = async (e) =>{
    const file = e.target.files[0]; 
    if(!file) return;

    const formData = new FormData(); // form data pentru upload
    formData.append("file", file); // adauga fisierul in form data

    try {
      const response = await fetch("http://127.0.0.1:8000/upload-pdf/", {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      console.log("File uploaded is: ", data);

      setMessages(prev => [...prev, {role: "system", content: `File ${data.filename}" uploaded successfully!`
      }]);
    } catch (error){
      console.error("error uploading file: ",error);
    }
  };

  // submit chat function
  const handleSubmit = async () => {
    if (!question.trim()) return;

    const userQuestion = question;

    // msg userului
    setMessages(prev => [...prev, { role: "user", content: userQuestion }]);
    setQuestion("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userQuestion,
          history: messages
        })
      });

      const data = await response.json();

      // rsp AI in UI
      setMessages(prev => [...prev, { role: "assistant", content: data.answer }]);

    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="app-container">
      <h1>AI DOCUMENT ANALYZER</h1>

      <input type="file" onChange={handleFileUpload} />

      <div className="chat-container">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <div className="input-row">
        <input
          type="text"
          placeholder="Please ask something..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={handleSubmit}>Send</button>
      </div>
    </div>
  );


}

export default App;
