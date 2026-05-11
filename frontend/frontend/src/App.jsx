import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [pdfList, setPdfList] = useState([]);
  const [activePdf, setActivePdf] = useState(null);

  // delete mode
  const [selectedForDelete, setSelectedForDelete] = useState([]);
  const [deleteMode, setDeleteMode] = useState(false);

  // upload file
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload-pdf/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("File uploaded:", data);

      setMessages((prev) => [
        ...prev,
        { role: "system", content: `File "${data.filename}" uploaded successfully!` },
      ]);

      fetchPdfList();
    } catch (error) {
      console.error("Upload error:", error);
    }
  };

  // fetch pdf list
  const fetchPdfList = async () => {
    const res = await fetch("http://127.0.0.1:8000/list-pdfs/");
    const data = await res.json();
    setPdfList(data.pdfs);
  };

  useEffect(() => {
    fetchPdfList();
  }, []);

  // chat submit
  const handleSubmit = async () => {
    if (!question.trim()) return;

    const userQuestion = question;

    setMessages((prev) => [...prev, { role: "user", content: userQuestion }]);
    setQuestion("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userQuestion,
          history: messages,
          pdf_name: activePdf,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
    }
  };

  // activate PDF
  const activatePdf = (pdf) => {
    if (!deleteMode) {
      setActivePdf(pdf);
    } else {
      toggleSelectForDelete(pdf);
    }
  };

  // select PDFs for delete
  const toggleSelectForDelete = (pdf) => {
    if (selectedForDelete.includes(pdf)) {
      setSelectedForDelete((prev) => prev.filter((p) => p !== pdf));
    } else {
      setSelectedForDelete((prev) => [...prev, pdf]);
    }
  };

  // confirm delete
  const handleDelete = async () => {
    await fetch("http://127.0.0.1:8000/delete-pdfs/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pdfs: selectedForDelete }),
    });

    fetchPdfList();
    setSelectedForDelete([]);
    setDeleteMode(false);
    if (selectedForDelete.includes(activePdf)) {
      setActivePdf(null);
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

      <div className="pdf-list">
        <h3>Loaded Documents</h3>

        <button onClick={() => setDeleteMode(!deleteMode)}>
          {deleteMode ? "Cancel Delete" : "Delete Documents"}
        </button>

        {deleteMode && selectedForDelete.length > 0 && (
          <button
            style={{
              background: "red",
              color: "white",
              marginLeft: "10px",
              padding: "5px 10px",
            }}
            onClick={handleDelete}
          >
            Confirm Delete ({selectedForDelete.length})
          </button>
        )}

        {pdfList.map((pdf, i) => (
          <div
            key={i}
            className={`pdf-item ${
              activePdf === pdf ? "selected" : ""
            } ${selectedForDelete.includes(pdf) ? "marked-delete" : ""}`}
            onClick={() => activatePdf(pdf)}
          >
            {deleteMode && (
              <input
                type="checkbox"
                checked={selectedForDelete.includes(pdf)}
                readOnly
              />
            )}
            {pdf}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
