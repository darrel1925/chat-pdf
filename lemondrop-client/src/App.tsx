import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import axios from 'axios';

const SSEComponent: React.FC = () => {

  const [message, setMessage] = useState("");

  useEffect(() => {
    const url = new URL('http://localhost:8000/stream');
    url.searchParams.append('thread_id', 'thread_aYVuUpHCU5XLfNwyJrEovkIE');
    url.searchParams.append('message', 'Tell me a joke!');
    const eventSource = new EventSource(url.toString());

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.end_of_stream) {
        eventSource.close();
        return;
      }

      setMessage((prev) => prev + data.message);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <div>This is  a component</div>
      <div>My message: {message}</div>
    </div>
  );
};


function App() {
  return (
      <Router>
        <Routes>
          <Route path="/" element={<SSEComponent />} />
        </Routes>
      </Router>
  );
}

export default App;
