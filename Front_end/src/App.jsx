import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [pdfName, setPdfName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [savingHistory, setSavingHistory] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    // Tạo session id ngắn, lưu vào localStorage để giữ lịch sử
    let sid = localStorage.getItem('chat_session_id');
    if (!sid) {
      sid = Math.random().toString(36).substring(2, 10);
      localStorage.setItem('chat_session_id', sid);
    }
    return sid;
  });
  const [allSessions, setAllSessions] = useState([]); // Danh sách các session
  const [selectedSession, setSelectedSession] = useState(null); // Session đang xem
  const fileInputRef = useRef();

  // Đổi URL này thành địa chỉ backend của bạn nếu cần
  const API_BASE = 'http://localhost:8085';

  // Lấy danh sách file lịch sử (dựa vào file trong data/chat_sessions)
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await fetch(`${API_BASE}/list_sessions/`);
        if (res.ok) {
          const data = await res.json();
          setAllSessions(data.sessions || []);
        }
      } catch {}
    };
    fetchSessions();
  }, []);

  // Tải lịch sử khi load lại trang hoặc chọn session khác
  useEffect(() => {
    const sid = selectedSession || sessionId;
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/history/${sid}`);
        if (res.ok) {
          const data = await res.json();
          setChatHistory(data.history || []);
        }
      } catch {}
    };
    fetchHistory();
  }, [sessionId, selectedSession]);

  // Upload PDF
  const handleUpload = async (e) => {
    e.preventDefault();
    const file = fileInputRef.current.files[0];
    if (!file) return;
    setUploading(true);
    setUploadSuccess(false);
    setPdfName(file.name);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/upload_pdf/`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        setUploadSuccess(true);
        // Reset chat khi upload PDF mới
        setChatHistory([]);
        // Tạo session mới cho mỗi lần upload PDF khác
        const newSessionId = Math.random().toString(36).substring(2, 10);
        setSessionId(newSessionId);
        localStorage.setItem('chat_session_id', newSessionId);
        setSelectedSession(newSessionId);
        // Sau khi upload, reload lại danh sách session
        fetch(`${API_BASE}/list_sessions/`).then(res => res.json()).then(data => setAllSessions(data.sessions || []));
        alert('Tệp PDF đã upload và embeding thành công!');
      } else {
        setUploadSuccess(false);
        alert('Lỗi upload PDF!');
      }
    } catch (err) {
      alert('Lỗi kết nối backend!');
    }
    setUploading(false);
  };

  // Gửi câu hỏi
  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    // Không cần setAnswer ở đây nữa
    try {
      const formData = new FormData();
      formData.append('question', question);
      const res = await fetch(`${API_BASE}/ask/`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        // Thêm vào lịch sử, KHÔNG setAnswer nữa
        const newHistory = [...chatHistory, { role: 'user', content: question }, { role: 'assistant', content: data.answer }];
        setChatHistory(newHistory);
        saveHistory(sessionId, newHistory);
      } else {
        // Nếu lỗi, có thể hiển thị thông báo lỗi như một tin nhắn assistant
        const newHistory = [...chatHistory, { role: 'user', content: question }, { role: 'assistant', content: data.error || 'Lỗi truy vấn!' }];
        setChatHistory(newHistory);
        saveHistory(sessionId, newHistory);
      }
    } catch (err) {
      const newHistory = [...chatHistory, { role: 'user', content: question }, { role: 'assistant', content: 'Lỗi kết nối backend!' }];
      setChatHistory(newHistory);
      saveHistory(sessionId, newHistory);
    }
    setQuestion('');
  };

  // Lưu lịch sử trò chuyện, thêm tên session nếu có
  const saveHistory = async (sid, history, sessionName, callback) => {
    setSavingHistory(true);
    try {
      await fetch(`${API_BASE}/save_history/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid, history, session_name: sessionName }),
      });
      if (typeof callback === 'function') callback();
    } catch {}
    setSavingHistory(false);
  };

  // Tạo đoạn chat mới (reset)
  const handleNewChat = () => {
    if (chatHistory.length > 0) {
      let sessionName = window.prompt('Đặt tên cho đoạn chat này để lưu vào lịch sử:', '');
      if (sessionName !== null) {
        sessionName = sessionName.trim() || 'Chưa đặt tên';
        // Sau khi lưu xong thì reload lại danh sách session
        saveHistory(sessionId, chatHistory, sessionName, () => {
          fetch(`${API_BASE}/list_sessions/`).then(res => res.json()).then(data => setAllSessions(data.sessions || []));
        });
      }
    }
    // Tạo session mới
    const newSessionId = Math.random().toString(36).substring(2, 10);
    setSessionId(newSessionId);
    localStorage.setItem('chat_session_id', newSessionId);
    setSelectedSession(newSessionId);
    setChatHistory([]);
    setAnswer('');
    setPdfName('');
    setUploadSuccess(false);
    // Luôn cập nhật lại danh sách session sau khi tạo mới
    fetch(`${API_BASE}/list_sessions/`).then(res => res.json()).then(data => setAllSessions(data.sessions || []));
  };

  // Xoá session
  const handleDeleteSession = async (sid) => {
    if (!window.confirm('Bạn có chắc muốn xoá đoạn chat này?')) return;
    try {
      const res = await fetch(`${API_BASE}/history/${sid}`, { method: 'DELETE' });
      if (res.ok) {
        setAllSessions(sessions => sessions.filter(s => s.id !== sid));
        // Nếu đang xem session bị xoá thì chuyển về session hiện tại
        if ((selectedSession || sessionId) === sid) {
          setSelectedSession(null);
          setChatHistory([]);
        }
      } else {
        alert('Xoá không thành công!');
      }
    } catch {
      alert('Lỗi kết nối khi xoá!');
    }
  };

  return (
    <div className="gpt-layout">
      <aside className="gpt-sidebar">
        <h2>Lịch sử chat</h2>
        <ul className="gpt-session-list">
          <li
            key="current-session"
            className={!selectedSession || selectedSession === sessionId ? 'active' : ''}
            style={{ fontWeight: 'bold', color: '#1976d2', cursor: 'pointer' }}
            onClick={() => setSelectedSession(null)}
          >
            ⬅️ Quay lại đoạn chat hiện tại
          </li>
          {allSessions.map(session => (
            <li
              key={session.id}
              className={session.id === (selectedSession || sessionId) ? 'active' : ''}
              onClick={() => setSelectedSession(session.id)}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            >
              <span style={{ flex: 1, cursor: 'pointer' }}>
                {session.id === sessionId ? 'Phiên hiện tại' : (session.name || session.id)}
              </span>
              {session.id !== sessionId && (
                <button
                  title="Xoá đoạn chat"
                  style={{ marginLeft: 8, color: 'red', background: 'none', border: 'none', cursor: 'pointer' }}
                  onClick={e => { e.stopPropagation(); handleDeleteSession(session.id); }}
                >
                  🗑️
                </button>
              )}
            </li>
          ))}
        </ul>
      </aside>
      <div className="gpt-container">
        <header className="gpt-header">
          <button className="gpt-new-chat-btn" onClick={handleNewChat}>+ Đoạn chat mới</button>
          <div className="gpt-upload-form">
            <input
              type="file"
              accept="application/pdf"
              ref={fileInputRef}
              id="pdf-upload-input"
              style={{ display: 'none' }}
              onChange={e => {
                // Khi chọn file xong thì submit form upload
                if (fileInputRef.current.files[0]) {
                  handleUpload({ preventDefault: () => {} });
                }
              }}
            />
            <label htmlFor="pdf-upload-input">
              <button
                type="button"
                disabled={uploading}
                onClick={() => fileInputRef.current.click()}
              >
                {uploading ? 'Đang tải lên...' : 'Đọc file PDF'}
              </button>
            </label>
          </div>
          {pdfName && (
            <div className="gpt-pdf-status">
              <span>Đã chọn: <b>{pdfName}</b></span>
              {uploadSuccess && <span style={{color:'green',marginLeft:8}}>✔️ Đã upload thành công!</span>}
            </div>
          )}
        </header>
        <main className="gpt-main">
          <div className="gpt-chat-window">
            {chatHistory.length === 0 && (
              <div className="gpt-empty-chat">Hãy tải PDF và bắt đầu trò chuyện!</div>
            )}
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`gpt-msg gpt-msg-${msg.role}`}>
                <div className="gpt-msg-content">{msg.role === 'user' ? '🧑‍💻' : '🤖'} {msg.content}</div>
              </div>
            ))}
          </div>
          <form onSubmit={handleAsk} className="gpt-chat-input-form" style={{ display: selectedSession && selectedSession !== sessionId ? 'none' : 'flex' }}>
            <input
              type="text"
              placeholder="Nhập câu hỏi..."
              value={question}
              onChange={e => setQuestion(e.target.value)}
              disabled={!uploadSuccess}
              className="gpt-chat-input"
            />
            <button type="submit" disabled={!uploadSuccess || !question.trim()}>Gửi</button>
          </form>
          {savingHistory && <div className="gpt-saving">Đang lưu lịch sử...</div>}
        </main>
      </div>
    </div>
  );
}

export default App;
