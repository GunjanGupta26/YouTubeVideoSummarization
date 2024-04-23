import axios from "axios";
import { useState } from "react";
import './App.css'
function App() {
  const [disabled, setDisabled] = useState(true);
  const [inputValue, setInputValue] = useState("");
  const [response, setResponse] = useState("");
  const handleInputChange = (event) => {
    setInputValue(event.target.value);
    if (event.target.length === 0) {
      setDisabled(true);
    } else {
      setDisabled(false);
    }
  };

  const handleClick = async () => {
    axios
      .post("http://127.0.0.1:5000", {
        yt_link: inputValue,
      })
      .then((res) => {
        setResponse(res.data[0])
        console.log(res.data[0])
      });
    setInputValue("");
  };
  return (
    <div>
      <h1>Youtube Video Summarizer</h1>
      <h2>Navigate YouTube with Ease: Concise Video Summaries</h2>
      <p>Paste your youtube link below</p>
      <input
        type="text"
        value={inputValue}
        onChange={(event) => handleInputChange(event)}
      />
      <button onClick={handleClick} disabled={disabled} type="submit">
        Click
      </button>
      <p>{response}</p>
    </div>
  );
}

export default App;
